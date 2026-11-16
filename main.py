import sys
import time
import pygame

from config import (
    TITLE, FPS, WINDOW_WIDTH, WINDOW_HEIGHT, P1, P2,
    PLAYER_VS_PLAYER, AI_VS_PLAYER, AI_VS_AI, MINIMAX, MCTS,
    MINIMAX_DEPTH, MCTS_ITERATION, AI_MOVE_DELAY,
)
from src.game_logic import GameState
from src.gui import GameGUI
from src.audio import AudioManager
from src.store import StoreManager
from src.ai.minimax import get_minimax_move
from src.ai.mcts import get_mcts_move
from src.logger import save_match_report

LOG_FILE = "logs/match_results.txt"


def compute_ai_move(state, ai_type):
    safe_moves = state.get_safe_moves()
    capturing_moves = state.get_capturing_moves()
    good_moves = set(safe_moves) | set(capturing_moves)
    stats = {}
    t0 = time.perf_counter()

    if ai_type == MINIMAX:
        total_boxes = state.row * state.col
        depth = MINIMAX_DEPTH if total_boxes <= 25 else min(MINIMAX_DEPTH, 3)
        move = get_minimax_move(state, depth=depth, time_limit=1.5, stats=stats)
        agent_name = "Minimax"
    else:
        move = get_mcts_move(state, iterations=MCTS_ITERATION, stats=stats)
        agent_name = "MCTS"

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    is_blunder = bool(good_moves) and (move not in good_moves)

    move_record = {
        "agent": agent_name,
        "player": state.curr_player,
        "time_ms": elapsed_ms,
        "blunder": is_blunder,
        **stats,
    }
    return move, move_record


def current_bot_type(mode, curr_player, selected_ai):
    if mode == AI_VS_AI:
        return MINIMAX if curr_player == P1 else MCTS
    if mode == AI_VS_PLAYER and curr_player == P2:
        return selected_ai
    return None


def is_match_in_progress(state):
    return state.last_move is not None and not state.is_game_over()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    audio = AudioManager()
    audio.play_bgm()
    store = StoreManager()
    gui = GameGUI(bgm_volume=audio.bgm_pct, sfx_volume=audio.sfx_pct, store=store)

    screen_state = "menu"
    mode = PLAYER_VS_PLAYER
    ai_type = MINIMAX
    rows, cols = 4, 4
    state = GameState(rows, cols)
    ai_wait_until = 0
    move_logs = []
    match_logged = False

    def apply_move_with_audio(move):
        completed = state.make_move(move)
        if completed > 0:
            audio.play_sfx("capture")
        else:
            audio.play_sfx("draw")

        if state.is_game_over():
            audio.play_sfx("win")

    def start_new_match():
        nonlocal state, ai_wait_until, move_logs, match_logged
        state = GameState(rows, cols)
        move_logs = []
        match_logged = False
        ai_wait_until = pygame.time.get_ticks() + int(AI_MOVE_DELAY * 1000) if mode == AI_VS_AI else 0

    def request_game_action(action):
        nonlocal screen_state
        if is_match_in_progress(state):
            gui.open_confirm(action)
        elif action == "menu":
            gui.reset_menu()
            screen_state = "menu"
        elif action == "restart":
            start_new_match()

    running = True
    while running:
        now = pygame.time.get_ticks()
        active_bot = None
        if screen_state == "playing" and not state.is_game_over() and gui.confirm_action is None:
            active_bot = current_bot_type(mode, state.curr_player, ai_type)
        is_ai_turn = active_bot is not None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Global mute toggle (S atau F10)
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_s, pygame.K_F10):
                audio.toggle_mute()

            elif screen_state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        audio.play_sfx("click")
                        if gui.menu_page == "size":
                            gui.menu_page = "mode"
                        elif gui.menu_page in ("mode", "settings"):
                            gui.menu_page = "home"
                        else:
                            running = False
                    elif event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                else:
                    prev_page = gui.menu_page
                    result = gui.handle_menu_event(event)
                    if result == "exit":
                        audio.play_sfx("click")
                        running = False
                    elif result == "test_sfx":
                        audio.play_sfx("capture")
                    elif result == "theme_changed":
                        audio.play_sfx("click")
                        audio.play_theme_bgm(gui.theme_name)
                    elif result in ("skin_changed", "buy_skin"):
                        audio.play_sfx("click")
                    elif isinstance(result, dict):
                        if result.get("resolution_changed"):
                            audio.play_sfx("click")
                            screen = pygame.display.set_mode(result["size"], pygame.SCALED)
                            gui.set_window_size(*result["size"])
                        elif result.get("audio_changed"):
                            audio.set_bgm_volume(result["bgm"])
                            audio.set_sfx_volume(result["sfx"])
                        else:
                            audio.play_sfx("click")
                            mode = result["mode"]
                            ai_type = result["ai"]
                            rows = result["rows"]
                            cols = result["cols"]
                            start_new_match()
                            screen_state = "playing"
                    elif gui.menu_page != prev_page:
                        audio.play_sfx("click")

            elif screen_state == "playing":
                was_confirming = gui.confirm_action is not None
                ui_action = gui.handle_game_ui_event(event, state)

                if ui_action in ("menu", "restart"):
                    audio.play_sfx("click")
                    request_game_action(ui_action)
                    continue
                elif ui_action == "handled":
                    if was_confirming and gui.confirm_action is None:
                        audio.play_sfx("click")
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        audio.play_sfx("click")
                        request_game_action("menu")
                    elif event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    elif event.key == pygame.K_r:
                        audio.play_sfx("click")
                        request_game_action("restart")
                    elif event.key == pygame.K_m:
                        audio.play_sfx("click")
                        request_game_action("menu")
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if state.is_game_over():
                        audio.play_sfx("click")
                        start_new_match()
                    elif not is_ai_turn:
                        move = gui.pos_to_move(event.pos, state)
                        if move is not None:
                            apply_move_with_audio(move)
                            if current_bot_type(mode, state.curr_player, ai_type) is not None:
                                ai_wait_until = pygame.time.get_ticks() + int(AI_MOVE_DELAY * 1000)

        if screen_state == "menu":
            gui.draw_menu(screen)
        else:
            hover = None
            if not state.is_game_over() and not is_ai_turn and gui.confirm_action is None:
                hover = gui.pos_to_move(pygame.mouse.get_pos(), state)
            gui.draw(screen, state, hover, mode=mode, ai_type=ai_type, ai_thinking=is_ai_turn)

        pygame.display.flip()

        if is_ai_turn and now >= ai_wait_until:
            move, record = compute_ai_move(state, active_bot)
            if move is not None:
                move_logs.append(record)
                apply_move_with_audio(move)
                if not state.is_game_over() and current_bot_type(mode, state.curr_player, ai_type) is not None:
                    ai_wait_until = pygame.time.get_ticks() + int(AI_MOVE_DELAY * 1000)

        # Simpan laporan performa ke .txt tepat satu kali saat match selesai
        if screen_state == "playing" and state.is_game_over() and not match_logged:
            labels = gui._player_labels(mode, ai_type)
            save_match_report(
                LOG_FILE, mode, rows, cols,
                labels[P1], labels[P2], state, move_logs,
            )
            match_logged = True

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
import sys
import pygame

from config import (
    TITLE, FPS, WINDOW_WIDTH, WINDOW_HEIGHT, P1, P2,
    PLAYER_VS_PLAYER, AI_VS_PLAYER, AI_VS_AI, MINIMAX, MCTS,
    MINIMAX_DEPTH, MCTS_ITERATION, AI_MOVE_DELAY,
)
from src.game_logic import GameState
from src.gui import GameGUI
from src.ai.minimax import get_minimax_move
from src.ai.mcts import get_mcts_move


def compute_ai_move(state, ai_type):
    if ai_type == MINIMAX:
        total_boxes = state.row * state.col
        depth = MINIMAX_DEPTH if total_boxes <= 25 else min(MINIMAX_DEPTH, 3)
        return get_minimax_move(state, depth=depth, time_limit=1.5)
    return get_mcts_move(state, iterations=MCTS_ITERATION)


def current_bot_type(mode, curr_player, selected_ai):
    if mode == AI_VS_AI:
        return MINIMAX if curr_player == P1 else MCTS
    if mode == AI_VS_PLAYER and curr_player == P2:
        return selected_ai
    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    gui = GameGUI()
    screen_state = "menu"
    mode = PLAYER_VS_PLAYER
    ai_type = MINIMAX
    rows, cols = 4, 4
    state = GameState(rows, cols)
    ai_wait_until = 0

    running = True
    while running:
        now = pygame.time.get_ticks()
        active_bot = None
        if screen_state == "playing" and not state.is_game_over():
            active_bot = current_bot_type(mode, state.curr_player, ai_type)
        is_ai_turn = active_bot is not None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif screen_state == "playing":
                    if event.key == pygame.K_r:
                        state = GameState(rows, cols)
                        ai_wait_until = pygame.time.get_ticks() + int(AI_MOVE_DELAY * 1000) if mode == AI_VS_AI else 0
                    elif event.key == pygame.K_m:
                        gui.reset_menu()
                        screen_state = "menu"
            elif screen_state == "menu":
                result = gui.handle_menu_event(event)
                if result == "exit":
                    running = False
                elif isinstance(result, dict):
                    mode = result["mode"]
                    ai_type = result["ai"]
                    rows = result["rows"]
                    cols = result["cols"]
                    state = GameState(rows, cols)
                    ai_wait_until = pygame.time.get_ticks() + int(AI_MOVE_DELAY * 1000) if mode == AI_VS_AI else 0
                    screen_state = "playing"
            elif screen_state == "playing" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state.is_game_over():
                    state = GameState(rows, cols)
                    ai_wait_until = pygame.time.get_ticks() + int(AI_MOVE_DELAY * 1000) if mode == AI_VS_AI else 0
                elif not is_ai_turn:
                    move = gui.pos_to_move(event.pos, state)
                    if move is not None:
                        state.make_move(move)
                        if current_bot_type(mode, state.curr_player, ai_type) is not None:
                            ai_wait_until = pygame.time.get_ticks() + int(AI_MOVE_DELAY * 1000)

        if screen_state == "menu":
            gui.draw_menu(screen)
        else:
            hover = None
            if not state.is_game_over() and not is_ai_turn:
                hover = gui.pos_to_move(pygame.mouse.get_pos(), state)
            gui.draw(screen, state, hover, mode=mode, ai_type=ai_type, ai_thinking=is_ai_turn)

        pygame.display.flip()

        if is_ai_turn and now >= ai_wait_until:
            move = compute_ai_move(state, active_bot)
            if move is not None:
                state.make_move(move)
                if not state.is_game_over() and current_bot_type(mode, state.curr_player, ai_type) is not None:
                    ai_wait_until = pygame.time.get_ticks() + int(AI_MOVE_DELAY * 1000)

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
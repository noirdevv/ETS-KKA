import os
import pygame

from config import (
    P1, P2, P1_NAME, P2_NAME,
    PLAYER_VS_PLAYER, AI_VS_PLAYER, AI_VS_AI, MINIMAX, MCTS,
    MARGIN, WINDOW_WIDTH, WINDOW_HEIGHT, CLICK_TOLERANCE,
    COLOR_BG, COLOR_BAR, COLOR_DOT, COLOR_EMPTY_LINE,
    COLOR_TEXT, COLOR_MUTED, COLOR_WHITE,
    COLOR_P1, COLOR_P2, COLOR_BOX_P1, COLOR_BOX_P2,
    COLOR_BTN, COLOR_BTN_PRIMARY, COLOR_BTN_DISABLED,
    COLOR_TEXT_DISABLED, COLOR_TRACK, COLOR_FILL,
    UI_FONT_STACK, MONO_FONT_STACK, DISPLAY_TTF, MONO_TTF
)
from src.game_logic import HORIZONTAL, VERTICAL

LINE_THICK = 9
DOT_R = 8
HUD_HEIGHT = 105
FOOTER_HEIGHT = 44

PLAYER_COLOR = {P1: COLOR_P1, P2: COLOR_P2}
BOX_COLOR = {P1: COLOR_BOX_P1, P2: COLOR_BOX_P2}


def load_font(ttf_path, fallback_stack, size, bold=True):
    if os.path.exists(ttf_path):
        return pygame.font.Font(ttf_path, size)
    return pygame.font.SysFont(fallback_stack, size, bold=bold)


def lighten(color, amount=0.5):
    return tuple(int(c + (255 - c) * amount) for c in color)


class GameGUI:
    def __init__(self):
        self.font_hero = load_font(DISPLAY_TTF, UI_FONT_STACK, 44)
        self.font_title = load_font(DISPLAY_TTF, UI_FONT_STACK, 28)
        self.font_big = load_font(MONO_TTF, MONO_FONT_STACK, 28)
        self.font = load_font(DISPLAY_TTF, UI_FONT_STACK, 20)
        self.font_small = load_font(DISPLAY_TTF, UI_FONT_STACK, 15, bold=False)

        # Navigasi tampilan layar game
        self.menu_page = "home"  # "home" -> "mode" -> "size"
        self.selected_mode = PLAYER_VS_PLAYER
        self.selected_ai = MINIMAX
        self.selected_rows = 4
        self.selected_cols = 4

        # UI interaktif (buttons, sliders)
        self.buttons = {}
        self.sliders = {}
        self.dragging_slider = None

    def reset_menu(self):
        self.menu_page = "home"
        self.dragging_slider = None

    def draw_menu(self, screen):
        screen.fill(COLOR_BG)
        self.buttons.clear()
        self.sliders.clear()

        if self.menu_page == "home":
            self._draw_home_screen(screen)
        elif self.menu_page == "mode":
            self._draw_mode_screen(screen)
        elif self.menu_page == "size":
            self._draw_size_screen(screen)

    def _draw_home_screen(self, screen):
        pygame.draw.rect(screen, COLOR_BAR, (0, 0, WINDOW_WIDTH, 18))

        cx = WINDOW_WIDTH // 2
        t1 = self.font_hero.render("GARIS-GARIS", True, COLOR_P1)
        t2 = self.font_hero.render("SQUARE", True, COLOR_TEXT)
        sub = self.font_small.render("Dots & Boxes Adversarial AI", True, COLOR_MUTED)

        screen.blit(t1, t1.get_rect(center=(cx, 175)))
        screen.blit(t2, t2.get_rect(center=(cx, 228)))
        screen.blit(sub, sub.get_rect(center=(cx, 272)))

        btn_w, btn_h = 280, 58
        start_y = 365
        gap = 20

        items = [
            ("play", "Play", "primary"),
            ("settings", "Settings", "disabled"),
            ("exit", "Exit", "secondary"),
        ]

        for i, (key, label, style) in enumerate(items):
            rect = pygame.Rect(cx - btn_w // 2, start_y + i * (btn_h + gap), btn_w, btn_h)
            self._draw_button(screen, rect, label, style)
            if style != "disabled":
                self.buttons[key] = rect

    def _draw_mode_screen(self, screen):
        self._draw_header(screen, "Pilih Lawan")
        cx = WINDOW_WIDTH // 2
        btn_w, btn_h = 310, 60
        start_y = 175
        gap = 18

        # Pvp / Pva
        options = [
            ("pvp", "versus Player"),
            ("mcts", "versus MCTS Bot"),
            ("minimax", "versus Minimax Bot"),
        ]

        for i, (key, label) in enumerate(options):
            rect = pygame.Rect(cx - btn_w // 2, start_y + i * (btn_h + gap), btn_w, btn_h)
            self._draw_button(screen, rect, label, "secondary")
            self.buttons[key] = rect

        # Ava
        div_y = start_y + 3 * btn_h + 2 * gap + 24
        pygame.draw.line(
            screen, COLOR_TRACK,
            (cx - btn_w // 2, div_y),
            (cx + btn_w // 2, div_y),
            width=2,
        )

        ava_rect = pygame.Rect(cx - btn_w // 2, div_y + 24, btn_w, btn_h)
        self._draw_button(screen, ava_rect, "Minimax Bot vs. MCTS Bot", "secondary")
        self.buttons["ava"] = ava_rect

        self._draw_back_button(screen, "back_home")

    def _draw_size_screen(self, screen):
        self._draw_header(screen, "Ukuran Grid")
        cx = WINDOW_WIDTH // 2

        badge = pygame.Rect(cx - 110, 155, 220, 52)
        pygame.draw.rect(screen, COLOR_WHITE, badge, border_radius=14)
        pygame.draw.rect(screen, COLOR_BAR, badge, width=2, border_radius=14)
        dim_txt = self.font_title.render(f"{self.selected_rows} × {self.selected_cols}", True, COLOR_TEXT)
        screen.blit(dim_txt, dim_txt.get_rect(center=badge.center))

        self._draw_range_slider(
            screen,
            key="rows",
            label=f"Height (Baris): {self.selected_rows}",
            value=self.selected_rows,
            min_val=3,
            max_val=7,
            y=275,
        )
        self._draw_range_slider(
            screen,
            key="cols",
            label=f"Width (Kolom): {self.selected_cols}",
            value=self.selected_cols,
            min_val=3,
            max_val=7,
            y=405,
        )

        start_rect = pygame.Rect(cx - 145, 535, 290, 60)
        self._draw_button(screen, start_rect, "Mulai Main", "primary")
        self.buttons["start_game"] = start_rect

        self._draw_back_button(screen, "back_mode")

    def _draw_header(self, screen, title_text):
        pygame.draw.rect(screen, COLOR_BAR, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
        lbl = self.font_title.render(title_text, True, COLOR_WHITE)
        screen.blit(lbl, lbl.get_rect(center=(WINDOW_WIDTH // 2, HUD_HEIGHT // 2)))

    def _draw_back_button(self, screen, key):
        rect = pygame.Rect(WINDOW_WIDTH // 2 - 90, WINDOW_HEIGHT - 95, 180, 44)
        lbl = self.font.render("< Kembali", True, COLOR_MUTED)
        screen.blit(lbl, lbl.get_rect(center=rect.center))
        self.buttons[key] = rect

    def _draw_button(self, screen, rect, text, style="secondary"):
        if style == "primary":
            bg, fg, border = COLOR_BTN_PRIMARY, COLOR_WHITE, None
        elif style == "disabled":
            bg, fg, border = COLOR_BTN_DISABLED, COLOR_TEXT_DISABLED, None
        else:
            bg, fg, border = COLOR_BTN, COLOR_TEXT, COLOR_BAR

        pygame.draw.rect(screen, bg, rect, border_radius=16)
        if border:
            pygame.draw.rect(screen, border, rect, width=2, border_radius=16)

        lbl = self.font.render(text, True, fg)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_range_slider(self, screen, key, label, value, min_val, max_val, y):
        track_w = 300
        track_h = 8
        track_x = (WINDOW_WIDTH - track_w) // 2

        lbl = self.font.render(label, True, COLOR_TEXT)
        screen.blit(lbl, (track_x, y - 34))

        track_rect = pygame.Rect(track_x, y, track_w, track_h)
        pygame.draw.rect(screen, COLOR_TRACK, track_rect, border_radius=4)

        ratio = (value - min_val) / (max_val - min_val)
        knob_x = int(track_x + ratio * track_w)
        knob_y = y + track_h // 2

        fill_rect = pygame.Rect(track_x, y, knob_x - track_x, track_h)
        pygame.draw.rect(screen, COLOR_FILL, fill_rect, border_radius=4)

        for v in range(min_val, max_val + 1):
            tx = int(track_x + ((v - min_val) / (max_val - min_val)) * track_w)
            tick_lbl = self.font_small.render(str(v), True, COLOR_MUTED)
            screen.blit(tick_lbl, tick_lbl.get_rect(center=(tx, y + 26)))

        pygame.draw.circle(screen, COLOR_FILL, (knob_x, knob_y), 13)
        pygame.draw.circle(screen, COLOR_WHITE, (knob_x, knob_y), 5)

        hit_rect = pygame.Rect(track_x - 18, y - 20, track_w + 36, 48)
        self.sliders[key] = (hit_rect, track_x, track_w, min_val, max_val)

    def _update_slider_from_x(self, key, mouse_x):
        if key not in self.sliders:
            return
        _, track_x, track_w, min_val, max_val = self.sliders[key]
        clamped = max(0.0, min(1.0, (mouse_x - track_x) / track_w))
        val = round(min_val + clamped * (max_val - min_val))
        if key == "rows":
            self.selected_rows = val
        elif key == "cols":
            self.selected_cols = val

    # Event handler menu
    def handle_menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            for key, (hit_rect, *_rest) in self.sliders.items():
                if hit_rect.collidepoint(pos):
                    self.dragging_slider = key
                    self._update_slider_from_x(key, pos[0])
                    return None

            for key, rect in self.buttons.items():
                if rect.collidepoint(pos):
                    if key == "play":
                        self.menu_page = "mode"
                    elif key == "exit":
                        return "exit"
                    elif key == "back_home":
                        self.menu_page = "home"
                    elif key == "back_mode":
                        self.menu_page = "mode"
                    elif key == "pvp":
                        self.selected_mode = PLAYER_VS_PLAYER
                        self.menu_page = "size"
                    elif key == "mcts":
                        self.selected_mode = AI_VS_PLAYER
                        self.selected_ai = MCTS
                        self.menu_page = "size"
                    elif key == "minimax":
                        self.selected_mode = AI_VS_PLAYER
                        self.selected_ai = MINIMAX
                        self.menu_page = "size"
                    elif key == "ava":
                        self.selected_mode = AI_VS_AI
                        self.menu_page = "size"
                    elif key == "start_game":
                        return {
                            "mode": self.selected_mode,
                            "ai": self.selected_ai,
                            "rows": self.selected_rows,
                            "cols": self.selected_cols,
                        }

        elif event.type == pygame.MOUSEMOTION and self.dragging_slider is not None:
            self._update_slider_from_x(self.dragging_slider, event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_slider = None

        return None

    # Layout board game
    def _layout(self, state):
        side_pad = 32
        avail_w = WINDOW_WIDTH - 2 * side_pad
        avail_h = WINDOW_HEIGHT - HUD_HEIGHT - FOOTER_HEIGHT - 2 * MARGIN
        cell_size = min(avail_w // state.col, avail_h // state.row)
        ox = (WINDOW_WIDTH - cell_size * state.col) // 2
        oy = HUD_HEIGHT + (WINDOW_HEIGHT - HUD_HEIGHT - FOOTER_HEIGHT - cell_size * state.row) // 2
        return cell_size, ox, oy

    def dot_pos(self, row, col, state):
        cell_size, ox, oy = self._layout(state)
        return (ox + col * cell_size, oy + row * cell_size)

    def _endpoints(self, move, state):
        edge_type, r, c = move
        if edge_type == HORIZONTAL:
            return self.dot_pos(r, c, state), self.dot_pos(r, c + 1, state)
        return self.dot_pos(r, c, state), self.dot_pos(r + 1, c, state)

    def pos_to_move(self, pos, state):
        cell_size, ox, oy = self._layout(state)
        tolerance = max(CLICK_TOLERANCE, cell_size // 3)
        x, y = pos[0] - ox, pos[1] - oy
        candidates = []

        move = (HORIZONTAL, round(y / cell_size), int(x // cell_size))
        if state.is_valid_move(move):
            candidates.append((abs(y - move[1] * cell_size), move))

        move = (VERTICAL, int(y // cell_size), round(x / cell_size))
        if state.is_valid_move(move):
            candidates.append((abs(x - move[2] * cell_size), move))

        candidates = [(d, m) for d, m in candidates if d <= tolerance]
        return min(candidates)[1] if candidates else None

    # Rendering game
    def _player_labels(self, mode, ai_type):
        if mode == AI_VS_AI:
            return {P1: "Bot Minimax", P2: "Bot MCTS"}
        if mode == AI_VS_PLAYER:
            bot_label = "Minimax" if ai_type == MINIMAX else "MCTS"
            return {P1: "Anda", P2: f"Bot {bot_label}"}
        return {P1: P1_NAME, P2: P2_NAME}

    def draw(self, screen, state, hover=None, mode=PLAYER_VS_PLAYER, ai_type=MINIMAX, ai_thinking=False):
        labels = self._player_labels(mode, ai_type)
        screen.fill(COLOR_BG)
        self._draw_boxes(screen, state)
        self._draw_lines(screen, state, hover)
        self._draw_dots(screen, state)
        self._draw_top_bar(screen, state, labels)
        self._draw_footer(screen, state, labels, ai_thinking)
        if state.is_game_over():
            self._draw_game_over(screen, state, labels)

    def _draw_top_bar(self, screen, state, labels):
        pygame.draw.rect(screen, COLOR_BAR, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
        over = state.is_game_over()
        card_w = (WINDOW_WIDTH // 2) - 24
        for i, p in enumerate((P1, P2)):
            cx = WINDOW_WIDTH * (2 * i + 1) // 4
            active = (p == state.curr_player) and not over
            if active:
                pygame.draw.rect(
                    screen, COLOR_WHITE,
                    (cx - card_w // 2, 12, card_w, HUD_HEIGHT - 24),
                    border_radius=14,
                )
            fg = PLAYER_COLOR[p] if active else COLOR_WHITE
            name = self.font.render(labels[p], True, fg)
            score = self.font_big.render(str(state.score[p]), True, fg)
            screen.blit(name, name.get_rect(center=(cx, 35)))
            screen.blit(score, score.get_rect(center=(cx, 70)))

    def _draw_footer(self, screen, state, labels, ai_thinking):
        y = WINDOW_HEIGHT - FOOTER_HEIGHT
        pygame.draw.rect(screen, COLOR_BAR, (0, y, WINDOW_WIDTH, FOOTER_HEIGHT))
        if state.is_game_over():
            text = "Selesai  |  [M] Menu  [R] Ulang"
        elif ai_thinking:
            text = f"{labels[state.curr_player]} berpikir..."
        else:
            text = f"Giliran: {labels[state.curr_player]}  |  [M] Menu"
        label = self.font_small.render(text, True, COLOR_WHITE)
        screen.blit(label, label.get_rect(center=(WINDOW_WIDTH // 2, y + FOOTER_HEIGHT // 2)))

    def _draw_boxes(self, screen, state):
        cell_size, _, _ = self._layout(state)
        box_font = load_font(MONO_TTF, MONO_FONT_STACK, max(16, cell_size // 3))
        for r in range(state.row):
            for c in range(state.col):
                owner = int(state.box_owner[r, c])
                if owner == 0:
                    continue
                x, y = self.dot_pos(r, c, state)
                pygame.draw.rect(screen, BOX_COLOR[owner], (x, y, cell_size, cell_size))
                label = box_font.render(str(owner), True, PLAYER_COLOR[owner])
                screen.blit(label, label.get_rect(center=(x + cell_size // 2, y + cell_size // 2)))

    def _draw_lines(self, screen, state, hover):
        cell_size, _, _ = self._layout(state)
        thick = max(6, min(LINE_THICK, cell_size // 7))
        taken = []

        for r in range(state.row + 1):
            for c in range(state.col):
                owner = int(state.h_line[r, c])
                if owner == 0:
                    a, b = self._endpoints((HORIZONTAL, r, c), state)
                    pygame.draw.line(screen, COLOR_EMPTY_LINE, a, b, thick)
                else:
                    taken.append(((HORIZONTAL, r, c), owner))
        for r in range(state.row):
            for c in range(state.col + 1):
                owner = int(state.v_line[r, c])
                if owner == 0:
                    a, b = self._endpoints((VERTICAL, r, c), state)
                    pygame.draw.line(screen, COLOR_EMPTY_LINE, a, b, thick)
                else:
                    taken.append(((VERTICAL, r, c), owner))

        for move, owner in taken:
            a, b = self._endpoints(move, state)
            if move == state.last_move:
                pygame.draw.line(screen, COLOR_TEXT, a, b, thick + 4)
            pygame.draw.line(screen, PLAYER_COLOR[owner], a, b, thick)

        if hover is not None and not state.is_game_over():
            a, b = self._endpoints(hover, state)
            pygame.draw.line(screen, lighten(PLAYER_COLOR[state.curr_player], 0.45),
                             a, b, thick)

    def _draw_dots(self, screen, state):
        cell_size, _, _ = self._layout(state)
        dot_r = max(5, min(DOT_R, cell_size // 9))
        for r in range(state.row + 1):
            for c in range(state.col + 1):
                pygame.draw.circle(screen, COLOR_DOT, self.dot_pos(r, c, state), dot_r)

    def _draw_game_over(self, screen, state, labels):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*COLOR_BG, 230))
        screen.blit(overlay, (0, 0))

        winner = state.get_winner()
        if winner in labels:
            title, color = f"{labels[winner]} Menang!", PLAYER_COLOR[winner]
        else:
            title, color = "Seri!", COLOR_TEXT
        score_txt = f"{state.score[P1]}  -  {state.score[P2]}"

        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        for surf, dy in (
            (self.font_title.render(title, True, color), -35),
            (self.font.render(score_txt, True, COLOR_TEXT), 10),
            (self.font_small.render("Klik / R untuk ulang  |  M untuk menu", True, COLOR_MUTED), 50),
        ):
            screen.blit(surf, surf.get_rect(center=(cx, cy + dy)))
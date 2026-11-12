import pygame

from config import (
    P1, P2, P1_NAME, P2_NAME,
    CELL_SIZE, MARGIN, PANEL_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
    DOT_RADIUS, LINE_WIDTH, CLICK_TOLERANCE,
    COLOR_BG, COLOR_DOT, COLOR_EMPTY_LINE, COLOR_HOVER_LINE, COLOR_TEXT,
    COLOR_P1, COLOR_P2, COLOR_BOX_P1, COLOR_BOX_P2,
)
from src.game_logic import HORIZONTAL, VERTICAL

PLAYER_COLOR = {P1: COLOR_P1, P2: COLOR_P2}
BOX_COLOR = {P1: COLOR_BOX_P1, P2: COLOR_BOX_P2}
PLAYER_NAME = {P1: P1_NAME, P2: P2_NAME}

COLOR_PANEL = (232, 232, 226)
COLOR_MUTED = (120, 120, 120)


class GameGUI:
    def __init__(self):
        self.ox = MARGIN
        self.oy = MARGIN + PANEL_HEIGHT
        self.font_big = pygame.font.SysFont("arial", 34, bold=True)
        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.font_small = pygame.font.SysFont("arial", 16)

    def dot_pos(self, row, col):
        return (self.ox + col * CELL_SIZE, self.oy + row * CELL_SIZE)

    def _endpoints(self, move):
        edge_type, r, c = move
        if edge_type == HORIZONTAL:
            return self.dot_pos(r, c), self.dot_pos(r, c + 1)
        return self.dot_pos(r, c), self.dot_pos(r + 1, c)

    def pos_to_move(self, pos, state):
        x, y = pos[0] - self.ox, pos[1] - self.oy
        candidates = []

        move = (HORIZONTAL, round(y / CELL_SIZE), int(x // CELL_SIZE))
        if state.is_valid_move(move):
            candidates.append((abs(y - move[1] * CELL_SIZE), move))

        move = (VERTICAL, int(y // CELL_SIZE), round(x / CELL_SIZE))
        if state.is_valid_move(move):
            candidates.append((abs(x - move[2] * CELL_SIZE), move))

        candidates = [(d, m) for d, m in candidates if d <= CLICK_TOLERANCE]
        return min(candidates)[1] if candidates else None

    def draw(self, screen, state, hover=None):
        screen.fill(COLOR_BG)
        self._draw_panel(screen, state)
        self._draw_boxes(screen, state)
        self._draw_lines(screen, state, hover)
        self._draw_dots(screen, state)
        if state.is_game_over():
            self._draw_game_over(screen, state)

    def _draw_panel(self, screen, state):
        pygame.draw.rect(screen, COLOR_PANEL, (0, 0, WINDOW_WIDTH, PANEL_HEIGHT))
        over = state.is_game_over()
        for i, p in enumerate((P1, P2)):
            cx = WINDOW_WIDTH * (2 * i + 1) // 4
            if p == state.curr_player and not over:
                pygame.draw.rect(screen, PLAYER_COLOR[p],
                                 (cx - 85, 10, 170, PANEL_HEIGHT - 20), 3, border_radius=12)
            name = self.font.render(PLAYER_NAME[p], True, PLAYER_COLOR[p])
            score = self.font_big.render(str(state.score[p]), True, COLOR_TEXT)
            screen.blit(name, name.get_rect(center=(cx, 34)))
            screen.blit(score, score.get_rect(center=(cx, 68)))

    def _draw_boxes(self, screen, state):
        for r in range(state.row):
            for c in range(state.col):
                owner = int(state.box_owner[r, c])
                if owner == 0:
                    continue
                x, y = self.dot_pos(r, c)
                pygame.draw.rect(screen, BOX_COLOR[owner], (x, y, CELL_SIZE, CELL_SIZE))
                label = self.font_big.render(str(owner), True, PLAYER_COLOR[owner])
                screen.blit(label, label.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    def _draw_lines(self, screen, state, hover):
        taken = []
        for r in range(state.row + 1):
            for c in range(state.col):
                owner = int(state.h_line[r, c])
                if owner == 0:
                    a, b = self._endpoints((HORIZONTAL, r, c))
                    pygame.draw.line(screen, COLOR_EMPTY_LINE, a, b, 2)
                else:
                    taken.append(((HORIZONTAL, r, c), owner))
        for r in range(state.row):
            for c in range(state.col + 1):
                owner = int(state.v_line[r, c])
                if owner == 0:
                    a, b = self._endpoints((VERTICAL, r, c))
                    pygame.draw.line(screen, COLOR_EMPTY_LINE, a, b, 2)
                else:
                    taken.append(((VERTICAL, r, c), owner))

        for move, owner in taken:
            a, b = self._endpoints(move)
            if move == state.last_move:
                pygame.draw.line(screen, COLOR_TEXT, a, b, LINE_WIDTH + 4)
            pygame.draw.line(screen, PLAYER_COLOR[owner], a, b, LINE_WIDTH)

        if hover is not None and not state.is_game_over():
            a, b = self._endpoints(hover)
            pygame.draw.line(screen, COLOR_HOVER_LINE, a, b, LINE_WIDTH)

    def _draw_dots(self, screen, state):
        for r in range(state.row + 1):
            for c in range(state.col + 1):
                pygame.draw.circle(screen, COLOR_DOT, self.dot_pos(r, c), DOT_RADIUS)

    def _draw_game_over(self, screen, state):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((245, 245, 240, 215))
        screen.blit(overlay, (0, 0))

        winner = state.get_winner()
        if winner in PLAYER_NAME:
            title, color = f"{PLAYER_NAME[winner]} Menang!", PLAYER_COLOR[winner]
        else:
            title, color = "Seri!", COLOR_TEXT
        score_txt = f"{state.score[P1]}  -  {state.score[P2]}"

        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        for surf, dy in (
            (self.font_big.render(title, True, color), -30),
            (self.font.render(score_txt, True, COLOR_TEXT), 12),
            (self.font_small.render("Klik atau tekan R untuk main lagi", True, COLOR_MUTED), 50),
        ):
            screen.blit(surf, surf.get_rect(center=(cx, cy + dy)))

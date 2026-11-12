import sys

import pygame

from config import TITLE, FPS, WINDOW_WIDTH, WINDOW_HEIGHT, ROW, COL
from src.game_logic import GameState
from src.gui import GameGUI


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    gui = GameGUI()
    state = GameState(ROW, COL)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    state = GameState(ROW, COL)
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state.is_game_over():
                    state = GameState(ROW, COL)
                else:
                    move = gui.pos_to_move(event.pos, state)
                    if move is not None:
                        state.make_move(move)

        hover = None
        if not state.is_game_over():
            hover = gui.pos_to_move(pygame.mouse.get_pos(), state)

        gui.draw(screen, state, hover)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

import pygame

from config import (
    DARK_THEME,
    LIGHT_THEME,
    NARUTO_THEME,
    DEFAULT_RESOLUTION_MODE,
    NARUTO_BOX_SKINS,
    P1,
    P2,
    RESOLUTION_SIZES,
)
from src.gui import GameGUI
from src.game_logic import GameState


def test_theme_toggle_cycles_through_all_themes():
    gui = GameGUI.__new__(GameGUI)
    gui.theme_name = "dark"
    gui.theme = DARK_THEME
    gui.buttons = {"toggle_theme": pygame.Rect(0, 0, 10, 10)}
    gui.pressed_key = "toggle_theme"
    gui.dragging_slider = None

    for theme_name, theme in (
        ("light", LIGHT_THEME),
        ("naruto", NARUTO_THEME),
        ("dark", DARK_THEME),
    ):
        event = pygame.event.Event(
            pygame.MOUSEBUTTONUP,
            {"button": 1, "pos": (5, 5)},
        )
        assert GameGUI.handle_menu_event(gui, event) == "theme_changed"
        assert gui.theme_name == theme_name
        assert gui.theme is theme
        gui.pressed_key = "toggle_theme"


def test_resolution_buttons_switch_between_laptop_and_phone():
    gui = GameGUI.__new__(GameGUI)
    gui.resolution_mode = DEFAULT_RESOLUTION_MODE
    gui.window_width, gui.window_height = RESOLUTION_SIZES[DEFAULT_RESOLUTION_MODE]
    gui._bg_cache = {"laptop": pygame.Surface((1, 1))}
    gui.buttons = {"resolution_phone": pygame.Rect(0, 0, 10, 10)}
    gui.pressed_key = "resolution_phone"
    gui.dragging_slider = None

    event = pygame.event.Event(
        pygame.MOUSEBUTTONUP,
        {"button": 1, "pos": (5, 5)},
    )
    result = GameGUI.handle_menu_event(gui, event)

    assert result == {"resolution_changed": True, "size": RESOLUTION_SIZES["phone"]}
    assert gui.resolution_mode == "phone"
    gui.set_window_size(*result["size"])
    assert (gui.window_width, gui.window_height) == RESOLUTION_SIZES["phone"]
    assert gui._bg_cache == {}

    gui.buttons = {"resolution_laptop": pygame.Rect(0, 0, 10, 10)}
    gui.pressed_key = "resolution_laptop"
    result = GameGUI.handle_menu_event(gui, event)
    assert result == {"resolution_changed": True, "size": RESOLUTION_SIZES["laptop"]}


def test_naruto_theme_uses_character_images_for_box_owners(monkeypatch):
    gui = GameGUI.__new__(GameGUI)
    gui.window_width = 440
    gui.window_height = 800
    gui.theme_name = "naruto"
    gui.theme = NARUTO_THEME
    gui.selected_skin = "classic"
    state = GameState(1, 2)
    state.box_owner[:] = [[P1, P2]]
    loaded_images = []
    image = pygame.Surface((1, 1))

    monkeypatch.setattr("src.gui.load_font", lambda *args, **kwargs: None)
    gui._get_skin_sprite = lambda path, size: loaded_images.append(path) or image

    gui._draw_boxes(pygame.Surface((440, 800)), state)

    assert loaded_images == [NARUTO_BOX_SKINS[P1], NARUTO_BOX_SKINS[P2]]

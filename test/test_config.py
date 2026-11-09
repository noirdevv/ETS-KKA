# CARA PAKAI:
# 1. Install pytest: pip install pytest
# 2. Pergi ke direktori root (ETS-KKA\)
# 3. Execute di terminal: python -m pytest test/test_config.py -v
# 4. Kalau passed semua, logic udah aman

import importlib

import pytest

import config

# Semua nama yang dipakai modul lain. Kalau ada yang hilang/salah ketik, tes ini yang menunjukkannya.
REQUIRED_NAMES = [
    "ROW", "COL", "EMPTY", "P1", "P2", "P1_NAME", "P2_NAME",
    "PLAYER_VS_PLAYER", "AI_VS_PLAYER", "AI_VS_AI", "MINIMAX", "MCTS",
    "MINIMAX_DEPTH", "MCTS_ITERATION", "MCTS_EXPLORATION", "AI_MOVE_DELAY",
    "TITLE", "FPS", "CELL_SIZE", "MARGIN", "PANEL_HEIGHT",
    "DOT_RADIUS", "LINE_WIDTH", "CLICK_TOLERANCE",
    "WINDOW_WIDTH", "WINDOW_HEIGHT",
    "COLOR_BG", "COLOR_DOT", "COLOR_EMPTY_LINE", "COLOR_HOVER_LINE", "COLOR_TEXT",
    "COLOR_P1", "COLOR_P2", "COLOR_BOX_P1", "COLOR_BOX_P2",
]

COLOR_NAMES = [n for n in REQUIRED_NAMES if n.startswith("COLOR_")]


def is_positive_int(x):
    return isinstance(x, int) and not isinstance(x, bool) and x > 0


# ---------- kelengkapan ----------
@pytest.mark.parametrize("name", REQUIRED_NAMES)
def test_required_names_exist(name):
    assert hasattr(config, name), f"config.py kehilangan: {name}"


def test_game_logic_can_import_config():
    # Menangkap ketidakcocokan nama antara config.py dan game_logic.py
    importlib.import_module("src.game_logic")


# ---------- papan ----------
def test_board_size_is_positive_int():
    assert is_positive_int(config.ROW)
    assert is_positive_int(config.COL)


# ---------- pemain ----------
def test_empty_is_zero():
    # game_logic memakai np.zeros(...) sebagai papan kosong, jadi EMPTY harus 0
    assert config.EMPTY == 0


def test_player_ids_are_distinct_and_not_empty():
    assert len({config.EMPTY, config.P1, config.P2}) == 3


def test_player_names():
    for name in (config.P1_NAME, config.P2_NAME):
        assert isinstance(name, str) and name.strip()
    assert config.P1_NAME != config.P2_NAME


# ---------- mode & tipe AI ----------
def test_modes_are_distinct_strings():
    modes = [config.PLAYER_VS_PLAYER, config.AI_VS_PLAYER, config.AI_VS_AI]
    assert all(isinstance(m, str) and m for m in modes)
    assert len(set(modes)) == 3


def test_ai_types_are_distinct_strings():
    ais = [config.MINIMAX, config.MCTS]
    assert all(isinstance(a, str) and a for a in ais)
    assert len(set(ais)) == 2


# ---------- parameter AI ----------
def test_ai_parameters_are_sane():
    assert is_positive_int(config.MINIMAX_DEPTH)
    assert is_positive_int(config.MCTS_ITERATION)
    assert isinstance(config.MCTS_EXPLORATION, (int, float))
    assert config.MCTS_EXPLORATION > 0
    assert isinstance(config.AI_MOVE_DELAY, (int, float))
    assert config.AI_MOVE_DELAY >= 0


# ---------- tampilan ----------
def test_title_is_non_empty_string():
    assert isinstance(config.TITLE, str) and config.TITLE.strip()


def test_display_sizes_are_positive():
    assert is_positive_int(config.FPS)
    for name in ("CELL_SIZE", "MARGIN", "PANEL_HEIGHT",
                 "DOT_RADIUS", "LINE_WIDTH", "CLICK_TOLERANCE"):
        assert is_positive_int(getattr(config, name)), name


def test_window_size_matches_board():
    assert config.WINDOW_WIDTH == config.COL * config.CELL_SIZE + 2 * config.MARGIN
    assert config.WINDOW_HEIGHT == (
        config.ROW * config.CELL_SIZE + 2 * config.MARGIN + config.PANEL_HEIGHT
    )


def test_geometry_is_consistent():
    # Zona klik dua garis bersebelahan tidak boleh saling tumpang tindih
    assert config.CLICK_TOLERANCE < config.CELL_SIZE / 2
    # Titik dan garis harus lebih kecil dari satu sel, dan titik tidak terpotong tepi jendela
    assert config.DOT_RADIUS < config.CELL_SIZE / 2
    assert config.LINE_WIDTH < config.CELL_SIZE
    assert config.MARGIN > config.DOT_RADIUS


# ---------- warna ----------
@pytest.mark.parametrize("name", COLOR_NAMES)
def test_color_is_valid_rgb(name):
    color = getattr(config, name)
    assert isinstance(color, tuple) and len(color) == 3, name
    assert all(isinstance(v, int) and 0 <= v <= 255 for v in color), name


def test_player_colors_are_distinguishable():
    assert config.COLOR_P1 != config.COLOR_P2
    assert config.COLOR_BOX_P1 != config.COLOR_BOX_P2
    assert config.COLOR_EMPTY_LINE != config.COLOR_HOVER_LINE


def test_box_colors_visible_on_background():
    assert config.COLOR_BOX_P1 != config.COLOR_BG
    assert config.COLOR_BOX_P2 != config.COLOR_BG
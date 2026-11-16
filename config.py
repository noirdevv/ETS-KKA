import os

#BOARD
ROW = 4
COL = 4

#PLAYER
EMPTY = 0
P1 = 1
P2 = 2

P1_NAME = 'Pemain A'
P2_NAME = 'Pemain B'

#MODE
PLAYER_VS_PLAYER = 'pvp'
AI_VS_PLAYER = 'avp'
AI_VS_AI = 'ava'

#AI
MINIMAX = 'minimax'
MCTS = 'mcts'

MINIMAX_DEPTH = 4
MCTS_ITERATION = 1000
MCTS_EXPLORATION = 1.41 #sqrt(2)
AI_MOVE_DELAY = 0.5 #detik

#PYGAME
TITLE = 'GGS — Garis-Garis Square'
FPS = 60

CELL_SIZE = 90
MARGIN = 40
PANEL_HEIGHT = 360

DOT_RADIUS = 5
LINE_WIDTH = 5
CLICK_TOLERANCE = 15

PHONE_WINDOW_WIDTH = COL * CELL_SIZE + 2 * MARGIN
PHONE_WINDOW_HEIGHT = ROW * CELL_SIZE + 2 * MARGIN + PANEL_HEIGHT
LAPTOP_WINDOW_WIDTH = 1280
LAPTOP_WINDOW_HEIGHT = 720
RESOLUTION_SIZES = {
    "laptop": (LAPTOP_WINDOW_WIDTH, LAPTOP_WINDOW_HEIGHT),
    "phone": (PHONE_WINDOW_WIDTH, PHONE_WINDOW_HEIGHT),
}
DEFAULT_RESOLUTION_MODE = "laptop"
WINDOW_WIDTH, WINDOW_HEIGHT = RESOLUTION_SIZES[DEFAULT_RESOLUTION_MODE]

#WARNA
COLOR_BG = (22, 24, 34)
COLOR_BAR = (34, 38, 54)
COLOR_DOT = (226, 232, 240)
COLOR_EMPTY_LINE = (48, 53, 74)
COLOR_HOVER_LINE = (82, 90, 122)
COLOR_TEXT = (241, 245, 249)
COLOR_TEXT_INV = (10, 14, 24, 185)
COLOR_MUTED = (148, 163, 184)
COLOR_WHITE = (255, 255, 255)

COLOR_P1 = (255, 89, 100)
COLOR_P2 = (56, 189, 248)

COLOR_BOX_P1 = (84, 38, 48)
COLOR_BOX_P2 = (32, 68, 92)

#FONT
UI_FONT_STACK = "trebuchetms,verdana,comicsansms"
MONO_FONT_STACK = "consolas,sfmono,ubuntumono,couriernew"

FONT_DIR = os.path.join("assets", "fonts")
DISPLAY_TTF = os.path.join(FONT_DIR, "Fredoka-Bold.ttf")
MONO_TTF = os.path.join(FONT_DIR, "JetBrainsMono-Bold.ttf")

#WARNA UI & MENU
COLOR_BTN = (34, 38, 54)
COLOR_BTN_PRIMARY = (56, 189, 248)
COLOR_BTN_DISABLED = (30, 33, 46)
COLOR_TEXT_DISABLED = (82, 90, 115)
COLOR_TRACK = (51, 58, 82)
COLOR_FILL = (56, 189, 248)

#WARNA (Default Dark Mode)
COLOR_BG = (22, 24, 34)
COLOR_BAR = (34, 38, 54)
COLOR_DOT = (226, 232, 240)
COLOR_EMPTY_LINE = (48, 53, 74)
COLOR_HOVER_LINE = (82, 90, 122)
COLOR_TEXT = (241, 245, 249)
COLOR_TEXT_INV = (10, 14, 24, 185)
COLOR_MUTED = (148, 163, 184)
COLOR_WHITE = (255, 255, 255)

COLOR_P1 = (255, 89, 100)
COLOR_P2 = (56, 189, 248)

COLOR_BOX_P1 = (84, 38, 48)
COLOR_BOX_P2 = (32, 68, 92)

#WARNA UI & MENU
COLOR_BTN = (34, 38, 54)
COLOR_BTN_PRIMARY = (56, 189, 248)
COLOR_BTN_DISABLED = (30, 33, 46)
COLOR_TEXT_DISABLED = (82, 90, 115)
COLOR_TRACK = (51, 58, 82)
COLOR_FILL = (56, 189, 248)

DARK_THEME = {
    "BG": COLOR_BG,
    "BAR": COLOR_BAR,
    "DOT": COLOR_DOT,
    "EMPTY_LINE": COLOR_EMPTY_LINE,
    "HOVER_LINE": COLOR_HOVER_LINE,
    "TEXT": COLOR_TEXT,
    "TEXT_INV": COLOR_TEXT_INV,
    "MUTED": COLOR_MUTED,
    "WHITE": COLOR_WHITE,
    "P1": COLOR_P1,
    "P2": COLOR_P2,
    "BOX_P1": COLOR_BOX_P1,
    "BOX_P2": COLOR_BOX_P2,
    "BTN": COLOR_BTN,
    "BTN_PRIMARY": COLOR_BTN_PRIMARY,
    "BTN_DISABLED": COLOR_BTN_DISABLED,
    "TEXT_DISABLED": COLOR_TEXT_DISABLED,
    "TRACK": COLOR_TRACK,
    "FILL": COLOR_FILL,
}

LIGHT_THEME = {
    "BG": (244, 246, 250),
    "BAR": (34, 38, 54),
    "DOT": (30, 34, 48),
    "EMPTY_LINE": (212, 217, 228),
    "HOVER_LINE": (165, 174, 192),
    "TEXT": (22, 24, 34),
    "TEXT_INV": (244, 246, 250, 215),
    "MUTED": (100, 110, 130),
    "WHITE": (255, 255, 255),
    "P1": (235, 68, 82),
    "P2": (14, 145, 212),
    "BOX_P1": (252, 212, 216),
    "BOX_P2": (206, 236, 252),
    "BTN": (255, 255, 255),
    "BTN_PRIMARY": (14, 145, 212),
    "BTN_DISABLED": (226, 230, 238),
    "TEXT_DISABLED": (150, 158, 174),
    "TRACK": (203, 210, 224),
    "FILL": (14, 145, 212),
}

NARUTO_THEME = {
    "BG": (255, 247, 230),
    "BAR": (38, 50, 56),
    "DOT": (38, 50, 56),
    "EMPTY_LINE": (224, 213, 193),
    "HOVER_LINE": (56, 142, 60),
    "TEXT": (38, 50, 56),
    "TEXT_INV": (255, 247, 230, 220),
    "MUTED": (111, 105, 94),
    "WHITE": (255, 255, 255),
    "P1": (245, 124, 0),
    "P2": (21, 101, 192),
    "BOX_P1": (255, 224, 178),
    "BOX_P2": (187, 222, 251),
    "BTN": (255, 250, 240),
    "BTN_PRIMARY": (239, 108, 0),
    "BTN_DISABLED": (232, 224, 209),
    "TEXT_DISABLED": (160, 151, 134),
    "TRACK": (205, 190, 164),
    "FILL": (239, 108, 0),
}

BOX_SKINS = {
    "classic": {
        "label": "Klasik (A / B)",
        "type": "text",
        P1: "A",
        P2: "B",
    },
    "crown": {
        "label": "Mahkota & Perisai",
        "type": "icon",
        P1: "crown",
        P2: "shield",
    },
    "stripes": {
        "label": "Garis & Polkadot",
        "type": "pattern",
        P1: "diagonal",
        P2: "dots",
    },
    "pixel": {
        "label": "Fire & Water",
        "type": "image",
        P1: os.path.join("assets", "skins", "flame.png"),
        P2: os.path.join("assets", "skins", "water.png"),
    },
    "face": {
        "label": "Duo Maut",
        "type": "image",
        P1: os.path.join("assets", "skins", "dewa.jpg"),
        P2: os.path.join("assets", "skins", "komang.jpg"),
    },
}

NARUTO_BOX_SKINS = {
    P1: os.path.join("assets", "skins", "sharingan.png"),
    P2: os.path.join("assets", "skins", "rasengan.png"),
}
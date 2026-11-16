import math
import os
import pygame

from config import (
    P1, P2, P1_NAME, P2_NAME,
    PLAYER_VS_PLAYER, AI_VS_PLAYER, AI_VS_AI, MINIMAX, MCTS,
    MARGIN, WINDOW_WIDTH, WINDOW_HEIGHT, CLICK_TOLERANCE,
    DEFAULT_RESOLUTION_MODE, RESOLUTION_SIZES,
    DARK_THEME, LIGHT_THEME, NARUTO_THEME, BOX_SKINS, NARUTO_BOX_SKINS,
    UI_FONT_STACK, MONO_FONT_STACK, DISPLAY_TTF, MONO_TTF,
)
from src.game_logic import HORIZONTAL, VERTICAL
from src.store import SKIN_PRICES

LINE_THICK = 9
DOT_R = 8
HUD_HEIGHT = 105
FOOTER_HEIGHT = 48

BOX_LABEL = {P1: "A", P2: "B"}
THEMES = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "naruto": NARUTO_THEME,
}
THEME_NAMES = ("dark", "light", "naruto")
THEME_LABELS = {
    "dark": "Dark Mode",
    "light": "Light Mode",
    "naruto": "Naruto",
}


def load_font(ttf_path, fallback_stack, size, bold=True):
    if os.path.exists(ttf_path):
        return pygame.font.Font(ttf_path, size)
    return pygame.font.SysFont(fallback_stack, size, bold=bold)


def lighten(color, amount=0.5):
    return tuple(min(255, int(c + (255 - c) * amount)) for c in color)


def darken(color, amount=0.2):
    return tuple(max(0, int(c * (1.0 - amount))) for c in color)


class GameGUI:
    def __init__(
        self,
        bgm_volume=35,
        sfx_volume=65,
        store=None,
        window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
    ):
        self.font_hero = load_font(DISPLAY_TTF, UI_FONT_STACK, 44)
        self.font_title = load_font(DISPLAY_TTF, UI_FONT_STACK, 28)
        self.font_big = load_font(MONO_TTF, MONO_FONT_STACK, 28)
        self.font = load_font(DISPLAY_TTF, UI_FONT_STACK, 20)
        self.font_small = load_font(DISPLAY_TTF, UI_FONT_STACK, 15, bold=False)

        # Tema tampilan
        self.theme_name = "dark"
        self.theme = THEMES[self.theme_name]
        self.resolution_mode = DEFAULT_RESOLUTION_MODE
        self.window_width, self.window_height = window_size

        # Navigasi tampilan layar game
        self.menu_page = "home"  # "home" | "mode" | "size" | "settings"
        self.selected_mode = PLAYER_VS_PLAYER
        self.selected_ai = MINIMAX
        self.selected_rows = 4
        self.selected_cols = 4

        # Pengaturan audio (0 - 100)
        self.bgm_volume = bgm_volume
        self.sfx_volume = sfx_volume

        # State interaktif (hover, press, slider, modal konfirmasi)
        self.buttons = {}
        self.game_buttons = {}
        self.modal_buttons = {}
        self.sliders = {}
        self.dragging_slider = None
        self.pressed_key = None
        self.confirm_action = None  # "menu" | "restart" | None

        # Skins, store, and background
        self.store = store
        self.selected_skin = "classic"
        self._skin_cache = {}  # Cache gambar PNG yang sudah di-resize per cell_size
        self._bg_cache = {}

    def set_window_size(self, width, height):
        self.window_width = width
        self.window_height = height
        self._bg_cache.clear()

    @property
    def _player_colors(self):
        return {P1: self.theme["P1"], P2: self.theme["P2"]}

    @property
    def _box_colors(self):
        return {P1: self.theme["BOX_P1"], P2: self.theme["BOX_P2"]}

    def reset_menu(self):
        self.menu_page = "home"
        self.dragging_slider = None
        self.pressed_key = None
        self.confirm_action = None

    def open_confirm(self, action):
        self.confirm_action = action
        self.pressed_key = None

    def close_confirm(self):
        self.confirm_action = None
        self.pressed_key = None

    def _pulse(self, speed=0.006):
        """Nilai gelombang halus 0.0..1.0 untuk efek kedip tombol."""
        return 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * speed)

    def _update_cursor(self, mouse_pos):
        """Ubah kursor menjadi pointer saat mengarah ke elemen interaktif."""
        interactive_rects = []
        if self.confirm_action is not None:
            interactive_rects.extend(self.modal_buttons.values())
        else:
            interactive_rects.extend(self.buttons.values())
            interactive_rects.extend(self.game_buttons.values())
            interactive_rects.extend(hit for hit, *_ in self.sliders.values())

        hovered = any(r.collidepoint(mouse_pos) for r in interactive_rects)
        cursor = pygame.SYSTEM_CURSOR_HAND if hovered else pygame.SYSTEM_CURSOR_ARROW
        pygame.mouse.set_cursor(cursor)

    # Rendering menu
    def draw_menu(self, screen):
        self._draw_background(screen)
        self.buttons.clear()
        self.game_buttons.clear()
        self.modal_buttons.clear()
        self.sliders.clear()

        if self.menu_page == "home":
            self._draw_home_screen(screen)
        elif self.menu_page == "mode":
            self._draw_mode_screen(screen)
        elif self.menu_page == "size":
            self._draw_size_screen(screen)
        elif self.menu_page == "settings":
            self._draw_settings_screen(screen)

        self._update_cursor(pygame.mouse.get_pos())

    def _draw_background(self, screen):
        """Render background dengan pola grid Dots & Boxes halus yang di-cache."""
        if self.theme_name not in self._bg_cache:
            surf = pygame.Surface((self.window_width, self.window_height))
            bg = self.theme["BG"]
            surf.fill(bg)

            # Warna garis & titik sangat tipis (~5-7% kontras dari BG agar tidak ramai)
            if self.theme_name == "dark":
                line_col = lighten(bg, 0.045)
                dot_col = lighten(bg, 0.11)
                accent_col = lighten(bg, 0.065)
            else:
                line_col = darken(bg, 0.045)
                dot_col = darken(bg, 0.12)
                accent_col = darken(bg, 0.065)

            step = 44  # Jarak antar titik pola
            for x in range(22, self.window_width, step):
                pygame.draw.line(surf, line_col, (x, 0), (x, self.window_height), 1)
            for y in range(22, self.window_height, step):
                pygame.draw.line(surf, line_col, (0, y), (self.window_width, y), 1)

            # Isi beberapa kotak kecil secara jarang agar terasa seperti papan game
            for gx, x in enumerate(range(22, self.window_width - step, step)):
                for gy, y in enumerate(range(22, self.window_height - step, step)):
                    if (gx * 7 + gy * 13) % 11 == 0:
                        pygame.draw.rect(surf, accent_col, (x + 4, y + 4, step - 8, step - 8), border_radius=6)

            # Titik-titik kecil di setiap persimpangan grid
            for x in range(22, self.window_width, step):
                for y in range(22, self.window_height, step):
                    pygame.draw.circle(surf, dot_col, (x, y), 2)

            self._bg_cache[self.theme_name] = surf

        screen.blit(self._bg_cache[self.theme_name], (0, 0))

    def _draw_home_screen(self, screen):
        pygame.draw.rect(screen, self.theme["BAR"], (0, 0, self.window_width, 18))

        cx = self.window_width // 2
        t1 = self.font_hero.render("GARIS-GARIS", True, self.theme["P1"])
        t2 = self.font_hero.render("SQUARE", True, self.theme["TEXT"])
        sub = self.font_small.render("Dots & Boxes Adversarial AI", True, self.theme["MUTED"])

        screen.blit(t1, t1.get_rect(center=(cx, 175)))
        screen.blit(t2, t2.get_rect(center=(cx, 228)))
        screen.blit(sub, sub.get_rect(center=(cx, 272)))

        btn_w, btn_h = 280, 58
        start_y = 365
        gap = 20

        items = [
            ("play", "Play", "primary"),
            ("settings", "Settings", "secondary"),
            ("exit", "Exit", "secondary"),
        ]

        for i, (key, label, style) in enumerate(items):
            rect = pygame.Rect(cx - btn_w // 2, start_y + i * (btn_h + gap), btn_w, btn_h)
            if style != "disabled":
                self.buttons[key] = rect
            self._draw_button(screen, rect, label, style, key=key)

    def _draw_mode_screen(self, screen):
        self._draw_header(screen, "Pilih Lawan")
        cx = self.window_width // 2
        btn_w, btn_h = 310, 60
        start_y = 175
        gap = 18

        options = [
            ("pvp", "versus Player"),
            ("mcts", "versus MCTS Bot"),
            ("minimax", "versus Minimax Bot"),
        ]

        for i, (key, label) in enumerate(options):
            rect = pygame.Rect(cx - btn_w // 2, start_y + i * (btn_h + gap), btn_w, btn_h)
            self.buttons[key] = rect
            self._draw_button(screen, rect, label, "secondary", key=key)

        # Garis pemisah mode pemain dan mode nonton bot
        div_y = start_y + 3 * btn_h + 2 * gap + 24
        pygame.draw.line(
            screen, self.theme["TRACK"],
            (cx - btn_w // 2, div_y),
            (cx + btn_w // 2, div_y),
            width=2,
        )

        # Opsi ke-4: mode spectator AI vs AI
        ava_rect = pygame.Rect(cx - btn_w // 2, div_y + 24, btn_w, btn_h)
        self.buttons["ava"] = ava_rect
        self._draw_button(screen, ava_rect, "Minimax Bot vs. MCTS Bot", "secondary", key="ava")

        self._draw_back_button(screen, "back_home")

    def _draw_size_screen(self, screen):
        self._draw_header(screen, "Ukuran Grid")
        cx = self.window_width // 2

        badge = pygame.Rect(cx - 110, 155, 220, 52)
        pygame.draw.rect(screen, self.theme["BTN"], badge, border_radius=14)
        pygame.draw.rect(screen, self.theme["FILL"], badge, width=2, border_radius=14)
        dim_txt = self.font_title.render(f"{self.selected_rows} × {self.selected_cols}", True, self.theme["TEXT"])
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
        self.buttons["start_game"] = start_rect
        self._draw_button(screen, start_rect, "Mulai Main", "primary", key="start_game")

        self._draw_back_button(screen, "back_mode")

    def _draw_settings_screen(self, screen):
        self._draw_header(screen, "Settings")
        cx = self.window_width // 2

        self._draw_range_slider(
            screen,
            key="bgm",
            label=f"Background Music: {self.bgm_volume}%",
            value=self.bgm_volume,
            min_val=0,
            max_val=100,
            y=150,
            tick_step=25,
        )
        self._draw_range_slider(
            screen,
            key="sfx",
            label=f"Sound Effects: {self.sfx_volume}%",
            value=self.sfx_volume,
            min_val=0,
            max_val=100,
            y=225,
            tick_step=25,
        )

        theme_label = f"Tema: {THEME_LABELS[self.theme_name]}"
        theme_rect = pygame.Rect(cx - 145, 275, 290, 46)
        self.buttons["toggle_theme"] = theme_rect
        self._draw_button(screen, theme_rect, theme_label, "secondary", key="toggle_theme")

        for key, label, mode, x in (
            ("resolution_laptop", "Laptop", "laptop", cx - 145),
            ("resolution_phone", "HP", "phone", cx + 5),
        ):
            rect = pygame.Rect(x, 355, 140, 42)
            self.buttons[key] = rect
            style = "primary" if self.resolution_mode == mode else "secondary"
            self._draw_button(screen, rect, label, style, key=key)

        # Skins
        pygame.draw.line(screen, self.theme["TRACK"], (cx - 145, 417), (cx + 145, 417), width=2)
        skin_hdr = self.font.render("Skin", True, self.theme["TEXT"])
        screen.blit(skin_hdr, skin_hdr.get_rect(center=(cx, 436)))

        unlocked = self.store is None or self.store.is_unlocked(self.selected_skin)
        skin_name = BOX_SKINS[self.selected_skin]["label"]
        skin_label = f"{skin_name}" if unlocked else f"{skin_name} [Terkunci]"
        skin_rect = pygame.Rect(cx - 145, 459, 290, 46)
        self.buttons["cycle_skin"] = skin_rect
        self._draw_button(screen, skin_rect, skin_label, "secondary", key="cycle_skin")

        # Microtransaction
        buy_rect = pygame.Rect(cx - 145, 512, 290, 46)
        if not unlocked:
            price = SKIN_PRICES.get(self.selected_skin, 0)
            self.buttons["buy_skin"] = buy_rect
            self._draw_button(screen, buy_rect, f"Beli Skin (Rp {price:,})", "primary", key="buy_skin")
        else:
            self._draw_button(screen, buy_rect, "Skin Sudah Terbuka", "disabled")

        # Status transaksi Midtrans (jika sedang/baru saja membeli)
        if self.store and self.store.status_message:
            status_surf = self.font_small.render(self.store.status_message, True, self.theme["FILL"])
            screen.blit(status_surf, status_surf.get_rect(center=(cx, 578)))

        self._draw_back_button(screen, "back_home")

    def _draw_header(self, screen, title_text):
        pygame.draw.rect(screen, self.theme["BAR"], (0, 0, self.window_width, HUD_HEIGHT))
        lbl = self.font_title.render(title_text, True, self.theme["WHITE"])
        screen.blit(lbl, lbl.get_rect(center=(self.window_width // 2, HUD_HEIGHT // 2)))

    def _draw_back_button(self, screen, key):
        rect = pygame.Rect(self.window_width // 2 - 90, self.window_height - 95, 180, 44)
        self.buttons[key] = rect
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = self.theme["TEXT"] if hovered else self.theme["MUTED"]
        lbl = self.font.render("< Kembali", True, color)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_button(self, screen, rect, text, style="secondary", key=None):
        mouse_pos = pygame.mouse.get_pos()
        hovered = (style != "disabled") and rect.collidepoint(mouse_pos)
        pressed = (key is not None) and (self.pressed_key == key) and hovered

        draw_rect = rect.move(0, 2) if pressed else rect
        pulse = self._pulse()

        if style == "primary":
            bg = self.theme["BTN_PRIMARY"]
            if pressed:
                bg = darken(bg, 0.15)
            elif hovered:
                bg = lighten(bg, 0.14 + 0.14 * pulse)
            fg, border = self.theme["WHITE"], None
        elif style == "disabled":
            bg, fg, border = self.theme["BTN_DISABLED"], self.theme["TEXT_DISABLED"], None
        elif style == "danger":
            bg = self.theme["P1"]
            if pressed:
                bg = darken(bg, 0.15)
            elif hovered:
                bg = lighten(bg, 0.14 + 0.14 * pulse)
            fg, border = self.theme["WHITE"], None
        else:
            bg = self.theme["BTN"]
            if pressed:
                bg = darken(bg, 0.08)
            elif hovered:
                bg = lighten(self.theme["FILL"], 0.78 + 0.10 * pulse)
            fg = self.theme["FILL"] if hovered else self.theme["TEXT"]
            border = self.theme["FILL"] if hovered else self.theme["TRACK"]

        # Lingkaran cahaya tipis di luar tombol saat hover
        if hovered and not pressed:
            glow_rect = draw_rect.inflate(6, 6)
            glow_color = lighten(self.theme["FILL"] if style != "danger" else self.theme["P1"], 0.55)
            pygame.draw.rect(screen, glow_color, glow_rect, width=2, border_radius=18)

        pygame.draw.rect(screen, bg, draw_rect, border_radius=16)
        if border:
            pygame.draw.rect(screen, border, draw_rect, width=2, border_radius=16)

        lbl = self.font.render(text, True, fg)
        screen.blit(lbl, lbl.get_rect(center=draw_rect.center))

    def _draw_range_slider(self, screen, key, label, value, min_val, max_val, y, tick_step=1):
        track_w = 300
        track_h = 8
        track_x = (self.window_width - track_w) // 2
        hit_rect = pygame.Rect(track_x - 18, y - 20, track_w + 36, 48)
        self.sliders[key] = (hit_rect, track_x, track_w, min_val, max_val)

        hovered = hit_rect.collidepoint(pygame.mouse.get_pos()) or (self.dragging_slider == key)

        lbl = self.font.render(label, True, self.theme["TEXT"])
        screen.blit(lbl, (track_x, y - 34))

        track_rect = pygame.Rect(track_x, y, track_w, track_h)
        pygame.draw.rect(screen, self.theme["TRACK"], track_rect, border_radius=4)

        ratio = (value - min_val) / (max_val - min_val)
        knob_x = int(track_x + ratio * track_w)
        knob_y = y + track_h // 2

        fill_color = lighten(self.theme["FILL"], 0.15) if hovered else self.theme["FILL"]
        fill_rect = pygame.Rect(track_x, y, knob_x - track_x, track_h)
        pygame.draw.rect(screen, fill_color, fill_rect, border_radius=4)

        for v in range(min_val, max_val + 1, tick_step):
            tx = int(track_x + ((v - min_val) / (max_val - min_val)) * track_w)
            tick_color = self.theme["TEXT"] if v == value else self.theme["MUTED"]
            tick_lbl = self.font_small.render(str(v), True, tick_color)
            screen.blit(tick_lbl, tick_lbl.get_rect(center=(tx, y + 26)))

        if hovered:
            pygame.draw.circle(screen, lighten(self.theme["FILL"], 0.65), (knob_x, knob_y), 19)
        pygame.draw.circle(screen, fill_color, (knob_x, knob_y), 13)
        pygame.draw.circle(screen, self.theme["WHITE"], (knob_x, knob_y), 5)

    def _update_slider_from_x(self, key, mouse_x):
        if key not in self.sliders:
            return None
        _, track_x, track_w, min_val, max_val = self.sliders[key]
        clamped = max(0.0, min(1.0, (mouse_x - track_x) / track_w))
        val = round(min_val + clamped * (max_val - min_val))
        if key == "rows":
            self.selected_rows = val
        elif key == "cols":
            self.selected_cols = val
        elif key == "bgm":
            self.bgm_volume = val
            return {"audio_changed": True, "bgm": self.bgm_volume, "sfx": self.sfx_volume}
        elif key == "sfx":
            self.sfx_volume = val
            return {"audio_changed": True, "bgm": self.bgm_volume, "sfx": self.sfx_volume}
        return None

    # Event handler menu
    def handle_menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            for key, (hit_rect, *_rest) in self.sliders.items():
                if hit_rect.collidepoint(pos):
                    self.dragging_slider = key
                    return self._update_slider_from_x(key, pos[0])

            for key, rect in self.buttons.items():
                if rect.collidepoint(pos):
                    self.pressed_key = key
                    return None

        elif event.type == pygame.MOUSEMOTION and self.dragging_slider is not None:
            return self._update_slider_from_x(self.dragging_slider, event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_sfx_slider = self.dragging_slider == "sfx"
            self.dragging_slider = None
            released_key = self.pressed_key
            self.pressed_key = None

            if was_sfx_slider:
                return "test_sfx"

            if released_key and released_key in self.buttons and self.buttons[released_key].collidepoint(event.pos):
                if released_key == "play":
                    self.menu_page = "mode"
                elif released_key == "settings":
                    self.menu_page = "settings"
                elif released_key == "toggle_theme":
                    next_theme = (THEME_NAMES.index(self.theme_name) + 1) % len(THEME_NAMES)
                    self.theme_name = THEME_NAMES[next_theme]
                    self.theme = THEMES[self.theme_name]
                    return "theme_changed"
                elif released_key in ("resolution_laptop", "resolution_phone"):
                    mode = "laptop" if released_key == "resolution_laptop" else "phone"
                    if mode == self.resolution_mode:
                        return None
                    self.resolution_mode = mode
                    return {
                        "resolution_changed": True,
                        "size": RESOLUTION_SIZES[mode],
                    }
                elif released_key == "test_sfx":
                    return "test_sfx"
                elif released_key == "exit":
                    return "exit"
                elif released_key == "back_home":
                    self.menu_page = "home"
                elif released_key == "back_mode":
                    self.menu_page = "mode"
                elif released_key == "pvp":
                    self.selected_mode = PLAYER_VS_PLAYER
                    self.menu_page = "size"
                elif released_key == "mcts":
                    self.selected_mode = AI_VS_PLAYER
                    self.selected_ai = MCTS
                    self.menu_page = "size"
                elif released_key == "minimax":
                    self.selected_mode = AI_VS_PLAYER
                    self.selected_ai = MINIMAX
                    self.menu_page = "size"
                elif released_key == "ava":
                    self.selected_mode = AI_VS_AI
                    self.menu_page = "size"
                elif released_key == "buy_skin":
                    if self.store and not self.store.is_unlocked(self.selected_skin):
                        self.store.start_purchase(self.selected_skin)
                    return "buy_skin"
                elif released_key == "start_game":
                    if self.store and not self.store.is_unlocked(self.selected_skin):
                        self.selected_skin = "classic"
                    return {
                        "mode": self.selected_mode,
                        "ai": self.selected_ai,
                        "rows": self.selected_rows,
                        "cols": self.selected_cols,
                    }
                elif released_key == "cycle_skin":
                    keys = list(BOX_SKINS.keys())
                    next_idx = (keys.index(self.selected_skin) + 1) % len(keys)
                    self.selected_skin = keys[next_idx]
                    return "skin_changed"


        return None

    # Event handler game
    def handle_game_ui_event(self, event, state):
        """Menangani klik pada footer (Menu/Ulang) dan modal konfirmasi.
        Mengembalikan 'menu', 'restart', 'handled', atau None.
        """
        if self.confirm_action is not None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close_confirm()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action = self.confirm_action
                    state.__init__(state.row, state.col)
                    self.close_confirm()
                    return action
                return "handled"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in self.modal_buttons.items():
                    if rect.collidepoint(event.pos):
                        self.pressed_key = key
                return "handled"

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                released = self.pressed_key
                self.pressed_key = None
                if released and released in self.modal_buttons and self.modal_buttons[released].collidepoint(event.pos):
                    if released == "confirm_yes":
                        action = self.confirm_action
                        state.__init__(state.row, state.col)
                        self.close_confirm()
                        return action
                    elif released == "confirm_no":
                        self.close_confirm()
                return "handled"

            return "handled"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for key, rect in self.game_buttons.items():
                if rect.collidepoint(event.pos):
                    self.pressed_key = key
                    return "handled"

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            released = self.pressed_key
            self.pressed_key = None
            if released and released in self.game_buttons and self.game_buttons[released].collidepoint(event.pos):
                if released == "btn_menu":
                    return "menu"
                elif released == "btn_restart":
                    return "restart"

        return None

    # Layout board game
    def _layout(self, state):
        side_pad = 32
        avail_w = self.window_width - 2 * side_pad
        avail_h = self.window_height - HUD_HEIGHT - FOOTER_HEIGHT - 2 * MARGIN
        cell_size = min(avail_w // state.col, avail_h // state.row)
        ox = (self.window_width - cell_size * state.col) // 2
        oy = HUD_HEIGHT + (self.window_height - HUD_HEIGHT - FOOTER_HEIGHT - cell_size * state.row) // 2
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

    # Rendering permainan
    def _player_labels(self, mode, ai_type):
        if mode == AI_VS_AI:
            return {P1: "Bot Minimax", P2: "Bot MCTS"}
        if mode == AI_VS_PLAYER:
            bot_label = "Minimax" if ai_type == MINIMAX else "MCTS"
            return {P1: "Anda", P2: f"Bot {bot_label}"}
        return {P1: P1_NAME, P2: P2_NAME}

    def draw(self, screen, state, hover=None, mode=PLAYER_VS_PLAYER, ai_type=MINIMAX, ai_thinking=False):
        self.buttons.clear()
        self.sliders.clear()
        self.game_buttons.clear()
        self.modal_buttons.clear()

        labels = self._player_labels(mode, ai_type)
        self._draw_background(screen)
        self._draw_boxes(screen, state)
        self._draw_lines(screen, state, hover)
        self._draw_dots(screen, state)
        self._draw_top_bar(screen, state, labels)
        self._draw_footer(screen, state, labels, ai_thinking)

        if state.is_game_over():
            self._draw_game_over(screen, state, labels)
        elif self.confirm_action is not None:
            self._draw_confirm_modal(screen)

        self._update_cursor(pygame.mouse.get_pos())

    def _draw_top_bar(self, screen, state, labels):
        pygame.draw.rect(screen, self.theme["BAR"], (0, 0, self.window_width, HUD_HEIGHT))
        over = state.is_game_over()
        card_w = (self.window_width // 2) - 24
        p_colors = self._player_colors
        for i, p in enumerate((P1, P2)):
            cx = self.window_width * (2 * i + 1) // 4
            active = (p == state.curr_player) and not over
            if active:
                pygame.draw.rect(
                    screen, self.theme["WHITE"],
                    (cx - card_w // 2, 12, card_w, HUD_HEIGHT - 24),
                    border_radius=14,
                )
            fg = p_colors[p] if active else self.theme["WHITE"]
            name = self.font.render(labels[p], True, fg)
            score = self.font_big.render(str(state.score[p]), True, fg)
            screen.blit(name, name.get_rect(center=(cx, 35)))
            screen.blit(score, score.get_rect(center=(cx, 70)))

    def _draw_footer(self, screen, state, labels, ai_thinking):
        y = self.window_height - FOOTER_HEIGHT
        pygame.draw.rect(screen, self.theme["BAR"], (0, y, self.window_width, FOOTER_HEIGHT))

        if state.is_game_over():
            status = "Permainan Selesai"
        elif ai_thinking:
            status = f"{labels[state.curr_player]} berpikir..."
        else:
            status = f"Giliran: {labels[state.curr_player]}"

        lbl = self.font_small.render(status, True, self.theme["WHITE"])
        screen.blit(lbl, lbl.get_rect(midleft=(16, y + FOOTER_HEIGHT // 2)))

        # Tombol interaktif
        mouse_pos = pygame.mouse.get_pos()
        btn_h = 30
        btn_y = y + (FOOTER_HEIGHT - btn_h) // 2
        actions = [("btn_restart", "Ulang", 68), ("btn_menu", "Menu", 68)]
        right_x = self.window_width - 12

        for key, text, btn_w in actions:
            right_x -= btn_w
            rect = pygame.Rect(right_x, btn_y, btn_w, btn_h)
            self.game_buttons[key] = rect
            hovered = rect.collidepoint(mouse_pos)
            bg = lighten(self.theme["BAR"], 0.25) if hovered else lighten(self.theme["BAR"], 0.12)
            pygame.draw.rect(screen, bg, rect, border_radius=8)
            if hovered:
                pygame.draw.rect(screen, self.theme["WHITE"], rect, width=1, border_radius=8)
            btn_lbl = self.font_small.render(text, True, self.theme["WHITE"])
            screen.blit(btn_lbl, btn_lbl.get_rect(center=rect.center))
            right_x -= 8

    def _draw_confirm_modal(self, screen):
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill(self.theme["TEXT_INV"])
        screen.blit(overlay, (0, 0))

        card_w, card_h = 340, 210
        card_rect = pygame.Rect(
            (self.window_width - card_w) // 2,
            (self.window_height - card_h) // 2,
            card_w,
            card_h,
        )
        pygame.draw.rect(screen, self.theme["BG"], card_rect, border_radius=20)
        pygame.draw.rect(screen, self.theme["MUTED"], card_rect, width=2, border_radius=20)

        if self.confirm_action == "menu":
            title_txt = "Kembali ke Menu?"
            desc_txt = "Progres permainan saat ini akan hilang."
        else:
            title_txt = "Ulang Permainan?"
            desc_txt = "Papan akan direset dari awal."

        cx = self.window_width // 2
        title_surf = self.font_title.render(title_txt, True, self.theme["TEXT"])
        desc_surf = self.font_small.render(desc_txt, True, self.theme["MUTED"])
        screen.blit(title_surf, title_surf.get_rect(center=(cx, card_rect.top + 48)))
        screen.blit(desc_surf, desc_surf.get_rect(center=(cx, card_rect.top + 88)))

        btn_w, btn_h = 132, 46
        btn_y = card_rect.bottom - btn_h - 24
        no_rect = pygame.Rect(cx - btn_w - 10, btn_y, btn_w, btn_h)
        yes_rect = pygame.Rect(cx + 10, btn_y, btn_w, btn_h)

        self.modal_buttons["confirm_no"] = no_rect
        self.modal_buttons["confirm_yes"] = yes_rect

        self._draw_button(screen, no_rect, "Batal", "secondary", key="confirm_no")
        self._draw_button(screen, yes_rect, "Ya", "danger", key="confirm_yes")

    def _draw_boxes(self, screen, state):
        cell_size, _, _ = self._layout(state)
        skin = BOX_SKINS[self.selected_skin]
        box_font = load_font(MONO_TTF, MONO_FONT_STACK, max(16, cell_size // 3))
        p_colors = self._player_colors
        b_colors = self._box_colors

        for r in range(state.row):
            for c in range(state.col):
                owner = int(state.box_owner[r, c])
                if owner == 0:
                    continue

                x, y = self.dot_pos(r, c, state)
                box_rect = pygame.Rect(x, y, cell_size, cell_size)

                pygame.draw.rect(screen, b_colors[owner], box_rect)

                if self.theme_name == "naruto":
                    surf = self._get_skin_sprite(NARUTO_BOX_SKINS[owner], cell_size)
                    if surf is not None:
                        screen.blit(surf, (x, y))
                        continue

                if skin["type"] == "image":
                    surf = self._get_skin_sprite(skin[owner], cell_size)
                    if surf is not None:
                        screen.blit(surf, (x, y))
                        continue
                if skin["type"] == "pattern":
                    self._draw_box_pattern(screen, box_rect, skin[owner], p_colors[owner])
                elif skin["type"] == "icon":
                    self._draw_box_icon(screen, box_rect, skin[owner], p_colors[owner])
                else:
                    label = box_font.render(skin[owner], True, p_colors[owner])
                    screen.blit(label, label.get_rect(center=box_rect.center))

    def _draw_lines(self, screen, state, hover):
        cell_size, _, _ = self._layout(state)
        thick = max(6, min(LINE_THICK, cell_size // 7))
        p_colors = self._player_colors
        taken = []

        for r in range(state.row + 1):
            for c in range(state.col):
                owner = int(state.h_line[r, c])
                if owner == 0:
                    a, b = self._endpoints((HORIZONTAL, r, c), state)
                    pygame.draw.line(screen, self.theme["EMPTY_LINE"], a, b, thick)
                else:
                    taken.append(((HORIZONTAL, r, c), owner))
        for r in range(state.row):
            for c in range(state.col + 1):
                owner = int(state.v_line[r, c])
                if owner == 0:
                    a, b = self._endpoints((VERTICAL, r, c), state)
                    pygame.draw.line(screen, self.theme["EMPTY_LINE"], a, b, thick)
                else:
                    taken.append(((VERTICAL, r, c), owner))

        for move, owner in taken:
            a, b = self._endpoints(move, state)
            if move == state.last_move:
                pygame.draw.line(screen, self.theme["TEXT"], a, b, thick + 4)
            pygame.draw.line(screen, p_colors[owner], a, b, thick)

        if hover is not None and not state.is_game_over() and self.confirm_action is None:
            a, b = self._endpoints(hover, state)
            pulse_amt = 0.35 + 0.25 * self._pulse(0.008)
            pygame.draw.line(screen, lighten(p_colors[state.curr_player], pulse_amt),
                             a, b, thick)

    def _draw_dots(self, screen, state):
        cell_size, _, _ = self._layout(state)
        dot_r = max(5, min(DOT_R, cell_size // 9))
        for r in range(state.row + 1):
            for c in range(state.col + 1):
                pygame.draw.circle(screen, self.theme["DOT"], self.dot_pos(r, c, state), dot_r)

    def _draw_game_over(self, screen, state, labels):
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((*self.theme["BG"], 230))
        screen.blit(overlay, (0, 0))

        p_colors = self._player_colors
        winner = state.get_winner()
        if winner in labels:
            title, color = f"{labels[winner]} Menang!", p_colors[winner]
        else:
            title, color = "Seri!", self.theme["TEXT"]
        score_txt = f"{state.score[P1]}  -  {state.score[P2]}"

        cx, cy = self.window_width // 2, self.window_height // 2
        for surf, dy in (
            (self.font_title.render(title, True, color), -35),
            (self.font.render(score_txt, True, self.theme["TEXT"]), 10),
            (self.font_small.render("Klik / R untuk ulang  |  M untuk menu", True, self.theme["MUTED"]), 50),
        ):
            screen.blit(surf, surf.get_rect(center=(cx, cy + dy)))

    def _get_skin_sprite(self, path, cell_size):
        """Muat & scale sprite PNG sekali per ukuran sel agar FPS tetap 60."""
        cache_key = (path, cell_size)
        if cache_key not in self._skin_cache:
            if not os.path.exists(path):
                self._skin_cache[cache_key] = None
            else:
                raw = pygame.image.load(path).convert_alpha()
                self._skin_cache[cache_key] = pygame.transform.smoothscale(raw, (cell_size, cell_size))
        return self._skin_cache[cache_key]

    def _draw_box_pattern(self, screen, rect, pattern, color):
        """Gambar motif geometris di dalam kotak."""
        pad = max(8, rect.width // 6)
        if pattern == "diagonal":
            pygame.draw.line(screen, color, (rect.left + pad, rect.top + pad), (rect.right - pad, rect.bottom - pad), 4)
            pygame.draw.line(screen, color, (rect.right - pad, rect.top + pad), (rect.left + pad, rect.bottom - pad), 4)
        elif pattern == "dots":
            r = max(4, rect.width // 14)
            for dx in (-pad, pad):
                for dy in (-pad, pad):
                    pygame.draw.circle(screen, color, (rect.centerx + dx, rect.centery + dy), r)

    def _draw_box_icon(self, screen, rect, icon_name, color):
        """Gambar ikon vektor sederhana (mahkota / perisai) di tengah kotak."""
        cx, cy = rect.center
        s = rect.width // 4
        if icon_name == "crown":
            pts = [
                (cx - s, cy + s // 2),
                (cx - s, cy - s // 2),
                (cx - s // 2, cy),
                (cx, cy - s),
                (cx + s // 2, cy),
                (cx + s, cy - s // 2),
                (cx + s, cy + s // 2),
            ]
            pygame.draw.polygon(screen, color, pts)
        elif icon_name == "shield":
            pts = [
                (cx - s, cy - s),
                (cx + s, cy - s),
                (cx + s, cy),
                (cx, cy + s),
                (cx - s, cy),
            ]
            pygame.draw.polygon(screen, color, pts)
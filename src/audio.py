import os
import pygame

AUDIO_DIR = os.path.join("assets", "audio")

class AudioManager:
    def __init__(self, bgm_pct=35, sfx_pct=65):
        self.enabled = True
        self.muted = False
        self.bgm_filename = None
        self.bgm_pct = max(0, min(100, int(bgm_pct)))
        self.sfx_pct = max(0, min(100, int(sfx_pct)))
        self.sounds = {}

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            self.enabled = False
            return

        self._load_sfx("click", "click.wav")
        self._load_sfx("draw", "draw_line.wav")
        self._load_sfx("capture", "capture.wav")
        self._load_sfx("win", "win.wav")

    def _load_sfx(self, name, filename):
        path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.sfx_pct / 100.0)
            self.sounds[name] = sound

    def set_bgm_volume(self, pct):
        self.bgm_pct = max(0, min(100, int(pct)))
        self.muted = False
        if self.enabled:
            pygame.mixer.music.set_volume(self.bgm_pct / 100.0)

    def set_sfx_volume(self, pct):
        self.sfx_pct = max(0, min(100, int(pct)))
        self.muted = False
        if self.enabled:
            vol = self.sfx_pct / 100.0
            for s in self.sounds.values():
                s.set_volume(vol)

    def play_sfx(self, name):
        if not self.enabled or self.muted or self.sfx_pct == 0 or name not in self.sounds:
            return
        self.sounds[name].play()

    def play_bgm(self, filename="bgm.mp3", loops=-1):
        if not self.enabled:
            return
        path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(path):
            if filename == self.bgm_filename and pygame.mixer.music.get_busy():
                return
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.0 if self.muted else self.bgm_pct / 100.0)
            pygame.mixer.music.play(loops=loops)
            self.bgm_filename = filename

    def play_theme_bgm(self, theme_name):
        filename = "naruto backsound.mp3" if theme_name == "naruto" else "bgm.mp3"
        self.play_bgm(filename)

    def toggle_mute(self):
        if not self.enabled:
            return
        self.muted = not self.muted
        bgm_vol = 0.0 if self.muted else self.bgm_pct / 100.0
        sfx_vol = 0.0 if self.muted else self.sfx_pct / 100.0
        pygame.mixer.music.set_volume(bgm_vol)
        for s in self.sounds.values():
            s.set_volume(sfx_vol)
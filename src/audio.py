import os
import pygame

AUDIO_DIR = os.path.join("assets", "audio")


class AudioManager:
    def __init__(self, bgm_volume=0.35, sfx_volume=0.65):
        self.enabled = True
        self.bgm_volume = bgm_volume
        self.sfx_volume = sfx_volume
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
            sound.set_volume(self.sfx_volume)
            self.sounds[name] = sound

    def play_sfx(self, name):
        if not self.enabled or name not in self.sounds:
            return
        self.sounds[name].play()

    def play_bgm(self, filename="bgm.mp3", loops=-1):
        if not self.enabled:
            return
        path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.bgm_volume)
            pygame.mixer.music.play(loops=loops)

    def toggle_mute(self):
        if not self.enabled:
            return
        if pygame.mixer.music.get_volume() > 0:
            pygame.mixer.music.set_volume(0.0)
            for s in self.sounds.values():
                s.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(self.bgm_volume)
            for s in self.sounds.values():
                s.set_volume(self.sfx_volume)
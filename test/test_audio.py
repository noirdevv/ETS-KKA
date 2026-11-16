from src.audio import AudioManager


def test_play_theme_bgm_selects_theme_track():
    audio = AudioManager.__new__(AudioManager)
    played_files = []
    audio.play_bgm = lambda filename="bgm.mp3", loops=-1: played_files.append(filename)

    audio.play_theme_bgm("naruto")
    audio.play_theme_bgm("dark")

    assert played_files == ["naruto backsound.mp3", "bgm.mp3"]

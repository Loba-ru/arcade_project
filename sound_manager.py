# ========== ТЕКСТУРНЫЙ МЕНЕДЖЕР ==========
# Модуль для воспроизведения звуков игры Monster Chase (arcade)

import arcade


class SoundManager:
    def __init__(self, file_manager):
        self.sounds = {}
        self.file_manager = file_manager

    def _load_sound(self, name):
        """Внутренний метод загрузки звука"""
        try:
            if name not in self.sounds:
                path = self.file_manager.get_sound_path(f"{name}.wav")
                self.sounds[name] = arcade.load_sound(path)
        except Exception as e:
            print(f"[DEBUG]: ошибка загрузки звука '{name}.wav': {e}")

    def play(self, name, volume=0.5):
        """Воспроизводит звук, загружая его при первом вызове"""
        self._load_sound(name)
        try:
            arcade.play_sound(self.sounds[name], volume=volume)
        except Exception as e:
            print(f"[DEBUG]: ошибка воспроизведения {name!r}: {e}")

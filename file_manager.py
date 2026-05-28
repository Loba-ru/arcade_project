# ========== УПРАВЛЕНИЕ ФАЙЛАМИ ==========
# Модуль для организации работы с файлами игры Monster Chase (arcade)

import arcade

from pathlib import Path


class FileManager:
    """Централизованное управление путями к файлам ресурсов."""

    def __init__(self, window: arcade.Window):
        self.window = window

        resources_path = Path(__file__).parent.resolve() / "resources"

        self.bg_path = resources_path / "bg"
        self.images_path = resources_path / "images"
        self.maps_path = resources_path / "maps"
        self.sounds_path = resources_path / "sounds"

    def get_bg_path(self, bg_name: str) -> str:
        """Возвращает полный путь к карте."""
        return str(self.bg_path / bg_name)

    def get_image_path(self, subdirectory_name: str, image_name: str) -> str:
        """Возвращает полный путь к изображению."""
        return str(self.images_path / subdirectory_name / image_name)

    def get_map_path(self, map_name: str) -> str:
        """Возвращает полный путь к карте."""
        return str(self.maps_path / map_name)

    def get_sound_path(self, sound_name: str) -> str:
        """Возвращает полный путь к звуковому файлу."""
        return str(self.sounds_path / sound_name)

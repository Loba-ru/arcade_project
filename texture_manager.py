# ========== ТЕКСТУРНЫЙ МЕНЕДЖЕР ==========
# Модуль для централизованного создания текстур игры Monster Chase (arcade)


import arcade

from constants import ENTITIES_DIR, ITEMS_DIR, COIN_FRAMES
from window_manager import WindowManager


class TextureManager:
    def __init__(self, file_manager: WindowManager):
        self.file_manager = file_manager

    def load_player_textures(self):
        textures = {}

        for frame in ("idle", "jump", "fall"):
            file_path = self.file_manager.get_image_path(
                ENTITIES_DIR, f"player_{frame}.png"
            )
            textures[frame] = [arcade.load_texture(file_path)]

        walk_frames = []
        for i in range(8):
            file_path = self.file_manager.get_image_path(
                ENTITIES_DIR, f"player_walk{i}.png"
            )
            walk_frames.append(arcade.load_texture(file_path))
        textures["walk"] = walk_frames

        climb_frames = []
        for i in range(2):
            file_path = self.file_manager.get_image_path(
                ENTITIES_DIR, f"player_climb{i}.png"
            )
            climb_frames.append(arcade.load_texture(file_path))
        textures["climb"] = climb_frames

        return textures

    def load_friend_textures(self):
        """Загружает текстуры для анимированного союзника."""
        textures = {}

        # Idle текстура
        idle_path = self.file_manager.get_image_path(
            ENTITIES_DIR, "friend_idle.png"
        )
        textures["idle"] = [arcade.load_texture(idle_path)]

        # Текстуры ходьбы
        walk_frames = []
        for i in range(8):
            path = self.file_manager.get_image_path(
                ENTITIES_DIR, f"friend_walk{i}.png"
            )
            walk_frames.append(arcade.load_texture(path))
        textures["walk"] = walk_frames

        return textures

    def load_coin_textures(self):
        """Загружает текстуры для анимированной монеты."""
        textures = []
        for frame_name in COIN_FRAMES:
            path = self.file_manager.get_image_path(ITEMS_DIR, frame_name)
            textures.append(arcade.load_texture(path))
        return textures

    def load_enemy_textures(self, name: str, count: int):
        """Загружает текстуры врага."""
        textures = []
        for i in range(count):
            path = self.file_manager.get_image_path(
                ENTITIES_DIR, f"{name}{i}.png"
            )
            try:
                textures.append(arcade.load_texture(path))
            except Exception as e:
                print(
                    f"[DEBUG]: ошибка загрузки текстуры '{name}{i}.png': {e}"
                )
        return textures

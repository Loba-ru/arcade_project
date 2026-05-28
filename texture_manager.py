# ========== ТЕКСТУРНЫЙ МЕНЕДЖЕР ==========
# Модуль для централизованного создания текстур игры Monster Chase (arcade)


import arcade

from constants import ENTITIES_DIR
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

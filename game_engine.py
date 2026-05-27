# ========== МЕНЕДЖЕР ИГРЫ ==========
# Центральный модуль управления игровым процессом

import arcade

from constants import *
from levels import GroundLevel, DungeonLevel, SkyLevel
from window_manager import WindowManager


class MyGame:
    def __init__(self, window: arcade.Window):
        self.window = window
        self.has_all_gems = False
        self.player = None

        self.level_registry = {}
        self.current_view = None

        self.level_display_names = {
            "ground": "Земля",
            "dungeon": "Подземелье",
            "sky": "Небо",
        }

        self.difficulty_names = ["Лёгкая", "Средняя", "Тяжёлая"]

        self.register_level("ground", GroundLevel)
        self.register_level("dungeon", DungeonLevel)
        self.register_level("sky", SkyLevel)

        self.coin_count = 0
        self.lives = PLAYER_LIVES_DEFAULT
        self.difficulty = 1

    def register_level(self, name: str, level_class):
        self.level_registry[name] = level_class

    def create_level(self, level_name: str):
        if level_name not in self.level_registry:
            raise ValueError(f"Unknown level: {level_name}")

        level_class = self.level_registry[level_name]
        level = level_class(self)
        level.setup()
        return level

    def start_game(self, start_level: str = "ground"):
        self.current_view = self.create_level(start_level)
        self.window.show_view(self.current_view)

    def change_level(self, level_name: str):
        self.current_view = self.create_level(level_name)
        self.window.show_view(self.current_view)

    def reset_current_level(self):
        if self.current_view is not None:
            self.current_view.reset_level()

    def pause(self):
        if self.current_view is not None:
            self.current_view.is_paused = True

    def resume(self):
        if self.current_view is not None:
            self.current_view.is_paused = False

    def add_coin(self):
        self.coin_count += 1

    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1

    def set_on_win_callback(self, callback):
        self.on_win_callback = callback

    def set_on_lose_callback(self, callback):
        self.on_lose_callback = callback

    def set_on_menu_callback(self, callback):
        self.on_menu_callback = callback

    def get_level_difficulty_text(self):
        level_name_display = self.level_display_names.get(
            getattr(self.current_view, "level_name", "unknown"), "Неизвестно"
        )
        try:
            difficulty_name = self.difficulty_names[self.difficulty]
        except IndexError:
            difficulty_name = "Ошибка"
        return f"Уровень: {level_name_display} | Сложность: {difficulty_name}"

    def check_victory(self, current_level_name: str):
        if current_level_name == "ground" and self.has_all_gems:
            print(
                "[VICTORY] Игрок вернулся на старт со всеми драгоценностями!"
            )
            self.on_win_callback()

    def set_difficulty(self, difficulty_rank):
        """Устанавливает сложность игры"""
        self.difficulty = difficulty_rank
        if self.difficulty == DIFFICULTY_EASY:
            self.lives = PLAYER_LIVES_EASY
        elif self.difficulty == DIFFICULTY_HARD:
            self.lives = PLAYER_LIVES_HARD
        else:  # по умолчанию
            self.lives = PLAYER_LIVES_MEDIUM
        print(
            f"[DIFFICULTY] Сложность {self.difficulty}, жизней: {self.lives}"
        )

    def set_difficulty_before_start(self, difficulty_rank):
        """Устанавливает сложность игры ДО загрузки уровней"""
        self.set_difficulty(difficulty_rank)

    def on_resize(self, width, height):
        """Обновление камер при изменении размера окна"""
        current_view = self.current_view

        if current_view:
            if hasattr(current_view, "setup_cameras"):
                current_view.setup_cameras()

            if hasattr(current_view, "resize_gui"):
                current_view.resize_gui(width, height)


class TestWindow(arcade.Window):
    """Окно для тестового запуска игры (без StateManager)"""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.window_manager = WindowManager(self)
        self.window_manager.center_window()
        self.window_manager.hide_cursor()

        self.game_manager = MyGame(self)
        self.game_manager.start_game("ground")

    def on_resize(self, width, height):
        """Обработка изменения размера окна (включая полноэкранный режим)"""
        # super().on_resize(width, height)
        self.game_manager.on_resize(width, height)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.F11:
            self.window_manager.toggle_fullscreen()
        else:
            if self.current_view:
                self.current_view.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        if self.current_view:
            self.current_view.on_key_release(key, modifiers)

    def on_draw(self):
        self.clear()
        if self.current_view:
            self.current_view.on_draw()

    def on_update(self, delta_time):
        if self.current_view:
            self.current_view.on_update(delta_time)


if __name__ == "__main__":
    window = TestWindow()
    arcade.run()

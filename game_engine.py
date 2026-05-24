import arcade

from constants import *
from levels import GroundLevel, DungeonLevel, SkyLevel


class MyGame:
    def __init__(self, window: arcade.Window):
        self.window = window
        self.level_registry = {}
        self.current_view = None

        # Словарь: техническое имя уровня -> красивое название
        self.level_display_names = {
            "ground": "Земля",
            "dungeon": "Подземелье",
            "sky": "Небо",
        }

        # Список названий сложностей игры
        self.difficulty_names = ["Лёгкая", "Средняя", "Тяжёлая"]

        self.register_level("ground", GroundLevel)
        self.register_level("dungeon", DungeonLevel)
        self.register_level("sky", SkyLevel)

        self.coin_count = 0
        self.lives = PLAYER_LIVES
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

    # ========== Методы для управления состоянием ==========

    def add_coin(self):
        self.coin_count += 1

    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1

    def set_difficulty(self, level):
        self.difficulty = level

    # ========== Методы для назначения callback-функций ==========

    def set_on_win_callback(self, callback):
        """Назначает функцию, которая вызовется при победе."""
        self.on_win_callback = callback

    def set_on_lose_callback(self, callback):
        """Назначает функцию, которая вызовется при поражении."""
        self.on_lose_callback = callback

    def set_on_menu_callback(self, callback):
        """Назначает функцию, которая вызовется при вызове меню (паузы)."""
        self.on_menu_callback = callback

    def get_level_difficulty_text(self):
        """Возвращает строку вида 'Уровень: Земля | Сложность: Средняя'"""
        level_name_display = self.level_display_names.get(
            getattr(self.current_view, "level_name", "unknown"), "Неизвестно"
        )
        try:
            difficulty_name = self.difficulty_names[self.difficulty]
        except IndexError:
            difficulty_name = "Ошибка"
        return f"Уровень: {level_name_display} | Сложность: {difficulty_name}"


def center_window(window):
    # Получаем основной монитор через pyglet.display
    from pyglet.display import get_display

    display = get_display()
    screens = display.get_screens()
    screen = screens[0]  # основной экран

    # Вычисляем позицию для центрирования
    x = (screen.width - SCREEN_WIDTH) // 2
    y = (screen.height - SCREEN_HEIGHT) // 2

    # Устанавливаем позицию окна
    window.set_location(x, y)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    center_window(window)
    game = MyGame(window)
    game.start_game("ground")  # "ground", "dungeon", "sky"
    arcade.run()


if __name__ == "__main__":
    main()

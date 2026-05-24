# ========== ТОЧКА ВХОДА И ГЛАВНОЕ ОКНО ==========
# Основной файл запуска приложения

# Класс GameWindow:
#  - главное окно игры
#  - инициализация менеджера состояний

# Метод center_window:
#  - центрирование окна на экране

# Метод main (внизу):
#  - главная точка входа в приложение

import arcade
from states import StateManager, StartView
from gui_manager import GUIManager

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class GameWindow(arcade.Window):
    """Окно игры, которое делегирует всё менеджеру состояний"""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.center_window()
        self.background_color = arcade.color.AMAZON
        self.gui_manager = GUIManager(self)  # добавил GUI менеджер
        self.state_manager = StateManager(
            self, self.gui_manager
        )  # передаю в StateManager
        # Устанавливаю начальное состояние
        self.state_manager.change_state(StartView(self.state_manager))

    def center_window(self):
        """Центрирует окно на экране"""
        # Получаем основной монитор через pyglet.display
        from pyglet.display import get_display

        display = get_display()
        screens = display.get_screens()
        screen = screens[0]  # основной экран

        # Размер экрана
        screen_width = screen.width
        screen_height = screen.height

        # Вычисляем позицию для центрирования
        x = (screen_width - SCREEN_WIDTH) // 2
        y = (screen_height - SCREEN_HEIGHT) // 2

        # Устанавливаем позицию окна
        self.set_location(x, y)

    def on_draw(self):
        self.state_manager.on_draw()
        self.gui_manager.draw()  # рисовую GUI поверх

    def on_update(self, delta_time: float):
        self.state_manager.on_update(delta_time)
        self.gui_manager.on_update(delta_time)  # обновляю GUI

    def on_key_press(self, key: int, modifiers: int):
        self.state_manager.on_key_press(key, modifiers)

    def on_key_release(self, key: int, modifiers: int):
        self.state_manager.on_key_release(key, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.gui_manager.on_mouse_press(x, y, button, modifiers)  # сначала GUI
        self.state_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.gui_manager.on_mouse_motion(
            x, y, dx, dy
        )  # для эффектов наведения


if __name__ == "__main__":
    window = GameWindow()
    arcade.run()

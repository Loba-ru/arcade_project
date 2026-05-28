# ========== ТОЧКА ВХОДА И ГЛАВНОЕ ОКНО ==========
# Основной файл запуска игры Monster Chase (arcade)

# Класс GameWindow:
# - главное окно игры
# - инициализация менеджера состояний


import arcade
from file_manager import FileManager
from window_manager import WindowManager
from gui_manager import GUIManager
from states import StateManager, StartView
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class GameWindow(arcade.Window):
    """Окно игры, которое делегирует всё менеджеру состояний."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.background_color = arcade.color.AMAZON

        self.window_manager = WindowManager(self)
        self.window_manager.toggle_fullscreen()

        self.file_manager = FileManager(self)

        self.gui_manager = GUIManager(self)

        self.state_manager = StateManager(self, self.gui_manager)
        self.state_manager.change_state(StartView(self.state_manager))

    def on_resize(self, width, height):
        super().on_resize(width, height)

        current_view = self.state_manager._current_state

        if current_view:
            if hasattr(current_view, "on_resize"):
                current_view.on_resize(width, height)
            if hasattr(current_view, "resize_gui"):
                current_view.resize_gui(width, height)

    def on_draw(self):
        self.state_manager.on_draw()
        self.gui_manager.draw()

    def on_update(self, delta_time: float):
        self.state_manager.on_update(delta_time)
        self.gui_manager.on_update(delta_time)

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.F11:
            self.window_manager.toggle_fullscreen()
        else:
            self.state_manager.on_key_press(key, modifiers)

    def on_key_release(self, key: int, modifiers: int):
        self.state_manager.on_key_release(key, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.gui_manager.on_mouse_press(x, y, button, modifiers)
        self.state_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.gui_manager.on_mouse_motion(x, y, dx, dy)


if __name__ == "__main__":
    window = GameWindow()
    arcade.run()

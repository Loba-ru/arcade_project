# ========== УПРАВЛЕНИЕ ОКНОМ ==========
# Централизованное управление окном игры

import arcade
from pyglet.display import get_display


class WindowManager:
    """Класс для управления окном игры"""

    def __init__(self, window: arcade.Window):
        self.window = window
        self.is_fullscreen = False
        self._cursor_hidden = False
        self._original_width = window.width
        self._original_height = window.height

    def toggle_fullscreen(self):
        """Переключает полноэкранный режим по F11"""
        self.is_fullscreen = not self.is_fullscreen
        self.window.set_fullscreen(self.is_fullscreen)

        width, height = self.window.get_size()
        self.window.dispatch_event("on_resize", width, height)

        if self._cursor_hidden:
            self.window.set_mouse_visible(False)

        if not self.is_fullscreen:
            self.center_window()

    def center_window(self):
        """Центрирует окно на экране"""
        display = get_display()
        screens = display.get_screens()
        screen = screens[0]

        x = (screen.width - self.window.width) // 2
        y = (screen.height - self.window.height) // 2

        self.window.set_location(x, y)

    def hide_cursor(self):
        """Скрывает курсор"""
        self._cursor_hidden = True
        self.window.set_mouse_visible(False)

    def show_cursor(self):
        """Показывает курсор"""
        self._cursor_hidden = False
        self.window.set_mouse_visible(True)

    def toggle_cursor(self):
        """Переключает видимость курсора"""
        if self._cursor_hidden:
            self.show_cursor()
        else:
            self.hide_cursor()

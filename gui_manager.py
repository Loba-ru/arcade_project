"""Менеджер GUI с текстурными кнопками для меню"""

import arcade
from arcade.gui import (
    UIManager,
    UIFlatButton,
    UIBoxLayout,
    UIAnchorLayout,
    UIWidget,
)


class GUIManager:
    """Централизованное управление GUI для всех состояний"""

    def __init__(self, window: arcade.Window):
        self.window = window
        self.manager = UIManager()
        self.manager.enable()

        # Корневые лейауты для разных экранов
        self.current_layout = None

    def show_menu_gui(self, on_new_game_callback):
        """Показывает GUI для меню (кнопка 'Новая игра')"""

        print("[GUI] show_menu_gui вызван")
        self.manager.clear()

        anchor = UIAnchorLayout()
        box = UIBoxLayout(vertical=True, space_between=20, align="center")

        spacer = UIWidget(width=200, height=250)  # 200 пикселей отступа
        box.add(spacer)

        # Создаём простую кнопку с полным набором стилей
        new_game_button = UIFlatButton(
            text="НОВАЯ ИГРА",
            width=200,
            height=50,
            style={
                "normal": {
                    "font_size": 20,
                    "font_color": (255, 255, 255, 255),
                    "bg_color": (0, 150, 0, 255),
                    "border_color": (255, 255, 0, 255),
                    "border_width": 3,
                },
                "hover": {
                    "font_size": 20,
                    "font_color": (255, 255, 0, 255),
                    "bg_color": (0, 180, 0, 255),
                    "border_color": (255, 255, 0, 255),
                    "border_width": 3,
                },
                "press": {
                    "font_size": 20,
                    "font_color": (200, 200, 200, 255),
                    "bg_color": (0, 100, 0, 255),
                    "border_color": (200, 200, 0, 255),
                    "border_width": 2,
                },
            },
        )
        new_game_button.on_click = lambda event: on_new_game_callback(event)

        box.add(new_game_button)
        anchor.add(box, anchor_x="center", anchor_y="center")

        self.manager.add(anchor)
        self.current_layout = anchor

        print(f"[GUI] Кнопка создана, добавлена в layout")

    def hide_gui(self):
        """Скрывает GUI"""
        self.manager.clear()
        self.current_layout = None

    def draw(self):
        """Отрисовка GUI"""
        self.manager.draw()

    def on_update(self, delta_time: float):
        """Обновление GUI"""
        self.manager.on_update(delta_time)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Обработка кликов для GUI"""
        self.manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.manager.on_mouse_motion(x, y, dx, dy)

    def disable(self):
        self.manager.disable()

    def enable(self):
        self.manager.enable()

    def is_visible(self) -> bool:
        """Проверяет, активен ли GUI"""
        return self.current_layout is not None

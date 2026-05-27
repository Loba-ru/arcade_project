# ========== GUI ИНТЕРФЕЙС ==========

# Класс GUIManager (основной класс управления GUI):
#  - обеспечивает централизованное управление GUI для всех состояний (экранов)
#  - изолирует всю работу с кнопками от основной логики приложения

# Предопределённые стили оформления:
#  - унифицированный шаблон стиля кнопок

import arcade
from arcade.gui import (
    UIManager,
    UIFlatButton,
    UIBoxLayout,
    UIAnchorLayout,
    UIWidget,
)

button_style = {
    "normal": arcade.gui.UIFlatButton.UIStyle(
        bg=(255, 215, 0),  # золотой цвет (RGB)
        border=arcade.color.DARK_GREEN,
        border_width=2,
        font_color=arcade.color.GRAY,
        font_size=14,
    ),
    "hover": arcade.gui.UIFlatButton.UIStyle(
        bg=(255, 255, 0),  # жёлтый
        border=arcade.color.BLACK,
        border_width=2,
        font_color=arcade.color.BLACK,
        font_size=14,
    ),
    "press": arcade.gui.UIFlatButton.UIStyle(
        bg=(255, 165, 0),  # тёмно‑оранжевый
        border=arcade.color.RED,
        border_width=2,
        font_color=arcade.color.WHITE,
        font_size=14,
    ),
}


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

        self.manager.clear()

        anchor = UIAnchorLayout()
        box = UIBoxLayout(vertical=True, space_between=20, align="center")

        spacer = UIWidget(width=200, height=250)  # 200 пикселей отступа
        box.add(spacer)

        # Создаём простую кнопку с полным набором стилей
        new_game_button = UIFlatButton(
            text="НОВАЯ ИГРА", width=200, height=50, style=button_style
        )
        new_game_button.on_click = lambda event: on_new_game_callback(event)

        box.add(new_game_button)
        anchor.add(box, anchor_x="center", anchor_y="center")

        self.manager.add(anchor)
        self.current_layout = anchor

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

import arcade
from abc import ABC, abstractmethod
from pyglet.graphics import Batch

# Нет циклического импорта, используем строковую аннотацию

# Базовый интерфейс состояния игры


class GameState(ABC):
    """Абстрактное состояние — интерфейс для всех экранов"""

    @abstractmethod
    def on_show(self):
        """Вызывается при переходе в это состояние"""
        pass

    @abstractmethod
    def on_draw(self):
        """Отрисовка текущего состояния"""
        pass

    @abstractmethod
    def on_update(self, delta_time: float):
        """Логика обновления"""
        pass

    @abstractmethod
    def on_key_press(self, key: int, modifiers: int):
        """Обработка нажатий клавиш"""
        pass

    @abstractmethod
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Обработка кликов мыши"""
        pass


class StateManager:
    """Контекст — управляет текущим состоянием"""

    def __init__(self, window: arcade.Window, gui_manager=None):
        self.window = window
        self.gui_manager = gui_manager
        self._current_state: GameState = None

    def change_state(self, new_state: GameState):
        """Переключение между состояниями (главный метод паттерна)"""
        if self._current_state:
            # Опционально: cleanup текущего состояния
            pass
        self._current_state = new_state
        self._current_state.on_show()

    # Делегирование всех методов текущему состоянию
    def on_draw(self):
        if self._current_state:
            self._current_state.on_draw()

    def on_update(self, delta_time: float):
        if self._current_state:
            self._current_state.on_update(delta_time)

    def on_key_press(self, key: int, modifiers: int):
        if self._current_state:
            self._current_state.on_key_press(key, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self._current_state:
            self._current_state.on_mouse_press(x, y, button, modifiers)


# Конкретные состояния (экраны)


class StartView(GameState):
    """Стартовое окно с названием и кнопкой 'Старт'"""

    def __init__(self, manager: StateManager):
        self.manager = manager
        self.gui_shown = False
        self.batch = None
        self.title_text = None
        self.prompt_text = None

    def on_show(self):
        print("[State] Переход в StartView")
        if self.manager.gui_manager:
            self.manager.gui_manager.hide_gui()
        self.gui_shown = False

        # Создаём Batch и тексты при первом показе
        if self.batch is None:
            self.batch = Batch()
            w = self.manager.window.width
            h = self.manager.window.height
            self.title_text = arcade.Text(
                "MY PLATFORMER",
                w // 2,
                h // 2 + 50,
                arcade.color.WHITE,
                40,
                anchor_x="center",
                batch=self.batch,
            )
            self.prompt_text = arcade.Text(
                "Нажмите ПРОБЕЛ или кликните для старта",
                w // 2,
                h // 2 - 50,
                arcade.color.LIGHT_GRAY,
                20,
                anchor_x="center",
                batch=self.batch,
            )

    def start_game(self, event):
        print("[GUI] Нажата кнопка 'Старт'")
        self.manager.change_state(MenuView(self.manager))

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.SPACE:
            self.manager.change_state(MenuView(self.manager))

    def on_draw(self):
        self.manager.window.clear()
        if self.batch:
            self.batch.draw()

    def on_update(self, delta_time: float):
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.manager.change_state(MenuView(self.manager))


class MenuView(GameState):
    """Меню выбора сложности с поддержкой мыши"""

    def __init__(self, manager: StateManager, return_to_game=None):
        self.manager = manager
        self.difficulty = 1
        self.return_to_game = return_to_game

        self.batch = None
        self.title_text = None
        self.difficulty_texts = []
        self.hint_text = None
        self.pause_text = None

    def on_show(self):
        print("[State] Переход в MenuView")

        w = self.manager.window.width
        h = self.manager.window.height

        if self.return_to_game is None:
            self.difficulty = 1
        else:
            self.difficulty = self.return_to_game.difficulty
            print(
                f"  (возврат из игры, сложность сохранена: {self.difficulty})"
            )

        if self.batch is None:
            self.batch = Batch()

            self.title_text = arcade.Text(
                "ВЫБОР СЛОЖНОСТИ",
                w // 2,
                h // 2 + 50,
                arcade.color.YELLOW,
                30,
                anchor_x="center",
                batch=self.batch,
            )

            difficulties = ["ЛЕГКИЙ", "СРЕДНИЙ", "ВЫСОКИЙ"]
            y_pos = h // 2
            for i, diff in enumerate(difficulties):
                marker = "▶ " if i == self.difficulty else "\u2800  "
                color = (
                    arcade.color.RED
                    if i == self.difficulty
                    else arcade.color.WHITE
                )
                text = arcade.Text(
                    f"{marker}{diff}",
                    w // 2 - 100,
                    y_pos - i * 40,
                    color,
                    24,
                    anchor_x="left",
                    batch=self.batch,
                )
                self.difficulty_texts.append(text)

            self.hint_text = arcade.Text(
                "← →  - изменить сложность | ENTER - новая игра | ESC - продолжить",
                w // 2,
                50,
                arcade.color.LIGHT_GRAY,
                16,
                anchor_x="center",
                batch=self.batch,
            )

            # Текст паузы (только при возврате из игры)
            if self.return_to_game is not None:
                self.pause_text = arcade.Text(
                    "ПАУЗА",
                    w // 2,
                    h // 2 + 150,
                    arcade.color.GOLD,
                    50,
                    anchor_x="center",
                    batch=self.batch,
                )

        self._update_text_colors()

        if self.manager.gui_manager:
            self.manager.gui_manager.show_menu_gui(
                on_new_game_callback=self.start_new_game
            )

    def _update_text_colors(self):
        difficulties = ["ЛЕГКИЙ", "СРЕДНИЙ", "ВЫСОКИЙ"]
        for i, text in enumerate(self.difficulty_texts):
            marker = "▶ " if i == self.difficulty else "\u2800  "
            text.text = f"{marker}{difficulties[i]}"
            text.color = (
                arcade.color.RED
                if i == self.difficulty
                else arcade.color.WHITE
            )

    def start_new_game(self, event):
        print("[GUI] Нажата кнопка 'Новая игра'")
        self.manager.change_state(GameplayView(self.manager, self.difficulty))

    def on_draw(self):
        self.manager.window.clear()
        if self.batch:
            self.batch.draw()

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, key: int, modifiers: int):
        if key in (
            arcade.key.UP,
            arcade.key.DOWN,
            arcade.key.LEFT,
            arcade.key.RIGHT,
        ):
            self.difficulty = (self.difficulty + 1) % 3
            self._update_text_colors()
        elif key == arcade.key.ENTER:
            self.start_new_game(None)
        elif key == arcade.key.ESCAPE and self.return_to_game:
            if self.manager.gui_manager:
                self.manager.gui_manager.hide_gui()
            self.manager.change_state(self.return_to_game)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        for i, text in enumerate(self.difficulty_texts):
            width_approx = len(text.text) * 24 * 0.6
            left = text.x
            right = text.x + width_approx
            bottom = text.y - 15
            top = text.y + 15
            if left <= x <= right and bottom <= y <= top:
                if self.difficulty != i:
                    self.difficulty = i
                    self._update_text_colors()
                break


class GameplayView(GameState):
    """Игровое окно (минимальная заглушка для теста переключений)"""

    def __init__(self, manager: StateManager, difficulty: int):
        self.manager = manager
        self.difficulty = difficulty
        self.is_paused = False
        self.frame_count = 0
        self.batch = None
        self.status_text = None
        self.diff_text = None
        self.hint_text = None

    def on_show(self):
        diff_names = ["легкий", "средний", "высокий"]
        print(
            f"[State] Переход в GameplayView (сложность: {diff_names[self.difficulty]})"
        )
        if not self.is_paused:
            self.frame_count = 0

        # Создаём Batch и тексты при первом показе
        if self.batch is None:
            self.batch = Batch()
            w = self.manager.window.width
            h = self.manager.window.height

            self.status_text = arcade.Text(
                "ИГРА ЗАПУЩЕНА (ЗАГЛУШКА)",
                w // 2,
                h // 2 + 50,
                arcade.color.GREEN,
                30,
                anchor_x="center",
                batch=self.batch,
            )
            self.diff_text = arcade.Text(
                f"Сложность: {['Easy', 'Medium', 'Hard'][self.difficulty]}",
                w // 2,
                h // 2,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                batch=self.batch,
            )
            self.hint_text = arcade.Text(
                "Нажмите 'W' для победы | 'L' для проигрыша | 'M' для меню",
                w // 2,
                50,
                arcade.color.LIGHT_GRAY,
                16,
                anchor_x="center",
                batch=self.batch,
            )
        else:
            # Обновляем текст сложности (при возврате из меню)
            self.diff_text.text = (
                f"Сложность: {['Easy', 'Medium', 'Hard'][self.difficulty]}"
            )

        if self.manager.gui_manager:
            self.manager.gui_manager.hide_gui()

    def on_draw(self):
        self.manager.window.clear()
        if self.batch:
            self.batch.draw()

    def on_update(self, delta_time: float):
        self.frame_count += 1
        pass

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.W:  # Победа
            if self.manager.gui_manager:
                self.manager.gui_manager.hide_gui()
            self.manager.change_state(
                ResultView(self.manager, won=True, coins=15, kills=3)
            )
        elif key == arcade.key.L:  # Проигрыш
            if self.manager.gui_manager:
                self.manager.gui_manager.hide_gui()
            self.manager.change_state(
                ResultView(self.manager, won=False, coins=5, kills=1)
            )
        elif (
            key == arcade.key.M or key == arcade.key.ESCAPE
        ):  # ← сохраняем игру и уходим в меню
            self.is_paused = True
            self.manager.change_state(
                MenuView(self.manager, return_to_game=self)
            )

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        pass


class ResultView(GameState):
    """Окно результата (победа или поражение)"""

    def __init__(
        self, manager: StateManager, won: bool, coins: int, kills: int
    ):
        self.manager = manager
        self.won = won
        self.coins = coins
        self.kills = kills
        self.batch = None
        self.title_text = None
        self.coins_text = None
        self.kills_text = None
        self.hint_text = None

    def on_show(self):
        print(f"[State] Переход в ResultView (Победа: {self.won})")
        if self.manager.gui_manager:
            self.manager.gui_manager.hide_gui()

        # Создаём Batch и тексты при первом показе
        if self.batch is None:
            self.batch = Batch()
            w = self.manager.window.width
            h = self.manager.window.height

            title = "ПОБЕДА!" if self.won else "GAME OVER"
            color = arcade.color.GREEN if self.won else arcade.color.RED

            self.title_text = arcade.Text(
                title,
                w // 2,
                h // 2 + 150,
                color,
                50,
                anchor_x="center",
                batch=self.batch,
            )
            self.coins_text = arcade.Text(
                f"Собрано монет: {self.coins}",
                w // 2,
                h // 2 + 50,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                batch=self.batch,
            )
            self.kills_text = arcade.Text(
                f"Убито врагов: {self.kills}",
                w // 2,
                h // 2,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                batch=self.batch,
            )
            self.hint_text = arcade.Text(
                "Нажмите ПРОБЕЛ для возврата в меню | ESC для выхода",
                w // 2,
                80,
                arcade.color.LIGHT_GRAY,
                18,
                anchor_x="center",
                batch=self.batch,
            )
        else:
            # Обновляем текст, если результат изменился
            self.title_text.text = "ПОБЕДА!" if self.won else "GAME OVER"
            self.title_text.color = (
                arcade.color.GOLD if self.won else arcade.color.RED
            )
            self.coins_text.text = f"Собрано монет: {self.coins}"
            self.kills_text.text = f"Убито врагов: {self.kills}"

    def on_draw(self):
        self.manager.window.clear()
        if self.batch:
            self.batch.draw()

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.SPACE:
            if self.manager.gui_manager:
                self.manager.gui_manager.hide_gui()
            self.manager.change_state(StartView(self.manager))
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        pass

import arcade
from abc import ABC, abstractmethod
from pyglet.graphics import Batch


from constants import SCREEN_TITLE, GAMEPLAY_USE_DUMMY
from game_engine import MyGame

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

    def on_key_release(self, key: int, modifiers: int):
        if self._current_state:
            self._current_state.on_key_release(key, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self._current_state:
            self._current_state.on_mouse_press(x, y, button, modifiers)


# Конкретные состояния (экраны)


class StartView(GameState):
    """Стартовое окно с названием и кнопкой 'Старт'"""

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.gui_shown = False
        self.batch = None
        self.title_text = None
        self.prompt_text = None

    def on_show(self):
        print("[State] Переход в StartView")
        arcade.set_background_color(arcade.color.AMAZON)
        if self.state_manager.gui_manager:
            self.state_manager.gui_manager.hide_gui()
        self.gui_shown = False

        # Создаём Batch и тексты при первом показе
        if self.batch is None:
            self.batch = Batch()
            w = self.state_manager.window.width
            h = self.state_manager.window.height
            self.title_text = arcade.Text(
                SCREEN_TITLE,
                w // 2,
                h // 2 + 50,
                arcade.color.GOLD,
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
        self.state_manager.change_state(MenuView(self.state_manager))

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.SPACE:
            self.state_manager.change_state(MenuView(self.state_manager))

    def on_key_release(self, key: int, modifiers: int):
        pass

    def on_draw(self):
        self.state_manager.window.clear()
        if self.batch:
            self.batch.draw()

    def on_update(self, delta_time: float):
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.state_manager.change_state(MenuView(self.state_manager))


class MenuView(GameState):
    """Меню выбора сложности с поддержкой мыши"""

    def __init__(self, state_manager: StateManager, return_to_game=None):
        self.state_manager = state_manager
        self.difficulty = 1
        self.return_to_game = return_to_game

        self.batch = None
        self.title_text = None
        self.difficulty_texts = []
        self.hint_text = None
        self.pause_text = None

    def on_show(self):
        print("[State] Переход в MenuView")
        arcade.set_background_color(arcade.color.AMAZON)

        w = self.state_manager.window.width
        h = self.state_manager.window.height

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

        if self.state_manager.gui_manager:
            self.state_manager.gui_manager.show_menu_gui(
                on_new_game_callback=self.start_new_game
            )

    def _update_text_colors(self):
        difficulties = ["ЛЕГКАЯ", "СРЕДНЯЯ", "ТЯЖЁЛАЯ"]
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
        self.state_manager.change_state(
            GameplayView(self.state_manager, self.difficulty)
        )

    def on_draw(self):
        self.state_manager.window.clear()
        if self.batch:
            self.batch.draw()

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, key: int, modifiers: int):
        if key in (arcade.key.UP, arcade.key.LEFT):
            # Вверх/влево — к лёгкой (сложность -1)
            self.difficulty = (self.difficulty - 1) % 3
            self._update_text_colors()
        elif key in (arcade.key.DOWN, arcade.key.RIGHT):
            # Вниз/вправо — к тяжёлой (сложность +1)
            self.difficulty = (self.difficulty + 1) % 3
            self._update_text_colors()
        elif key == arcade.key.ENTER:
            self.start_new_game(None)
        elif key == arcade.key.ESCAPE and self.return_to_game:
            if self.state_manager.gui_manager:
                self.state_manager.gui_manager.hide_gui()
            self.state_manager.change_state(self.return_to_game)

    def on_key_release(self, key: int, modifiers: int):
        pass

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
    """Игровое окно (заглушка или настоящая игра по флагу)"""

    def __init__(self, state_manager: StateManager, difficulty: int):
        self.state_manager = state_manager
        self.difficulty = difficulty
        self.game_manager = None
        self.use_dummy = GAMEPLAY_USE_DUMMY  # ← флаг из constants.py

        # Для заглушки (batch и тексты)
        self.batch = None
        self.status_text = None
        self.diff_text = None
        self.hint_text = None

    def on_show(self):
        diff_names = ["легкий", "средний", "высокий"]
        print(
            f"[State] Переход в GameplayView (сложность: {diff_names[self.difficulty]})"
        )

        if self.use_dummy:
            # ========== ЗАГЛУШКА ==========
            print("[State] GameplayView: используется ЗАГЛУШКА")
            arcade.set_background_color(arcade.color.BLACK)
            if self.batch is None:
                self.batch = Batch()
                w = self.state_manager.window.width
                h = self.state_manager.window.height
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
                    "Нажмите 'W' для победы | 'L' для проигрыша | M/ESC для меню",
                    w // 2,
                    50,
                    arcade.color.LIGHT_GRAY,
                    16,
                    anchor_x="center",
                    batch=self.batch,
                )
            if self.state_manager.gui_manager:
                self.state_manager.gui_manager.hide_gui()

        else:
            # ========== НАСТОЯЩАЯ ИГРА ==========
            print("[State] GameplayView: используется НАСТОЯЩАЯ ИГРА")

            # Создаём игровой движок
            self.game_manager = MyGame(self.state_manager.window)

            # Назначаем callback-и ПЕРЕД запуском игры
            self.game_manager.set_on_win_callback(
                lambda: self.state_manager.change_state(
                    ResultView(
                        self.state_manager,
                        won=True,
                        coins=self.game_manager.coin_count,
                        kills=0,
                        difficulty=self.difficulty,
                    )
                )
            )
            self.game_manager.set_on_lose_callback(
                lambda: self.state_manager.change_state(
                    ResultView(
                        self.state_manager,
                        won=False,
                        coins=self.game_manager.coin_count,
                        kills=0,
                        difficulty=self.difficulty,
                    )
                )
            )
            self.game_manager.set_on_menu_callback(
                lambda: self.state_manager.change_state(
                    MenuView(self.state_manager, return_to_game=self)
                )
            )

            # Запускаем игру с выбранным уровнем и сложностью
            self.game_manager.start_game("ground")

            # Передаем сложность в игру (если это влияет на геймплей)
            self.game_manager.set_difficulty(self.difficulty)

            if self.state_manager.gui_manager:
                self.state_manager.gui_manager.hide_gui()

    def on_draw(self):
        if self.use_dummy:  # заглушка
            self.state_manager.window.clear()
            if self.batch:
                self.batch.draw()
        # настоящая игра
        pass

    def on_update(self, delta_time):
        # настоящая игра
        pass

    def on_key_press(self, key, modifiers):
        if self.use_dummy:  # заглушка
            if key == arcade.key.W:
                # Передаём сложность в ResultView
                self.state_manager.change_state(
                    ResultView(
                        self.state_manager,
                        won=True,
                        coins=15,
                        kills=3,
                        difficulty=self.difficulty,
                    )
                )
            elif key == arcade.key.L:
                # Передаём сложность в ResultView
                self.state_manager.change_state(
                    ResultView(
                        self.state_manager,
                        won=False,
                        coins=5,
                        kills=1,
                        difficulty=self.difficulty,
                    )
                )
            elif key == arcade.key.ESCAPE or key == arcade.key.M:
                self.state_manager.change_state(
                    MenuView(self.state_manager, return_to_game=self)
                )
        else:  # настоящая игра
            # Перехватываем клавишу ESCAPE для вызова меню/паузы
            # Вызываем callback, который настроили в on_show
            if key == arcade.key.ESCAPE:
                self.game_manager.on_menu_callback()
            elif key == arcade.key.W:
                self.game_manager.on_win_callback()
            elif key == arcade.key.L:
                self.game_manager.on_lose_callback()

    def on_key_release(self, key, modifiers):
        # настоящая игра
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        # настоящая игра
        pass


class ResultView(GameState):
    """Окно результата (победа или поражение)"""

    def __init__(
        self,
        state_manager: StateManager,
        won: bool,
        coins: int,
        kills: int,
        difficulty: int,
    ):
        self.state_manager = state_manager
        self.won = won
        self.coins = coins
        self.kills = kills
        self.difficulty = difficulty
        self.batch = None
        self.title_text = None
        self.coins_text = None
        self.kills_text = None
        self.hint_text = None
        self.difficulty_text = None

    def on_show(self):
        print(f"[State] Переход в ResultView (Победа: {self.won})")
        arcade.set_background_color(arcade.color.AMAZON)
        if self.state_manager.gui_manager:
            self.state_manager.gui_manager.hide_gui()

        # Создаём Batch и тексты при первом показе
        if self.batch is None:
            self.batch = Batch()
            w = self.state_manager.window.width
            h = self.state_manager.window.height

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

        # Текст сложности
        difficulty_names = ["Лёгкая", "Средняя", "Тяжёлая"]
        self.difficulty_text = arcade.Text(
            f"Сложность: {difficulty_names[self.difficulty]}",
            w // 2,
            h // 2 - 50,
            arcade.color.LIGHT_GRAY,
            20,
            anchor_x="center",
            batch=self.batch,
        )

    def on_draw(self):
        self.state_manager.window.clear()
        if self.batch:
            self.batch.draw()

    def on_update(self, delta_time: float):
        pass

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.SPACE:
            if self.state_manager.gui_manager:
                self.state_manager.gui_manager.hide_gui()
            self.state_manager.change_state(StartView(self.state_manager))
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_key_release(self, key: int, modifiers: int):
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        pass

import arcade
from abc import ABC, abstractmethod

from game_engine import MyGame


class GameState(ABC):
    @abstractmethod
    def on_show(self):
        pass

    @abstractmethod
    def on_draw(self):
        pass

    @abstractmethod
    def on_update(self, delta_time):
        pass

    @abstractmethod
    def on_key_press(self, key, modifiers):
        pass

    @abstractmethod
    def on_mouse_press(self, x, y, button, modifiers):
        pass


class StateManager:
    def __init__(self, window: arcade.Window):
        self.window = window
        self._current_state = None

    def change_state(self, new_state: GameState):
        self._current_state = new_state
        self._current_state.on_show()

    def on_draw(self):
        if self._current_state:
            self._current_state.on_draw()

    def on_update(self, delta_time):
        if self._current_state:
            self._current_state.on_update(delta_time)

    def on_key_press(self, key, modifiers):
        if self._current_state:
            self._current_state.on_key_press(key, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        if self._current_state:
            self._current_state.on_mouse_press(x, y, button, modifiers)


class StartView(GameState):
    def __init__(self, manager: StateManager):
        self.manager = manager

    def on_show(self):
        print("[State] StartView")
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.manager.window.clear()
        arcade.draw_text(
            "START VIEW",
            self.manager.window.width // 2,
            self.manager.window.height // 2,
            arcade.color.WHITE,
            40,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.manager.change_state(GameplayView(self.manager))

    def on_update(self, dt):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass


class MenuView(GameState):
    def __init__(self, manager: StateManager, return_to_game=None):
        self.manager = manager
        self.return_to_game = return_to_game

    def on_show(self):
        print("[State] MenuView (заглушка)")
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        self.manager.window.clear()
        arcade.draw_text(
            "MENU VIEW (ЗАГЛУШКА)",
            self.manager.window.width // 2,
            self.manager.window.height // 2,
            arcade.color.WHITE,
            40,
            anchor_x="center",
        )
        if self.return_to_game:
            arcade.draw_text(
                "Нажмите ESC для возврата в игру",
                self.manager.window.width // 2,
                self.manager.window.height // 2 - 50,
                arcade.color.LIGHT_GRAY,
                20,
                anchor_x="center",
            )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE and self.return_to_game:
            # Безопасно пытаемся возобновить игру
            if (
                hasattr(self.return_to_game, "game")
                and self.return_to_game.game
            ):
                self.return_to_game.game.resume()
            self.manager.change_state(self.return_to_game)

    def on_update(self, dt):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass


class GameplayView(GameState):
    def __init__(self, manager: StateManager, difficulty=1):
        self.manager = manager
        self.difficulty = difficulty
        self.game = None  # пока заглушка
        self.is_dummy = True  # флаг, что это заглушка

    def on_show(self):
        print("[State] GameplayView (заглушка — игра в разработке)")
        arcade.set_background_color(arcade.color.BLACK)
        # self.game = MyGame()
        # self.game.reset(self.difficulty)
        # Отключаем стандартное окно arcade, встраиваем в текущее
        # Перенаправляем камеры и контекст (сложный момент)
        # Временно: просто показываем, что игра запущена

    def on_draw(self):
        """
        self.manager.window.clear()
        if self.game:
            self.game.on_draw()
        """
        self.manager.window.clear()
        arcade.draw_text(
            "GAMEPLAY VIEW (ЗАГЛУШКА)\nИгра будет здесь",
            self.manager.window.width // 2,
            self.manager.window.height // 2,
            arcade.color.GREEN,
            30,
            anchor_x="center",
            multiline=True,
            align="center",
            width=400,
        )  # временно

    def on_update(self, delta_time):
        """
        if self.game:
            self.game.on_update(delta_time)
        """
        pass  # временно

    def on_key_press(self, key, modifiers):
        """
        if key == arcade.key.ESCAPE:
            self.game.pause()
            self.manager.change_state(
                MenuView(self.manager, return_to_game=self)
            )
        elif self.game:
            self.game.on_key_press(key, modifiers)
        """
        if key == arcade.key.ESCAPE:  # временно
            self.manager.change_state(
                MenuView(self.manager, return_to_game=self)
            )

    def on_key_release(self, key, modifiers):
        """
        if self.game:
            self.game.on_key_release(key, modifiers)
        """
        pass  # временно

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # временно

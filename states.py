import arcade
from abc import ABC, abstractmethod


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


class GameplayView(GameState):
    def __init__(self, manager: StateManager):
        self.manager = manager

    def on_show(self):
        print("[State] GameplayView")
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.manager.window.clear()
        arcade.draw_text(
            "GAMEPLAY VIEW",
            self.manager.window.width // 2,
            self.manager.window.height // 2,
            arcade.color.GREEN,
            40,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.manager.change_state(StartView(self.manager))

    def on_update(self, dt):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

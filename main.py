import arcade
from states import StateManager, StartView

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Monster Chase"


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.state_manager = StateManager(self)
        self.state_manager.change_state(StartView(self.state_manager))

    def on_draw(self):
        self.state_manager.on_draw()

    def on_update(self, delta_time):
        self.state_manager.on_update(delta_time)

    def on_key_press(self, key, modifiers):
        self.state_manager.on_key_press(key, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        self.state_manager.on_mouse_press(x, y, button, modifiers)


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()

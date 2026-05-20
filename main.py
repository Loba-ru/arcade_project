import arcade
from pyglet.graphics import Batch

# Константы окна
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Monster Chase"

# Константы карты
MAP_WIDTH = 3000
MAP_HEIGHT = 600
GROUND_HEIGHT = 32
PLAYER_START_X = 100
PLAYER_START_Y = 64

# Константы игрока
PLAYER_SCALE = 1.0
PLAYER_JUMP_SPEED = 15
PLAYER_MOVEMENT_SPEED = 5
PLAYER_LIVES = 3

# Константы физики
GRAVITY = 0.8

# Тайлы
TILE_SCALE = 0.5
TILE_SIZE = 64

# Камера: плавность следования
CAMERA_LERP = 0.12
DEAD_ZONE_W = int(SCREEN_WIDTH * 0.35)
DEAD_ZONE_H = int(SCREEN_HEIGHT * 0.45)


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            PLAYER_SCALE,
        )
        self.change_x = 0
        self.change_y = 0
        self.lives = PLAYER_LIVES


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.player_list = None
        self.wall_list = None
        self.physics_engine = None
        self.world_camera = None
        self.gui_camera = None
        self.batch = Batch()
        self.score_text = None

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Игрок
        player = Player()
        player.center_x = PLAYER_START_X
        player.center_y = PLAYER_START_Y
        self.player_list.append(player)

        # Земля
        ground = arcade.Sprite(
            ":resources:images/tiles/grassMid.png", TILE_SCALE
        )
        ground.center_x = MAP_WIDTH // 2
        ground.center_y = GROUND_HEIGHT
        ground.width = MAP_WIDTH
        self.wall_list.append(ground)

        # Физика
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player, self.wall_list, gravity_constant=GRAVITY
        )

        # Камеры (как в LMS)
        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        # Текст интерфейса
        self.score_text = arcade.Text(
            "Монеты: 0",
            SCREEN_WIDTH - 100,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
            batch=self.batch,
        )

    def on_draw(self):
        self.clear()

        # 1) Мировая камера
        self.world_camera.use()
        self.wall_list.draw()
        self.player_list.draw()

        # 2) GUI камера (интерфейс)
        self.gui_camera.use()
        self.batch.draw()

        # Сердечки (жизни) — рисуем отдельно
        for i in range(self.player_list[0].lives):
            x = 30 + i * 40
            y = SCREEN_HEIGHT - 40
            arcade.draw_text(
                "❤️", x, y, arcade.color.RED, font_size=30, anchor_x="center"
            )

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.update_camera()

    def update_camera(self):
        if not self.player_list:
            return

        player = self.player_list[0]
        cam_x, cam_y = self.world_camera.position

        # Мёртвая зона
        dz_left = cam_x - DEAD_ZONE_W // 2
        dz_right = cam_x + DEAD_ZONE_W // 2
        dz_bottom = cam_y - DEAD_ZONE_H // 2
        dz_top = cam_y + DEAD_ZONE_H // 2

        px, py = player.center_x, player.center_y
        target_x, target_y = cam_x, cam_y

        if px < dz_left:
            target_x = px + DEAD_ZONE_W // 2
        elif px > dz_right:
            target_x = px - DEAD_ZONE_W // 2
        if py < dz_bottom:
            target_y = py + DEAD_ZONE_H // 2
        elif py > dz_top:
            target_y = py - DEAD_ZONE_H // 2

        # Не показываем пустоту за краями карты
        half_w = self.world_camera.viewport_width // 2
        half_h = self.world_camera.viewport_height // 2
        target_x = max(half_w, min(MAP_WIDTH - half_w, target_x))
        target_y = max(half_h, min(MAP_HEIGHT - half_h, target_y))

        # Плавное движение камеры
        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y
        self.world_camera.position = (smooth_x, smooth_y)

    def on_key_press(self, key, modifiers):
        player = self.player_list[0]
        if key == arcade.key.LEFT:
            player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            player.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                player.change_y = PLAYER_JUMP_SPEED

    def on_key_release(self, key, modifiers):
        player = self.player_list[0]
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            player.change_x = 0


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()

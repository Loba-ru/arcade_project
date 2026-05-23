import arcade

from pyglet.display import get_display
from pyglet.graphics import Batch

from constants import *
from classes import Player


# class MyGame(arcade.Window):
class MyGame:
    # def __init__(self):
    def __init__(self, window: arcade.Window):
        # super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.window = window  # теперь получает готовое окно

        self.center_window()
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.player_list = None
        self.wall_list = None
        self.physics_engine = None
        self.world_camera = None
        self.gui_camera = None
        self.batch = Batch()
        self.score_text = None
        self.is_paused = False
        self.text_display = None
        self.on_win_callback = None
        self.on_lose_callback = None
        self.on_menu_callback = None
        self.difficulty = 1

    def center_window(self):
        """Центрирует окно на экране"""
        # Получаем основной монитор через pyglet.display
        display = get_display()
        screens = display.get_screens()
        screen = screens[0]  # основной экран

        # Размер экрана
        screen_width = screen.width
        screen_height = screen.height

        # Вычисляем позицию для центрирования
        x = (screen_width - SCREEN_WIDTH) // 2
        y = (screen_height - SCREEN_HEIGHT) // 2

        # Устанавливаем позицию окна
        self.window.set_location(x, y)

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Игрок
        player = Player(
            PLAYER_START_X,
            PLAYER_START_Y,
            PLAYER_SCALE,
            PLAYER_HEALTH,
            PLAYER_MOVEMENT_SPEED,
        )
        self.player_list.append(player)

        # Земля
        ground = arcade.Sprite(
            ":resources:images/tiles/grassMid.png", TILE_SCALE
        )
        ground.center_x = MAP_WIDTH // 2
        # ground.center_y = GROUND_HEIGHT
        ground.bottom = 0
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

        # Сердечки (жизни) — добавляем в batch
        self.heart_texts = []  # список для хранения объектов сердечек
        for i in range(PLAYER_LIVES):
            heart = arcade.Text(
                "❤️",
                30 + i * 40,
                SCREEN_HEIGHT - 40,
                arcade.color.RED,
                font_size=30,
                anchor_x="center",
                batch=self.batch,
            )
            self.heart_texts.append(heart)

        # Надпись внизу для тестирования ResultView
        self.text_display = arcade.Text(
            "W - победа | L - проигрыш | ESC - меню",
            SCREEN_WIDTH // 2,
            20,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
            batch=self.batch,
        )

        # Надпись вверху о выбранной сложности и текущем уровне
        self.level_text = arcade.Text(
            f"Уровень: Земля | Сложность: "
            f"{['Лёгкая', 'Средняя', 'Тяжёлая'][self.difficulty]}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 40,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
            batch=self.batch,
        )

    def update_level_display(self, level_name):
        """Обновляет отображение текущего уровня"""
        self.level_text.text = (
            f"Уровень: Земля | Сложность: "
            f"{['Лёгкая', 'Средняя', 'Тяжёлая'][self.difficulty]}"
        )

    def on_draw(self):
        self.window.clear()

        # 1) Мировая камера
        self.world_camera.use()
        self.wall_list.draw()
        self.player_list.draw()

        # 2) GUI камера (интерфейс)
        self.gui_camera.use()
        self.batch.draw()

    def on_update(self, delta_time):
        if not self.is_paused:
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

        # Кнопки для тестирования ResultView
        elif key == arcade.key.W:
            print("[DEBUG] W pressed — победа")
            if self.on_win_callback:
                self.on_win_callback()
            else:
                print("[DEBUG] (нет callback, только вывод)")

        elif key == arcade.key.L:
            print("[DEBUG] L pressed — поражение")
            if self.on_lose_callback:
                self.on_lose_callback()
            else:
                print("[DEBUG] (нет callback, только вывод)")

        elif key == arcade.key.ESCAPE:
            print("[DEBUG] ESC pressed — меню/пауза")
            if self.on_menu_callback:
                self.on_menu_callback()
            else:
                # ESC -> пауза (движение останавливается),
                # ещё раз ESC — возобновление
                self.is_paused = not self.is_paused
                print(f"[DEBUG] Пауза: {self.is_paused}")

    def on_key_release(self, key, modifiers):
        player = self.player_list[0]
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            player.change_x = 0

    def pause(self):
        """Приостанавливает игру (не обновляет физику)"""
        self.is_paused = True

    def resume(self):
        """Возобновляет игру"""
        self.is_paused = False

    def reset(self, difficulty=1):
        """Сбрасывает игру с новой сложностью"""
        self.difficulty = difficulty
        self.setup()
        self.is_paused = False


if __name__ == "__main__":
    """Только для тестового запуска (игру запускать из main.py)!"""

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game = MyGame(window)
    game.setup()

    # Перенаправляю события окна в game
    window.on_draw = game.on_draw
    window.on_update = game.on_update
    window.on_key_press = game.on_key_press
    window.on_key_release = game.on_key_release

    arcade.run()

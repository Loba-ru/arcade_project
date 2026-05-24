import arcade
from pyglet.graphics import Batch

from constants import *
from classes import Player


class BaseLevel(arcade.View):
    def __init__(
        self,
        game_manager,
        map_name: str,
        level_name: str,
        next_level_name: str | None,
        spawn_point=None,
    ):
        super().__init__()
        self.game_manager = game_manager
        self.map_name = map_name
        self.level_name = level_name
        self.next_level_name = next_level_name
        self.spawn_point = spawn_point or (PLAYER_START_X, PLAYER_START_Y)

        self.batch = Batch()

        self.tile_map = None
        self.player = None
        self.player_list = None
        self.physics_engine = None

        self.world_camera = None
        self.gui_camera = None

        self.ground_list = None
        self.floor1_list = None
        self.floor2_list = None
        self.ladder_list = None
        self.start_list = None
        self.entry_exit_list = None
        self.collision_list = None

        self.is_paused = False
        self.key_count = 0
        self.has_emerald = False
        self.up_pressed = False
        self.down_pressed = False

    def setup(self):
        self.load_map()
        self.spawn_player()
        self.setup_physics()
        self.setup_cameras()
        self.setup_gui()
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def load_map(self):
        self.tile_map = arcade.load_tilemap(self.map_name, TILE_SCALE)

        self.ground_list = self.tile_map.sprite_lists.get("ground")
        self.floor1_list = self.tile_map.sprite_lists.get("floor1")
        self.floor2_list = self.tile_map.sprite_lists.get("floor2")
        self.ladder_list = self.tile_map.sprite_lists.get("ladders")
        self.start_list = self.tile_map.sprite_lists.get("start")
        self.entry_exit_list = self.tile_map.sprite_lists.get("entry_exit")
        self.collision_list = self.tile_map.sprite_lists.get("collision")

    def get_next_spawn_point(self):
        return self.spawn_point

    def spawn_player(self):
        self.player_list = arcade.SpriteList()
        self.player = Player(
            self.spawn_point[0],
            self.spawn_point[1],
            PLAYER_SCALE,
            PLAYER_HEALTH,
            PLAYER_MOVEMENT_SPEED,
        )
        self.player_list.append(self.player)

    def setup_physics(self):
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.collision_list,
            gravity_constant=GRAVITY,
            ladders=self.ladder_list,
        )

    def setup_cameras(self):
        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

    def setup_gui(self):
        self.ui_level_difficulty_text = arcade.Text(
            self.game_manager.get_level_difficulty_text(),
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            16,
            anchor_x="center",
            batch=self.batch,
        )

        self.ui_left_text = arcade.Text(
            f"Ключи: {self.key_count}",
            20,
            20,
            arcade.color.WHITE,
            16,
            anchor_x="left",
            batch=self.batch,
        )
        self.ui_right_text = arcade.Text(
            self.get_goal_text(),
            SCREEN_WIDTH - 20,
            20,
            arcade.color.WHITE,
            16,
            anchor_x="right",
            batch=self.batch,
        )
        self.portal_hint_text = arcade.Text(
            "",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            batch=self.batch,
        )
        self.ui_coin_text = arcade.Text(
            f"Монеты: {self.game_manager.coin_count}",
            SCREEN_WIDTH - 20,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            20,
            anchor_x="right",
            batch=self.batch,
        )
        self.heart_texts = []
        for i in range(self.game_manager.lives):
            heart = arcade.Text(
                "❤️",
                30 + i * 40,
                SCREEN_HEIGHT - 40,
                arcade.color.RED,
                30,
                anchor_x="left",
                batch=self.batch,
            )
            self.heart_texts.append(heart)

        self.test_text = arcade.Text(
            "W - победа | L - проигрыш | ESC - меню",
            SCREEN_WIDTH // 2,
            20,
            arcade.color.WHITE,
            16,
            anchor_x="center",
            batch=self.batch,
        )

    def get_goal_text(self):
        if self.level_name == "ground":
            return "Цель: найти ключ"
        if self.level_name == "dungeon":
            return "Цель: найти ключ"
        if self.level_name == "sky":
            return "Цель: найти изумруд"
        return "Цель:"

    def on_draw(self):
        self.clear()

        self.world_camera.use()

        for layer in (
            self.ground_list,
            self.floor1_list,
            self.floor2_list,
            self.ladder_list,
            self.start_list,
            self.entry_exit_list,
        ):
            if layer:
                layer.draw()

        if self.player_list:
            self.player_list.draw()

        self.gui_camera.use()

        self.draw_gui()

    def draw_gui(self):
        """Отрисовка интерфейса"""
        self.batch.draw()

    def on_update(self, delta_time):
        if self.is_paused:
            return

        # Обновляем текст монет (если изменилось)
        new_coin_text = f"Монеты: {self.game_manager.coin_count}"
        if self.ui_coin_text.text != new_coin_text:
            self.ui_coin_text.text = new_coin_text

        # Обновляем цвет сердечек (если изменилось)
        for i in range(len(self.heart_texts)):
            new_color = (
                arcade.color.RED
                if i < self.game_manager.lives
                else arcade.color.GRAY
            )
            if self.heart_texts[i].color != new_color:
                self.heart_texts[i].color = new_color

        # Обновляем текст "Уровень | Сложность" (если изменилось)
        new_level_diff_text = self.game_manager.get_level_difficulty_text()
        if self.ui_level_difficulty_text.text != new_level_diff_text:
            self.ui_level_difficulty_text.text = new_level_diff_text

        # Обновляем текст "Ключи" (если изменилось)
        new_keys_text = f"Ключи: {self.key_count}"
        if self.ui_left_text.text != new_keys_text:
            self.ui_left_text.text = new_keys_text

        # Обновляем текст "Цель" (если изменилось)
        new_goal_text = self.get_goal_text()
        if self.ui_right_text.text != new_goal_text:
            self.ui_right_text.text = new_goal_text

        if self.physics_engine.is_on_ladder():
            if self.up_pressed and not self.down_pressed:
                self.player.change_y = LADDER_SPEED
            elif self.down_pressed and not self.up_pressed:
                self.player.change_y = -LADDER_SPEED
            elif not self.up_pressed and not self.down_pressed:
                self.player.change_y = 0
        else:
            if self.player.change_y in (LADDER_SPEED, -LADDER_SPEED):
                self.player.change_y = 0

        self.physics_engine.update()

        self.player.is_walking = (
            self.player.change_x != 0
            and not self.physics_engine.is_on_ladder()
        )
        self.player.update_animation(delta_time)

        self.update_camera()
        self.check_portal()
        self.sync_gui()

    def sync_gui(self):
        pass

    def update_camera(self):
        if not self.player:
            return

        cam_x, cam_y = self.world_camera.position
        px, py = self.player.center_x, self.player.center_y

        dz_left = cam_x - DEAD_ZONE_W // 2
        dz_right = cam_x + DEAD_ZONE_W // 2
        dz_bottom = cam_y - DEAD_ZONE_H // 2
        dz_top = cam_y + DEAD_ZONE_H // 2

        target_x, target_y = cam_x, cam_y

        if px < dz_left:
            target_x = px + DEAD_ZONE_W // 2
        elif px > dz_right:
            target_x = px - DEAD_ZONE_W // 2

        if py < dz_bottom:
            target_y = py + DEAD_ZONE_H // 2
        elif py > dz_top:
            target_y = py - DEAD_ZONE_H // 2

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        target_x = max(half_w, min(MAP_WIDTH - half_w, target_x))
        target_y = max(half_h, min(MAP_HEIGHT - half_h, target_y))

        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y
        self.world_camera.position = (smooth_x, smooth_y)

    def check_portal(self):
        if not self.entry_exit_list:
            return
        if arcade.check_for_collision_with_list(
            self.player, self.entry_exit_list
        ):
            self.on_enter_portal()

    def on_enter_portal(self):
        if self.next_level_name is None:
            return

        if self.level_name == "ground" and self.key_count == 0:
            self.show_portal_hint("Нужен ключ")
            return

        self.clear_portal_hint()
        self.game_manager.change_level(self.next_level_name)

    def show_portal_hint(self, message: str):
        if self.portal_hint_text:
            self.portal_hint_text.text = message

    def clear_portal_hint(self):
        if self.portal_hint_text:
            self.portal_hint_text.text = ""

    def reset_level(self):
        self.setup()

    def on_key_press(self, key, modifiers):
        # Горизонтальное движение
        if key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_MOVEMENT_SPEED

        # Вертикальное движение и прыжок (клавиша UP)
        elif key == arcade.key.UP:
            # Если на лестнице — просто поднимаемся
            if self.physics_engine.is_on_ladder():
                self.up_pressed = True
                self.player.change_y = LADDER_SPEED
            # Если НЕ на лестнице, но можем прыгнуть (стоим на земле) — прыгаем
            elif self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED

        # Движение вниз по лестнице (клавиша DOWN)
        elif key == arcade.key.DOWN:
            if self.physics_engine.is_on_ladder():
                self.down_pressed = True
                self.player.change_y = -LADDER_SPEED

        # Прыжок по клавише ПРОБЕЛ (альтернатива UP)
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED

        # Пауза
        elif key == arcade.key.ESCAPE:
            self.is_paused = not self.is_paused

        # Для тестирования
        elif key == arcade.key.W:
            print("[DEBUG] W pressed — победа")
        elif key == arcade.key.L:
            print("[DEBUG] L pressed — поражение")

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0
        elif key == arcade.key.UP:
            self.up_pressed = False
            if self.physics_engine.is_on_ladder() and not self.down_pressed:
                self.player.change_y = 0
        elif key == arcade.key.DOWN:
            self.down_pressed = False
            if self.physics_engine.is_on_ladder() and not self.up_pressed:
                self.player.change_y = 0


class GroundLevel(BaseLevel):
    def __init__(self, game_manager):
        super().__init__(
            game_manager=game_manager,
            map_name="assets/ladders_only.tmx",
            level_name="ground",
            next_level_name="dungeon",
            spawn_point=(PLAYER_START_X, PLAYER_START_Y),
        )


class DungeonLevel(BaseLevel):
    def __init__(self, game_manager):
        super().__init__(
            game_manager=game_manager,
            map_name="assets/level2.tmx",
            level_name="dungeon",
            next_level_name="sky",
            spawn_point=(PLAYER_START_X, PLAYER_START_Y),
        )


class SkyLevel(BaseLevel):
    def __init__(self, game_manager):
        super().__init__(
            game_manager=game_manager,
            map_name="assets/level3.tmx",
            level_name="sky",
            next_level_name=None,
            spawn_point=(PLAYER_START_X, PLAYER_START_Y),
        )

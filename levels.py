# ========== УРОВНИ ИГРЫ ==========
# BaseLevel (базовый класс)
# ├── GroundLevel (уровень "Земля")
# ├── DungeonLevel (уровень "Подземелье")
# └── SkyLevel (уровень "Небо")

import arcade
from pyglet.graphics import Batch

from constants import *
from classes import *


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
        self.spawn_point = spawn_point or PLAYER_SPAWN_DEFAULT

        self.batch = Batch()

        self.tile_map = None
        self.player = None
        self.player_list = None
        self.physics_engine = None

        self.world_camera = None
        self.gui_camera = None

        self.platform_list = None
        self.decoration_list = None
        self.hazards_list = None
        self.ladder_list = None
        self.start_list = None
        self.entry_exit_list = None
        self.collision_list = None
        self.gem_list = None
        self.key_list = None
        self.door_list = None
        self.door_trigger_list = None
        self.door_active = True
        self.block_list = None

        self.is_paused = False
        self.key_count = 0
        self.has_emerald = False
        self.up_pressed = False
        self.down_pressed = False
        self.invincible_frames = 0

    def setup(self):
        self.load_map()
        self.spawn_player()
        self.setup_physics()
        self.setup_cameras()
        self.setup_gui()
        arcade.set_background_color(arcade.color.SKY_BLUE)

        if self.level_name == "sky":
            self.gem_list = arcade.SpriteList()
            self.key_list = arcade.SpriteList()

            emerald = Emerald(EMERALD_SPAWN[0], EMERALD_SPAWN[1])
            sapphire = Sapphire(SAPPHIRE_SPAWN[0], SAPPHIRE_SPAWN[1])
            ruby = Ruby(RUBY_SPAWN[0], RUBY_SPAWN[1])

            self.gem_list.append(emerald)
            self.gem_list.append(sapphire)
            self.gem_list.append(ruby)

            self.total_gems = 3

            key = Key(KEY_SPAWN_SKY[0], KEY_SPAWN_SKY[1])
            self.key_list.append(key)

        elif self.level_name == "dungeon":
            self.key_list = arcade.SpriteList()
            key = Key(KEY_SPAWN_DUNGEON[0], KEY_SPAWN_DUNGEON[1])
            self.key_list.append(key)

    def load_map(self):
        self.tile_map = arcade.load_tilemap(self.map_name, TILE_SCALE)

        self.platform_list = self.tile_map.sprite_lists.get("platform")
        self.ladder_list = self.tile_map.sprite_lists.get("ladders")
        self.collision_list = self.tile_map.sprite_lists.get("collision")
        self.decoration_list = self.tile_map.sprite_lists.get("decoration")
        self.hazards_list = self.tile_map.sprite_lists.get("hazards")

        if self.level_name == "ground":
            if not self.game_manager.has_all_gems:
                self.start_list = self.tile_map.sprite_lists.get("startA")
                self.entry_exit_list = self.tile_map.sprite_lists.get(
                    "entry_exitA"
                )
                self.block_list = self.tile_map.sprite_lists.get("blockA")

                self.door_trigger_list = self.tile_map.sprite_lists.get(
                    "door_trigger"
                )
                self.door_list = self.tile_map.sprite_lists.get("door")
            else:
                self.door_list = None
                self.start_list = self.tile_map.sprite_lists.get("startB")
                self.entry_exit_list = self.tile_map.sprite_lists.get(
                    "entry_exitB"
                )
                self.block_list = self.tile_map.sprite_lists.get("blockB")
        else:
            self.start_list = self.tile_map.sprite_lists.get("startA")
            self.entry_exit_list = self.tile_map.sprite_lists.get("entry_exit")
            self.block_list = self.tile_map.sprite_lists.get("blockA")

            self.door_trigger_list = self.tile_map.sprite_lists.get(
                "door_trigger"
            )
            self.door_list = self.tile_map.sprite_lists.get("door")

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
        all_walls = arcade.SpriteList()
        for layer in (
            self.platform_list,
            self.collision_list,
            self.door_list,
            self.block_list,
        ):
            if layer:
                all_walls.extend(layer)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            all_walls,
            gravity_constant=GRAVITY,
            ladders=self.ladder_list,
        )

    def setup_cameras(self):
        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.world_camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

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
            f"Ключи: {self.key_count} | Драгоценности: {self.player.inventory.total_gems()}",
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
        if self.level_name == "sky":
            if not self.game_manager.has_all_gems:
                return "Цель: найти драгоценности - 3"
            return "Цель: найти портал"
        return "Цель: найти портал"

    def on_draw(self):
        self.clear()
        self.world_camera.use()

        for layer in (
            self.platform_list,
            self.ladder_list,
            self.start_list,
            self.entry_exit_list,
            self.decoration_list,
            self.hazards_list,
            self.door_list,
        ):
            if layer:
                layer.draw()

        if self.player_list:
            self.player_list.draw()

        if self.gem_list:
            self.gem_list.draw()

        if self.key_list:
            self.key_list.draw()

        self.gui_camera.use()
        self.draw_gui()

    def draw_gui(self):
        self.batch.draw()

    def on_update(self, delta_time):
        if self.is_paused:
            return

        self.ui_coin_text.text = f"Монеты: {self.game_manager.coin_count}"

        for i in range(len(self.heart_texts)):
            self.heart_texts[i].color = (
                arcade.color.RED
                if i < self.game_manager.lives
                else arcade.color.GRAY
            )

        self.ui_level_difficulty_text.text = (
            self.game_manager.get_level_difficulty_text()
        )
        self.ui_left_text.text = f"Ключи: {self.key_count}"
        self.ui_right_text.text = self.get_goal_text()

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

        if self.door_active:
            self.check_door()

        self.check_portal()

        if self.gem_list:
            gem_hit = arcade.check_for_collision_with_list(
                self.player, self.gem_list
            )
            for gem in gem_hit:
                gem.collect(self.player.inventory)
                gem.remove_from_sprite_lists()
                print(f"[DEBUG] Подобран {gem.gem_type}!")

                if self.player.inventory.total_gems() >= self.total_gems:
                    self.game_manager.has_all_gems = True
                    print("[DEBUG] Все драгоценности собраны!")

        self.check_hazards()

        for i, heart in enumerate(self.heart_texts):
            heart.color = (
                arcade.color.RED
                if i < self.game_manager.lives
                else arcade.color.GRAY
            )

        self.ui_left_text.text = (
            f"Ключи: {self.key_count} | "
            f"Драгоценности: {self.player.inventory.total_gems()}"
        )

        if self.key_list:
            key_hit = arcade.check_for_collision_with_list(
                self.player, self.key_list
            )
            for key in key_hit:
                key.collect(self.player.inventory)
                key.remove_from_sprite_lists()
                self.key_count += 1
                print(f"[DEBUG] Подобран ключ! Всего ключей: {self.key_count}")

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
            if self.door_active:
                print("[DEBUG] Нужен ключ, чтобы покинуть уровень!")
                self.show_portal_hint("Нужен ключ!")
                return

            self.on_enter_portal()

    def on_enter_portal(self):
        if self.level_name == "ground":
            if self.player.inventory.total_gems() >= 3:
                self.game_manager.check_victory("ground")
            else:
                print("[DEBUG] Не все камни собраны!")
            return

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
        if key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.UP:
            self.up_pressed = True
            if self.physics_engine.is_on_ladder():
                self.player.change_y = LADDER_SPEED
            elif self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.DOWN:
            self.down_pressed = True
            if self.physics_engine.is_on_ladder():
                self.player.change_y = -LADDER_SPEED
        elif key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.ESCAPE:
            self.is_paused = not self.is_paused
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

    def check_hazards(self):
        if self.invincible_frames > 0:
            self.invincible_frames -= 1
            return

        if not self.hazards_list:
            return

        if arcade.check_for_collision_with_list(
            self.player, self.hazards_list
        ):
            self.game_manager.lives -= 1
            print(f"[DEBUG] Урон! Осталось жизней: {self.game_manager.lives}")

            if self.game_manager.lives <= 0:
                if (
                    hasattr(self.game_manager, "on_lose_callback")
                    and self.game_manager.on_lose_callback
                ):
                    self.game_manager.on_lose_callback()
                else:
                    print("[DEBUG] Game Over! Выход...")
                    arcade.close_window()
                return

            self.respawn_player()
            self.invincible_frames = 60

    def respawn_player(self):
        """Воскрешает игрока в точке спавна."""
        self.player.center_x = self.spawn_point[0]
        self.player.center_y = self.spawn_point[1]
        self.player.change_x = 0
        self.player.change_y = 0

    def check_door(self):
        """Проверка касания триггера перед дверью."""
        if not self.door_list or not self.door_trigger_list:
            return

        hit_list = arcade.check_for_collision_with_list(
            self.player, self.door_trigger_list
        )
        if not hit_list:
            return

        print("[DEBUG] КАСАНИЕ ТРИГГЕРА ДВЕРИ! (Игрок нажал на кнопку)")

        if self.key_count > 0 and self.game_manager.has_all_gems:
            print("[DEBUG] Дверь открыта! Ключ использован.")

            self.key_count -= 1
            self.player.inventory.discard("key", 1)

            for door in self.door_list:
                door.remove_from_sprite_lists()

            self.door_list = None
            self.door_active = False

            all_walls = arcade.SpriteList()
            for layer in (
                self.platform_list,
                self.collision_list,
                self.block_list,
            ):
                if layer:
                    all_walls.extend(layer)

            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player,
                all_walls,
                gravity_constant=GRAVITY,
                ladders=self.ladder_list,
            )

            print("[DEBUG] Физика обновлена, дверь удалена")
        else:
            if self.key_count == 0:
                print("[DEBUG] Нужен ключ для открытия двери!")
                self.show_portal_hint("Нужен ключ!")
            elif not self.game_manager.has_all_gems:
                print("[DEBUG] Нужны все драгоценности!")
                self.show_portal_hint("Нужны все драгоценности!")


class GroundLevel(BaseLevel):
    def __init__(self, game_manager):
        if game_manager.has_all_gems:
            spawn_point = PLAYER_SPAWN_GROUND_B
        else:
            spawn_point = PLAYER_SPAWN_GROUND_A
        super().__init__(
            game_manager=game_manager,
            map_name=MAP_PATH_GROUND,
            level_name="ground",
            next_level_name="dungeon",
            spawn_point=spawn_point,
        )


class DungeonLevel(BaseLevel):
    def __init__(self, game_manager):
        super().__init__(
            game_manager=game_manager,
            map_name=MAP_PATH_DUNGEON,
            level_name="dungeon",
            next_level_name="sky",
            spawn_point=PLAYER_SPAWN_DUNGEON,
        )


class SkyLevel(BaseLevel):
    def __init__(self, game_manager):
        super().__init__(
            game_manager=game_manager,
            map_name=MAP_PATH_SKY,
            level_name="sky",
            next_level_name="ground",
            spawn_point=PLAYER_SPAWN_SKY,
        )

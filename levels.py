# ========== УРОВНИ ИГРЫ ==========
# Модуль для работы с уровнями игры Monster Chase (arcade)
#
# BaseLevel (базовый класс)
# ├── GroundLevel (уровень "Земля")
# ├── DungeonLevel (уровень "Подземелье")
# └── SkyLevel (уровень "Небо")

import arcade
from pyglet.graphics import Batch

from constants import *
from classes import *


class BaseLevel(arcade.View):
    """Базовый класс для всех уровней игры."""

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

        self.physics_engine = None
        self.tile_map = None
        self.player = None

        self.player_list = None
        self.enemy_list = None

        self.world_camera = None
        self.gui_camera = None

        self.background_list = None
        self.platform_list = None
        self.decoration_list = None
        self.hazards_list = None
        self.ladder_list = None
        self.start_list = None
        self.entry_exit_list = None
        self.collision_list = None
        self.gem_list = None
        self.key_list = None
        self.coin_list = None
        self.collected_coin_list = None
        self.door_list = None
        self.door_trigger_list = None
        self.block_list = None

        self.all_walls = None

        self.door_active = True
        self.is_paused = False
        self.hint_timer = 0
        self.key_count = 0
        self.up_pressed = False
        self.down_pressed = False
        self.invincible_frames = 0
        self.hurt_flash_timer = 0
        self.hurt_freeze_timer = 0
        self.pending_game_over = False
        self.pending_respawn = False
        self.total_gems = 0
        self.dust_particles = None
        self.was_jumping = False
        self.dead_zone_w = DEAD_ZONE_W
        self.dead_zone_h = DEAD_ZONE_H

        self.ui_level_difficulty_text = None
        self.ui_left_text = None
        self.ui_right_text = None
        self.portal_hint_text = None
        self.ui_coin_text = None
        self.heart_texts = None
        self.test_text = None

    def setup(self):
        """Инициализация уровня."""
        self.set_background()
        self.load_map()
        self.spawn_player()
        self.setup_physics()
        self.setup_cameras()
        self.setup_gui()

        fm = self.game_manager.window.file_manager

        if self.level_name == "sky":
            self.gem_list = arcade.SpriteList()
            self.key_list = arcade.SpriteList()

            img_path = fm.get_image_path(ITEMS_DIR, EMERALD_IMAGE)
            emerald = Emerald(img_path, EMERALD_SPAWN[0], EMERALD_SPAWN[1])

            img_path = fm.get_image_path(ITEMS_DIR, SAPPHIRE_IMAGE)
            sapphire = Sapphire(img_path, SAPPHIRE_SPAWN[0], SAPPHIRE_SPAWN[1])

            img_path = fm.get_image_path(ITEMS_DIR, RUBY_IMAGE)
            ruby = Ruby(img_path, RUBY_SPAWN[0], RUBY_SPAWN[1])

            self.gem_list.append(emerald)
            self.gem_list.append(sapphire)
            self.gem_list.append(ruby)
            self.total_gems = 3

            img_path = fm.get_image_path(ITEMS_DIR, KEY_IMAGE)
            key = Key(img_path, KEY_SPAWN_SKY[0], KEY_SPAWN_SKY[1])
            self.key_list.append(key)

        elif self.level_name == "dungeon":
            self.key_list = arcade.SpriteList()

            img_path = fm.get_image_path(ITEMS_DIR, KEY_IMAGE)
            key = Key(img_path, KEY_SPAWN_DUNGEON[0], KEY_SPAWN_DUNGEON[1])
            self.key_list.append(key)

        elif self.level_name == "ground":
            if not self.game_manager.has_all_gems:
                self.key_list = arcade.SpriteList()

                img_path = fm.get_image_path(ITEMS_DIR, KEY_IMAGE)
                key = Key(img_path, KEY_SPAWN_GROUND[0], KEY_SPAWN_GROUND[1])
                self.key_list.append(key)
            else:
                self.key_list = None

            self.coin_list = arcade.SpriteList()

            textures = self.game_manager.texture_manager.load_coin_textures()
            coin = AnimatedCoin(textures, 704, 256)
            self.coin_list.append(coin)

            self.enemy_list = arcade.SpriteList()

            enemy = EasyEnemy(832, 178)
            self.enemy_list.append(enemy)

        self.dust_particles = arcade.SpriteList()

        self.collected_coin_list = arcade.SpriteList()

    def load_map(self):
        """Загрузка карты из Tiled."""
        map_path = self.game_manager.window.file_manager.get_map_path(
            self.map_name
        )
        self.tile_map = arcade.load_tilemap(map_path, TILE_SCALE)

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
                self.door_list = self.tile_map.sprite_lists.get("door")
                self.door_trigger_list = self.tile_map.sprite_lists.get(
                    "door_trigger"
                )
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
        """Возвращает точку спавна для следующего уровня."""
        return self.spawn_point

    def spawn_player(self):
        """Спавн игрока с восстановлением здоровья и жизней."""
        if self.game_manager.player is None:
            textures = self.game_manager.texture_manager.load_player_textures()
            self.game_manager.player = AnimatedPlayer(
                textures,
                self.spawn_point[0],
                self.spawn_point[1],
                PLAYER_SCALE,
                PLAYER_HEALTH,
                PLAYER_MOVEMENT_SPEED,
            )
        else:
            self.game_manager.player.center_x = self.spawn_point[0]
            self.game_manager.player.center_y = self.spawn_point[1]
            self.game_manager.player.change_x = 0
            self.game_manager.player.change_y = 0

        self.game_manager.player.health = PLAYER_HEALTH
        self.game_manager.player.lives = self.game_manager.lives

        self.player = self.game_manager.player
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

    def setup_physics(self):
        """Настройка физического движка."""
        self.all_walls = arcade.SpriteList()
        for layer in (
            self.platform_list,
            self.collision_list,
            self.block_list,
        ):
            if layer:
                self.all_walls.extend(layer)

        if self.door_active:
            self.all_walls.extend(self.door_list)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.all_walls,
            gravity_constant=GRAVITY,
            ladders=self.ladder_list,
        )

        self.game_manager.player.physics_engine = self.physics_engine

    def setup_cameras(self):
        """Настройка камер с динамическим dead zone."""
        screen_width, screen_height = self.game_manager.window.get_size()
        self.dead_zone_w = int(screen_width * 0.35)
        self.dead_zone_h = int(screen_height * 0.35)
        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.world_camera.position = (screen_width / 2, screen_height / 2)

    def setup_gui(self):
        """Создание UI элементов."""
        screen_width, screen_height = self.game_manager.window.get_size()
        self.ui_level_difficulty_text = arcade.Text(
            self.game_manager.get_level_difficulty_text(),
            screen_width // 2,
            screen_height - 40,
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
            screen_width - 20,
            20,
            arcade.color.WHITE,
            16,
            anchor_x="right",
            batch=self.batch,
        )
        self.portal_hint_text = arcade.Text(
            "",
            screen_width // 2,
            screen_height // 2,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            batch=self.batch,
        )
        self.ui_coin_text = arcade.Text(
            f"Монеты: {self.game_manager.coin_count}",
            screen_width - 20,
            screen_height - 40,
            arcade.color.WHITE,
            20,
            anchor_x="right",
            batch=self.batch,
        )

        self.heart_texts = []
        for i in range(self.player.lives):
            heart = arcade.Text(
                "❤️",
                30 + i * 40,
                screen_height - 40,
                arcade.color.RED,
                30,
                anchor_x="left",
                batch=self.batch,
            )
            self.heart_texts.append(heart)

        self.test_text = arcade.Text(
            "W - победа | L - проигрыш | ESC - меню",
            screen_width // 2,
            20,
            arcade.color.WHITE,
            16,
            anchor_x="center",
            batch=self.batch,
        )

    def resize_gui(self, screen_width, screen_height):
        """Пересчёт позиций GUI при изменении размера окна."""
        if self.ui_level_difficulty_text:
            self.ui_level_difficulty_text.x = screen_width // 2
            self.ui_level_difficulty_text.y = screen_height - 40

        if self.ui_coin_text:
            self.ui_coin_text.x = screen_width - 20
            self.ui_coin_text.y = screen_height - 40

        if self.ui_left_text:
            self.ui_left_text.x = 20
            self.ui_left_text.y = 20

        if self.ui_right_text:
            self.ui_right_text.x = screen_width - 20
            self.ui_right_text.y = 20

        if self.portal_hint_text:
            self.portal_hint_text.x = screen_width // 2
            self.portal_hint_text.y = screen_height // 2

        if self.heart_texts:
            for i, heart in enumerate(self.heart_texts):
                heart.x = 30 + i * 40
                heart.y = screen_height - 40

        if self.test_text:
            self.test_text.x = screen_width // 2
            self.test_text.y = 20

        if self.background_list:
            for bg_sprite in self.background_list:
                bg_sprite.center_x = screen_width // 2
                bg_sprite.center_y = screen_height // 2

                texture = bg_sprite.texture
                if texture:
                    scale_x = screen_width / texture.width
                    scale_y = screen_height / texture.height
                    bg_sprite.scale = max(scale_x, scale_y)

    def on_draw(self):
        """Отрисовка уровня."""
        self.clear()

        if self.background_list:
            self.background_list.draw()

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

        if self.coin_list:
            self.coin_list.draw()

        if self.collected_coin_list:
            self.collected_coin_list.draw()

        if self.enemy_list:
            self.enemy_list.draw()

        if self.dust_particles:
            self.dust_particles.draw()

        self.gui_camera.use()
        self.draw_gui()

    def draw_gui(self):
        """Отрисовка GUI."""
        self.batch.draw()

    def on_update(self, delta_time):
        """Обновление состояния уровня."""
        if self.is_paused:
            return

        self.ui_coin_text.text = f"Монеты: {self.game_manager.coin_count}"
        self.ui_level_difficulty_text.text = (
            self.game_manager.get_level_difficulty_text()
        )
        self.ui_right_text.text = self.get_goal_text()

        for i, heart in enumerate(self.heart_texts):
            heart.color = (
                arcade.color.RED
                if i < self.player.lives
                else arcade.color.GRAY
            )

        self.update_ui_left_text()

        if self.hint_timer > 0:
            self.hint_timer -= 1
            if self.hint_timer == 0:
                self.clear_portal_hint()

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

        on_ground = self.physics_engine.can_jump()
        if self.was_jumping and on_ground:
            self.create_dust_effect()
            self.was_jumping = False
        else:
            self.was_jumping = not on_ground

        self.dust_particles.update()

        # Обновление анимации собранных монет
        if self.collected_coin_list:
            for coin in self.collected_coin_list:
                if hasattr(coin, "update_animation"):
                    coin.update_animation(delta_time)

        self.update_enemies()

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

        if self.key_list:
            key_hit = arcade.check_for_collision_with_list(
                self.player, self.key_list
            )
            for key in key_hit:
                key.collect(self.player.inventory)
                key.remove_from_sprite_lists()
                self.key_count += 1
                print(f"[DEBUG] Подобран ключ! Всего ключей: {self.key_count}")

        # Сбор монет с анимацией
        if self.coin_list:
            coins_hit = arcade.check_for_collision_with_list(
                self.player, self.coin_list
            )
            for coin in coins_hit[:]:
                if hasattr(self.game_manager.window, "sound_manager"):
                    self.game_manager.window.sound_manager.play(
                        "coin", volume=0.5
                    )

                if hasattr(coin, "collect_with_animation"):
                    coin.remove_from_sprite_lists()
                    self.collected_coin_list.append(coin)
                    coin.collect_with_animation(self.player.inventory)
                else:
                    coin.collect(self.player.inventory)

                self.game_manager.coin_count = self.player.inventory.get_count(
                    "coin"
                )

        self.check_hazards()
        self.update_hurt_effect()
        if (
            self.pending_game_over
            and self.hurt_freeze_timer == 0
            and self.hurt_flash_timer == 0
        ):
            if (
                hasattr(self.game_manager, "on_lose_callback")
                and self.game_manager.on_lose_callback
            ):
                self.game_manager.on_lose_callback()
            else:
                print("[DEBUG] Game Over! Выход...")
                arcade.close_window()
            self.pending_game_over = False

    def update_camera(self):
        """Плавное обновление камеры с dead zone."""
        if not self.player:
            return

        cam_x, cam_y = self.world_camera.position
        px, py = self.player.center_x, self.player.center_y

        dz_left = cam_x - self.dead_zone_w // 2
        dz_right = cam_x + self.dead_zone_w // 2
        dz_bottom = cam_y - self.dead_zone_h // 2
        dz_top = cam_y + self.dead_zone_h // 2

        target_x, target_y = cam_x, cam_y

        if px < dz_left:
            target_x = px + self.dead_zone_w // 2
        elif px > dz_right:
            target_x = px - self.dead_zone_w // 2

        if py < dz_bottom:
            target_y = py + self.dead_zone_h // 2
        elif py > dz_top:
            target_y = py - self.dead_zone_h // 2

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2

        target_x = max(half_w, min(MAP_WIDTH - half_w, target_x))
        target_y = max(half_h, min(MAP_HEIGHT - half_h, target_y))

        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y
        self.world_camera.position = (smooth_x, smooth_y)

    def check_portal(self):
        """Проверка столкновения с порталом/выходом."""
        if not self.entry_exit_list:
            return

        hits = arcade.check_for_collision_with_list(
            self.player, self.entry_exit_list
        )

        if self.game_manager.in_victory_portal:
            if not hits:
                self.game_manager.check_victory_from_portal()
        else:
            if hits:
                if (
                    self.level_name == "ground"
                    and self.game_manager.has_all_gems
                ):
                    self.game_manager.in_victory_portal = True
                else:
                    self.game_manager.change_level(self.next_level_name)

    def show_portal_hint(self, message: str):
        """Показать подсказку у портала."""
        if self.portal_hint_text:
            self.portal_hint_text.text = message
            self.hint_timer = 120

    def clear_portal_hint(self):
        """Очистить подсказку у портала."""
        if self.portal_hint_text:
            self.portal_hint_text.text = ""

    def reset_level(self):
        """Сброс и пересоздание уровня."""
        self.setup()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш."""
        if self.game_manager.in_victory_portal:
            if key == arcade.key.LEFT:
                self.player.change_x = -PLAYER_MOVEMENT_SPEED
            return

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
        """Обработка отпускания клавиш."""
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
        """Проверка столкновения с ловушками (телепорт + потеря жизни)."""
        if self.invincible_frames > 0:
            self.invincible_frames -= 1
            return

        if not self.hazards_list:
            return

        if arcade.check_for_collision_with_list(
            self.player, self.hazards_list
        ):
            if not self.player.is_alive:
                return

            life_lost = self.player.lose_life()
            if life_lost:
                print(
                    f"[DEBUG] Урон от ловушки! Осталось жизней: {self.player.lives}"
                )
                self.game_manager.lives = self.player.lives

                self.hurt_freeze_timer = 30
                self.hurt_flash_timer = 60
                self.invincible_frames = 60
                self.pending_respawn = True

                if not self.player.is_alive:
                    self.pending_game_over = True

    def respawn_player(self):
        """Воскрешение игрока в точке спавна."""
        self.player.center_x = self.spawn_point[0]
        self.player.center_y = self.spawn_point[1]
        self.player.change_x = 0
        self.player.change_y = 0
        self.player.alpha = 255
        self.hurt_flash_timer = 0
        self.hurt_freeze_timer = 0

    def check_door(self):
        """Проверка касания триггера перед дверью."""
        if not self.door_list or not self.door_trigger_list:
            return

        hit_list = arcade.check_for_collision_with_list(
            self.player, self.door_trigger_list
        )
        if not hit_list:
            return

        trigger = hit_list[0]
        if (
            trigger.properties.get("type") != "trigger"
            or trigger.properties.get("action") != "open_door"
        ):
            return

        can_open = self.key_count > 0
        if self.level_name == "sky":
            can_open = can_open and self.game_manager.has_all_gems

        if can_open:
            print("[DEBUG] Дверь открыта! Ключ использован.")

            self.key_count -= 1
            if hasattr(self.player, "inventory"):
                self.player.inventory.discard("key", 1)

            if self.door_list:
                for tile in self.door_list[:]:
                    tile.remove_from_sprite_lists()
            self.door_list = None

            self.door_active = False
        else:
            if self.key_count == 0:
                self.show_portal_hint("Нужен ключ!")
            elif not self.game_manager.has_all_gems:
                self.show_portal_hint("Нужны все драгоценности!")

    def update_hurt_effect(self):
        """Обновление эффекта получения урона (заморозка и мигание)."""
        if self.hurt_freeze_timer > 0:
            self.player.change_x = 0
            self.player.change_y = 0
            self.hurt_freeze_timer -= 1

            if self.hurt_freeze_timer == 0 and self.pending_respawn:
                self.respawn_player()
                self.pending_respawn = False

        if self.hurt_flash_timer > 0:
            self.hurt_flash_timer -= 1
            if self.hurt_flash_timer % 10 < 5:
                self.player.alpha = 128
            else:
                self.player.alpha = 255
        else:
            self.player.alpha = 255

    def get_goal_text(self):
        """Возвращает текст цели для UI."""
        if self.level_name == "sky":
            if not self.game_manager.has_all_gems:
                return "Цель: найти драгоценности!"
            elif not self.door_active:
                return "Цель: войти в портал"
            elif self.key_count == 0:
                return "Цель: найти ключ"
            else:
                return "Цель: открыть дверь"

        elif self.level_name == "dungeon":
            if not self.door_active:
                return "Цель: войти в портал"
            elif self.key_count == 0:
                return "Цель: найти ключ"
            else:
                return "Цель: открыть дверь"

        elif self.level_name == "ground":
            if self.game_manager.has_all_gems:
                return "Цель: вернуться живым!"
            elif not self.door_active:
                return "Цель: войти в портал"
            elif self.key_count == 0:
                return "Цель: найти ключ"
            else:
                return "Цель: открыть дверь"

        return "Цель: продолжить путь"

    def update_ui_left_text(self):
        """Обновляет текст в левом нижнем углу в зависимости от уровня."""
        if self.level_name == "sky":
            gems = self.player.inventory.total_gems()
            keys = self.player.inventory.get_count("key")
            self.ui_left_text.text = (
                f"Ключи: {keys} | Драгоценности: {gems} из 3"
            )

        elif self.level_name == "dungeon":
            keys = self.player.inventory.get_count("key")
            self.ui_left_text.text = f"Ключи: {keys}"

        elif self.level_name == "ground":
            if self.game_manager.has_all_gems:
                gems = self.player.inventory.total_gems()
                self.ui_left_text.text = f"Драгоценности: {gems}"
            else:
                keys = self.player.inventory.get_count("key")
                self.ui_left_text.text = f"Ключи: {keys}"

    def create_dust_effect(self):
        """Создаёт эффект пыли при приземлении."""
        for _ in range(15):
            particle = DustParticle(self.player.center_x, self.player.bottom)
            self.dust_particles.append(particle)

    def set_background(self, bg_name=None, color=None):
        """Установка фона уровня (текстура или цвет)."""
        if bg_name:
            try:
                self.background_list = arcade.SpriteList()

                window = self.game_manager.window

                bg_path = window.file_manager.get_bg_path(bg_name)
                texture = arcade.load_texture(bg_path)

                screen_width, screen_height = window.get_size()

                bg_sprite = arcade.Sprite(texture)
                bg_sprite.center_x = screen_width / 2
                bg_sprite.center_y = screen_height / 2

                scale_x = screen_width / texture.width
                scale_y = screen_height / texture.height
                bg_sprite.scale = max(scale_x, scale_y)

                self.background_list.append(bg_sprite)

            except Exception as e:
                print(f"[ERROR] Не удалось загрузить текстуру {bg_path}: {e}")
                arcade.set_background_color(arcade.color.SKY_BLUE)
                self.background_list = None

        elif color:
            arcade.set_background_color(color)
            self.background_list = None
        else:
            arcade.set_background_color(arcade.color.SKY_BLUE)
            self.background_list = None

    def update_enemies(self):
        """Обновление врагов и проверка коллизий с игроком (отбрасывание)."""
        if not self.enemy_list:
            return

        self.enemy_list.update()

        for enemy in self.enemy_list:
            if arcade.check_for_collision(self.player, enemy):
                if self.invincible_frames <= 0:
                    self.player.take_damage(enemy.damage)
                    print(
                        f"[DEBUG] Урон от врага! Здоровье: {self.player.health}"
                    )

                    self.invincible_frames = 60
                    self.hurt_flash_timer = 60

                    if self.player.center_x < enemy.center_x:
                        self.player.change_x = -12
                    else:
                        self.player.change_x = 12
                    self.player.change_y = 8

                    if self.player.health <= 0:
                        life_lost = self.player.lose_life()
                        if life_lost:
                            print(
                                f"[DEBUG] Потеряна жизнь! Осталось: {self.player.lives}"
                            )
                            self.game_manager.lives = self.player.lives

                            self.respawn_player()

                            if not self.player.is_alive:
                                self.pending_game_over = True
                    break


class GroundLevel(BaseLevel):
    """Уровень 'Земля'."""

    def __init__(self, game_manager):
        spawn_point = (
            PLAYER_SPAWN_GROUND_B
            if game_manager.has_all_gems
            else PLAYER_SPAWN_GROUND_A
        )
        super().__init__(
            game_manager=game_manager,
            map_name=MAP_GROUND,
            level_name="ground",
            next_level_name="dungeon",
            spawn_point=spawn_point,
        )
        if game_manager.has_all_gems:
            self.door_active = False

    def set_background(self):
        super().set_background(bg_name=BG_GROUND)


class DungeonLevel(BaseLevel):
    """Уровень 'Подземелье'."""

    def __init__(self, game_manager):
        super().__init__(
            game_manager=game_manager,
            map_name=MAP_DUNGEON,
            level_name="dungeon",
            next_level_name="sky",
            spawn_point=PLAYER_SPAWN_DUNGEON,
        )

    def set_background(self):
        super().set_background(bg_name=BG_DUNGEON)


class SkyLevel(BaseLevel):
    """Уровень 'Небо'."""

    def __init__(self, game_manager):
        super().__init__(
            game_manager=game_manager,
            map_name=MAP_SKY,
            level_name="sky",
            next_level_name="ground",
            spawn_point=PLAYER_SPAWN_SKY,
        )

    def set_background(self):
        super().set_background(bg_name=BG_SKY)

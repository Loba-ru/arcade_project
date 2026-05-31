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
        self.friend = None
        self.friend_cage = None
        self.friend_activated = False

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
        self.friend_list = None
        self.cage_trigger_list = None
        self.cage_list = None
        self.all_walls = None
        self.center_hint_background_list = None
        self.victory_block_list = None

        self.ui_top_background_list = None
        self.ui_bottom_background_list = None

        self.door_active = True
        self.is_paused = False
        self.central_hint_timer = 0
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
        self.footstep_timer = 0
        self.footstep_interval = 0.35
        self.portal_cooldown = False
        self.dead_zone_w = DEAD_ZONE_W
        self.dead_zone_h = DEAD_ZONE_H
        self.key_dropped_from_enemy = False
        self.enemy_total_count = 0
        self.enemies_killed = 0
        self.last_death_reason = None
        self.tickle_cooldown = 0

        # Только для 2-го захода ground:
        # "defeat_enemies", "collect_key", "save_friend", "enter_portal"
        self.victory_task = None

        # Для всех уровней (кроме 2-го захода ground)
        # "find_key", "find_gems", "open_door", "enter_portal"
        self.current_task = None

        self.ui_level_difficulty_text = None
        self.ui_left_text = None
        self.ui_right_text = None
        self.center_hint_text = None
        self.center_hint_background = None
        self.ui_top_background = None
        self.ui_bottom_background = None
        self.ui_coin_text = None
        self.heart_texts = None
        self.test_text = None

    def setup(self):
        """Инициализация уровня."""
        self.set_background()
        self.load_map()
        self.spawn_player()

        # Инициализация задачи победы (с задержкой) только для 2-го захода на ground
        if self.level_name == "ground" and self.game_manager.has_all_gems:
            self.victory_task = "defeat_enemies"
            hint = "Победите всех врагов-призраков!"
            arcade.schedule_once(lambda dt: self.show_central_hint(hint), 2.0)
        else:
            # Для 1-го захода на ground, для "dungeon" и для "sky"
            if self.level_name == "ground" or self.level_name == "dungeon":
                self.current_task = "find_key"
                hint = "Найдите ключ!"
            elif self.level_name == "sky":
                self.current_task = "find_gems"
                hint = "Найдите драгоценности!"
            arcade.schedule_once(lambda dt: self.show_central_hint(hint), 2.0)

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

            self.friend_list = arcade.SpriteList()

            x, y = FRIEND_SPAWN_GROUND
            texture = self.game_manager.texture_manager.load_friend_textures()
            self.friend = AnimatedFriend(texture, x, y)

            self.friend_list.append(self.friend)

            # TODO: будет удалено после тестирования MediumEnemy и HardEnemy
            """
            self.enemy_list = arcade.SpriteList()

            tm = self.game_manager.texture_manager
            texture = tm.load_enemy_textures("slime_green", 2)
            enemy = AnimatedEasyEnemy(texture, 832, 178)

            self.enemy_list.append(enemy)
            """
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
            self.cage_trigger_list = self.tile_map.sprite_lists.get(
                "cage_trigger"
            )
            self.cage_list = self.tile_map.sprite_lists.get("cage")

            # Блокировка портала победы (только для 2-го захода на ground)
            self.victory_block_list = self.tile_map.sprite_lists.get(
                "victory_block"
            )

        else:
            self.start_list = self.tile_map.sprite_lists.get("startA")
            self.entry_exit_list = self.tile_map.sprite_lists.get("entry_exit")
            self.block_list = self.tile_map.sprite_lists.get("blockA")
            self.door_trigger_list = self.tile_map.sprite_lists.get(
                "door_trigger"
            )
            self.door_list = self.tile_map.sprite_lists.get("door")

        self.coin_list = self.tile_map.sprite_lists.get("coins")
        if self.coin_list:
            animated_coins = arcade.SpriteList()
            texture = self.game_manager.texture_manager.load_coin_textures()
            for coin in self.coin_list:
                x, y = coin.center_x, coin.center_y
                animated_coins.append(AnimatedCoin(texture, x, y))
            self.coin_list = animated_coins

        self.enemy_list = self.tile_map.sprite_lists.get("enemies")
        if self.enemy_list:
            animated_enemies = arcade.SpriteList()
            tm = self.game_manager.texture_manager

            if self.game_manager.has_all_gems:
                for enemy_data in self.enemy_list:
                    enemy_type = enemy_data.properties.get("type")
                    if enemy_type == "easy_enemy":
                        texture = tm.load_enemy_textures("ghost", 2)
                        x, y = enemy_data.center_x, enemy_data.center_y
                        animated_enemies.append(
                            AnimatedEasyEnemy(texture, x, y)
                        )
                self.enemy_total_count = len(self.enemy_list)
            else:
                for enemy_data in self.enemy_list:
                    enemy_type = enemy_data.properties.get("type")
                    name = enemy_data.properties.get("name", "slime_green")

                    if enemy_type == "easy_enemy":
                        texture = tm.load_enemy_textures(name, 2)
                        x, y = enemy_data.center_x, enemy_data.center_y
                        animated_enemies.append(
                            AnimatedEasyEnemy(texture, x, y)
                        )

                    elif enemy_type == "enemy_medium":
                        texture = tm.load_enemy_textures(name, 3)
                        x, y = enemy_data.center_x, enemy_data.center_y
                        animated_enemies.append(
                            AnimatedMediumEnemy(texture, x, y)
                        )

                    # TODO: добавить medium_enemy и hard_enemy

            self.enemy_list = animated_enemies
        else:
            self.enemy_list = arcade.SpriteList()

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
            self.victory_block_list,
        ):
            if layer:
                self.all_walls.extend(layer)

        if self.door_active:
            self.all_walls.extend(self.door_list)

        if self.cage_list:
            self.all_walls.extend(self.cage_list)

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

        self.setup_ui_backgrounds()

        self.ui_level_difficulty_text = arcade.Text(
            self.game_manager.get_level_difficulty_text(),
            screen_width // 2,
            screen_height - 40,
            arcade.color.WHITE,
            20,
            anchor_x="center",
            batch=self.batch,
        )
        self.ui_left_text = arcade.Text(
            f"Ключи: {self.key_count} | Драгоценности: {self.player.inventory.total_gems()}",
            20,
            20,
            arcade.color.WHITE,
            22,
            anchor_x="left",
            batch=self.batch,
        )
        self.ui_right_text = arcade.Text(
            self.get_goal_text(),
            screen_width - 20,
            20,
            arcade.color.WHITE,
            22,
            anchor_x="right",
            batch=self.batch,
        )
        self.center_hint_text = arcade.Text(
            "",
            screen_width // 2,
            screen_height // 2,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center",
            bold=True,
            batch=self.batch,
        )
        texture = arcade.Texture.create_empty(
            "hint_bg", size=(600, 60), color=(0, 0, 0, 50)
        )
        self.center_hint_background = arcade.Sprite(texture)
        self.center_hint_background.center_x = screen_width // 2
        self.center_hint_background.center_y = screen_height // 2
        self.center_hint_background_list = arcade.SpriteList()
        self.center_hint_background_list.append(self.center_hint_background)

        coin = self.player.inventory.get_count("coin") if self.player else 0
        self.ui_coin_text = arcade.Text(
            f"Монеты: {coin}",
            screen_width - 20,
            screen_height - 40,
            arcade.color.WHITE,
            22,
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
            "F11 - экран | ESC - меню",
            screen_width // 2,
            20,
            arcade.color.WHITE,
            16,
            anchor_x="center",
            batch=self.batch,
        )
        gems = self.game_manager.has_all_gems
        level_names = {
            "ground": ("УРОВЕНЬ 4. Земля" if gems else "УРОВЕНЬ 1. Земля"),
            "dungeon": "УРОВЕНЬ 2. Подземелье",
            "sky": "УРОВЕНЬ 3. Небо",
        }
        level_display = level_names.get(self.level_name, self.level_name)
        self.show_central_hint(level_display)

    def resize_gui(self, screen_width, screen_height):
        """Пересчёт позиций GUI при изменении размера окна."""
        if self.ui_top_background_list:
            for bg_sprite in self.ui_top_background_list:
                bg_sprite.center_x = screen_width // 2
                bg_sprite.center_y = screen_height - 30

                texture = bg_sprite.texture
                if texture:
                    scale_x = screen_width / texture.width
                    bg_sprite.scale = scale_x
                    bg_sprite.scale_y = 1

        if self.ui_bottom_background_list:
            for bg_sprite in self.ui_bottom_background_list:
                bg_sprite.center_x = screen_width // 2
                bg_sprite.center_y = 30

                texture = bg_sprite.texture
                if texture:
                    scale_x = screen_width / texture.width
                    bg_sprite.scale = scale_x
                    bg_sprite.scale_y = 1

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

        if self.center_hint_text:
            self.center_hint_text.x = screen_width // 2
            self.center_hint_text.y = screen_height // 2
        if self.center_hint_background:
            self.center_hint_background.center_x = screen_width // 2
            self.center_hint_background.center_y = screen_height // 2

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

        if self.friend_list:
            self.friend_list.draw()

        if self.cage_trigger_list:
            self.cage_trigger_list.draw()

        if self.dust_particles:
            self.dust_particles.draw()

        self.gui_camera.use()
        self.draw_gui()

    def draw_gui(self):
        """Отрисовка GUI."""
        if self.ui_top_background_list:
            self.ui_top_background_list.draw()

        if self.ui_bottom_background_list:
            self.ui_bottom_background_list.draw()

        if (
            self.center_hint_text
            and self.center_hint_text.text
            and self.center_hint_background_list
        ):
            self.center_hint_background_list.draw()

        self.batch.draw()

    def on_update(self, delta_time):
        """Обновление состояния уровня."""
        # Если физика отключена (победа/портал), ничего не обновляем
        if self.physics_engine is None:
            return

        if self.is_paused:
            return

        coin = self.player.inventory.get_count("coin") if self.player else 0
        self.ui_coin_text.text = f"Монеты: {coin}"

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

        if self.central_hint_timer > 0:
            self.central_hint_timer -= 1
            if self.central_hint_timer == 0:
                self.clear_central_hint()

        if self.physics_engine.is_on_ladder():
            # # Выравнивание по центру лестницы
            self.align_to_ladder()

            # Собственно движение по лестнице
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

        if abs(self.player.change_x) > 0 and self.physics_engine.can_jump():
            self.footstep_timer += delta_time
            if self.footstep_timer >= self.footstep_interval:
                self.footstep_timer = 0
                if hasattr(self.game_manager.window, "sound_manager"):
                    self.game_manager.window.sound_manager.play(
                        "footstep", volume=0.3
                    )

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

        self.check_cage_collision()

        if (
            self.cage_trigger_list
            and not self.friend_activated
            and self.game_manager.has_all_gems
            and self.key_count > 0
        ):
            hits = arcade.check_for_collision_with_list(
                self.player, self.cage_trigger_list
            )
            if hits:
                # Друг спасён
                self.friend_activated = True

                # Обновление задачи победы и разблокировка портала победы
                if self.victory_task == "save_friend":
                    self.victory_task = "enter_portal"

                    # Удаляем блокировку c портала победы
                    if self.victory_block_list:
                        for block in self.victory_block_list[:]:
                            block.remove_from_sprite_lists()
                        self.victory_block_list = None

                    self.show_central_hint("Вернитесь домой!")

                self.friend.activate()

                self.key_count -= 1
                if hasattr(self.player, "inventory"):
                    self.player.inventory.discard("key", 1)

                for tile in self.cage_trigger_list:
                    self._fade_out_tile(tile)

                for _ in range(50):
                    x = self.friend.center_x + random.randint(-60, 60)
                    y = self.friend.center_y + random.randint(-60, 60)
                    color = random.choice(
                        [(160, 100, 60), (120, 70, 40), (200, 150, 100)]
                    )
                    particle = CagePiece(x, y, color)
                    self.dust_particles.append(particle)

                if self.cage_list:
                    for tile in self.cage_list[:]:
                        tile.remove_from_sprite_lists()
                    self.cage_list = None

                for trigger in self.cage_trigger_list[:]:
                    trigger.remove_from_sprite_lists()
                self.cage_trigger_list = None

                if hasattr(self.game_manager.window, "sound_manager"):
                    self.game_manager.window.sound_manager.play(
                        "door_open", volume=0.7
                    )

        self.player.is_walking = (
            self.player.change_x != 0
            and not self.physics_engine.is_on_ladder()
        )
        self.player.update_animation(delta_time)

        self.create_trail_effect()

        if self.friend_list and self.friend.is_active:
            x, y = self.player.center_x, self.player.center_y
            self.friend.follow_player(x, y, offset_x=50, offset_y=0)
            self.friend.update_animation(delta_time)

        self.update_camera()

        if self.door_active:
            self.check_door()

        self.check_portal()

        if self.gem_list:
            gem_hit = arcade.check_for_collision_with_list(
                self.player, self.gem_list
            )
            for gem in gem_hit:
                if hasattr(self.game_manager.window, "sound_manager"):
                    self.game_manager.window.sound_manager.play(
                        "gem", volume=0.8
                    )
                gem.collect(self.player.inventory)
                gem.remove_from_sprite_lists()
                print(f"[DEBUG] Подобран {gem.gem_type}!")

                self.show_central_hint(f"Найден {gem.name}!")

                if self.player.inventory.total_gems() >= self.total_gems:
                    self.game_manager.has_all_gems = True
                    print("[DEBUG] Все драгоценности собраны!")

                    # Звук получения усиления от кристаллов
                    if hasattr(self.game_manager.window, "sound_manager"):
                        arcade.schedule_once(
                            lambda dt: self.game_manager.window.sound_manager.play(
                                "powerup", volume=0.7
                            ),
                            2.0,
                        )

                    hint = f"Получена невосприимчивость к врагам!"
                    arcade.schedule_once(
                        lambda dt: self.show_central_hint(hint), 2.0
                    )

                    # Проверяем, найден ли уже ключ
                    if self.key_count > 0:
                        self.current_task = "open_door"

                        def show_door_hint(dt):
                            if self.door_active:
                                self.show_central_hint("Откройте дверь!")

                        arcade.schedule_once(show_door_hint, 4.0)
                    else:
                        self.current_task = "find_key"

                        def show_key_hint(dt):
                            if self.key_count == 0:
                                self.show_central_hint("Найдите ключ!")

                        arcade.schedule_once(show_key_hint, 4.0)

                else:
                    hint = "Найдите все драгоценности!"
                    arcade.schedule_once(
                        lambda dt: self.show_central_hint(hint), 2.0
                    )

        # Подбор ключа
        if self.key_list:
            key_hit = arcade.check_for_collision_with_list(
                self.player, self.key_list
            )
            for key in key_hit:
                if hasattr(self.game_manager.window, "sound_manager"):
                    self.game_manager.window.sound_manager.play(
                        "key", volume=0.6
                    )
                key.collect(self.player.inventory)
                key.remove_from_sprite_lists()
                self.key_count += 1
                print(f"[DEBUG] Подобран ключ! Всего ключей: {self.key_count}")
                self.show_central_hint("Подобран ключ!")

                # Обновление задачи победы (только для 2-го захода на ground)
                if self.victory_task == "collect_key":
                    self.victory_task = "save_friend"

                    def show_cage_hint(dt):
                        # Показываем подсказку только если друг ещё не активирован
                        if not self.friend_activated:
                            self.show_central_hint("Откройте клетку!")

                    arcade.schedule_once(show_cage_hint, 2.0)

                # Обновление задачи для 1-го захода на ground, "dungeon", "sky"
                elif self.current_task == "find_key":
                    self.current_task = "open_door"

                    def show_door_hint(dt):
                        if self.door_active:
                            self.show_central_hint("Откройте дверь!")

                    arcade.schedule_once(show_door_hint, 2.0)

                elif self.current_task == "find_gems":
                    # На sky ключ найден, но камни ещё не собраны
                    # Оставляем задачу find_gems, не меняем current_task
                    def show_gems_hint(dt):
                        if not self.game_manager.has_all_gems:
                            self.show_central_hint("Найдите драгоценности!")

                    arcade.schedule_once(show_gems_hint, 2.0)

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
                arcade.exit()
            self.pending_game_over = False

        if self.tickle_cooldown > 0:
            self.tickle_cooldown -= 1

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
        if not self.entry_exit_list:
            return

        hits = arcade.check_for_collision_with_list(
            self.player, self.entry_exit_list
        )

        if self.game_manager.in_victory_portal:
            if not hits:
                self.physics_engine = None
                self.game_manager.check_victory_from_portal()

        else:
            if hits:
                # Победа на ground (2-й заход)
                if (
                    self.level_name == "ground"
                    and self.game_manager.has_all_gems
                ):
                    # Пускаем в портал
                    if self.victory_task == "enter_portal":
                        if hasattr(self.game_manager.window, "sound_manager"):
                            self.game_manager.window.sound_manager.play(
                                "portal", volume=0.7
                            )
                        self.game_manager.in_victory_portal = True
                        self.show_central_hint("Пройдите через портал!")

                    # Выводим подсказки для пропуска в портал
                    elif self.victory_task == "defeat_enemies":
                        self.show_central_hint(
                            "Победите всех врагов-призраков!"
                        )
                    elif self.victory_task == "collect_key":
                        self.show_central_hint("Подберите ключ!")
                    elif self.victory_task == "save_friend":
                        self.show_central_hint("Откройте клетку!")

                # Обычный переход между уровнями
                elif self.next_level_name:
                    if hasattr(self.game_manager.window, "sound_manager"):
                        self.game_manager.window.sound_manager.play(
                            "portal", volume=0.7
                        )
                    self.physics_engine = None
                    self.game_manager.change_level(self.next_level_name)

    def show_central_hint(self, message: str):
        """Показать подсказку в центре экрана"""
        if self.center_hint_text:
            self.center_hint_text.text = message
            self.central_hint_timer = 120

    def clear_central_hint(self):
        """Очистить подсказку в центре экрана."""
        if self.center_hint_text:
            self.center_hint_text.text = ""

    def reset_level(self):
        """Сброс и пересоздание уровня."""
        self.setup()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш."""

        # Блокировка управления после спасения друга (только движение влево/вправо)
        if (
            self.victory_task == "enter_portal"
            or self.game_manager.in_victory_portal
        ):
            if key == arcade.key.LEFT:
                self.player.change_x = -PLAYER_MOVEMENT_SPEED
            return

        # В остальных случаях управление не блокируется
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
        elif key == arcade.key.W and GAMEPLAY_USE_DUMMY:
            print("[DEBUG] W pressed — победа")
        elif key == arcade.key.L and GAMEPLAY_USE_DUMMY:
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
                if hasattr(self.game_manager.window, "sound_manager"):
                    self.game_manager.window.sound_manager.play(
                        "lose_life", volume=0.5
                    )
                print(
                    f"[DEBUG] Урон от ловушки! Осталось жизней: {self.player.lives}"
                )
                self.game_manager.lives = self.player.lives

                self.hurt_freeze_timer = 30
                self.hurt_flash_timer = 60
                self.invincible_frames = 60
                self.pending_respawn = True

                if self.player.is_alive:
                    self.last_death_reason = "hazard"
                else:
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

        if self.last_death_reason == "hazard":
            self.show_central_hint("Остерегайтесь ловушек!")
        elif self.last_death_reason == "enemy":
            self.show_central_hint("Остерегайтесь врагов-животных!")
        elif self.last_death_reason == "cage":
            self.show_central_hint("Не прикасайтесь к клетке!")

        self.last_death_reason = None

    def check_door(self):
        """Проверка касания триггера перед дверью."""
        if self.level_name == "ground" and self.game_manager.has_all_gems:
            print("[DEBUG] check_door пропущен (ground с кристаллами)")
            return

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
            if hasattr(self.game_manager.window, "sound_manager"):
                self.game_manager.window.sound_manager.play(
                    "door_open", volume=0.7
                )

            print("[DEBUG] Дверь открыта! Ключ использован.")

            self.key_count -= 1
            if hasattr(self.player, "inventory"):
                self.player.inventory.discard("key", 1)

            if self.door_list:
                for tile in self.door_list[:]:
                    tile.remove_from_sprite_lists()
            self.door_list = None

            self.door_active = False
            if self.current_task == "open_door":
                self.current_task = "enter_portal"
            self.show_central_hint("Войдите в портал!")

        else:
            if self.key_count == 0:
                self.show_central_hint("Нужен ключ!")
            elif not self.game_manager.has_all_gems:
                self.show_central_hint("Нужны все драгоценности!")

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
            if not self.game_manager.has_all_gems:
                if not self.door_active:
                    return "Цель: войти в портал"
                elif self.key_count == 0:
                    return "Цель: найти ключ"
                else:
                    return "Цель: открыть дверь"

            if self.enemies_killed < self.enemy_total_count:
                return "Цель: победить врагов!"

            if self.key_dropped_from_enemy:
                if self.friend_activated:
                    return "Цель: войти в портал"
                else:
                    if self.key_count == 0:
                        return "Цель: подобрать ключ"
                    else:
                        return "Цель: открыть клетку!"
            else:
                return "Цель: победить врагов!"

        return "Цель: вернуться живым!"

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
                keys = self.player.inventory.get_count("key")
                killed = self.enemies_killed
                total = self.enemy_total_count
                self.ui_left_text.text = (
                    f"Ключи: {keys} | Врагов повержено: {killed} из {total}"
                )
            else:
                keys = self.player.inventory.get_count("key")
                self.ui_left_text.text = f"Ключи: {keys}"

    def create_dust_effect(self):
        """Создаёт эффект пыли при приземлении."""
        for _ in range(15):
            particle = DustParticle(self.player.center_x, self.player.bottom)
            self.dust_particles.append(particle)

    def create_trail_effect(self):
        """Создаёт шлейф за игроком в зависимости от собранных камней."""
        if (
            self.friend_activated
            or self.victory_task == "enter_portal"
            or self.game_manager.in_victory_portal
        ):
            return

        total_gems = self.player.inventory.total_gems()
        if total_gems == 0 or abs(self.player.change_x) == 0:
            return

        colors = []

        base_colors = [
            (255, 215, 0, 180),  # GOLD
            (255, 140, 0, 180),  # ORANGE_RED
            (200, 200, 200, 180),  # Светло-серый
        ]

        gem_colors = []
        if self.player.inventory.has("ruby"):
            gem_colors.append((255, 80, 80, 180))  # Красный
        if self.player.inventory.has("emerald"):
            gem_colors.append((80, 255, 80, 180))  # Зелёный
        if self.player.inventory.has("sapphire"):
            gem_colors.append((80, 80, 255, 180))  # Синий

        # Формируем палитру в зависимости от количества камней
        if total_gems == 1:
            colors = gem_colors + [random.choice(base_colors)]
        elif total_gems == 2:
            colors = gem_colors + [random.choice(base_colors)]
        else:  # total_gems == 3
            colors = gem_colors + base_colors

        if not colors:
            return

        color = random.choice(colors)

        # Основная частица
        if self.player.change_x > 0:
            offset_x = -30
        else:
            offset_x = 30

        particle = TrailParticle(
            self.player.center_x + offset_x,
            self.player.center_y - 25,
            color,
        )
        self.dust_particles.append(particle)

        # Вторая частица с вероятностью 50%
        if random.random() < 0.5:
            if self.player.change_x > 0:
                offset_x2 = -50
            else:
                offset_x2 = 50
            color2 = random.choice(colors) if len(colors) > 1 else color
            particle2 = TrailParticle(
                self.player.center_x + offset_x2,
                self.player.center_y - 15,
                color2,
            )
            self.dust_particles.append(particle2)

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
        """Обновление врагов и проверка коллизий с игроком."""
        if not self.enemy_list:
            return

        self.enemy_list.update()

        for enemy in self.enemy_list[:]:
            if arcade.check_for_collision(self.player, enemy):

                if self.game_manager.has_all_gems:
                    # Звук хихиканья при касании с врагами-животными (не на ground)
                    if self.level_name != "ground":
                        if self.tickle_cooldown == 0 and hasattr(
                            self.game_manager.window, "sound_manager"
                        ):
                            self.game_manager.window.sound_manager.play(
                                "tickle", volume=0.5
                            )
                            self.tickle_cooldown = 120
                        continue

                    if self.level_name == "ground":
                        if hasattr(enemy, "start_dying") and not getattr(
                            enemy, "_death_started", False
                        ):
                            enemy._death_started = True
                            enemy.start_dying()

                            # Призраки лопаются, как пузырьки
                            if hasattr(
                                self.game_manager.window, "sound_manager"
                            ):
                                self.game_manager.window.sound_manager.play(
                                    "pop", volume=0.8
                                )
                            print(f"[DEBUG] Враг повержен!")
                            self.game_manager.enemies_defeated += 1
                            self.enemies_killed += 1

                            for _ in range(25):
                                particle = ExplosionEffect(
                                    enemy.center_x, enemy.center_y + 64
                                )
                                self.dust_particles.append(particle)

                            # Обновление задачи победы
                            if (
                                self.victory_task == "defeat_enemies"
                                and self.enemies_killed
                                >= self.enemy_total_count
                            ):
                                self.victory_task = "collect_key"
                            if (
                                self.enemies_killed == self.enemy_total_count
                                and not self.key_dropped_from_enemy
                            ):
                                self._drop_key(enemy.center_x, enemy.center_y)
                    continue

                # Обычная логика урона (без кристаллов)
                if self.invincible_frames <= 0:
                    if hasattr(self.game_manager.window, "sound_manager"):
                        self.game_manager.window.sound_manager.play(
                            "hit", volume=0.3
                        )

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
                            window = self.game_manager.window
                            if hasattr(window, "sound_manager"):
                                window.sound_manager.play(
                                    "lose_life", volume=0.5
                                )
                            print(
                                f"[DEBUG] Потеряна жизнь! Осталось: {self.player.lives}"
                            )
                            self.game_manager.lives = self.player.lives

                            if self.player.is_alive:
                                self.last_death_reason = "enemy"
                            else:
                                self.pending_game_over = True

                            self.respawn_player()
                    break

    def check_cage_collision(self):
        """Проверка столкновения с клеткой (отталкивание, если нет кристаллов)."""
        if not self.cage_trigger_list:
            return

        hits = arcade.check_for_collision_with_list(
            self.player, self.cage_trigger_list
        )
        if not hits:
            return

        # Показываем подсказку всегда при контакте с клеткой
        if self.key_count == 0:
            self.show_central_hint("Нужен ключ!")

        elif self.key_count > 0 and not self.key_dropped_from_enemy:
            self.show_central_hint("Ключ не подходит!")
            next_hint = "Откройте дверь!"
            arcade.schedule_once(
                lambda dt: self.show_central_hint(next_hint), 2.0
            )

        if self.game_manager.has_all_gems:
            return

        if self.invincible_frames > 0:
            return

        self.player.take_damage(20)
        print(f"[DEBUG] Урон от клетки! Здоровье: {self.player.health}")

        self.player.change_x = -8
        self.player.change_y = 5

        if self.player.center_x < hits[0].center_x + 20:
            self.player.center_x = hits[0].center_x - 50

        self.invincible_frames = 20
        self.hurt_flash_timer = 20

        # ДОБАВИТЬ ПРОВЕРКУ ПОТЕРИ ЖИЗНИ
        if self.player.health <= 0:
            life_lost = self.player.lose_life()
            if life_lost:
                if hasattr(self.game_manager.window, "sound_manager"):
                    self.game_manager.window.sound_manager.play(
                        "lose_life", volume=0.5
                    )
                print(f"[DEBUG] Потеряна жизнь! Осталось: {self.player.lives}")
                self.game_manager.lives = self.player.lives

                if self.player.is_alive:
                    self.last_death_reason = "cage"
                else:
                    self.pending_game_over = True

                self.respawn_player()

        if hasattr(self.game_manager.window, "sound_manager"):
            self.game_manager.window.sound_manager.play("hit", volume=0.3)

    def _fade_out_tile(self, tile):
        """Плавное исчезновение тайла клетки."""
        if tile.alpha > 0:
            tile.alpha = max(0, tile.alpha - 25)
            arcade.schedule(lambda dt, t=tile: self._fade_out_tile(t), 0.02)
        else:
            tile.remove_from_sprite_lists()

    def _drop_key(self, x, y):
        """Создаёт ключ из поверженного врага."""
        if self.key_dropped_from_enemy:
            return

        self.key_dropped_from_enemy = True

        fm = self.game_manager.window.file_manager
        img_path = fm.get_image_path(ITEMS_DIR, KEY_IMAGE)

        key = Key(img_path, x, y + 64)

        if self.key_list is None:
            self.key_list = arcade.SpriteList()
        self.key_list.append(key)

        print(f"[DEBUG] Ключ выпал в позиции ({x}, {y + 80})")

        self.show_central_hint("Выпал ключ!")

        def show_pickup_hint(dt):
            if self.key_count == 0:  # Ключ всё ещё не поднят
                self.show_central_hint("Подберите ключ!")

        arcade.schedule_once(show_pickup_hint, 2.0)

    def setup_ui_backgrounds(self):
        """Создаёт фоны для верхнего и нижнего UI."""
        screen_width, screen_height = self.game_manager.window.get_size()

        # Верхний фон (сердечки, монеты) — создаём текстуру нужного размера
        texture_top = arcade.Texture.create_empty(
            "ui_top_bg", size=(screen_width, 60), color=(0, 0, 0, 20)
        )
        self.ui_top_background = arcade.Sprite(texture_top)
        self.ui_top_background.center_x = screen_width // 2
        self.ui_top_background.center_y = screen_height - 30
        self.ui_top_background_list = arcade.SpriteList()
        self.ui_top_background_list.append(self.ui_top_background)

        # Нижний фон (ключи, цели)
        texture_bottom = arcade.Texture.create_empty(
            "ui_bottom_bg", size=(screen_width, 60), color=(0, 0, 0, 20)
        )
        self.ui_bottom_background = arcade.Sprite(texture_bottom)
        self.ui_bottom_background.center_x = screen_width // 2
        self.ui_bottom_background.center_y = 30
        self.ui_bottom_background_list = arcade.SpriteList()
        self.ui_bottom_background_list.append(self.ui_bottom_background)

    def align_to_ladder(self):
        """Выравнивание игрока по центру лестницы."""
        if not self.ladder_list:
            return

        for ladder in self.ladder_list:
            # Проверяем, на этой ли лестнице стоит игрок
            if (
                abs(self.player.center_x - ladder.center_x) < 96
                and abs(self.player.center_y - ladder.center_y) < 96
            ):
                # Двигаем игрока к центру лестницы
                if self.player.center_x < ladder.center_x:
                    self.player.center_x = min(
                        ladder.center_x, self.player.center_x + 2
                    )
                elif self.player.center_x > ladder.center_x:
                    self.player.center_x = max(
                        ladder.center_x, self.player.center_x - 2
                    )
                break  # Нашли лестницу, выходим


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

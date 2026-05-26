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

        # Списки спрайтов
        self.tile_map = None
        self.player = None
        self.player_list = None
        self.physics_engine = None

        # Камеры
        self.world_camera = None
        self.gui_camera = None

        # Списки объектов уровня
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
        self.block_list = None

        # Список стен для физики
        self.all_walls = None

        # Состояние уровня
        self.door_active = True
        self.is_paused = False
        self.hint_timer = 0
        self.key_count = 0
        self.up_pressed = False
        self.down_pressed = False
        self.invincible_frames = 0
        self.hurt_flash_timer = 0
        self.hurt_freeze_timer = 0
        self.total_gems = 0

        # UI элементы
        self.ui_level_difficulty_text = None
        self.ui_left_text = None
        self.ui_right_text = None
        self.portal_hint_text = None
        self.ui_coin_text = None
        self.heart_texts = None
        self.test_text = None

    def setup(self):
        """Инициализация уровня."""
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

        elif self.level_name == "ground":
            # Ключ нужен только при первом проходе
            if not self.game_manager.has_all_gems:
                self.key_list = arcade.SpriteList()
                key = Key(KEY_SPAWN_GROUND[0], KEY_SPAWN_GROUND[1])
                self.key_list.append(key)
            else:
                self.key_list = None

    def load_map(self):
        """Загрузка карты из Tiled."""
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
        if self.game_manager.player is None:
            self.game_manager.player = Player(
                self.spawn_point[0],
                self.spawn_point[1],
                PLAYER_SCALE,
                PLAYER_HEALTH,
                PLAYER_MOVEMENT_SPEED,
            )
        else:
            # Спавним существующего игрока, просто меняем позицию
            self.game_manager.player.center_x = self.spawn_point[0]
            self.game_manager.player.center_y = self.spawn_point[1]
            self.game_manager.player.change_x = 0
            self.game_manager.player.change_y = 0

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

    def setup_cameras(self):
        """Настройка камер."""
        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.world_camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def setup_gui(self):
        """Создание UI элементов."""
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

    def on_draw(self):
        """Отрисовка уровня."""
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
                if i < self.game_manager.lives
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

        self.check_hazards()

        self.update_hurt_effect()

    def update_camera(self):
        """Плавное обновление камеры с dead zone."""
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
        """Проверка столкновения с порталом/выходом."""
        if not self.entry_exit_list:
            return

        if arcade.check_for_collision_with_list(
            self.player, self.entry_exit_list
        ):
            self.on_enter_portal()

    def on_enter_portal(self):
        """Обработка входа в портал."""

        # Если это ground и камни собраны -> победа!
        if (
            self.level_name == "ground"
            and self.player.inventory.total_gems() >= 3
        ):
            if (
                hasattr(self.game_manager, "on_win_callback")
                and self.game_manager.on_win_callback
            ):
                self.game_manager.check_victory("ground")
            else:
                # Если запуск был через game_engine.py
                print("[DEBUG] ПОБЕДА! (тестовый режим)")
                arcade.close_window()
            return

        # Для остальных случаев -> смена уровня
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

            # Замораживаем игрока и запускаем мигание
            self.hurt_freeze_timer = 30  # заморозка на 0.5 сек (при 60 FPS)
            self.hurt_flash_timer = 60  # мигание на 1 сек
            self.invincible_frames = 60  # неуязвимость на 1 сек

            # Сохраняем позицию для телепортации
            self.death_position = (self.player.center_x, self.player.center_y)

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

            # Удаляем дверь правильно
            if self.door_list:
                for tile in self.door_list[:]:
                    tile.remove_from_sprite_lists()
            self.door_list = None

            self.door_active = False

            # print("[DEBUG] Дверь удалена")

        else:
            if self.key_count == 0:
                self.show_portal_hint("Нужен ключ!")
            elif not self.game_manager.has_all_gems:
                self.show_portal_hint("Нужны все драгоценности!")

    def update_hurt_effect(self):
        """Обновление эффекта получения урона (заморозка и мигание)"""
        if self.hurt_freeze_timer > 0:
            # Игрок заморожен
            self.player.change_x = 0
            self.player.change_y = 0
            self.hurt_freeze_timer -= 1

            if self.hurt_freeze_timer == 0:
                # Телепортируем на спавн
                self.respawn_player()

        if self.hurt_flash_timer > 0:
            # Мигание (меняем прозрачность или видимость)
            self.hurt_flash_timer -= 1
            if self.hurt_flash_timer % 10 < 5:
                self.player.alpha = 128  # полупрозрачный
            else:
                self.player.alpha = 255  # нормальный
        else:
            self.player.alpha = 255

    def get_goal_text(self):
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
                return "Цель: вернуться живым!"  # после боя с боссом
            elif not self.door_active:
                return "Цель: войти в портал"
            elif self.key_count == 0:
                return "Цель: найти ключ"
            else:
                return "Цель: открыть дверь"

        # Запасной вариант
        return "Цель: продолжить путь"

    def update_ui_left_text(self):
        """Обновляет текст в левом нижнем углу в зависимости от уровня"""
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


class GroundLevel(BaseLevel):
    """Уровень "Земля"."""

    def __init__(self, game_manager):
        spawn_point = (
            PLAYER_SPAWN_GROUND_B
            if game_manager.has_all_gems
            else PLAYER_SPAWN_GROUND_A
        )
        super().__init__(
            game_manager=game_manager,
            map_name=MAP_PATH_GROUND,
            level_name="ground",
            next_level_name="dungeon",
            spawn_point=spawn_point,
        )
        if game_manager.has_all_gems:
            self.door_active = False  # для второго захода


class DungeonLevel(BaseLevel):
    """Уровень "Подземелье"."""

    def __init__(self, game_manager):
        super().__init__(
            game_manager=game_manager,
            map_name=MAP_PATH_DUNGEON,
            level_name="dungeon",
            next_level_name="sky",
            spawn_point=PLAYER_SPAWN_DUNGEON,
        )


class SkyLevel(BaseLevel):
    """Уровень "Небо"."""

    def __init__(self, game_manager):
        super().__init__(
            game_manager=game_manager,
            map_name=MAP_PATH_SKY,
            level_name="sky",
            next_level_name="ground",
            spawn_point=PLAYER_SPAWN_SKY,
        )

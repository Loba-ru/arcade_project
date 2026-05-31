# ========== АРХИТЕКТУРА СУЩНОСТЕЙ ==========
# Модуль с классами сущностей, предметов, инвентаря игры Monster Chase (arcade)

# Иерархия классов Существ:
# Entity (базовый класс)
# ├── Player (игрок)
# |   └── AnimatedPlayer (игрок с анимацией)
# └── Enemy (Враг)
#     ├── EasyEnemy (Лёгкий враг)
#     |   └── AnimatedEasyEnemy (Лёгкий враг с анимацией)
#     ├── MediumEnemy (Средний враг)
#     |   └── AnimatedMediumEnemy (Средний враг с анимацией)
#     └── HardEnemy (Тяжёлый враг)
#         └── AnimatedHardEnemy (Тяжёлый враг с анимацией)

# Иерархия классов внутриигровых предметов:
# BaseItem (базовый класс)
# ├── Emerald (Изумруд)
# ├── Sapphire (Сапфир)
# ├── Ruby (Рубин)
# ├── Key (Ключ)
# └── Coin (Монета)
#     └── AnimatedCoin (Монета с анимацией сбора)

# Союзники:
# Friend (Друг игрока)
# └── AnimatedFriend (Друг с анимацией)

# Вспомогательные классы:
# Inventory (Инвентарь игрока)
# DustParticle (Эффект приземления игрока)
# ExplosionEffect (Эффект взрыва при уничтожении врагов)
# CagePiece (Эффект разрушения клетки)
# TrailParticle (Эффект шлейфа за игроком после получения силы)

import arcade
import random
from abc import ABC, abstractmethod

from constants import *


class Inventory:
    """Инвентарь игрока."""

    def __init__(self):
        self.items = {}

    def add(self, item_type, count=1):
        self.items[item_type] = self.items.get(item_type, 0) + count

    def discard(self, item_type, count=1):
        if item_type in self.items:
            old_count = self.items.get(item_type, 0)
            if old_count - count > 0:
                self.items[item_type] = old_count - count
            else:
                self.items.pop(item_type)

    def has(self, item_type, count=1):
        return self.items.get(item_type, 0) >= count

    def get_count(self, item_type):
        return self.items.get(item_type, 0)

    def total_gems(self):
        """Возвращает общее количество драгоценных камней."""
        gem_types = ["emerald", "sapphire", "ruby"]
        return sum(self.get_count(g) for g in gem_types)


class Entity(arcade.Sprite, ABC):
    """Базовый класс для всех живых существ."""

    def __init__(
        self, path_or_texture: str, scale: float, health: int, speed: float
    ):
        super().__init__(path_or_texture, scale)
        self.health = health
        self.speed = speed
        self.is_alive = True

    @abstractmethod
    def update(self, delta_time: float):
        pass

    def take_damage(self, amount: int):
        self.health -= amount
        if self.health <= 0:
            self.is_alive = False
            self.kill()


class Player(Entity):
    """Игрок."""

    def __init__(
        self,
        image_path: str,
        x: float,
        y: float,
        scale=1.0,
        health=100,
        speed=5.0,
    ):
        super().__init__(
            image_path,
            scale,
            health,
            speed,
        )
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.lives = 3
        self.max_health = health
        self.inventory = Inventory()

    def take_damage(self, amount: int):
        self.health -= amount
        if self.health <= 0:
            self.health = 0

    def lose_life(self):
        """Потеря жизни (при health <= 0)."""
        if self.lives > 0:
            self.lives -= 1
            self.health = self.max_health
            if self.lives <= 0:
                self.is_alive = False
            return True
        return False

    def heal(self, amount: int):
        """Лечение."""
        self.health = min(self.max_health, self.health + amount)

    def update(self, delta_time: float):
        self.center_x += self.change_x * self.speed * delta_time
        self.center_y += self.change_y * self.speed * delta_time


class AnimatedPlayer(Player):
    """Игрок с анимацией из атласа."""

    def __init__(
        self,
        textures: dict,
        x: float,
        y: float,
        scale=1.0,
        health=100,
        speed=5.0,
    ):
        idle_texture = textures.get("idle", [None])[0]
        super().__init__(idle_texture, x, y, scale, health, speed)

        self.state = "idle"
        self.textures = textures

        self.current_texture_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.12
        self.last_direction = 1

        self.physics_engine = None

    def update_state(self):
        """Определяет текущее состояние игрока по физике."""
        if self.physics_engine and self.physics_engine.is_on_ladder():
            if abs(self.change_y) > 0:
                self.state = "climb"
            else:
                self.state = "idle"
            return

        if self.change_y > 0:
            self.state = "jump"
            return
        elif self.change_y < 0:
            self.state = "fall"
            return

        if abs(self.change_x) > 0:
            self.state = "walk"
        else:
            self.state = "idle"

    def update_animation(self, delta_time):
        """Обновляет анимацию в зависимости от состояния."""
        self.update_state()

        textures = self.textures.get(self.state, self.textures.get("idle", []))
        if not textures:
            return

        if self.current_texture_index >= len(textures):
            self.current_texture_index = 0

        self.animation_timer += delta_time

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_texture_index = (
                self.current_texture_index + 1
            ) % len(textures)

        base_texture = textures[self.current_texture_index]

        if self.change_x > 0:
            self.last_direction = 1
            self.texture = base_texture
        elif self.change_x < 0:
            self.last_direction = -1
            self.texture = base_texture.flip_horizontally()
        else:
            if self.last_direction == -1:
                self.texture = base_texture.flip_horizontally()
            else:
                self.texture = base_texture


class Friend(arcade.Sprite):
    """Союзник, который следует за игроком."""

    def __init__(
        self, image_path: str, x: float, y: float, scale: float = 1.0
    ):
        super().__init__(image_path, scale=scale)
        self.center_x = x
        self.center_y = y
        self.is_active = False

    def activate(self):
        """Активация союзника (освобождение из клетки)."""
        self.is_active = True

    def follow_player(self, player_x, player_y, offset_x=-50, offset_y=0):
        """Следование за игроком с отступом."""
        if self.is_active:
            self.center_x = player_x + offset_x
            self.center_y = player_y + offset_y


class AnimatedFriend(Friend):
    """Союзник с анимацией ходьбы."""

    def __init__(self, textures: dict, x: float, y: float, scale: float = 1.0):
        idle_texture = textures.get("idle", [None])[0]
        super().__init__(idle_texture, x, y, scale)
        self.textures = textures
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.12
        self.last_direction = 1
        self.is_moving = False

    def update_animation(self, delta_time: float):
        """Обновляет анимацию в зависимости от движения."""
        if not self.is_active:
            return

        if not self.is_moving:
            # Стоим на месте — idle
            idle_texture = self.textures["idle"][0]
            if self.last_direction == -1:
                self.texture = idle_texture.flip_horizontally()
            else:
                self.texture = idle_texture
            return

        # Идём — анимация ходьбы
        walk_textures = self.textures["walk"]
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(walk_textures)
            base_texture = walk_textures[self.current_frame]

            if self.last_direction == -1:
                self.texture = base_texture.flip_horizontally()
            else:
                self.texture = base_texture

    def follow_player(self, player_x, player_y, offset_x=-50, offset_y=0):
        """Следование за игроком с обновлением направления и состояния движения."""
        if not self.is_active:
            return

        old_x = self.center_x
        self.center_x = player_x + offset_x
        self.center_y = player_y + offset_y

        if self.center_x < old_x:
            self.last_direction = -1
            self.is_moving = True
        elif self.center_x > old_x:
            self.last_direction = 1
            self.is_moving = True
        else:
            self.is_moving = False


class Enemy(Entity, ABC):
    """Базовый враг с ИИ движения."""

    def __init__(
        self,
        path_or_texture: str,
        scale: float,
        health: int,
        speed: float,
        damage: int,
    ):
        super().__init__(path_or_texture, scale, health, speed)
        self.damage = damage
        self.change_x = random.choice([-1, 1]) * speed
        self.change_y = random.choice([-1, 1]) * speed

    def update(self, delta_time: float):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time


class EasyEnemy(Enemy):
    """Враг простой сложности."""

    def __init__(self, image_path: str, x: float, y: float):
        super().__init__(
            image_path,
            scale=1.0,
            health=1,
            speed=80,
            damage=20,
        )
        self.center_x = x
        self.center_y = y
        self.boundary_left = x - 150
        self.boundary_right = x + 150
        self.direction = 1

    def update(self, delta_time: float):
        self.center_x += self.speed * self.direction * delta_time

        if self.center_x >= self.boundary_right:
            self.center_x = self.boundary_right
            self.direction = -1
        elif self.center_x <= self.boundary_left:
            self.center_x = self.boundary_left
            self.direction = 1

        self.scale_x = self.direction * 0.8


class AnimatedEasyEnemy(EasyEnemy):
    def __init__(self, textures: list, x: float, y: float):
        super().__init__(textures[0], x, y)
        self.textures = textures
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.5
        self.is_dying = False
        self.death_timer = 0
        self.death_duration = 0.3
        self._death_started = False

    def start_dying(self):
        """Начинает процесс смерти (подбрасывание вверх)."""
        self.is_dying = True
        self.death_timer = 0
        self.change_y = 200
        self.change_x = random.uniform(-100, 100)

    def update_animation(self, delta_time: float):
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.textures)
            self.texture = self.textures[self.current_frame]

    def update(self, delta_time: float):
        if self.is_dying:
            self.death_timer += delta_time
            # Мигание
            if int(self.death_timer * 20) % 2 == 0:
                self.alpha = 128
            else:
                self.alpha = 255

            # Подбрасывание вверх
            self.center_x += self.change_x * delta_time
            self.center_y += self.change_y * delta_time
            self.change_y -= 400 * delta_time  # гравитация

            if self.death_timer >= self.death_duration:
                self.kill()
            return

        super().update(delta_time)
        self.update_animation(delta_time)


class MediumEnemy(Enemy):
    """Враг средней сложности с рандомными остановками."""

    def __init__(self, image_path: str, x: float, y: float):
        super().__init__(
            image_path,
            scale=1.0,
            health=2,
            speed=80,
            damage=35,
        )
        self.center_x = x
        self.center_y = y
        self.boundary_left = x - 150
        self.boundary_right = x + 150
        self.direction = random.choice([-1, 1])

        # Для пауз
        self.paused = False
        self.pause_timer = 0

    def update(self, delta_time: float):
        # Если на паузе
        if self.paused:
            self.pause_timer -= delta_time
            if self.pause_timer <= 0:
                self.paused = False
                # Меняем направление после паузы
                self.direction = random.choice([-1, 1])
            return

        # Движение
        self.center_x += self.speed * self.direction * delta_time

        # Границы
        if self.center_x >= self.boundary_right:
            self.center_x = self.boundary_right
            self.direction = -1
        elif self.center_x <= self.boundary_left:
            self.center_x = self.boundary_left
            self.direction = 1

        # Рандомная остановка (0.5% шанс каждый кадр)
        if random.random() < 0.005:
            self.paused = True
            self.pause_timer = random.uniform(0.5, 2.0)  # от 0.5 до 2 секунд

        # Поворот спрайта в сторону движения
        self.scale_x = self.direction * 0.8


class AnimatedMediumEnemy(MediumEnemy):
    """Средний враг с анимацией (паук)."""

    def __init__(self, textures: list, x: float, y: float):
        super().__init__(textures[0], x, y)  # textures[0] - idle
        self.textures = textures
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15  # скорость смены кадров
        self.is_walking = False

    def update_animation(self, delta_time: float):
        """Обновляет анимацию в зависимости от движения."""
        # Определяем, идёт ли враг
        self.is_walking = not self.paused and abs(self.change_x) > 0

        if self.is_walking:
            # Анимация ходьбы (кадры 1 и 2)
            walk_textures = self.textures[1:]  # spider1, spider2
            if walk_textures:
                self.animation_timer += delta_time
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0
                    self.current_frame = (self.current_frame + 1) % len(
                        walk_textures
                    )
                    self.texture = walk_textures[self.current_frame]
        else:
            # Idle (кадр 0)
            self.texture = self.textures[0]
            self.current_frame = 0

        # Поворот спрайта в сторону движения
        if self.direction != 0:
            self.scale_x = self.direction * 0.8

    def update(self, delta_time: float):
        super().update(delta_time)
        self.update_animation(delta_time)


class HardEnemy(Enemy):
    """Враг высокой сложности (летучая мышь)."""

    def __init__(
        self,
        image_path: str,
        x: float,
        y: float,
        fly_moves: int = 10,
        rest_duration: float = 3.0,
        fly_height: float = 200,
    ):
        super().__init__(
            image_path,
            scale=1.0,
            health=3,
            speed=120,
            damage=50,
        )
        self.start_x = x
        self.start_y = y

        self.center_x = x
        self.center_y = y

        self.state = "hanging"
        self.hang_timer = 0
        self.hang_duration = 1.0

        # Для полёта
        self.boundary_left = x - 150
        self.boundary_right = x + 150
        self.direction = random.choice([-1, 1])
        self.fly_height = fly_height  # на сколько опускается от start_y

        # Счётчик движений
        self.move_counter = 0
        self.move_limit = fly_moves

        # Отдых
        self.rest_timer = 0
        self.rest_duration = rest_duration
        self.is_resting = False

    def start_diving(self):
        """Начинает пикирование вниз."""
        self.state = "diving"
        self.center_x = self.start_x
        self.center_y = self.start_y
        self.direction = random.choice([-1, 1])

    def start_flying(self):
        """Начинает горизонтальный полёт (патрульный режим)."""
        self.state = "flying"
        self.move_counter = 0

    def return_to_hang(self):
        """Возвращается в точку подвеса."""
        self.state = "returning"
        self.target_x = self.start_x
        self.target_y = self.start_y

    def update(self, delta_time: float):
        if self.state == "hanging":
            # Висим на потолке
            self.center_x = self.start_x
            self.center_y = self.start_y
            self.scale_x = self.direction * 0.8

            # Если режим отдыха
            if self.is_resting:
                self.rest_timer += delta_time
                if self.rest_timer >= self.rest_duration:
                    self.is_resting = False
                    self.rest_timer = 0
                    self.hang_timer = 0
                return

            # Обычное зависание перед полётом
            self.hang_timer += delta_time
            if self.hang_timer >= self.hang_duration:
                self.hang_timer = 0
                self.start_diving()

        elif self.state == "diving":
            # Пикирование под углом вниз
            self.center_x += self.speed * self.direction * delta_time
            self.center_y -= self.speed * delta_time * 0.7
            self.scale_x = self.direction * 0.8

            if self.center_y <= self.start_y - self.fly_height:
                self.center_y = self.start_y - self.fly_height
                self.start_flying()

        elif self.state == "flying":
            # Патрульный режим
            self.center_x += self.speed * self.direction * delta_time
            self.center_y = self.start_y - self.fly_height
            self.scale_x = self.direction * 0.8

            if self.center_x >= self.boundary_right:
                self.center_x = self.boundary_right
                self.direction = -1
                self.move_counter += 1
            elif self.center_x <= self.boundary_left:
                self.center_x = self.boundary_left
                self.direction = 1
                self.move_counter += 1

            if self.move_counter >= self.move_limit:
                self.return_to_hang()

        elif self.state == "returning":
            # Возвращаемся к месту подвеса
            dx = self.target_x - self.center_x
            dy = self.target_y - self.center_y
            distance = (dx**2 + dy**2) ** 0.5

            if distance < 10:
                self.center_x = self.target_x
                self.center_y = self.target_y
                self.state = "hanging"
                self.is_resting = True
                self.rest_timer = 0
            else:
                self.center_x += dx * 0.1
                self.center_y += dy * 0.1
                self.scale_x = self.direction * 0.8


class AnimatedHardEnemy(HardEnemy):
    """Тяжёлый враг с анимацией (летучая мышь)."""

    def __init__(
        self,
        textures: list,
        x: float,
        y: float,
        fly_moves: int = 10,
        rest_duration: float = 3.0,
        fly_height: float = 200,
    ):
        super().__init__(
            textures[0], x, y, fly_moves, rest_duration, fly_height
        )
        self.textures = textures  # [bat0, bat1, bat2]
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.is_flying = False  # флаг: летит или висит

    def update_animation(self, delta_time: float):
        """Обновляет анимацию в зависимости от состояния."""
        # Летит (diving, flying, returning) - кадры 1, 2
        # Висит (hanging) - кадр 0
        if self.state in ("diving", "flying", "returning"):
            walk_textures = self.textures[1:]  # bat1, bat2
            if walk_textures:
                self.animation_timer += delta_time
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0
                    self.current_frame = (self.current_frame + 1) % len(
                        walk_textures
                    )
                    self.texture = walk_textures[self.current_frame]
        else:  # hanging
            self.texture = self.textures[0]
            self.current_frame = 0

        # Поворот спрайта в сторону движения
        if self.direction != 0:
            self.scale_x = self.direction * 0.8

    def update(self, delta_time: float):
        super().update(delta_time)
        self.update_animation(delta_time)


class BaseItem(arcade.Sprite):
    """Базовый класс для внутриигровых предметов."""

    def __init__(self, path_or_texture, scale, gem_type, x, y):
        super().__init__(path_or_texture, scale)
        self.gem_type = gem_type
        self.name = gem_type
        self.center_x = x
        self.center_y = y

    def collect(self, inventory):
        inventory.add(self.gem_type, 1)
        self.remove_from_sprite_lists()
        return self.gem_type


class Emerald(BaseItem):
    """Изумруд."""

    def __init__(self, image_path: str, x, y):
        super().__init__(image_path, GEM_SCALE, "emerald", x, y)
        self.name = "Изумруд"


class Sapphire(BaseItem):
    """Сапфир."""

    def __init__(self, image_path: str, x, y):
        super().__init__(image_path, GEM_SCALE, "sapphire", x, y)
        self.name = "Сапфир"


class Ruby(BaseItem):
    """Рубин."""

    def __init__(self, image_path: str, x, y):
        super().__init__(image_path, GEM_SCALE, "ruby", x, y)
        self.name = "Рубин"


class Key(BaseItem):
    """Ключ."""

    def __init__(self, image_path: str, x, y):
        super().__init__(image_path, KEY_SCALE, "key", x, y)


class Coin(BaseItem):
    """Монета."""

    def __init__(self, image_path: str, x, y):
        super().__init__(image_path, COIN_SCALE, "coin", x, y)


class AnimatedCoin(Coin):
    """Монета с анимацией при сборе."""

    def __init__(self, textures: list, x: float, y: float):
        super().__init__(textures[0], x, y)
        self.textures = textures
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.05
        self.is_collecting = False

    def collect_with_animation(self, inventory):
        """Запускает анимацию после сбора монеты."""
        self.pending_inventory = inventory
        self.is_collecting = True
        self.animation_timer = 0
        self.current_frame = 0

    def update_animation(self, delta_time: float):
        """Обновляет анимацию монеты при сборе."""
        if not self.is_collecting:
            return

        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1

            if self.current_frame >= len(self.textures):
                self.collect(self.pending_inventory)
                return
            else:
                self.texture = self.textures[self.current_frame]


class DustParticle(arcade.SpriteCircle):
    """Частица пыли для эффекта приземления."""

    def __init__(self, x, y):
        color = random.choice(
            [
                (200, 200, 200, 200),
                (180, 180, 180, 200),
                (220, 220, 220, 200),
                (190, 170, 150, 200),
            ]
        )
        size = random.randint(3, 8)
        super().__init__(size, color)
        self.center_x = x
        self.center_y = y
        self.change_x = random.uniform(-1.5, 1.5)
        self.change_y = random.uniform(0, 2)
        self.alpha = 200
        self.lifetime = random.uniform(0.5, 1.2)
        self.time_alive = 0

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.change_x *= 0.95
        self.change_y *= 0.95
        self.alpha -= 2
        self.time_alive += delta_time

        if self.time_alive >= self.lifetime or self.alpha <= 0:
            self.remove_from_sprite_lists()


class ExplosionEffect(arcade.SpriteCircle):
    """Частица взрыва для эффекта смерти врага."""

    def __init__(self, x: float, y: float):
        color = random.choice(
            [
                (255, 80, 80),
                (80, 255, 80),
                (80, 80, 255),
                arcade.color.GOLD,
                arcade.color.ORANGE_RED,
            ]
        )
        radius = random.randint(3, 8)
        super().__init__(radius, color)
        self.center_x = x
        self.center_y = y
        self.change_x = random.uniform(-2.5, 2.5)
        self.change_y = random.uniform(-2.5, 2.5)
        self.lifetime = random.uniform(0.4, 0.8)
        self.time_alive = 0
        self.alpha = 255

    def update(self, delta_time: float):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.change_x *= 0.95
        self.change_y *= 0.95
        self.time_alive += delta_time
        self.alpha = int(255 * (1 - self.time_alive / self.lifetime))
        if self.time_alive >= self.lifetime:
            self.remove_from_sprite_lists()


class CagePiece(arcade.SpriteCircle):
    """Частица разрушения клетки."""

    def __init__(self, x: float, y: float, color):
        radius = random.randint(4, 10)
        super().__init__(radius, color)
        self.center_x = x
        self.center_y = y
        self.change_x = random.uniform(-2, 2)
        self.change_y = random.uniform(-2, 2)
        self.lifetime = random.uniform(0.5, 1.0)
        self.time_alive = 0
        self.alpha = 255

    def update(self, delta_time: float):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.change_x *= 0.95
        self.change_y *= 0.95
        self.time_alive += delta_time
        self.alpha = int(255 * (1 - self.time_alive / self.lifetime))
        if self.time_alive >= self.lifetime:
            self.remove_from_sprite_lists()


class TrailParticle(arcade.SpriteCircle):
    """Частица шлейфа (след силы) за игроком."""

    def __init__(self, x: float, y: float, color):
        radius = random.randint(3, 6)
        super().__init__(radius, color)
        self.center_x = x
        self.center_y = y
        self.change_x = random.uniform(-0.5, 0.5)
        self.change_y = random.uniform(-0.5, 0.5)
        self.lifetime = random.uniform(0.3, 0.6)
        self.time_alive = 0
        self.alpha = 180

    def update(self, delta_time: float):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.time_alive += delta_time
        if self.time_alive >= self.lifetime:
            self.remove_from_sprite_lists()

# ========== АРХИТЕКТУРА СУЩНОСТЕЙ ==========
# Модуль с классами сущностей, предметов, инвентаря игры Monster Chase (arcade)

# Иерархия классов Существ:
# Entity (базовый класс)
# ├── Player (игрок)
# |   └── AnimatedPlayer (игрок с анимацией)
# └── Enemy (враг)
#     ├── EasyEnemy
#     ├── MediumEnemy
#     └── HardEnemy

# Иерархия классов внутриигровых предметов:
# BaseItem (базовый класс)
# ├── Emerald (Изумруд)
# ├── Sapphire (Сапфир)
# ├── Ruby (Рубин)
# ├── Key (Ключ)
# └── Coin (Монета)
#
# Вспомогательные классы:
# Inventory (инвентарь игрока)
# DustParticle (для эффекта приземления)

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
            0.8,
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

    def update_animation(self, delta_time: float):
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.textures)
            self.texture = self.textures[self.current_frame]

    def update(self, delta_time: float):
        super().update(delta_time)
        self.update_animation(delta_time)


class MediumEnemy(Enemy):
    """Враг средней сложности."""

    def __init__(self, x: float, y: float):
        super().__init__(
            ":resources:images/enemies/slimeBlue.png",
            1.0,
            health=2,
            speed=80,
            damage=35,
        )
        self.center_x = x
        self.center_y = y


class HardEnemy(Enemy):
    """Враг высокой сложности."""

    def __init__(self, x: float, y: float):
        super().__init__(
            ":resources:images/enemies/slimePurple.png",
            1.2,
            health=3,
            speed=120,
            damage=50,
        )
        self.center_x = x
        self.center_y = y


class BaseItem(arcade.Sprite):
    """Базовый класс для внутриигровых предметов."""

    def __init__(self, path_or_texture, scale, gem_type, x, y):
        super().__init__(path_or_texture, scale)
        self.gem_type = gem_type
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


class Sapphire(BaseItem):
    """Сапфир."""

    def __init__(self, image_path: str, x, y):
        super().__init__(image_path, GEM_SCALE, "sapphire", x, y)


class Ruby(BaseItem):
    """Рубин."""

    def __init__(self, image_path: str, x, y):
        super().__init__(image_path, GEM_SCALE, "ruby", x, y)


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

# ========== АРХИТЕКТУРА СУЩНОСТЕЙ ==========
#
# Иерархия классов Существ:
# Entity (базовый класс)
# ├── Player (игрок)
# └── Enemy (враг)
#
# Вспомогательный класс для Player:
# Inventory (Инвентарь игрока)
#
# Иерархия классов внутриигровых предметов:
# BaseItem (базовый класс)
# ├── Emerald (Изумруд)
# ├── Sapphire (Сапфир)
# ├── Ruby (Рубин)
# └── Key (Ключ)

import arcade
import random
from abc import ABC, abstractmethod

from constants import *


class Inventory:
    """Инвентарь игрока"""

    def __init__(self):
        self.items = {}  # {"emerald": 1, "sapphire": 1, "ruby": 1, "coin": 15}

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
        """Возвращает общее количество драгоценных камней"""
        gem_types = ["emerald", "sapphire", "ruby"]
        return sum(self.get_count(g) for g in gem_types)


class Entity(arcade.Sprite, ABC):
    """Базовый класс для всех живых существ"""

    def __init__(self, path: str, scale: float, health: int, speed: float):
        super().__init__(path, scale)
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
    """Игрок с тремя жизнями-сердечками"""

    def __init__(self, x: float, y: float, scale=1.0, health=100, speed=5.0):
        super().__init__(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            scale,
            health,
            speed,
        )
        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.lives = 3
        self.inventory = Inventory()

    def update(self, delta_time: float):
        self.center_x += self.change_x * self.speed * delta_time
        self.center_y += self.change_y * self.speed * delta_time


class Enemy(Entity, ABC):
    """Базовый враг с ИИ движения"""

    def __init__(
        self, path: str, scale: float, health: int, speed: float, damage: int
    ):
        super().__init__(path, scale, health, speed)
        self.damage = damage
        self.change_x = random.choice([-1, 1]) * speed
        self.change_y = random.choice([-1, 1]) * speed

    def update(self, delta_time: float):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time


class EasyEnemy(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(
            ":resources:images/enemies/slimeGreen.png",
            0.8,
            health=1,
            speed=50,
            damage=10,
        )
        self.center_x = x
        self.center_y = y


class MediumEnemy(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(
            ":resources:images/enemies/slimeBlue.png",
            1.0,
            health=2,
            speed=80,
            damage=20,
        )
        self.center_x = x
        self.center_y = y


class HardEnemy(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(
            ":resources:images/enemies/slimePurple.png",
            1.2,
            health=3,
            speed=120,
            damage=30,
        )
        self.center_x = x
        self.center_y = y


class BaseItem(arcade.Sprite):
    def __init__(self, image_path, scale, gem_type, x, y):
        super().__init__(image_path, scale)
        self.gem_type = gem_type
        self.center_x = x
        self.center_y = y

    def collect(self, inventory):
        inventory.add(self.gem_type, 1)
        self.remove_from_sprite_lists()
        return self.gem_type


class Emerald(BaseItem):
    def __init__(self, x, y):
        super().__init__(EMERALD_IMAGE, GEM_SCALE, "emerald", x, y)


class Sapphire(BaseItem):
    def __init__(self, x, y):
        super().__init__(SAPPHIRE_IMAGE, GEM_SCALE, "sapphire", x, y)


class Ruby(BaseItem):
    def __init__(self, x, y):
        super().__init__(RUBY_IMAGE, GEM_SCALE, "ruby", x, y)


class Key(BaseItem):
    def __init__(self, x, y):
        super().__init__(KEY_IMAGE, KEY_SCALE, "key", x, y)

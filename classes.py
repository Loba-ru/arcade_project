# ========== АРХИТЕКТУРА СУЩНОСТЕЙ ==========
# Иерархия классов:
#
# Entity (базовый класс)
# ├── Player (игрок)
# └── Enemy (враг)

import arcade
from abc import ABC, abstractmethod
import random


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
        self.items = set()

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

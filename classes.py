# ========== АРХИТЕКТУРА СУЩНОСТЕЙ ==========
#
# Иерархия классов Существ:
# Entity (базовый класс)
# ├── Player (игрок)
# |   └── AnimatedPlayer (игрок с анимацией)
# └── Enemy (враг)
#
# Иерархия классов внутриигровых предметов:
# BaseItem (базовый класс)
# ├── Emerald (Изумруд)
# ├── Sapphire (Сапфир)
# ├── Ruby (Рубин)
# └── Key (Ключ)
#
# Вспомогательные классы:
# Inventory (инвентарь игрока)
# DustParticle (для эффекта приземления)


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


class AnimatedPlayer(Player):
    """Игрок с анимацией из атласа"""

    def __init__(self, x: float, y: float, scale=1.0, health=100, speed=5.0):
        super().__init__(x, y, scale, health, speed)

        # Анимация
        self.state = "idle"  # idle, walk, jump, fall, climb
        self.textures = {}  # словарь {"idle": [текстуры], ...}
        self.current_texture_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.12  # секунд на кадр
        self.last_direction = 1  # 1 = вправо, -1 = влево

        # Загружаем текстуры
        self.load_textures()

        # Движок
        self.physics_engine = None

    def load_textures(self):
        """Загружает текстуры из спрайтшита femaleAdventurer_sheet.png"""
        try:
            file_name = "resources/images/entities/femaleAdventurer_sheet.png"
            full_sheet = arcade.load_texture(file_name)

            data = {
                "idle": [(0, 0, 96, 128)],
                "walk": [(i * 96, 512, 96, 128) for i in range(8)],
                "jump": [(96, 0, 96, 128)],
                "fall": [(192, 0, 96, 128)],
                "climb": [(480, 0, 96, 128), (576, 0, 96, 128)],
            }

            self.textures = {}
            for state, regions in data.items():
                self.textures[state] = []
                for r in regions:
                    sub_tex = full_sheet.crop(r[0], r[1], r[2], r[3])
                    self.textures[state].append(sub_tex)

            if self.textures.get("idle"):
                self.texture = self.textures["idle"][0]

        except Exception as e:
            print(f"[WARNING] Не удалось загрузить текстуры: {e}")

    def update_state(self):
        """Определяет текущее состояние игрока по физике"""
        # Лестница — самый высокий приоритет
        if self.physics_engine and self.physics_engine.is_on_ladder():
            # Если на лестнице и не двигается вверх/вниз — стоим (idle)
            if abs(self.change_y) > 0:
                self.state = "climb"
            else:
                self.state = "idle"
            return

        # Падение или прыжок (по вертикальной скорости)
        if self.change_y > 0:
            self.state = "jump"
            return
        elif self.change_y < 0:
            self.state = "fall"
            return

        # Ходьба или покой
        if abs(self.change_x) > 0:
            self.state = "walk"
        else:
            self.state = "idle"

    def update_animation(self, delta_time):
        """Обновляет анимацию в зависимости от состояния"""
        # Обновляем состояние
        self.update_state()

        # Получаем список текстур для текущего состояния
        textures = self.textures.get(self.state, self.textures.get("idle", []))
        if not textures:
            return

        # Защита от выхода за границы списка
        if self.current_texture_index >= len(textures):
            self.current_texture_index = 0

        # Обновляем таймер
        self.animation_timer += delta_time

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_texture_index = (
                self.current_texture_index + 1
            ) % len(textures)

        # Устанавливаем текстуру
        base_texture = textures[self.current_texture_index]

        # Отражение по горизонтали (направление движения)
        if self.change_x > 0:
            self.last_direction = 1
            self.texture = base_texture
        elif self.change_x < 0:
            self.last_direction = -1
            self.texture = base_texture.flip_horizontally()
        else:
            # Стоим на месте — используем последнее направление
            if self.last_direction == -1:
                self.texture = base_texture.flip_horizontally()
            else:
                self.texture = base_texture


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


class DustParticle(arcade.SpriteCircle):
    """Частица пыли для эффекта приземления"""

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

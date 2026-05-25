# ========== СИСТЕМНЫЕ КОНСТАНТЫ И ПАРАМЕТРЫ ==========

# ========== БАЗОВЫЕ НАСТРОЙКИ ==========
# Основное разрешение (4:3)
SCREEN_WIDTH_4_3 = 1024
SCREEN_HEIGHT_4_3 = 768

# Альтернативные разрешения
SCREEN_WIDTH_16_9 = 1600
SCREEN_HEIGHT_16_9 = 900

SCREEN_WIDTH_16_10 = 1440
SCREEN_HEIGHT_16_10 = 900

SCREEN_WIDTH = SCREEN_WIDTH_4_3
SCREEN_HEIGHT = SCREEN_HEIGHT_4_3

SCREEN_TITLE = "Monster Chase"

# ========== КОНСТАНТЫ СЛОЖНОСТИ ==========
DIFFICULTY_EASY = 0
DIFFICULTY_MEDIUM = 1
DIFFICULTY_HARD = 2

# ========== ФИЗИКА ==========
GRAVITY = 0.8

# ========== ТАЙЛЫ ==========
TILE_SCALE = 1.0
TILE_SIZE = 128
GEM_SCALE = 1.0
KEY_SCALE = 1.0

# ========== КАРТА И ИГРОК ==========
MAP_WIDTH = 3840
MAP_HEIGHT = 1920
GROUND_HEIGHT = 128
LADDER_SPEED = 3

# ========== ТОЧКИ СПАВНА ==========
PLAYER_SPAWN_DEFAULT = (192, 128)
PLAYER_SPAWN_GROUND_A = (192, 128)
PLAYER_SPAWN_GROUND_B = (3648, 1408)
PLAYER_SPAWN_DUNGEON = (192, 1408)
PLAYER_SPAWN_SKY = (3648, 128)

EMERALD_SPAWN = (832, 1426)
SAPPHIRE_SPAWN = (1728, 1426)
RUBY_SPAWN = (3520, 1426)

KEY_SPAWN_GROUND = (250, 128)
KEY_SPAWN_DUNGEON = (250, 128)
KEY_SPAWN_SKY = (704, 788)

# ========== КОНСТАНТЫ ИГРОКА ==========
PLAYER_SCALE = 1
PLAYER_HEALTH = 100
PLAYER_LIVES = 3
PLAYER_JUMP_SPEED = 15
PLAYER_MOVEMENT_SPEED = 5

# ========== КАМЕРА ==========
CAMERA_LERP = 0.12
DEAD_ZONE_W = int(SCREEN_WIDTH * 0.35)
DEAD_ZONE_H = int(SCREEN_HEIGHT * 0.35)

# ========== GUI ==========
SCORE_TEXT_X = SCREEN_WIDTH - 100
SCORE_TEXT_Y = SCREEN_HEIGHT - 40
HEARTS_START_X = 30
HEARTS_START_Y = SCREEN_HEIGHT - 40
HEART_OFFSET = 40

# ========== РЕЖИМ ОТЛАДКИ ==========
# True = заглушка (быстрое тестирование переходов)
# False = настоящая игра (физика, игрок, камера)
GAMEPLAY_USE_DUMMY = False

# ========== ПУТИ К ФАЙЛАМ РЕСУРСОВ ==========
# Карты
MAP_PATH_GROUND = "resources/maps/ground_level.tmx"
MAP_PATH_DUNGEON = "resources/maps/dungeon_level.tmx"
MAP_PATH_SKY = "resources/maps/sky_level.tmx"

# Тайловый набор
TILESET_PATH = "resources/images/tiles/tiles_spritesheet.tsx"

# Изображения
PLAYER_IMAGE = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
# или если свой спрайт:
# PLAYER_IMAGE = "resources/images/entities/femaleAdventurer_sheet.png"

COIN_IMAGE = "resources/images/items/coin.png"
KEY_IMAGE = "resources/images/items/key.png"

EMERALD_IMAGE = "resources/images/items/stone_green.png"
SAPPHIRE_IMAGE = "resources/images/items/stone_blue.png"
RUBY_IMAGE = "resources/images/items/stone_red.png"

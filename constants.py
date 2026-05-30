# ========== СИСТЕМНЫЕ КОНСТАНТЫ И ПАРАМЕТРЫ ==========
# Модуль с константами игры Monster Chase (arcade)

# ========== БАЗОВЫЕ НАСТРОЙКИ ==========
SCREEN_WIDTH_4_3 = 1024
SCREEN_HEIGHT_4_3 = 768

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
LADDER_SPEED = 3
PLAYER_JUMP_SPEED = 15
PLAYER_MOVEMENT_SPEED = 5

# ========== ТАЙЛЫ И РЕСУРСЫ ==========
TILE_SCALE = 1.0
TILE_SIZE = 128
GEM_SCALE = 1.0
KEY_SCALE = 1.0
COIN_SCALE = 1.0

# ========== КАРТА ==========
MAP_WIDTH = 3840
MAP_HEIGHT = 1920
GROUND_HEIGHT = 128

# ========== ТОЧКИ СПАВНА ==========
PLAYER_SPAWN_DEFAULT = (192, 128)
PLAYER_SPAWN_GROUND_A = (192, 128)
PLAYER_SPAWN_GROUND_B = (3648, 1408)
PLAYER_SPAWN_DUNGEON = (192, 1408)
PLAYER_SPAWN_SKY = (3648, 128)

FRIEND_SPAWN_GROUND = (960, 192)

EMERALD_SPAWN = (832, 1433)
SAPPHIRE_SPAWN = (1728, 1433)
RUBY_SPAWN = (3520, 1433)

KEY_SPAWN_GROUND = (320, 1435)
KEY_SPAWN_DUNGEON = (3648, 155)
KEY_SPAWN_SKY = (1088, 155)

# ========== ИГРОК ==========
PLAYER_SCALE = 1
PLAYER_HEALTH = 100
PLAYER_LIVES_EASY = 5
PLAYER_LIVES_MEDIUM = 3
PLAYER_LIVES_HARD = 1
PLAYER_LIVES_DEFAULT = PLAYER_LIVES_MEDIUM

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

# ========== ФАЙЛЫ ==========
MAP_GROUND = "ground_level.tmx"
MAP_DUNGEON = "dungeon_level.tmx"
MAP_SKY = "sky_level.tmx"

BG_GROUND = "ground_bg.png"
BG_DUNGEON = "dungeon_bg.png"
BG_SKY = "sky_bg.png"

ENTITIES_DIR = "entities"
PLAYER_IMAGE = "player_idle.png"

FRIEND_IMAGE = "friend_idle.png"

ITEMS_DIR = "items"
KEY_IMAGE = "key.png"
EMERALD_IMAGE = "gem_green.png"
SAPPHIRE_IMAGE = "gem_blue.png"
RUBY_IMAGE = "gem_red.png"
COIN_IMAGE = "coin1.png"
COIN_FRAMES = ["coin1.png", "coin2.png", "coin3.png", "coin4.png"]

ENEMY_IMAGE = "slime_green0.png"

# ========== РЕЖИМ ОТЛАДКИ ==========
GAMEPLAY_USE_DUMMY = False

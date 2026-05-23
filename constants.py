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

# ========== КАРТА И ИГРОК ==========
MAP_WIDTH = 3000
MAP_HEIGHT = SCREEN_HEIGHT
GROUND_HEIGHT = 64
PLAYER_START_X = 100
PLAYER_START_Y = 100

# ========== КОНСТАНТЫ ИГРОКА ==========
PLAYER_SCALE = 1.0
PLAYER_HEALTH = 100
PLAYER_LIVES = 3
PLAYER_JUMP_SPEED = 15
PLAYER_MOVEMENT_SPEED = 5

# ========== ФИЗИКА ==========
GRAVITY = 0.8

# ========== ТАЙЛЫ ==========
TILE_SCALE = 0.5
TILE_SIZE = 64

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

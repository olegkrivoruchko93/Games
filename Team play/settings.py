from os.path import isfile
FPS = 70
PLAYER_VEL = 5
PLAYER_MAX_HEALT = 5

LEVELS = 9

BLOCK_SIZE = 96

WIDTH, HEIGHT = 1000, 800 # screan width and height
SCROLL_AREA_DIDTH, SCROLL_AREA_HEIGHT = 300, 300

CURRENT_LEVEL = 1

CURRENT_MAX_LEVEL = 1

if isfile('saving.txt'):
    with open('saving.txt', 'r') as f:
        CURRENT_MAX_LEVEL = int(f.readline())
else:
    with open('saving.txt', 'w') as f:
        f.write("1")

MainCharacters = ("MaskDude", "NinjaFrog", "VirtualGuy")
import pygame
import os
import random
import copy
import math

# CONSTANTS
SCREEN_HEIGHT = 780
SCREEN_WIDTH = 440
TILE_WIDTH = 50
TILE_HEIGHT = 50
ITEM_BAR_WIDTH = 430
ITEM_BAR_HEIGHT = 65
ITEM_GAP = (ITEM_BAR_WIDTH-(7*TILE_WIDTH))/8
############# CHANGE THIS #####################
MAX_NUM_OF_TYPES = 15
###############################################
# NUMBER_OF_ROWS = 21
# NUMBER_OF_COLUMNS = 15
MAP_BLANK_LEVEL = \
[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
# MAP_BLANK_LEVEL = [[0]*NUMBER_OF_COLUMNS]*NUMBER_OF_ROWS

# initialize pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(0.3)
clock = pygame.time.Clock()

# setup game screen
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # no per-pixel alpha channel
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  # provides alpha channel for all objects displayed

# caption + icon
pygame.display.set_caption('Sheep Sheep Game')
icon = pygame.image.load('resources/pics/sheep_icon.png')
pygame.display.set_icon(icon)

# loading screen
loading_img = pygame.image.load('resources/pics/loading.png').convert_alpha()
loading_img = pygame.transform.smoothscale(loading_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
window.blit(loading_img, (0,0))
pygame.display.update()

# variables
map = [] # tile map, first layer is top layer
stacks = [] # stacked tiles, left to right -> bottom to top, dir: 1-up, 2-down, 3-left, 4-right
map_undo_list = []
map_prev = []
map_redo_list = []
stacks_undo_list = []
stacks_redo_list = []
extra_collected_tiles = []
extra_collected_tiles_undo_list = []
collected_tiles = []
collected_tiles_undo_list = []
tile_types = list(range(1,MAX_NUM_OF_TYPES+1))  # no of types must be < number of tiles/3

# variables

# boundary rects on game screen for diff regions (X undo)
LEVEL_NAME_RECT = pygame.Rect((0, 0), (300, 32))
LEVEL_NAME_RECT.center = (SCREEN_WIDTH / 2, 65)
level_name_full_rect = pygame.Rect(0,0,0,0)
MAP_BOUNDARY_RECT = pygame.Rect(45, 85, 14*25, 20*25)
LEFT_TOP_BG_RECT = pygame.Rect(0, 0, 36, 97)
LEFT_TOP_BG_RECT.topleft = (4, MAP_BOUNDARY_RECT.top)
LEFT_BOTTOM_BG_RECT = pygame.Rect(0, 0, 80, 390)
LEFT_BOTTOM_BG_RECT.midtop = (0, LEFT_TOP_BG_RECT.bottom+13)
LAYER_IMG_RECT = pygame.Rect((3, 220),(35, 35))
LAYER_RECT_WIDTH = LAYER_IMG_RECT.width
LAYER_RECT_HEIGHT = LAYER_IMG_RECT.height
LEFT_BOTTOM_BOUNDARY_RECT = pygame.Rect(3, 220, LAYER_RECT_WIDTH, 600 - 220)
RIGHT_BG_RECT = pygame.Rect(0, 0, 80, MAP_BOUNDARY_RECT.height)
RIGHT_BG_RECT.midtop = (SCREEN_WIDTH, MAP_BOUNDARY_RECT.top)
RENAME_NEW_LEVEL_RECT = pygame.Rect((0, 0), (LEVEL_NAME_RECT.width, LEVEL_NAME_RECT.height))
RENAME_NEW_LEVEL_RECT.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
RENAME_NEW_LEVEL_BG_RECT = pygame.Rect((0, 0), (RENAME_NEW_LEVEL_RECT.width + 40, RENAME_NEW_LEVEL_RECT.height + 150))
RENAME_NEW_LEVEL_BG_RECT.midtop = (RENAME_NEW_LEVEL_RECT.centerx, RENAME_NEW_LEVEL_RECT.top - 20)
RENAME_LEVEL_BG_RECT = pygame.Rect((0,0),(LEVEL_NAME_RECT.width+120, LEVEL_NAME_RECT.height+3))
RENAME_LEVEL_BG_RECT.center = LEVEL_NAME_RECT.center
SETTINGS_RECT = pygame.Rect((0,0),(300,400))
SETTINGS_RECT.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
ITEMS_BAR_RECT = pygame.Rect((0,0),(ITEM_BAR_WIDTH,ITEM_BAR_HEIGHT))
ITEMS_BAR_RECT.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT -100)
EXTENDED_ITEMS_BAR_RECT = pygame.Rect((0,0),(TILE_WIDTH*3, TILE_HEIGHT))
EXTENDED_ITEMS_BAR_RECT.midbottom = (SCREEN_WIDTH/2, ITEMS_BAR_RECT.top-5)
PROGRESS_BAR_RECT = pygame.Rect((0,0),(300, 15))
PROGRESS_BAR_RECT.midtop = (SCREEN_WIDTH/2, 60)
PLAY_LEVEL_NAME_RECT = pygame.Rect((0,0), (170,35))
PLAY_LEVEL_NAME_RECT.center = (SCREEN_WIDTH/2, 25)
PAGE_NUMBER_RECT = pygame.Rect((0,0), (60,40))
PAGE_NUMBER_RECT.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT - 80)
TILE_COUNT_WARNING_RECT = pygame.Rect((0,0),(400,170))
TILE_COUNT_WARNING_RECT.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)


# fonts & font sizes
TITLE_FONT = 'resources/fonts/BaloonEverydayRegular-4B8El.ttf'
WORD_FONT = 'resources/fonts/2PeasDramaQueen-pgny.ttf'
NEW_LEVEL_RENAME_FONT_SIZE = 25
LEVEL_SELECT_NAME_FONT_SIZE = 22
# RENAME_FONT_SIZE = 25
LEVEL_NAME_FONT_SIZE = 22
HOVER_MSG_FONT_SIZE = 20
CURSOR_HEIGHT = 20
DIALOG_BOX_TITLE_FONT_SIZE = 50
DIALOG_BOX_CONTENT_FONT_SIZE = 30

# game stats (recalc in undo only)
number_of_tiles_map = 0
number_of_tiles_stacks = 0
number_of_tiles = 0
MAX_LAYERS = 10
number_of_layers = 0
current_layer = 0
MAX_LEVELS = 9
number_of_levels = int(len(os.listdir('resources/levels'))/2)  # read how many levels exists/have been created currently
current_level = number_of_levels-1
MAX_STACK_COUNT = 15
MIN_STACK_COUNT = 2
MAX_EXTENDED_COUNT = 3
MAX_COLLECTED_ITEM_COUNT = 7



cursor_img_no = random.choice(tile_types)
add = True
dock_pop_up = False  # got activate floating dock before
layer_dragging = False
layer_selected = 0
layer_disp_list = []
edit_tile = True
stack_row = 0
stack_col = 0
stack_x = 0
stack_y = 0
stack_setting = False
stack_dir = 0
stack_count = 0
valid = False
display_gridbox = True
tile_count_warning = False
tile_count_pos_ori = [25,25]
tile_count_pos = copy.deepcopy(tile_count_pos_ori)
tile_count_lower_bound = tile_count_pos_ori[0] - 5
tile_count_upper_bound = tile_count_pos_ori[0] + 5
tile_count_speed = 1.5
tile_count_dir = 0
tile_count_rounds = 0
tile_count_rounds_max = 5
# level_name_max_char = 16
rename = False
key_pressed = None
# level_names = []
# level_name = ''
toUpper = False
MAX_NAME_LENGTH = 10
rename_cursor_index = 0
rename_cursor_tick_max = 60
rename_cursor_tick = 0
level_select_page = 0
new_level_name = ''
settings = False
# music_on = False
music_on = True
preview = False
running_count = 0
# depth = 0
# target_depth = 0
game_state = ""  # main menu, play level select, play level, editor level select, level editor, preview level, level editor settings, play settings
target_game_state = ""
MAX_UNDO = 3
undo_used = False
extend_used = False
shuffle_used = False
progress = 0
progress_sheep_x = PROGRESS_BAR_RECT.left+1
progress_sheep_x_target = PROGRESS_BAR_RECT.left+1
HOVER_MSG_TICK_START = 60*1  # wait 2s for info box to appear
hover_msg_tick = HOVER_MSG_TICK_START
transition = 0

# LOADING IMAGES
bg_img = pygame.image.load('resources/pics/bg.png').convert()
bg_img = pygame.transform.smoothscale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
main_menu_img = pygame.image.load('resources/pics/transitions/main_menu.png')
main_menu_img_rect = main_menu_img.get_rect(topleft=(0,0))
sheep_bg_img = pygame.image.load('resources/pics/transitions/sheep_bg.png')
sheep_bg_img = pygame.transform.smoothscale(sheep_bg_img, (4928*0.3, 6791*0.3))
sheep_bg_img_rect = sheep_bg_img.get_rect(midleft=(SCREEN_WIDTH,SCREEN_HEIGHT/2))
level_tile_img = pygame.image.load('resources/pics/level_tile.png').convert_alpha()
level_tile_img = pygame.transform.smoothscale(level_tile_img, (140, 250))
level_images = []
for img_name in os.listdir('resources/pics/levels'):
    img = pygame.image.load(f'resources/pics/levels/{img_name}').convert_alpha()
    img = pygame.transform.smoothscale(img, (350*0.28, 500*0.28))
    level_images.append(img)
tile_images = []
for num in range(MAX_NUM_OF_TYPES+1):  # extra 1 for blank tile
    img = pygame.image.load(f'resources/pics/{num}.png').convert_alpha()
    tile_images.append(img)

############################## BUTTONS #########################################
# BUTTON NAMING CONVENTION CAN ONLY HAVE 1 _ WHICH IS BEFORE NUMBER
BUTTONS = {
    # main menu
    "play":{
        "size":(168*0.75,75*0.75),
        "pos": (SCREEN_WIDTH/2, SCREEN_HEIGHT/2+70),
        "img": 'menu-play'
    },
    "level-editor":{
        "size":(693*0.5,101*0.5),
        "pos": (SCREEN_WIDTH/2, SCREEN_HEIGHT/2+130),
        "img": 'menu-level-editor'
    },
    "quit-game":{
        "size":(186*0.7,82*0.7),
        "pos": (SCREEN_WIDTH/2, SCREEN_HEIGHT/2+190),
        "img": 'menu-quit'
    },
    # level editor level select
    "level-left":{
        "size":(40,40),
        "pos": (35, SCREEN_HEIGHT/2),
        "img": 'left1'
    },
    "level-right":{
        "size":(40,40),
        "pos": (SCREEN_WIDTH-35, SCREEN_HEIGHT/2),
        "img": 'play'
    },
    "new-level":{
        "size":(60,60),
        "pos": (SCREEN_WIDTH-40, SCREEN_HEIGHT-40),
        "img": 'new'
    },
    "rename-new-level-back":{
        "size":(732*0.2, 208*0.2),
        "pos": (RENAME_NEW_LEVEL_RECT.centerx, RENAME_NEW_LEVEL_RECT.bottom+40),
        "img": 'cancel'
    },
    "create-new-level":{
        "size":(1143*0.2, 207*0.2),
        "pos": (RENAME_NEW_LEVEL_RECT.centerx, RENAME_NEW_LEVEL_RECT.bottom+90),
        "img": 'create-level'
    },
    # level editor
    "add-layer":{
        "size":(27,27),
        "pos": (22, MAP_BOUNDARY_RECT.top+20),
        "img": 'plus1'
    },
    "delete-layer":{
        "size":(27,27),
        "pos": (22, MAP_BOUNDARY_RECT.top+78),
        "img": 'minus1'
    },
    "settings":{
        "size":(40,40),
        "pos": (SCREEN_WIDTH-25, 25),
        "img": 'settings'
    },
    "save":{
        "size":(40,40),
        "pos": (SCREEN_WIDTH-25-40, 25),
        "img": 'save'
    },
    "delete-level":{
        "size":(40,40),
        "pos": (SCREEN_WIDTH-25-80, 25),
        "img": 'delete'
    },
    "reset-level":{
        "size":(40,40),
        "pos": (SCREEN_WIDTH-25-120, 25),
        "img": 'reset-level'
    },
    "back":{
        "size":(35,35),
        "pos": (25, 25),
        "img": 'back'
    },
    "rename":{
        "size":(30,30),
        "pos": (LEVEL_NAME_RECT.right + 30, RENAME_LEVEL_BG_RECT.centery),
        "img": 'rename'
    },
    "rename-done":{
        "size":(30,30),
        "pos": (LEVEL_NAME_RECT.right + 30, RENAME_LEVEL_BG_RECT.centery),
        "img": 'tick'
    },
    "add-tiles":{
        "size":(30,30),
        "pos": ((RIGHT_BG_RECT.left + RIGHT_BG_RECT.centerx)//2, RIGHT_BG_RECT.top+30),
        "img": 'add-tiles'
    },
    "add-stacks":{
        "size":(30,30),
        "pos": ((RIGHT_BG_RECT.left + RIGHT_BG_RECT.centerx)//2, RIGHT_BG_RECT.top+70),
        "img": 'add-stacks'
    },
    "delete-tiles":{
        "size":(30,30),
        "pos": ((RIGHT_BG_RECT.left + RIGHT_BG_RECT.centerx)//2, RIGHT_BG_RECT.top+110),
        "img": 'delete-tiles-stacks'
    },
    "stack-left":{
        "size":(24, 24),
        "pos": (0,0),
        "img": 'left2'
    },
    "stack-right":{
        "size":(24, 24),
        "pos": (0,0),
        "img": 'right2'
    },
    "stack-up":{
        "size":(24, 24),
        "pos": (0,0),
        "img": 'up2'
    },
    "stack-down":{
        "size":(24, 24),
        "pos": (0,0),
        "img": 'down2'
    },
    "add-stack-tile":{
        "size":(22,22),
        "pos": (0,0),
        "img": 'plus2'
    },
    "delete-stack-tile":{
        "size":(22,22),
        "pos": (0,0),
        "img": 'minus2'
    },
    "confirm-stack":{
        "size":(24,24),
        "pos": (0,0),
        "img": 'tick'
    },
    # settings
    "resume":{
        "size":(751*0.2,207*0.2),
        "pos": (SETTINGS_RECT.centerx, SETTINGS_RECT.centery),
        "img": 'resume'
    },
    "give-up":{
        "size":(794*0.2,208*0.2),
        "pos": (SETTINGS_RECT.centerx, SETTINGS_RECT.centery + 45),
        "img": 'restart'
    },
    "settings-checkbox-1":{
        "size":(25,25),
        "pos": (SETTINGS_RECT.centerx-100, SETTINGS_RECT.centery + 40),
        "img": 'settings-checkbox'
    },
    "settings-checkbox-2":{
        "size":(25,25),
        "pos": (SETTINGS_RECT.centerx-50, SETTINGS_RECT.centery + 82),
        "img": 'settings-checkbox'
    },
    "back-to-level-select":{
        "size":(1328*0.2,208*0.2),
        "pos": (SETTINGS_RECT.centerx, SETTINGS_RECT.centery + 120),
        "img": 'back-to-level-select'
    },
    "back-to-main-menu":{
        "size":(1189*0.2,208*0.2),
        "pos": (SETTINGS_RECT.centerx, SETTINGS_RECT.centery + 165),
        "img": 'back-to-main-menu'
    },
    "preview-on":{
        "size":(1119*0.2,208*0.2),
        "pos": (SCREEN_WIDTH/2, MAP_BOUNDARY_RECT.bottom + 50),
        "img": 'preview-on'
    },
    "preview-off":{
        "size":(1152*0.2,208*0.2),
        "pos": (SCREEN_WIDTH/2, MAP_BOUNDARY_RECT.bottom + 50),
        "img": 'preview-off'
    },
    "test-play":{
        "size":(1023*0.2,207*0.2),
        "pos": (SCREEN_WIDTH/2, MAP_BOUNDARY_RECT.bottom + 100),
        "img": 'play-test'
    },
    # play level
    "extend-items-bar":{
        "size":(184*0.35,136*0.35),
        "pos": (SCREEN_WIDTH/4, SCREEN_HEIGHT - 30),
        "img": 'extend-items-bar'
    },
    "undo":{
        "size":(183*0.35,136*0.35),
        "pos": (SCREEN_WIDTH/2, SCREEN_HEIGHT - 30),
        "img": 'undo'
    },
    "shuffle":{
        "size":(184*0.35,136*0.35),
        "pos": (3*SCREEN_WIDTH/4, SCREEN_HEIGHT - 30),
        "img": 'shuffle'
    },
    # win/lose screen
    "end-retry":{
        "size":(190,50),
        "pos": (SCREEN_WIDTH/2, SCREEN_HEIGHT - 120),
        "img": 'retry'
    },
    "end-back-to-level-select":{
        "size":(320,50),
        "pos": (SCREEN_WIDTH/2, SCREEN_HEIGHT - 60),
        "img": 'back-to-level-select'
    },
    "end-back-to-editing":{
        "size":(250,50),
        "pos": (SCREEN_WIDTH/2, SCREEN_HEIGHT - 60),
        "img": 'back-to-editing'
    },
    "okay":{
        "size":(751*0.15,207*0.15),
        "pos": (TILE_COUNT_WARNING_RECT.centerx, TILE_COUNT_WARNING_RECT.bottom-30),
        "img": 'okay'
    },
}

# generating buttons for level select page
number_of_rows = 2
number_of_cols = 2
number_of_pages = math.ceil(number_of_levels/(number_of_rows*number_of_cols))
for row in range(number_of_rows):
    for col in range(number_of_cols):
        level_tile_centerx = (col + 1) * (SCREEN_WIDTH / (number_of_cols + 1))
        level_tile_centery = (row + 1) * (SCREEN_HEIGHT / (number_of_rows + 1))
        btn_num = row*number_of_cols + (col+1)
        # adding buttons for level editor - level select page
        BUTTONS[f'level-tile-{btn_num}-view'] = {
            "size":(40,40),
            "pos": (level_tile_centerx+25, level_tile_centery+95),
            "img": 'edit'
        }
        BUTTONS[f'level-tile-{btn_num}-delete'] = {
            "size": (40, 40),
            "pos": (level_tile_centerx - 25, level_tile_centery + 95),
            "img": 'delete'
        }

        # adding button for play - level select page
        BUTTONS[f'level-tile-{btn_num}-play'] = {
            "size": (468*0.15, 207*0.15),
            "pos": (level_tile_centerx, level_tile_centery + 95),
            "img": 'menu-play'
        }

########################### COLOUR ASSIGNMENT ####################################
COLOURS = {
    'BRIGHT PINK': '#D95585',
    'DARK PINK': '#972476',
    'SHADOW': '#5e69a0',
    'LIGHT PURPLE': '#8F56A3',
    'DARK PURPLE': '#4B2A75',
    'LIGHT BLUE': '#98E2F2',
    'CYAN': '#68F2F2',
    'BACKGROUND': '#9AAAD9'
}

bg_colour = COLOURS['BACKGROUND']
grid_line_colour = "#515A73"
items_bar_colour = "#d9b191"
left_sidebar_colour = "#5e69a0"
right_sidebar_colour = "#5e69a0"
add_layer_btn_colour = "#9AAAD9"
del_layer_btn_colour = "#9AAAD9"
rename_cursor_colour = '#9AAAD9'
settings_bg_colour = COLOURS['DARK PURPLE']

########################## KEY ASSIGNMENTS ##############################
KEY_MAP = {
    pygame.K_a: 'a',
    pygame.K_b: 'b',
    pygame.K_c: 'c',
    pygame.K_d: 'd',
    pygame.K_e: 'e',
    pygame.K_f: 'f',
    pygame.K_g: 'g',
    pygame.K_h: 'h',
    pygame.K_i: 'i',
    pygame.K_j: 'j',
    pygame.K_k: 'k',
    pygame.K_l: 'l',
    pygame.K_m: 'm',
    pygame.K_n: 'n',
    pygame.K_o: 'o',
    pygame.K_p: 'p',
    pygame.K_q: 'q',
    pygame.K_r: 'r',
    pygame.K_s: 's',
    pygame.K_t: 't',
    pygame.K_u: 'u',
    pygame.K_v: 'v',
    pygame.K_w: 'w',
    pygame.K_x: 'x',
    pygame.K_y: 'y',
    pygame.K_z: 'z',
    pygame.K_SPACE: ' ',
    pygame.K_0: '0',
    pygame.K_1: '1',
    pygame.K_2: '2',
    pygame.K_3: '3',
    pygame.K_4: '4',
    pygame.K_5: '5',
    pygame.K_6: '6',
    pygame.K_7: '7',
    pygame.K_8: '8',
    pygame.K_9: '9',
    pygame.K_MINUS: '-'
}
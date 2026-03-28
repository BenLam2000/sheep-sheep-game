import pygame, sys
import random
import math
import numpy as np
import copy
import os
from config import *

# ----------------------- CLASSES -------------------------------#
class Button:
    def __init__(self, screen, images:list, **pos):  # all images should be same size
        self.state = "idle"
        self.image_idle = images[0]
        self.image_hovering = images[1]
        self.image_pressed = images[2]
        self.image_unavailable = images[3]
        self.rect = self.image_idle.get_rect(**pos)
        self.screen = screen

    def run(self, mouse_pos, left_mouse_down, available=True):  # available is the condition that if not met, the button will not respond to anything
        run = False
        if self.state == "idle":
            if available:
                if self.rect.collidepoint(mouse_pos) and not left_mouse_down:
                    self.state = "hovering"
            else:
                self.state = "unavailable"

        elif self.state == "hovering":
            if not self.rect.collidepoint(mouse_pos):
                self.state = "idle"
            else:  # staying within button rect
                if left_mouse_down:
                    play_sound('click.wav')
                    run = True
                    self.state = "pressed"

        elif self.state == "pressed":
            if not left_mouse_down:
                self.state = "idle"

        elif self.state == "unavailable":
            if available:
                self.state = "idle"

        self.draw()

        return run

    def draw(self):
        if self.state == "idle":
            self.screen.blit(self.image_idle, self.rect)
        elif self.state == "hovering":
            self.screen.blit(self.image_hovering, self.rect)
        elif self.state == "pressed":
            self.screen.blit(self.image_pressed, self.rect)
        elif self.state == "unavailable":
            self.screen.blit(self.image_unavailable, self.rect)


class Tile:
    def __init__(self, x, y, num, id):
        self.x = x
        self.y = y
        self.num = num
        self.image = pygame.image.load('')
        self.id = id


#--------------------------- FUNCTIONS --------------------------------#
def play_music(music):
    pygame.mixer.music.load("resources/audio/music/" + music)  # mixer.music -> music that plays for quite long and streamed on the spot to save memory, suitable for background music
    pygame.mixer.music.play(-1,fade_ms=1000)  # -1 means loop endlessly

def stop_music():
    # pygame.mixer.music.stop()
    # pygame.mixer.music.pause()
    pygame.mixer.music.set_volume(0.0)

def resume_music():
    pygame.mixer.music.set_volume(0.3)

def play_sound(sound):
    if music_on:
        sound = pygame.mixer.Sound("resources/audio/sounds/" + sound) # mixer.Sound -> short one off game sounds that are loaded completely before playing
        pygame.mixer.Sound.play(sound)

# def stop_sound():
#     pygame.mixer.Sound.stop()


def display_text(screen, text, sysfont=False, font=None, font_size=100, text_colour=(255, 255, 255), alpha=255, return_rect_only=False, **kwargs):
    if sysfont:
        font = pygame.font.SysFont(font, font_size)
    else:
        font = pygame.font.Font(font, font_size)
    text_surf = font.render(text, True, text_colour)  # surface for placing text, 2nd arg is anti-aliasing
    text_surf.set_alpha(alpha)
    text_rect = text_surf.get_rect(**kwargs)
    # alpha_surface = pygame.Surface(text_rect.size)
    if return_rect_only:  # dont draw, just give rect
        return text_rect
    else:
        screen.blit(text_surf, text_rect)
        return text_rect


def adjust_img(img_name, folder='resources/pics', alpha=255, transform_type='rotozoom', angle=0.0, scale=1.0, size=(50,50)):
    img = pygame.image.load(f'{folder}/{img_name}').convert_alpha()
    if transform_type == 'rotozoom':
        img = pygame.transform.rotozoom(img, angle, scale)
    elif transform_type == 'scale':
        img = pygame.transform.smoothscale(img, size)
    img.set_alpha(alpha)

    return img


# params:
# alpha = 0-255
# transform_type = 'rotozoom'/'scale'
# HOW TO DEAL WITH BOTH SCALE AND ROTOZOOM?
def display_img(screen, img_name, folder='resources/pics', alpha=255, transform_type='rotozoom', angle=0.0, scale=1.0, size=(50,50), return_rect_only=False, **kwargs):
    img = adjust_img(img_name, folder, alpha, transform_type, angle, scale, size)
    rect = img.get_rect(**kwargs)
    if return_rect_only:
        return rect
    else:
        screen.blit(img, rect)
        return rect


# bring all exposed tiles from layers beneath after removing tile onto top layer to be considered visible
def update_top_layer(map):
    for layer in range(len(map)-1,0,-1):  # from bottom to 2nd layer
        for i in range(len(map[layer])):  # for each row
            for j in range(len(map[layer][i])):  # for each column
                if map[layer][i][j] > 0:  # only if grid point is a tile
                    visible = True
                    for layer_above in range(layer-1,-1,-1):  # for each layer above it till top
                        # check if 9 surrounding tiles on layer above got overlap with current tile
                        if map[layer_above][i - 1][j - 1] + map[layer_above][i - 1][j] + map[layer_above][i - 1][j + 1] \
                            + map[layer_above][i][j - 1] + map[layer_above][i][j] + map[layer_above][i][j + 1] + \
                                map[layer_above][i + 1][j - 1] + map[layer_above][i + 1][j] + map[layer_above][i + 1][j + 1] > 0:
                            visible = False
                            break  # no need to check for this tile anymore, move to next tile

                    # bring tile to top layer if no tiles above blocking
                    if visible:
                        map[0][i][j] = map[layer][i][j]  # bring bottom layer tile to top
                        map[layer][i][j] = 0  # empty prev tile

    return map


def save_level(level_names, number_of_tiles, tile_count_warning, tile_count_rounds, tile_count_dir, level, map, stacks):  # level can be a string/int
    # check for tile count if multiple of 3
    if number_of_tiles % 3 == 0:
        # save map
        with open(f"resources/levels/level{level}_map.txt", "w") as file:
            for layer in map:
                for row in layer:
                    cols = ' '.join([str(int(num)) for num in row])
                    file.write(cols + '\n')  # write 1 row into file
                file.write('\n')  # to distinguish between layers

        # save stacks
        with open(f"resources/levels/level{level}_stacks.txt", "w") as file:
            for stack in stacks:
                s = ' '.join([str(num) for num in stack])
                file.write(s + '\n')

        # save level names
        with open("resources/level_names.txt", 'w') as file:
            file.write('\n'.join(level_names))

        # save level pic happens in the preview_level()

    else:  # invalid tile count
        if not tile_count_warning:  # just started the warning
            tile_count_warning = True
            tile_count_rounds = 0
            tile_count_dir = 1
            play_sound('error.wav')

    return tile_count_warning, tile_count_rounds, tile_count_dir



def load_level(level):
    # if level < 10:
    #     level = f'0{level}'  # 01, 02, 03, 04, 05...
    # else:
    #     level = str(level)  # 10, 11, 12, 13..
    #map
    map = []
    with open(f'resources/levels/level{level}_map.txt', 'r') as file:
        lines = file.readlines()
        # print(lines)

    lines.pop()  # remove last '\n'
    layer_count = 0
    if lines:
        map.append([])  # first layer -> map = [[]]
        for line in lines:  # '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n' OR '\n'
            if line == '\n':
                layer_count += 1
                map.append([])  # map = [[[0,0...],...],[]]
            else:
                row = line.splitlines()  # ['0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0']
                row = row[0].split(' ')  # ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0']
                for index, num in enumerate(row):  # convert into integer
                    row[index] = int(float(num))
                map[layer_count].append(row)

    #stacks
    stacks = []
    # works for 2d and 1d array, 1 single number
    with open(f'resources/levels/level{level}_stacks.txt', 'r') as file:
        lines = file.readlines()

    if lines:  # if stacks is not empty list
        for line in lines:
            stack = line.splitlines()
            stack = stack[0].split(' ')
            for index, num in enumerate(stack):
                stack[index] = int(float(num))  # -> [1,4]
            stacks.append(stack)

    return map, stacks


def update_number_of_tiles(map, stacks, return_map_and_stacks=False):
    number_of_tiles_stacks = 0
    for stack in stacks:  # handle all possible scenarios: txt file empty(), 1 number, 1 stack, >1 stack (array)
        number_of_tiles_stacks += len(stack)
    number_of_tiles_map = 0
    for layer in map:
        for row in layer:
            number_of_tiles_map += sum([math.ceil(num / 1000) for num in row])
    number_of_tiles_map -= len(stacks)
    number_of_tiles = number_of_tiles_map + number_of_tiles_stacks

    if return_map_and_stacks:
        return number_of_tiles_map, number_of_tiles_stacks, number_of_tiles
    else:
        return number_of_tiles


def update_layer_disp_list(current_layer, number_of_layers):
    layer_disp_list = [1] * number_of_layers
    layer_disp_list[current_layer] = 2

    return layer_disp_list


def load_level_complete(level):
    # if current_level+1 < 10:
    #     level = f'0{current_level+1}'  # 01, 02, 03, 04, 05...
    # else:
    #     level = str(current_level+1)  # 10, 11, 12, 13..

    if os.path.exists(f'resources/levels/level{level+1}_map.txt'):
        # load map and stacks
        map, stacks = load_level(level+1)
        print(map)
        number_of_layers = len(map)
        if number_of_layers == 0:  # text file empty
            map = [copy.deepcopy(MAP_BLANK_LEVEL)]
            stacks = []
            number_of_layers = len(map)
        # first layer selected and displayed
        current_layer = 0
        layer_disp_list = update_layer_disp_list(current_layer, number_of_layers)
        # count number of existing tiles
        number_of_tiles = update_number_of_tiles(map, stacks)

        return map, stacks, number_of_tiles, number_of_layers, current_layer, layer_disp_list
    else:
        print("THIS FILE DOES NOT EXIST IN THE DIRECTORY!")


def add_level(number_of_levels):
    number_of_levels += 1
    current_level = number_of_levels-1 # add at end
    # add first layer
    map = [copy.deepcopy(MAP_BLANK_LEVEL)]  # get ready level 0
    stacks = []
    number_of_layers = 1
    current_layer = number_of_layers - 1
    # add layer on side bar
    layer_disp_list = update_layer_disp_list(current_layer, number_of_layers)
    # initialize number of tiles
    number_of_tiles = update_number_of_tiles(map, stacks)
    # save file and make sure its in right file name order first before doing anything else
    # save_level(f'{current_level + 1}_1', map, stacks)
    # rename_file_order(-1)

    return map, stacks, number_of_tiles, current_layer, number_of_layers, layer_disp_list, current_level, number_of_levels


# 3 PLACES TO ACCOUNT FOR: levels map and stacks txt, level pics, level names
def remove_level(current_level, number_of_levels, level_names):
    # reduce level count
    number_of_levels -= 1
    # remove map and stacks file from directory
    if os.path.exists(f'resources/levels/level{current_level + 1}_map.txt'):
        os.remove(f"resources/levels/level{current_level + 1}_map.txt")
        os.remove(f"resources/levels/level{current_level + 1}_stacks.txt")
    # remove name from level names list and update text file
    level_names.pop(current_level)
    with open("resources/level_names.txt", 'w') as file:
        file.write('\n'.join(level_names))
    # remove level pic from directory
    if os.path.exists(f'resources/pics/levels/level{current_level + 1}.png'):
        os.remove(f"resources/pics/levels/level{current_level + 1}.png")
        level_images.pop(current_level)  # remove from list of level images
    # renaming the files (12345 -del3-> 1245 -rename-> 1234)
    rename_file_order(1)

    return number_of_levels, level_names


# renaming the files (level pics + levels) in the reverse order from highest to lowest (12345 -del3-> 1245 -rename-> 1234)
def rename_file_order(dir):
    level_folder = 'resources/levels'
    if dir == 1:  # going forwards for after deleting levels
        level_num = 0
        for file_count, filename in enumerate(os.listdir(level_folder)):  # filecount-> 0->11
            f = os.path.join(level_folder, filename)
            # checking if it is a file
            if os.path.isfile(f):
                # switch level number every 2 files, coz got map and stacks
                if file_count % 2 == 0:  # even number
                    level_num += 1
                    # rename map
                    old_filename = f
                    new_filename = os.path.join(level_folder, f'level{level_num}_map.txt')
                    os.rename(old_filename, new_filename)  # rename from old -> new
                else:  # odd number
                    # rename stacks
                    old_filename = f
                    new_filename = os.path.join(level_folder, f'level{level_num}_stacks.txt')
                    os.rename(old_filename, new_filename)
    elif dir == -1:  # going backwards for after adding levels
        level_num = int(len(os.listdir(level_folder))/2) + 1  # 12/2 +1 = 6 + 1 = 7
        for file_count, filename in reversed(list(enumerate(os.listdir(level_folder)))):  # filecount-> 11->0
            f = os.path.join(level_folder, filename)
            # checking if it is a file
            if os.path.isfile(f):
                # switch level number every 2 files, coz got map and stacks
                if file_count % 2 == 0:  # even number
                    # rename map
                    old_filename = f
                    new_filename = os.path.join(level_folder, f'level{level_num}_map.txt')
                    os.rename(old_filename, new_filename)  # rename from old -> new
                else:  # odd number
                    # rename stacks
                    level_num -= 1
                    old_filename = f
                    new_filename = os.path.join(level_folder, f'level{level_num}_stacks.txt')
                    os.rename(old_filename, new_filename)

    level_pic_folder = 'resources/pics/levels'
    if dir == 1:  # going forwards for after deleting level pics
        level_num = 0
        for file_count, filename in enumerate(os.listdir(level_pic_folder)):  # filecount-> 0->11
            f = os.path.join(level_pic_folder, filename)
            # checking if it is a file
            if os.path.isfile(f):
                level_num += 1  # increase level num every step
                # rename map
                old_filename = f
                new_filename = os.path.join(level_pic_folder, f'level{level_num}.png')
                os.rename(old_filename, new_filename)  # rename from old -> new
    elif dir == -1:  # going backwards for after adding levels
        level_num = len(os.listdir(level_pic_folder)) + 1  # 12/2 +1 = 6 + 1 = 7
        for file_count, filename in reversed(list(enumerate(os.listdir(level_pic_folder)))):  # filecount-> 11->0
            f = os.path.join(level_pic_folder, filename)
            # checking if it is a file
            if os.path.isfile(f):
                # rename stacks
                level_num -= 1
                old_filename = f
                new_filename = os.path.join(level_pic_folder, f'level{level_num}.png')
                os.rename(old_filename, new_filename)


def restart_level(current_level, MAX_NUM_OF_TYPES):
    ############################ CHANGE THIS ###################################
    # tile map, first layer is top layer
    # stacked tiles, left to right -> bottom to top, dir: 1-up, 2-down, 3-left, 4-right
    map, stacks, _, _, _, _ = \
        load_level_complete(current_level)
    number_of_tiles_map, number_of_tiles_stacks, number_of_tiles = update_number_of_tiles(map, stacks,
                                                                                          return_map_and_stacks=True)
    ###########################################################################################

    # TILE MAP RANDOM PIC GENERATOR BASED ON INPUT
    ##################################### CHANGE THIS ###################################
    number_of_types = int(number_of_tiles / 3)
    if number_of_types > MAX_NUM_OF_TYPES:
        number_of_types = MAX_NUM_OF_TYPES
    tile_types = list(range(1, number_of_types + 1))  # list of pics to be used in map
    #######################################################################################
    if len(tile_types) < int(number_of_tiles / 3):  # number of tile pics not enough to fill all sets
        # 1. add sets to fit the max no of sets
        sets_to_add = int(number_of_tiles / 3) - len(tile_types)
        for i in range(sets_to_add):
            tile_types.append(random.choice(tile_types))
    # 2. duplicate the array to fit number of tiles
    tile_types = tile_types * 3
    # 3. shuffle the tile types 5 times
    for i in range(5):
        random.shuffle(tile_types)
    print(tile_types)

    counter = 0
    complete = False  # completed generating for map, not stacks
    # 4. fill up map
    for layer, _ in enumerate(map):
        for row, _ in enumerate(map[layer]):
            for col, _ in enumerate(map[layer][row]):
                if 0 < map[layer][row][col] < 100:  # can be any tile type assigned from editor
                    map[layer][row][col] = tile_types[counter]
                    counter += 1  # move to next tile type in list
                    if counter >= number_of_tiles_map:  # generated all tiles according to pattern
                        complete = True
                        break
            if complete:
                break
        if complete:
            break

    # 5. fill up stacks
    for stack, _ in enumerate(stacks):
        for tile, _ in enumerate(stacks[stack]):
            stacks[stack][tile] = tile_types[counter]
            counter += 1

    # 6. bring any exposed tiles from bottom layers of tile map that have been missed out to the top layer
    map = update_top_layer(map)
    # print(tile_map)

    # initialize variables
    collected_tiles = []  # [1,3,2,4,3,4,2]  type
    play_state = "playing"  # playing, game won, game lost
    left_mouse_down_pos = (0, 0)
    left_mouse_down = False
    tile_count_warning = False
    tile_count_dir = 0
    tile_count_rounds = 0
    settings = False
    undo_used = False
    extend_used = False
    shuffle_used = False
    map_undo_list, stacks_undo_list, collected_tiles_undo_list, extra_collected_tiles = [],[],[],[]
    progress = 0
    progress_sheep_x = PROGRESS_BAR_RECT.left + 1
    progress_sheep_x_target = PROGRESS_BAR_RECT.left + 1

    return map, stacks, number_of_tiles, collected_tiles, play_state, left_mouse_down_pos, left_mouse_down, tile_count_warning, \
            tile_count_dir, tile_count_dir, tile_count_rounds, settings, undo_used, map_undo_list, stacks_undo_list, \
            collected_tiles_undo_list, extra_collected_tiles, extend_used, shuffle_used, \
            progress, progress_sheep_x, progress_sheep_x_target, extra_collected_tiles_undo_list, map_prev


# checks that preview rect is not colliding with any other single tile or stack on its layer and within map boundary rcct
def check_collision(map, stacks, preview_rect, current_layer, ignore_ij=None):
    # check for edge outside MAP BOUNDARY RECT
    if preview_rect.top < MAP_BOUNDARY_RECT.top:
        return False
    if preview_rect.bottom > MAP_BOUNDARY_RECT.bottom:
        return False
    if preview_rect.left < MAP_BOUNDARY_RECT.left:
        return False
    if preview_rect.right > MAP_BOUNDARY_RECT.right:
        return False

    # check for collision with tile/stack
    for i in range(len(map[current_layer])):
        for j in range(len(map[current_layer][i])):
            if ignore_ij is not None:
                if i == ignore_ij[0] and j == ignore_ij[1]:
                    continue  # bypass checking for this tile/stack

            # check for single tile
            if 0 < map[current_layer][i][j] < 100:
                tile_rect = pygame.Rect(
                    (MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2), MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)), \
                    (TILE_WIDTH, TILE_HEIGHT))
                if tile_rect.colliderect(preview_rect):
                    return False
            # check for all stacks
            elif map[current_layer][i][j] > 100:
                dir = math.floor(
                    map[current_layer][i][j] % 100 / 10)  # dir: 1-up, 2-down, 3-left, 4-right
                stack_id = (map[current_layer][i][j] % 100) - dir * 10

                # generating rects of the whole stack
                if dir == 1:  # up
                    stack_rect = pygame.Rect(MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2),
                                             MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                                             - (len(stacks[stack_id]) - 1) * 6, TILE_WIDTH,
                                             (len(stacks[stack_id]) - 1) * 6 + TILE_HEIGHT)
                elif dir == 2:  # down
                    stack_rect = pygame.Rect(MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2),
                                             MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2), TILE_WIDTH,
                                             (len(stacks[stack_id]) - 1) * 6 + TILE_HEIGHT)

                elif dir == 3:  # left
                    stack_rect = pygame.Rect(
                        MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2) - (len(stacks[stack_id]) - 1) * 6,
                        MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2), TILE_WIDTH +
                        (len(stacks[stack_id]) - 1) * 6, TILE_HEIGHT)

                elif dir == 4:  # right
                    stack_rect = pygame.Rect(
                        MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2),
                        MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2), TILE_WIDTH +
                        (len(stacks[stack_id]) - 1) * 6, TILE_HEIGHT)


                if stack_rect.colliderect(preview_rect):
                    return False

    return True


# checks if point is colliding with any other single tile or stack on its layer
def check_point_collision(map, stacks, point, current_layer):
    for i in range(len(map[current_layer])):
        for j in range(len(map[current_layer][i])):
            # check for single tile
            if 0 < map[current_layer][i][j] < 100:
                tile_rect = pygame.Rect(
                    (MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2), MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)), \
                    (TILE_WIDTH, TILE_HEIGHT))
                if tile_rect.collidepoint(point):
                    return [i, j], tile_rect

            # check for all stacks
            elif map[current_layer][i][j] > 100:
                dir = math.floor(
                    map[current_layer][i][j] % 100 / 10)  # dir: 1-up, 2-down, 3-left, 4-right
                stack_id = (map[current_layer][i][j] % 100) - dir * 10

                # generating rects of the whole stack
                if dir == 1:  # up
                    stack_rect = pygame.Rect(MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2),
                                             MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                                             - (len(stacks[stack_id]) - 1) * 6, TILE_WIDTH,
                                             (len(stacks[stack_id]) - 1) * 6 + TILE_HEIGHT)
                elif dir == 2:  # down
                    stack_rect = pygame.Rect(MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2),
                                             MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2), TILE_WIDTH,
                                             (len(stacks[stack_id]) - 1) * 6 + TILE_HEIGHT)

                elif dir == 3:  # left
                    stack_rect = pygame.Rect(
                        MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2) - (len(stacks[stack_id]) - 1) * 6,
                        MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2), TILE_WIDTH +
                        (len(stacks[stack_id]) - 1) * 6, TILE_HEIGHT)

                elif dir == 4:  # right
                    stack_rect = pygame.Rect(
                        MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2),
                        MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2), TILE_WIDTH +
                        (len(stacks[stack_id]) - 1) * 6, TILE_HEIGHT)

                if stack_rect.collidepoint(point):
                    return [i, j], stack_rect

    return [-1,-1], None

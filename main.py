import pygame, sys
import random
import math
import numpy as np
import copy
import os
from modules import *  # my own py file for storing all classes, functions
from config import *
# from main import *


# read level names from file
with open("resources/level_names.txt",'r') as file:
    level_names = file.readlines()
    level_names = ''.join(level_names)
    level_names = level_names.split('\n')

# adding button instance for each button key
for btn_name in BUTTONS:
    images = []
    # appending images for diff button states
    img_name = BUTTONS[btn_name]['img']  # 'delete'
    for img_num in range(1, 4):  # 1-3
        if os.path.exists(f'resources/pics/buttons/{img_name}_{img_num}.png'):
            images.append(adjust_img(f'{img_name}_{img_num}.png', folder='resources/pics/buttons', transform_type="scale",
                                     size=BUTTONS[btn_name]["size"]))
        else:
            print(f'WARNING! Image "{img_name}_{img_num}.png" not found!')
    # add 50% transparent idle image as unavailable image (4th)
    images.append(adjust_img(f'{img_name}_1.png', folder='resources/pics/buttons', alpha=128, transform_type="scale",
                             size=BUTTONS[btn_name]["size"]))
    BUTTONS[btn_name]["button"] = Button(screen, images, center=BUTTONS[btn_name]["pos"])


def main_menu():
    global game_state, target_game_state, transition, music_on
    game_state = 'main menu'
    print(game_state)
    play_music('intro.mp3')

    while True:
        left_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # print(event.button)
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True

        # filling background colour every frame to refresh prev frame
        screen.blit(bg_img, (0,0))

        # display game title
        display_img(screen, 'title.png', transform_type='scale', size=(1145*0.3,763*0.3), center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2-100))

        if BUTTONS["play"]["button"].run(mouse_pos, left_mouse_down):
            transition = 1
            main_menu_img_rect.right = SCREEN_WIDTH
            play_level_select(0)
            game_state = 'main menu'
            print(game_state)

        if BUTTONS["level-editor"]["button"].run(mouse_pos, left_mouse_down):
            transition = 1
            main_menu_img_rect.right = SCREEN_WIDTH
            level_select_page = 0
            editor_level_select(level_select_page)
            game_state = 'main menu'
            print(game_state)

        if BUTTONS["quit-game"]["button"].run(mouse_pos, left_mouse_down):
            pygame.quit()
            sys.exit()

        # music on/off toggle
        if music_on:
            music_on_rect = display_img(screen, 'music_on.png', transform_type='scale', size=(30,30), return_rect_only=True, center=(30, SCREEN_HEIGHT-30))
            if music_on_rect.collidepoint(mouse_pos):
                display_img(screen, 'music_on.png', transform_type='scale', size=(35, 35),
                            center=(30, SCREEN_HEIGHT - 30))
                if left_mouse_down:
                    music_on = False
                    stop_music()
            else:
                display_img(screen, 'music_on.png', transform_type='scale', size=(30, 30), center=(30, SCREEN_HEIGHT - 30))
        else:
            music_off_rect = display_img(screen, 'music_off.png', transform_type='scale', size=(40,40), return_rect_only=True, center=(30, SCREEN_HEIGHT - 30))
            if music_off_rect.collidepoint(mouse_pos):
                display_img(screen, 'music_off.png', transform_type='scale', size=(45, 45),
                            center=(30, SCREEN_HEIGHT - 30))
                if left_mouse_down:
                    music_on = True
                    resume_music()
            else:
                display_img(screen, 'music_off.png', transform_type='scale', size=(40, 40), center=(30, SCREEN_HEIGHT - 30))

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()
        clock.tick(60)


def display_transition():
    # screenshot_surf = screen.subsurface(pygame.Rect((0,0), (SCREEN_WIDTH, SCREEN_HEIGHT)))
    # pygame.image.save(screenshot_surf, f'pics/transitions/main_menu.png')
    global transition

    if transition == 1:  # main menu pic slide left out of view
        # move left until right edge touches left edge of screen
        if main_menu_img_rect.right > 0:
            main_menu_img_rect.right -= 10
            screen.blit(main_menu_img, main_menu_img_rect)
        else:
            main_menu_img_rect.right = 0
            screen.blit(main_menu_img, main_menu_img_rect)
            # reset back to no transition
            transition = 0

    elif transition == 2:  # main menu pic slide right into view
        # move right until right edge touches right edge of screen
        if main_menu_img_rect.right < SCREEN_WIDTH:
            main_menu_img_rect.right += 10
            screen.blit(main_menu_img, main_menu_img_rect)
        else:
            main_menu_img_rect.right = SCREEN_WIDTH
            screen.blit(main_menu_img, main_menu_img_rect)

    elif transition == 3:  # sheep pic swipe left
        if sheep_bg_img_rect.right > 0:
            sheep_bg_img_rect.right -= 15
            screen.blit(sheep_bg_img, sheep_bg_img_rect)
        else:
            sheep_bg_img_rect.right = 0
            screen.blit(sheep_bg_img, sheep_bg_img_rect)
            transition = 0

    elif transition == 4:  # sheep pic swipe left
        if sheep_bg_img_rect.right > 0:
            sheep_bg_img_rect.right -= 15
            screen.blit(sheep_bg_img, sheep_bg_img_rect)
        else:
            sheep_bg_img_rect.right = 0
            screen.blit(sheep_bg_img, sheep_bg_img_rect)
            transition = 0

    else:
        pass



def play_level_select(level_select_page):
    global current_level, number_of_levels, game_state, target_game_state, transition, music_on
    game_state = 'play level select'
    print(game_state)
    left_mouse_down_pos = (0, 0)

    running = True  # use this method for all menus other than the outermost main menu, so that you can break the loop and exit
    while running:  # game loop
        left_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True

        # filling background colour every frame to refresh prev frame
        # screen.fill(bg_colour)
        screen.blit(bg_img, (0,0))

        # back button
        if BUTTONS["back"]["button"].run(mouse_pos, left_mouse_down):
            transition = 2
            main_menu_img_rect.right = 0
        if transition == 2 and main_menu_img_rect.right == SCREEN_WIDTH:
            # reset back to no transition
            transition = 0
            screen.blit(main_menu_img, main_menu_img_rect)
            target_game_state = ''  # back to main menu
            running = False
            break

        # SELECT LEVEL TITLE
        display_text(screen, "SELECT LEVEL", False, TITLE_FONT, 50, "white", center=(SCREEN_WIDTH / 2, 70))

        # displaying all level tiles with delete and edit button
        number_of_pages = math.ceil(number_of_levels / (number_of_rows * number_of_cols))
        for row in range(number_of_rows):
            for col in range(number_of_cols):
                level_num = level_select_page * (number_of_rows * number_of_cols) + row * number_of_cols + (col + 1)  # start from 1
                if level_num <= number_of_levels:
                    level_tile_centerx = (col + 1) * (SCREEN_WIDTH / (number_of_cols + 1))
                    level_tile_centery = (row + 1) * (SCREEN_HEIGHT / (number_of_rows + 1))
                    btn_num = row * number_of_cols + (col + 1)
                    # display level bg tile
                    # level_tile_rect = display_img(screen, "level_tile.png", transform_type="scale", size=(140, 250),
                    #                               center=(level_tile_centerx, level_tile_centery))
                    screen.blit(level_tile_img, (level_tile_centerx-level_tile_img.get_width()/2, level_tile_centery-level_tile_img.get_height()/2))

                    # display level name
                    font_size = LEVEL_SELECT_NAME_FONT_SIZE
                    name_rect = display_text(screen, f"{level_names[level_num - 1]}", False, TITLE_FONT, font_size, "white", return_rect_only=True,
                                             center=(level_tile_centerx, level_tile_centery-100))
                    # keep checking if level name fits inside box
                    # while name_rect.width > level_tile_rect.width-10:
                    while name_rect.width > level_tile_img.get_width() - 10:
                        font_size -= 1
                        name_rect = display_text(screen, f"{level_names[level_num - 1]}", False, TITLE_FONT,
                                                 font_size, "white", return_rect_only=True,
                                                 center=(level_tile_centerx, level_tile_centery - 100))
                    display_text(screen, f"{level_names[level_num - 1]}", False, TITLE_FONT, font_size, "white",
                                 center=(level_tile_centerx, level_tile_centery - 100))

                    # display level pic
                    # display_img(screen, f"level{level_num}.png", folder="pics/levels", transform_type="rotozoom", scale=0.28,
                    #             center=(level_tile_centerx, level_tile_centery-10))
                    screen.blit(level_images[level_num-1], (level_tile_centerx-level_images[level_num-1].get_width()/2, level_tile_centery-10-level_images[level_num-1].get_height()/2))

                    # play level button
                    if BUTTONS[f'level-tile-{btn_num}-play']["button"].run(mouse_pos, left_mouse_down):
                        # setting transition
                        transition = 3
                        sheep_bg_img_rect.left = SCREEN_WIDTH
                        current_level = level_num - 1

        if transition == 3 and sheep_bg_img_rect.centerx < SCREEN_WIDTH/2:  # center of image pass center of screen
            play_level(current_level, play_test=False)  # not for testing, for real
            game_state = 'play level select'
            print(game_state)
            if target_game_state != '':  # got absolute target state
                if game_state != target_game_state:  # reach destination
                    running = False
                    break

        # prev page button
        if BUTTONS["level-left"]["button"].run(mouse_pos, left_mouse_down, level_select_page > 0):
            level_select_page -= 1

        # next page button
        if BUTTONS["level-right"]["button"].run(mouse_pos, left_mouse_down, level_select_page < number_of_pages - 1):
            level_select_page += 1

        # display page number
        pygame.draw.rect(screen, COLOURS['SHADOW'], PAGE_NUMBER_RECT, border_radius=10)
        display_text(screen, f'{level_select_page+1}/{number_of_pages}', False, WORD_FONT, 30, 'white',
                     center=(PAGE_NUMBER_RECT.centerx, PAGE_NUMBER_RECT.centery-5))

        # music on/off toggle
        if music_on:
            music_on_rect = display_img(screen, 'music_on.png', transform_type='scale', size=(30, 30),
                                        return_rect_only=True, center=(30, SCREEN_HEIGHT - 30))
            if music_on_rect.collidepoint(mouse_pos):
                display_img(screen, 'music_on.png', transform_type='scale', size=(35, 35),
                            center=(30, SCREEN_HEIGHT - 30))
                if left_mouse_down:
                    music_on = False
                    stop_music()
            else:
                display_img(screen, 'music_on.png', transform_type='scale', size=(30, 30),
                            center=(30, SCREEN_HEIGHT - 30))
        else:
            music_off_rect = display_img(screen, 'music_off.png', transform_type='scale', size=(40, 40),
                                         return_rect_only=True, center=(30, SCREEN_HEIGHT - 30))
            if music_off_rect.collidepoint(mouse_pos):
                display_img(screen, 'music_off.png', transform_type='scale', size=(45, 45),
                            center=(30, SCREEN_HEIGHT - 30))
                if left_mouse_down:
                    music_on = True
                    resume_music()
            else:
                display_img(screen, 'music_off.png', transform_type='scale', size=(40, 40),
                            center=(30, SCREEN_HEIGHT - 30))

        display_transition()

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()  # update game display
        clock.tick(60)  # run game at 60 fps


# needs to diff between play test and
def play_level(current_level, play_test=True):
    global map, stacks, number_of_tiles, collected_tiles, play_state, left_mouse_down_pos, left_mouse_down, \
        tile_count_warning, tile_count_dir, tile_count_dir, tile_count_rounds, settings,\
        display_gridbox, music_on, level_select_page, game_state, target_game_state, number_of_levels, level_names, \
        map_undo_list, map_prev, stacks_undo_list, collected_tiles_undo_list, undo_used, extra_collected_tiles, extra_collected_tiles_undo_list, extend_used, shuffle_used, \
        progress, progress_sheep_x, progress_sheep_x_target

    # reset all variables to make sue nothing left over from prev game
    map, stacks, number_of_tiles, collected_tiles, play_state, left_mouse_down_pos, left_mouse_down, \
    tile_count_warning, tile_count_dir, tile_count_dir, tile_count_rounds, settings, undo_used, \
    map_undo_list, stacks_undo_list, collected_tiles_undo_list, extra_collected_tiles, extend_used, shuffle_used, \
    progress, progress_sheep_x, progress_sheep_x_target, extra_collected_tiles_undo_list, map_prev = \
        restart_level(current_level, MAX_NUM_OF_TYPES)

    play_music('in_game.mp3')

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
    last_move = ''  # click tile / click stack / click extra tile / 3x combo / shuffle / undo / extend
    clicked_tile = 0
    collected_tiles = []  # [1,3,2,4,3,4,2]  type
    play_state = "playing"  # playing, game won, game lost
    left_mouse_down_pos = (0, 0)
    left_mouse_down = False
    tile_count_warning = False
    tile_count_dir = 0
    tile_count_rounds = 0
    settings = False
    game_state = 'play level'
    print(game_state)
    NUMBER_OF_TILES_START = copy.deepcopy(number_of_tiles)  # for calculating game progress
    PROGRESS_SHEEP_INCREMENT = 2
    tiles_to_move = []
    tile_coords_old = []
    tile_coords = []  # progressively changes
    tile_coords_new = []
    SPEED = 12
    tile_velocities = []
    animation_types = []  #1-click tile;
    clicked_tile_dest = 0
    collected_tiles_stationary = []


    # game loop
    running = True
    while running:
        left_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()
        left_mouse_down_pos = (0, 0)
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if play_test:
                        play_settings(pause=True, play_test=True)
                    else:
                        play_settings(pause=True, play_test=False)
                    game_state = 'play level'
                    print(game_state)
                    if target_game_state != '':  # got absolute target state
                        if game_state != target_game_state:  # reach destination
                            running = False
                            break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down_pos = event.pos  # update mouse position
                    left_mouse_down = True

        # mouse testing functions
        # print(pygame.mouse.get_focused())
        # print(pygame.mouse.get_pos())
        # print(pygame.mouse.get_pressed()[0]) # left click

        # filling background colour every frame to refresh prev frame
        # screen.fill(bg_colour)
        screen.blit(bg_img, (0, 0))

        if play_test:  # only make this button visible in play test mode
            # back button
            if BUTTONS["back"]["button"].run(mouse_pos, left_mouse_down):
                target_game_state = 'level editor'  # continue editing
                running = False
                break

            # delete level button
            if BUTTONS["delete-level"]["button"].run(mouse_pos, left_mouse_down,
                                                     number_of_levels > 1 and not rename and not settings):  # at least 2 levels
                number_of_levels, level_names = remove_level(current_level, number_of_levels, level_names)
                # print(level_names)
                number_of_pages = math.ceil(number_of_levels / (number_of_rows * number_of_cols))
                if level_select_page > number_of_pages - 1:
                    level_select_page = number_of_pages - 1
                target_game_state = 'editor level select'
                play_music('intro.mp3')
                running = False
                break  # after removing avoid anything below

            # save button
            if BUTTONS["save"]["button"].run(mouse_pos, left_mouse_down, not rename and not settings):
                tile_count_warning, tile_count_rounds, tile_count_dir = save_level(level_names, number_of_tiles,
                                                                                   tile_count_warning,
                                                                                   tile_count_rounds,
                                                                                   tile_count_dir,
                                                                                   current_level + 1, map,
                                                                                   stacks)
                if not tile_count_warning:
                    # store main components of level editor in temp first before being altered in preview by update top layer()
                    temp_map = copy.deepcopy(map)
                    temp_stacks = copy.deepcopy(stacks)
                    temp_number_of_tiles = copy.deepcopy(number_of_tiles)

                    preview_level(ss_only=True)

                    # return back stored temp editor components into original place
                    map = copy.deepcopy(temp_map)
                    stacks = copy.deepcopy(temp_stacks)
                    number_of_tiles = copy.deepcopy(temp_number_of_tiles)

                    game_state = 'level editor'
                    print(game_state)
                    if target_game_state != '':  # got absolute target state
                        if game_state != target_game_state:  # reach destination
                            running = False
                            break

        # only if the progress bar has reached the end, can move onto win/lose screen
        if play_state == "playing" or progress_sheep_x < progress_sheep_x_target or (1 in animation_types and 1 in animation_states) and len(collected_tiles)<=7:
            # drawing level name
            # draw bg
            pygame.draw.rect(screen, COLOURS['DARK PURPLE'], PLAY_LEVEL_NAME_RECT, border_radius=15)
            # display level name
            font_size = LEVEL_NAME_FONT_SIZE
            name_rect = display_text(screen, f"{level_names[current_level]}", False, TITLE_FONT, font_size, "white",
                                     return_rect_only=True,
                                     center=(PLAY_LEVEL_NAME_RECT.centerx, PLAY_LEVEL_NAME_RECT.centery+3))
            # keep checking if level name fits inside box
            while name_rect.width > PLAY_LEVEL_NAME_RECT.width - 15:
                font_size -= 1
                name_rect = display_text(screen, f"{level_names[current_level]}", False, TITLE_FONT,
                                         font_size, "white", return_rect_only=True,
                                         center=(PLAY_LEVEL_NAME_RECT.centerx, PLAY_LEVEL_NAME_RECT.centery+3))
            display_text(screen, f"{level_names[current_level]}", False, TITLE_FONT, font_size, "white",
                         center=(PLAY_LEVEL_NAME_RECT.centerx, PLAY_LEVEL_NAME_RECT.centery+3))

            # updating and drawing progress bar
            if progress_sheep_x < progress_sheep_x_target:
                progress_sheep_x += PROGRESS_SHEEP_INCREMENT  # move progress bar slowly to right until next target
                if progress_sheep_x > progress_sheep_x_target:
                    progress_sheep_x = progress_sheep_x_target
            pygame.draw.line(screen, 'orange', (PROGRESS_BAR_RECT.left, PROGRESS_BAR_RECT.centery),
                             (progress_sheep_x, PROGRESS_BAR_RECT.centery), width=8)
            pygame.draw.rect(screen, 'white', PROGRESS_BAR_RECT, width=3, border_radius=10)
            display_img(screen, 'sheep1.png', transform_type='scale', size=(82*0.5,66*0.5), center=(progress_sheep_x,PROGRESS_BAR_RECT.centery))

            # drawing each remaining tile on the game screen
            for layer in range(len(map) - 1, -1, -1):  # from bottom to top
                for i in range(len(map[layer])):  # for each row
                    for j in range(len(map[layer][i])):  # for each column
                        if map[layer][i][j] > 0:  # only if grid point contains top left corner of tile
                            if map[layer][i][j] < 100:  # for ordinary layout tiles
                                tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2)
                                tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                                img = tile_images[map[layer][i][j]]
                                tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                                screen.blit(img, tile_rect)
                                # draw transluscent mask for tiles that are not visible
                                if layer > 0:
                                    dark_surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
                                    dark_surf.set_alpha(128)  # 50 % opacity
                                    dark_surf.fill('#2F1443')  # dark purple
                                    screen.blit(dark_surf, tile_rect)
                            else:  # stack
                                dir = int(str(map[layer][i][j])[1])  # dir: 1-up, 2-down, 3-left, 4-right
                                stack_id = int(str(map[layer][i][j])[2])

                                for k, stack_tile in enumerate(stacks[stack_id]):
                                    # get tile position
                                    if dir == 1:  # up
                                        tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2)
                                        tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2) - k * 6
                                    elif dir == 2:  # down
                                        tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2)
                                        tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2) + k * 6
                                    elif dir == 3:  # left
                                        tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2) - k * 6
                                        tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                                    elif dir == 4:  # right
                                        tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2) + k * 6
                                        tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                                    # draw transluscent mask for tiles that are not visible
                                    if k < len(stacks[stack_id]) - 1:  # below top layer
                                        img = tile_images[0]  # blank tile
                                        tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                                        screen.blit(img, tile_rect)
                                        dark_surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
                                        dark_surf.set_alpha(128)  # 50 % opacity
                                        dark_surf.fill('#2F1443')  # dark purple
                                        screen.blit(dark_surf, tile_rect)
                                    else:
                                        img = tile_images[stack_tile]
                                        tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                                        screen.blit(img, tile_rect)

                            # game mechanics
                            if layer == 0:  # only for top layer (visible tiles)
                                # remove tile from top if clicked on and move to collected tiles(items bar)
                                # only if on top layer and no clicked tile is currently moving
                                if tile_rect.collidepoint(left_mouse_down_pos) and 1 not in animation_types:
                                    play_sound('click.wav')
                                    # update undo lists before anything change
                                    # map_undo_list = [copy.deepcopy(map)]
                                    # stacks_undo_list = [copy.deepcopy(stacks)]
                                    # collected_tiles_undo_list = [copy.deepcopy(collected_tiles)]
                                    # print(collected_tiles_undo_list)

                                    if map[layer][i][j] < 100:  # for ordinary layout tiles
                                        clicked_tile = map[layer][i][j]
                                        if not undo_used:
                                            last_move = 'click tile'
                                            map_undo_list = [layer, i, j]  # layer, row, col
                                            map_prev = copy.deepcopy(map)  # map will change if click tile
                                    else:  # stack
                                        # append top most tile in stack only if stack is not empty
                                        if stacks[stack_id]:
                                            clicked_tile = stacks[stack_id][-1]
                                            if not undo_used:
                                                last_move = 'click stack'
                                                stacks_undo_list = [layer, i, j, dir, stack_id]
                                        else:
                                            break

                                    # setup animation for clicked tile -> collected items - TYPE 1
                                    # 1. add tile to tiles to move (used for diff animations, so cannot start from empty list here)
                                    tiles_to_move.append(copy.copy(clicked_tile))
                                    # 2. find index to place the clicked tile
                                    if collected_tiles.count(clicked_tile):  # only if this tile exists within items bar
                                        # index of last occurence of clicked tile
                                        clicked_tile_dest = max(index for index, tile in enumerate(collected_tiles) if tile == clicked_tile) + 1
                                    else:  # not found in items bar
                                        # last index
                                        clicked_tile_dest = len(collected_tiles)
                                    collected_tiles_undo_list = [clicked_tile_dest]
                                    # 3. get old and new coord of clicked tile
                                    tile_coords_old.append([tile_x_pos, tile_y_pos])
                                    tile_coords.append([tile_x_pos, tile_y_pos])
                                    new_pos_x = ITEMS_BAR_RECT.left + (
                                                ITEM_GAP + (clicked_tile_dest) * (TILE_WIDTH + ITEM_GAP))
                                    new_pos_y = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                                    tile_coords_new.append([new_pos_x, new_pos_y])
                                    # 4. calculate velocity of clicked tile
                                    num_of_velocities_old = len(copy.deepcopy(tile_velocities))
                                    vel_x = (tile_coords_new[num_of_velocities_old][0] - tile_coords_old[num_of_velocities_old][0])
                                    vel_y = (tile_coords_new[num_of_velocities_old][1] - tile_coords_old[num_of_velocities_old][1])
                                    # fixing velocity to SPEED but in same direction
                                    old_speed = math.sqrt(vel_x ** 2 + vel_y ** 2)
                                    new_vel_x = (vel_x / old_speed) * SPEED
                                    new_vel_y = (vel_y / old_speed) * SPEED
                                    tile_velocities.append([round(new_vel_x, 3), round(new_vel_y, 3)])
                                    # 5. add animation types
                                    animation_types += [1]
                                    # 6. add stationary collected tiles list
                                    collected_tiles_stationary.append(copy.deepcopy(collected_tiles[:clicked_tile_dest]))

                                    # setup animation for collected items to move to right - TYPE 2
                                    # 1. make list for new collected tiles and add clicked tile in
                                    new_collected_tiles = copy.deepcopy(collected_tiles)
                                    if map[layer][i][j] < 100:  # for ordinary layout tiles
                                        new_collected_tiles.insert(clicked_tile_dest, copy.copy(clicked_tile))
                                    else:  # stack
                                        # append top most tile in stack only if stack is not empty
                                        if stacks[stack_id]:
                                            new_collected_tiles.insert(clicked_tile_dest, copy.copy(clicked_tile))
                                        else:
                                            break
                                    # 2. append tiles that should be to the right of clicked tile into tiles to move (only if dest is in between)
                                    if clicked_tile_dest < len(collected_tiles):
                                        tiles_to_move = tiles_to_move + new_collected_tiles[clicked_tile_dest+1:]
                                    # 3. get old and new coords of tiles in items bar to push to the right
                                    # will only enter for loop if there are tiles to push to the right
                                    for index, _ in enumerate(new_collected_tiles[clicked_tile_dest+1:]):
                                        old_pos_x = ITEMS_BAR_RECT.left + ITEM_GAP + ((clicked_tile_dest) * (TILE_WIDTH + ITEM_GAP)) \
                                                    + (index * (TILE_WIDTH + ITEM_GAP))
                                        new_pos_x = old_pos_x + TILE_WIDTH + ITEM_GAP
                                        old_pos_y = new_pos_y = ITEMS_BAR_RECT.centery - TILE_HEIGHT/2
                                        tile_coords_old.append([old_pos_x, old_pos_y])
                                        tile_coords.append([old_pos_x, old_pos_y])
                                        tile_coords_new.append([new_pos_x, new_pos_y])
                                        # 4. add stationary collected tiles list
                                        collected_tiles_stationary.append(
                                            copy.deepcopy(collected_tiles[:clicked_tile_dest]))
                                    # 4. obtain velocities of collected items to move to right from old coords -> new coords
                                    num_of_velocities_old = len(copy.deepcopy(tile_velocities))
                                    num_of_tiles_added = len(new_collected_tiles[clicked_tile_dest+1:])
                                    for index in range(num_of_velocities_old, num_of_velocities_old+num_of_tiles_added):
                                        vel_x = (tile_coords_new[index][0] - tile_coords_old[index][0])
                                        vel_y = (tile_coords_new[index][1] - tile_coords_old[index][1])
                                        # fixing velocity to SPEED but in same direction
                                        old_speed = math.sqrt(vel_x**2 + vel_y**2)
                                        new_vel_x = (vel_x/old_speed)*SPEED
                                        new_vel_y = (vel_y/old_speed)*SPEED
                                        tile_velocities.append([round(new_vel_x, 3), round(new_vel_y, 3)])
                                    # 5. setup variables for starting animation
                                    animation_types += [2]*num_of_tiles_added
                                    # 6. update collected tiles using new collected tiles
                                    collected_tiles = copy.deepcopy(new_collected_tiles)


                                    # remove tiles from map and won't be displayed anymore
                                    if map[layer][i][j] < 100:  # for ordinary layout tiles
                                        map[0][i][j] = 0  # remove clicked tile from game screen
                                    else:  # stack
                                        stacks[stack_id].pop()  # remove clicked tile from top of stack
                                        # remove stack from stacks if run out
                                        # if len(stacks[stack_id]) == 0:
                                        #     stacks.pop(stack_id)

                                    # update number of tiles and check for win
                                    # number_of_tiles = update_number_of_tiles(map, stacks)

                                    # left_mouse_down_pos = (0,0)  # once a tile has been removed, reset pos of mouse to prevent detection of more than 1 tile clicked

            # bring all exposed tiles from layers beneath after removing tile onto top layer to be considered visible
            map = update_top_layer(map)

            # display extended items bar + checking for click extra tiles
            # pygame.draw.rect(screen, 'white', EXTENDED_ITEMS_BAR_RECT, width=2)
            if extend_used and 6 not in animation_types:
                for index, tile in enumerate(extra_collected_tiles):
                    if tile > 0:
                        img = tile_images[tile]
                        tile_x_pos = EXTENDED_ITEMS_BAR_RECT.left + index*TILE_WIDTH
                        tile_y_pos = EXTENDED_ITEMS_BAR_RECT.centery - TILE_HEIGHT/2
                        tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                        screen.blit(img, tile_rect)

                        if tile_rect.collidepoint(left_mouse_down_pos):
                            play_sound('click.wav')
                            # update undo lists before anything change
                            # map_undo_list = [copy.deepcopy(map)]
                            # stacks_undo_list = [copy.deepcopy(stacks)]
                            # collected_tiles_undo_list = [copy.deepcopy(collected_tiles)]
                            # print(collected_tiles_undo_list)

                            # add clicked tile into items bar and remove from extra bar
                            clicked_tile = tile

                            # set most recent move to track undo button availability
                            if not undo_used:
                                last_move = 'click extra tile'
                                extra_collected_tiles_undo_list = [index]

                            # setup animation for extra collected tiles -> collected items - TYPE 1
                            # 1. add tile to tiles to move (used for diff animations, so cannot start from empty list here)
                            tiles_to_move.append(copy.copy(clicked_tile))
                            # 2. find index to place the clicked tile
                            if collected_tiles.count(clicked_tile):  # only if this tile exists within items bar
                                # index of last occurence of clicked tile
                                clicked_tile_dest = max(
                                    i for i, tile in enumerate(collected_tiles) if tile == clicked_tile) + 1
                            else:  # not found in items bar
                                # last index
                                clicked_tile_dest = len(collected_tiles)
                            collected_tiles_undo_list = [clicked_tile_dest]
                            # 3. get old and new coord of clicked tile
                            tile_coords_old.append([tile_x_pos, tile_y_pos])
                            tile_coords.append([tile_x_pos, tile_y_pos])
                            new_pos_x = ITEMS_BAR_RECT.left + (
                                    ITEM_GAP + (clicked_tile_dest) * (TILE_WIDTH + ITEM_GAP))
                            new_pos_y = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                            tile_coords_new.append([new_pos_x, new_pos_y])
                            # 4. calculate velocity of clicked tile
                            num_of_velocities_old = len(copy.deepcopy(tile_velocities))
                            vel_x = (tile_coords_new[num_of_velocities_old][0] - tile_coords_old[num_of_velocities_old][0])
                            vel_y = (tile_coords_new[num_of_velocities_old][1] - tile_coords_old[num_of_velocities_old][1])
                            # fixing velocity to SPEED but in same direction
                            old_speed = math.sqrt(vel_x ** 2 + vel_y ** 2)
                            new_vel_x = (vel_x / old_speed) * SPEED
                            new_vel_y = (vel_y / old_speed) * SPEED
                            tile_velocities.append([round(new_vel_x, 3), round(new_vel_y, 3)])
                            # 5. add animation types
                            animation_types += [1]
                            # 6. add stationary collected tiles list
                            collected_tiles_stationary.append(copy.deepcopy(collected_tiles[:clicked_tile_dest]))

                            # setup animation for collected items to move to right - TYPE 2
                            # 1. make list for new collected tiles and add clicked tile in
                            new_collected_tiles = copy.deepcopy(collected_tiles)
                            new_collected_tiles.insert(clicked_tile_dest, copy.copy(clicked_tile))
                            # 2. append tiles that should be to the right of clicked tile into tiles to move (only if dest is in between)
                            if clicked_tile_dest < len(collected_tiles):
                                tiles_to_move = tiles_to_move + new_collected_tiles[clicked_tile_dest + 1:]
                            # 3. get old and new coords of tiles in items bar to push to the right
                            # will only enter for loop if there are tiles to push to the right
                            for i, _ in enumerate(new_collected_tiles[clicked_tile_dest + 1:]):
                                old_pos_x = ITEMS_BAR_RECT.left + ITEM_GAP + ((clicked_tile_dest) * (TILE_WIDTH + ITEM_GAP)) \
                                            + (i * (TILE_WIDTH + ITEM_GAP))
                                new_pos_x = old_pos_x + TILE_WIDTH + ITEM_GAP
                                old_pos_y = new_pos_y = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                                tile_coords_old.append([old_pos_x, old_pos_y])
                                tile_coords.append([old_pos_x, old_pos_y])
                                tile_coords_new.append([new_pos_x, new_pos_y])
                                # 4. add stationary collected tiles list
                                collected_tiles_stationary.append(
                                    copy.deepcopy(collected_tiles[:clicked_tile_dest]))
                            # 4. obtain velocities of collected items to move to right from old coords -> new coords
                            num_of_velocities_old = len(copy.deepcopy(tile_velocities))
                            num_of_tiles_added = len(new_collected_tiles[clicked_tile_dest + 1:])
                            for i in range(num_of_velocities_old, num_of_velocities_old + num_of_tiles_added):
                                vel_x = (tile_coords_new[i][0] - tile_coords_old[i][0])
                                vel_y = (tile_coords_new[i][1] - tile_coords_old[i][1])
                                # fixing velocity to SPEED but in same direction
                                old_speed = math.sqrt(vel_x ** 2 + vel_y ** 2)
                                new_vel_x = (vel_x / old_speed) * SPEED
                                new_vel_y = (vel_y / old_speed) * SPEED
                                tile_velocities.append([round(new_vel_x, 3), round(new_vel_y, 3)])
                            # 5. setup variables for starting animation
                            animation_types += [2] * num_of_tiles_added
                            # 6. update collected tiles using new collected tiles
                            collected_tiles = copy.deepcopy(new_collected_tiles)

                            # removing tile from extend items bar
                            extra_collected_tiles[index] = 0


            # ending game states
            if not tiles_to_move:
                # check if items bar explodes
                if len(collected_tiles) >= MAX_COLLECTED_ITEM_COUNT and collected_tiles.count(clicked_tile) < 3:
                    play_state = "game lost"
                # if got 3x combo in items bar, reduce the number of tiles left
                if not play_test:  # play for real
                    condition = collected_tiles.count(clicked_tile) >= 3
                else:  # play test only
                    condition = len(collected_tiles) >= 3  # as long as got 3 tiles in items bar
                if condition:
                    play_sound('3x_combo.wav')
                    number_of_tiles -= 3
                    if not undo_used:
                        last_move = '3x combo'

                    # setup animation for 3x combo tiles shrinking  - TYPE 3
                    # 1. append tiles that should shrink
                    tiles_to_move += copy.deepcopy(collected_tiles[clicked_tile_dest-2:clicked_tile_dest+1])
                    # 2. fill up old and new coords for fun
                    for index, _ in enumerate(collected_tiles[clicked_tile_dest-2:clicked_tile_dest+1]):
                        pos_x = ITEMS_BAR_RECT.left + ITEM_GAP + ((clicked_tile_dest-2) * (TILE_WIDTH + ITEM_GAP)) \
                                + (index * (TILE_WIDTH + ITEM_GAP)) + TILE_WIDTH/2
                        pos_y = ITEMS_BAR_RECT.centery
                        # note that these are CENTER POSITIONS, NOT TOPLEFT for the sake of centering small img
                        tile_coords_old.append([pos_x, pos_y])  # fixed pos of shrinking img
                        tile_coords.append([TILE_WIDTH, TILE_HEIGHT])  # changing dimensions of tile img
                        tile_coords_new.append([5, 5])  # final dimensions of shrunk image
                        # 3. add stationary collected tiles list
                        collected_tiles_stationary.append(
                            copy.deepcopy(collected_tiles[:clicked_tile_dest-2] + [0,0,0] + collected_tiles[clicked_tile_dest+1:]))
                    # 4. set all velocities to 0
                    num_of_tiles_added = len(collected_tiles[clicked_tile_dest-2:clicked_tile_dest+1])
                    for index in range(num_of_tiles_added):
                        tile_velocities.append([0, 0])
                    # 5. setup variables for starting animation
                    animation_types += [3] * num_of_tiles_added

                    # setup animation for collected items to move left - TYPE 5
                    # 1. make list for new collected tiles, override only at the end
                    if not play_test:  # play for real
                        new_collected_tiles = [tile for tile in collected_tiles if
                                               tile != clicked_tile]  # discard 3x combo tiles from items bar
                    else:
                        new_collected_tiles = []  # all first 3 tiles will guarantee disappear
                    # 2. append tiles that should move to the left
                    if clicked_tile_dest < len(collected_tiles)-1:
                        tiles_to_move = tiles_to_move + copy.deepcopy(collected_tiles[clicked_tile_dest+1:])
                    # 3. get old and new coords of tiles in items bar to push to the left
                    # will only enter for loop if there are tiles to push to the left
                    for index, _ in enumerate(collected_tiles[clicked_tile_dest+1:]):
                        old_pos_x = ITEMS_BAR_RECT.left + ITEM_GAP + ((clicked_tile_dest+1) * (TILE_WIDTH + ITEM_GAP)) \
                                    + (index * (TILE_WIDTH + ITEM_GAP))
                        new_pos_x = old_pos_x - 3*(TILE_WIDTH + ITEM_GAP)
                        old_pos_y = new_pos_y = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                        tile_coords_old.append([old_pos_x, old_pos_y])
                        tile_coords.append([old_pos_x, old_pos_y])
                        tile_coords_new.append([new_pos_x, new_pos_y])
                        # 4. add stationary collected tiles list
                        collected_tiles_stationary.append(copy.deepcopy(collected_tiles[:clicked_tile_dest-2]))
                    # 5. obtain velocities of collected items to move to right from old coords -> new coords
                    num_of_velocities_old = len(copy.deepcopy(tile_velocities))
                    num_of_tiles_added = len(collected_tiles[clicked_tile_dest + 1:])
                    for index in range(num_of_velocities_old, num_of_velocities_old + num_of_tiles_added):
                        vel_x = (tile_coords_new[index][0] - tile_coords_old[index][0])
                        vel_y = (tile_coords_new[index][1] - tile_coords_old[index][1])
                        # fixing velocity to SPEED but in same direction
                        old_speed = math.sqrt(vel_x ** 2 + vel_y ** 2)
                        new_vel_x = (vel_x / old_speed) * SPEED
                        new_vel_y = (vel_y / old_speed) * SPEED
                        tile_velocities.append([round(new_vel_x, 3), round(new_vel_y, 3)])
                    # 6. setup variables for starting animation
                    animation_types += [5] * num_of_tiles_added
                    # 7. update collected tiles using new collected tiles
                    collected_tiles = copy.deepcopy(new_collected_tiles)

                    # updating progress
                    progress = (NUMBER_OF_TILES_START - number_of_tiles) / NUMBER_OF_TILES_START  # ratio 0-1
                    progress_sheep_x_target = PROGRESS_BAR_RECT.left + round(progress * PROGRESS_BAR_RECT.width)
                    # check if game won
                    if number_of_tiles <= 0:  # no more tiles remaining
                        play_state = "game won"

            # display items bar background
            pygame.draw.rect(screen, '#c4917c', pygame.Rect(ITEMS_BAR_RECT.left, ITEMS_BAR_RECT.top+7, ITEM_BAR_WIDTH, ITEM_BAR_HEIGHT), border_radius=10)
            pygame.draw.rect(screen, items_bar_colour, ITEMS_BAR_RECT, border_radius=10)

            # displaying collected tiles in items bar
            if not tiles_to_move:
                for index, tile in enumerate(collected_tiles):  # tile = tile_type
                    img = tile_images[tile]
                    tile_x_pos = ITEMS_BAR_RECT.left + ITEM_GAP + index * (TILE_WIDTH + ITEM_GAP)
                    tile_y_pos = ITEMS_BAR_RECT.centery
                    tile_rect = img.get_rect(midleft=(tile_x_pos, tile_y_pos))
                    screen.blit(img, tile_rect)

            print(f"\ncollected_tiles: {collected_tiles}")
            print(f"clicked_tile: {clicked_tile}")
            print(f"tiles_to_move: {tiles_to_move}")
            print(f"tile coords: {tile_coords}")
            print(f"tile_velocities: {tile_velocities}")
            print(f"collected tiles stationary: {collected_tiles_stationary}")

            # animation of tiles
            collected_items_stationary_index = 10
            tile_index_to_rm = []
            tiles_to_move_old = copy.deepcopy(tiles_to_move)  # create a temp copy so that popping later doesn't affect the real version
            if tiles_to_move_old:
                for index, _ in enumerate(tiles_to_move_old):
                    if animation_types[index] == 2:  # collected items move to the right
                        # draw stationary collected items to the left of clicked tile dest
                        for i, tile in enumerate(collected_tiles_stationary[index]):
                            if tile > 0:
                                img = tile_images[tile]
                                tile_x_pos = ITEMS_BAR_RECT.left + ITEM_GAP + i * (TILE_WIDTH + ITEM_GAP)
                                tile_y_pos = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                                screen.blit(img, (tile_x_pos, tile_y_pos))

                        # check if tile center has reached to final dest x
                        tile_x_pos = tile_coords[index][0] + tile_velocities[index][0]
                        tile_y_pos = tile_coords[index][1] + tile_velocities[index][1]
                        if tile_x_pos < tile_coords_new[index][0]:
                            # draw animation frames of tiles
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]
                        else:  # reached end of animation
                            # force final tile position to be set final destination
                            tile_x_pos = tile_coords_new[index][0]
                            tile_y_pos = tile_coords_new[index][1]

                            # draw final animation frame
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]

                            if 1 not in animation_types:
                                # add index for variable to remove at the end
                                tile_index_to_rm.append(copy.copy(index))

                for index, _ in enumerate(tiles_to_move_old):
                    if animation_types[index] == 3:  # shrink 3x combo tiles
                        # draw stationary collected items to the left of clicked tile dest
                        for i, tile in enumerate(collected_tiles_stationary[index]):
                            if tile > 0:
                                img = tile_images[tile]
                                tile_x_pos = ITEMS_BAR_RECT.left + ITEM_GAP + i * (TILE_WIDTH + ITEM_GAP)
                                tile_y_pos = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                                screen.blit(img, (tile_x_pos, tile_y_pos))

                        # check if tile center has reached to final dest x
                        tile_width = tile_coords[index][0] - 5
                        tile_height = tile_coords[index][1] - 5
                        if tile_height > tile_coords_new[index][0]:
                            # draw animation frames of tiles
                            display_img(screen, f'{tiles_to_move[index]}.png', transform_type='scale',
                                        size=(tile_width, tile_height),
                                        center=(tile_coords_old[index][0], tile_coords_old[index][1]))

                            # update changing image size
                            tile_coords[index] = [tile_width, tile_height]
                        else:  # reached end of animation
                            # # force final tile position to be set final destination
                            # tile_x_pos = tile_coords_new[index][0]
                            # tile_y_pos = tile_coords_new[index][1]

                            # draw animation frames of tiles
                            display_img(screen, f'{tiles_to_move[index]}.png', transform_type='scale',
                                        size=(tile_width, tile_height),
                                        center=(tile_coords_old[index][0], tile_coords_old[index][1]))

                            # update changing image size
                            tile_coords[index] = [tile_width, tile_height]

                            # change state to shiny star
                            tile_coords[index] = 0  # sprite effect frame
                            animation_types[index] = 4

                for index, _ in enumerate(tiles_to_move_old):
                    if animation_types[index] == 5 and 3 not in animation_types:  # collected items move to the left
                        # draw stationary collected items to the left of clicked tile dest
                        for i, tile in enumerate(collected_tiles_stationary[index]):
                            if tile > 0:
                                img = tile_images[tile]
                                tile_x_pos = ITEMS_BAR_RECT.left + ITEM_GAP + i * (TILE_WIDTH + ITEM_GAP)
                                tile_y_pos = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                                screen.blit(img, (tile_x_pos, tile_y_pos))

                        # check if tile center has reached to final dest x
                        tile_x_pos = tile_coords[index][0] + tile_velocities[index][0]
                        tile_y_pos = tile_coords[index][1] + tile_velocities[index][1]
                        if tile_x_pos > tile_coords_new[index][0]:
                            # draw animation frames of tiles
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]
                        else:  # reached end of animation
                            # force final tile position to be set final destination
                            tile_x_pos = tile_coords_new[index][0]
                            tile_y_pos = tile_coords_new[index][1]

                            # draw final animation frame
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]

                            if 2 and 4 not in animation_types:
                                # add index for variable to remove at the end
                                tile_index_to_rm.append(copy.copy(index))

                for index, _ in enumerate(tiles_to_move_old):
                    if animation_types[index] == 8:  # collected items move to the left undo
                        # draw stationary collected items to the left of clicked tile dest
                        for i, tile in enumerate(collected_tiles_stationary[index]):
                            if tile > 0:
                                img = tile_images[tile]
                                tile_x_pos = ITEMS_BAR_RECT.left + ITEM_GAP + i * (TILE_WIDTH + ITEM_GAP)
                                tile_y_pos = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                                screen.blit(img, (tile_x_pos, tile_y_pos))

                        # check if tile center has reached to final dest x
                        tile_x_pos = tile_coords[index][0] + tile_velocities[index][0]
                        tile_y_pos = tile_coords[index][1] + tile_velocities[index][1]
                        if tile_x_pos > tile_coords_new[index][0]:
                            # draw animation frames of tiles
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]
                        else:  # reached end of animation
                            # force final tile position to be set final destination
                            tile_x_pos = tile_coords_new[index][0]
                            tile_y_pos = tile_coords_new[index][1]

                            # draw final animation frame
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]

                            if 7 not in animation_types:
                                # add index for variable to remove at the end
                                tile_index_to_rm.append(copy.copy(index))

                for index, _ in enumerate(tiles_to_move_old):
                    if animation_types[index] == 1:  # clicked tile -> items bar
                        # draw stationary collected items to the left of clicked tile dest
                        for i, tile in enumerate(collected_tiles_stationary[index]):
                            if tile > 0:
                                img = tile_images[tile]
                                tile_x_pos = ITEMS_BAR_RECT.left + ITEM_GAP + i * (TILE_WIDTH + ITEM_GAP)
                                tile_y_pos = ITEMS_BAR_RECT.centery - TILE_HEIGHT/2
                                screen.blit(img, (tile_x_pos, tile_y_pos))

                        # check if tile center has reached to item bar center height
                        print(f"index: {index}")
                        tile_x_pos = tile_coords[index][0] + tile_velocities[index][0]
                        tile_y_pos = tile_coords[index][1] + tile_velocities[index][1]
                        if tile_y_pos < tile_coords_new[index][1]:
                            # draw animation frames of tiles
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]
                        else:  # reached end of animation
                            # force final tile position to be set final destination
                            tile_x_pos = tile_coords_new[index][0]
                            tile_y_pos = tile_coords_new[index][1]

                            # draw final animation frame
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]

                            # add index for variable to remove at the end
                            tile_index_to_rm.append(copy.copy(index))

                for index, _ in enumerate(tiles_to_move_old):
                    if animation_types[index] == 6:  # items bar -> extended items bar
                        # draw stationary collected items to the left of clicked tile dest
                        for i, tile in enumerate(collected_tiles_stationary[index]):
                            if tile > 0:
                                img = tile_images[tile]
                                tile_x_pos = ITEMS_BAR_RECT.left + ITEM_GAP + i * (TILE_WIDTH + ITEM_GAP)
                                tile_y_pos = ITEMS_BAR_RECT.centery - TILE_HEIGHT/2
                                screen.blit(img, (tile_x_pos, tile_y_pos))

                        # check if tile center has reached to item bar center height
                        tile_x_pos = tile_coords[index][0] + tile_velocities[index][0]
                        tile_y_pos = tile_coords[index][1] + tile_velocities[index][1]
                        if tile_y_pos > tile_coords_new[index][1]:
                            # draw animation frames of tiles
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]
                        else:  # reached end of animation
                            # force final tile position to be set final destination
                            tile_x_pos = tile_coords_new[index][0]
                            tile_y_pos = tile_coords_new[index][1]

                            # draw final animation frame
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]

                            # add index for variable to remove at the end
                            tile_index_to_rm.append(copy.copy(index))

                for index, _ in enumerate(tiles_to_move_old):
                    if animation_types[index] == 7:  # UNDO items bar -> map/stacks/extra collected items
                        # draw stationary collected items to the left of clicked tile dest
                        for i, tile in enumerate(collected_tiles_stationary[index]):
                            if tile > 0:
                                img = tile_images[tile]
                                tile_x_pos = ITEMS_BAR_RECT.left + ITEM_GAP + i * (TILE_WIDTH + ITEM_GAP)
                                tile_y_pos = ITEMS_BAR_RECT.centery - TILE_HEIGHT/2
                                screen.blit(img, (tile_x_pos, tile_y_pos))

                        # check if tile center has reached to item bar center height
                        tile_x_pos = tile_coords[index][0] + tile_velocities[index][0]
                        tile_y_pos = tile_coords[index][1] + tile_velocities[index][1]
                        if tile_y_pos > tile_coords_new[index][1]:
                            # draw animation frames of tiles
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]
                        else:  # reached end of animation
                            # force final tile position to be set final destination
                            tile_x_pos = tile_coords_new[index][0]
                            tile_y_pos = tile_coords_new[index][1]

                            # draw final animation frame
                            img = tile_images[tiles_to_move[index]]
                            screen.blit(img, (tile_x_pos, tile_y_pos))

                            # update changing tile coordinates
                            tile_coords[index] = [tile_x_pos, tile_y_pos]

                            # restore map, stacks and collected tiles
                            if last_move == 'click tile':
                                map = copy.deepcopy(map_prev)
                            elif last_move == 'click stack':
                                stacks[stacks_undo_list[4]].append(
                                    copy.copy(collected_tiles[collected_tiles_undo_list[0]]))
                            elif last_move == 'click extra tile':
                                extra_collected_tiles[extra_collected_tiles_undo_list[0]] = \
                                    collected_tiles[collected_tiles_undo_list[0]]
                            collected_tiles.pop(collected_tiles_undo_list[0])

                            # add index for variable to remove at the end
                            tile_index_to_rm.append(copy.copy(index))

                for index, _ in enumerate(tiles_to_move_old):
                    if animation_types[index] == 4:  # shiny star
                        # draw stationary collected items to the left of clicked tile dest
                        for i, tile in enumerate(collected_tiles_stationary[index]):
                            if tile > 0:
                                img = tile_images[tile]
                                tile_x_pos = ITEMS_BAR_RECT.left + ITEM_GAP + i * (TILE_WIDTH + ITEM_GAP)
                                tile_y_pos = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                                screen.blit(img, (tile_x_pos, tile_y_pos))
                            else:
                                break

                        # check if tile center has reached to final dest x
                        if tile_coords[index] < 4*7 -1:
                            # draw animation frames of tiles
                            frame_num = math.floor(tile_coords[index]/7)
                            display_img(screen, f'{frame_num}.png', folder='resources/pics/effects/vanish',
                                        transform_type='scale', size=(TILE_WIDTH, TILE_HEIGHT),
                                        center=(tile_coords_old[index][0], tile_coords_old[index][1]))

                            # increase sprite effect frame
                            tile_coords[index] += 1
                        else:  # reached end of animation
                            # add index for variable to remove at the end
                            tile_index_to_rm.append(copy.copy(index))


                if tile_index_to_rm:
                    # remove variables from tiles that are done
                    tiles_to_move = [tile for index, tile in enumerate(tiles_to_move_old) if index not in tile_index_to_rm]
                    tile_coords_old = [copy.deepcopy(old_coord) for index, old_coord in enumerate(tile_coords_old) if index not in tile_index_to_rm]
                    tile_coords = [copy.deepcopy(coord) for index, coord in enumerate(tile_coords) if index not in tile_index_to_rm]
                    tile_coords_new = [copy.deepcopy(new_coord) for index, new_coord in enumerate(tile_coords_new) if index not in tile_index_to_rm]
                    tile_velocities = [copy.deepcopy(vel) for index, vel in enumerate(tile_velocities) if index not in tile_index_to_rm]
                    # tile_click_tick = [tick for index, tick in enumerate(tile_click_tick) if index not in tile_index_to_rm]
                    # animation_states = [state for index, state in enumerate(animation_states) if index not in tile_index_to_rm]
                    animation_types = [_type for index, _type in enumerate(animation_types) if index not in tile_index_to_rm]
                    collected_tiles_stationary = [copy.deepcopy(tiles) for index, tiles in enumerate(collected_tiles_stationary) if index not in tile_index_to_rm]



            # extend items bar button
            if BUTTONS["extend-items-bar"]["button"].run(mouse_pos, left_mouse_down, not extend_used and len(collected_tiles) >= 3):
                extend_used = True
                if not undo_used:
                    last_move = 'extend'

                # setup animation for collected items -> extra collected items - TYPE 6
                # 1. add first 3 tiles from collected items into extra collected tiles
                extra_collected_tiles = copy.deepcopy(collected_tiles[:3])
                # 2. append tiles to move
                tiles_to_move += extra_collected_tiles
                # 3. get old and new coords of tiles
                for i, _ in enumerate(extra_collected_tiles):
                    old_pos_x = ITEMS_BAR_RECT.left + ITEM_GAP + (i * (TILE_WIDTH + ITEM_GAP))
                    old_pos_y = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                    new_pos_x = EXTENDED_ITEMS_BAR_RECT.left + i * TILE_WIDTH
                    new_pos_y = EXTENDED_ITEMS_BAR_RECT.centery - TILE_HEIGHT/2
                    tile_coords_old.append([old_pos_x, old_pos_y])
                    tile_coords.append([old_pos_x, old_pos_y])
                    tile_coords_new.append([new_pos_x, new_pos_y])
                    # 4. add stationary collected tiles list
                    collected_tiles_stationary.append([])
                # 4. obtain velocities of collected items to move to right from old coords -> new coords
                num_of_velocities_old = len(copy.deepcopy(tile_velocities))
                num_of_tiles_added = 3
                for i in range(num_of_velocities_old, num_of_velocities_old + num_of_tiles_added):
                    vel_x = (tile_coords_new[i][0] - tile_coords_old[i][0])
                    vel_y = (tile_coords_new[i][1] - tile_coords_old[i][1])
                    # fixing velocity to SPEED but in same direction
                    old_speed = math.sqrt(vel_x ** 2 + vel_y ** 2)
                    new_vel_x = (vel_x / old_speed) * SPEED
                    new_vel_y = (vel_y / old_speed) * SPEED
                    tile_velocities.append([round(new_vel_x, 3), round(new_vel_y, 3)])
                # 5. setup variables for starting animation
                animation_types += [6] * num_of_tiles_added


                # setup animation for collected items to move left - TYPE 5
                # 1. make list for new collected tiles (remove first 3 elements), override only at the end
                new_collected_tiles = copy.deepcopy(collected_tiles[3:])  # discard 3x combo tiles from items bar
                # 2. append tiles that should move to the left
                if new_collected_tiles:
                    tiles_to_move += new_collected_tiles
                # 3. get old and new coords of tiles in items bar to push to the left
                # will only enter for loop if there are tiles to push to the left
                for index, _ in enumerate(collected_tiles[3:]):
                    old_pos_x = ITEMS_BAR_RECT.left + ITEM_GAP + (3 * (TILE_WIDTH + ITEM_GAP)) \
                                + (index * (TILE_WIDTH + ITEM_GAP))
                    new_pos_x = old_pos_x - 3 * (TILE_WIDTH + ITEM_GAP)
                    old_pos_y = new_pos_y = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                    tile_coords_old.append([old_pos_x, old_pos_y])
                    tile_coords.append([old_pos_x, old_pos_y])
                    tile_coords_new.append([new_pos_x, new_pos_y])
                    # 4. add stationary collected tiles list (nothing to the left)
                    collected_tiles_stationary.append([])
                # 5. obtain velocities of collected items to move to right from old coords -> new coords
                num_of_velocities_old = len(copy.deepcopy(tile_velocities))
                num_of_tiles_added = len(collected_tiles[3:])
                for index in range(num_of_velocities_old, num_of_velocities_old + num_of_tiles_added):
                    vel_x = (tile_coords_new[index][0] - tile_coords_old[index][0])
                    vel_y = (tile_coords_new[index][1] - tile_coords_old[index][1])
                    # fixing velocity to SPEED but in same direction
                    old_speed = math.sqrt(vel_x ** 2 + vel_y ** 2)
                    new_vel_x = (vel_x / old_speed) * SPEED
                    new_vel_y = (vel_y / old_speed) * SPEED
                    tile_velocities.append([round(new_vel_x, 3), round(new_vel_y, 3)])
                # 6. setup variables for starting animation
                animation_types += [5] * num_of_tiles_added
                # 7. update collected tiles using new collected tiles
                collected_tiles = copy.deepcopy(new_collected_tiles)

            # undo button
            if BUTTONS["undo"]["button"].run(mouse_pos, left_mouse_down, not undo_used and
                                                                         (last_move=='click tile' or last_move=='click stack' or last_move=='click extra tile')):
                undo_used = True

                # setup animation for collected items -> map - TYPE 7
                # 1. append tiles to move
                tiles_to_move.append(copy.copy(collected_tiles[collected_tiles_undo_list[0]]))
                # 2. get old and new coords of tiles
                # ONLY MOVE 1 TILE
                old_pos_x = ITEMS_BAR_RECT.left + ITEM_GAP + (collected_tiles_undo_list[0] * (TILE_WIDTH + ITEM_GAP))
                old_pos_y = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                if last_move == 'click tile':
                    new_pos_x = MAP_BOUNDARY_RECT.left + map_undo_list[2] * (TILE_WIDTH/2)
                    new_pos_y = MAP_BOUNDARY_RECT.top + map_undo_list[1] * (TILE_HEIGHT/2)
                elif last_move == 'click stack':
                    dir = stacks_undo_list[3]
                    stack_id = stacks_undo_list[4]
                    if dir == 1:  # up
                        new_pos_x = MAP_BOUNDARY_RECT.left + stacks_undo_list[2] * (TILE_WIDTH / 2)
                        new_pos_y = MAP_BOUNDARY_RECT.top + stacks_undo_list[1] * (TILE_HEIGHT / 2) - len(stacks[stack_id]) * 6
                    elif dir == 2:  # down
                        new_pos_x = MAP_BOUNDARY_RECT.left + stacks_undo_list[2] * (TILE_WIDTH / 2)
                        new_pos_y = MAP_BOUNDARY_RECT.top + stacks_undo_list[1] * (TILE_HEIGHT / 2) + len(stacks[stack_id]) * 6
                    elif dir == 3:  # left
                        new_pos_x = MAP_BOUNDARY_RECT.left + stacks_undo_list[2] * (TILE_WIDTH / 2) - len(stacks[stack_id]) * 6
                        new_pos_y = MAP_BOUNDARY_RECT.top + stacks_undo_list[1] * (TILE_HEIGHT / 2)
                    elif dir == 4:  # right
                        new_pos_x = MAP_BOUNDARY_RECT.left + stacks_undo_list[2] * (TILE_WIDTH / 2) + len(stacks[stack_id]) * 6
                        new_pos_y = MAP_BOUNDARY_RECT.top + stacks_undo_list[1] * (TILE_HEIGHT / 2)
                elif last_move == 'click extra tile':
                    new_pos_x = EXTENDED_ITEMS_BAR_RECT.left + extra_collected_tiles_undo_list[0]*TILE_WIDTH
                    new_pos_y = EXTENDED_ITEMS_BAR_RECT.centery - TILE_HEIGHT/2
                tile_coords_old.append([old_pos_x, old_pos_y])
                tile_coords.append([old_pos_x, old_pos_y])
                tile_coords_new.append([new_pos_x, new_pos_y])
                # 3. add stationary collected tiles list
                collected_tiles_stationary.append(copy.deepcopy(collected_tiles[:collected_tiles_undo_list[0]]))
                # 4. obtain velocities of collected items to move to right from old coords -> new coords
                num_of_velocities_old = len(copy.deepcopy(tile_velocities))
                num_of_tiles_added = 1
                for i in range(num_of_velocities_old, num_of_velocities_old + num_of_tiles_added):
                    vel_x = (tile_coords_new[i][0] - tile_coords_old[i][0])
                    vel_y = (tile_coords_new[i][1] - tile_coords_old[i][1])
                    # fixing velocity to SPEED but in same direction
                    old_speed = math.sqrt(vel_x ** 2 + vel_y ** 2)
                    new_vel_x = (vel_x / old_speed) * SPEED
                    new_vel_y = (vel_y / old_speed) * SPEED
                    tile_velocities.append([round(new_vel_x, 3), round(new_vel_y, 3)])
                # 5. setup variables for starting animation
                animation_types += [7] * num_of_tiles_added

                # setup animation for collected items to move left - TYPE 8
                # 1. make list for new collected tiles (remove first 3 elements), override only at the end
                # new_collected_tiles = copy.deepcopy(collected_tiles[3:])  # discard 3x combo tiles from items bar
                # 2. append tiles that should move to the left
                if collected_tiles[collected_tiles_undo_list[0]+1:]:
                    tiles_to_move += copy.deepcopy(collected_tiles[collected_tiles_undo_list[0]+1:])
                # 3. get old and new coords of tiles in items bar to push to the left
                # will only enter for loop if there are tiles to push to the left
                for index, _ in enumerate(collected_tiles[collected_tiles_undo_list[0]+1:]):
                    old_pos_x = ITEMS_BAR_RECT.left + ITEM_GAP + ((collected_tiles_undo_list[0]+1) * (TILE_WIDTH + ITEM_GAP)) \
                                + (index * (TILE_WIDTH + ITEM_GAP))
                    new_pos_x = old_pos_x - (TILE_WIDTH + ITEM_GAP)
                    old_pos_y = new_pos_y = ITEMS_BAR_RECT.centery - TILE_HEIGHT / 2
                    tile_coords_old.append([old_pos_x, old_pos_y])
                    tile_coords.append([old_pos_x, old_pos_y])
                    tile_coords_new.append([new_pos_x, new_pos_y])
                    # 4. add stationary collected tiles list (nothing to the left)
                    collected_tiles_stationary.append(copy.deepcopy(collected_tiles[:collected_tiles_undo_list[0]]))
                # 5. obtain velocities of collected items to move to right from old coords -> new coords
                num_of_velocities_old = len(copy.deepcopy(tile_velocities))
                num_of_tiles_added = len(collected_tiles[collected_tiles_undo_list[0]+1:])
                for index in range(num_of_velocities_old, num_of_velocities_old + num_of_tiles_added):
                    vel_x = (tile_coords_new[index][0] - tile_coords_old[index][0])
                    vel_y = (tile_coords_new[index][1] - tile_coords_old[index][1])
                    # fixing velocity to SPEED but in same direction
                    old_speed = math.sqrt(vel_x ** 2 + vel_y ** 2)
                    new_vel_x = (vel_x / old_speed) * SPEED
                    new_vel_y = (vel_y / old_speed) * SPEED
                    tile_velocities.append([round(new_vel_x, 3), round(new_vel_y, 3)])
                # 6. setup variables for starting animation
                animation_types += [8] * num_of_tiles_added
                # 7. update collected tiles using new collected tiles
                # collected_tiles = copy.deepcopy(new_collected_tiles)

            # shuffle button
            if BUTTONS["shuffle"]["button"].run(mouse_pos, left_mouse_down, not shuffle_used):
                shuffle()
                if not undo_used:
                    last_move = 'shuffle'
                shuffle_used = True

        elif play_state == "game lost":
            lose_screen(play_test)
            game_state = 'play level'
            print(game_state)
            if target_game_state != '':  # got absolute target state
                if game_state != target_game_state:  # reach destination
                    running = False
                    break

        elif play_state == "game won":
            win_screen(play_test)
            game_state = 'play level'
            print(game_state)
            if target_game_state != '':  # got absolute target state
                if game_state != target_game_state:  # reach destination
                    running = False
                    break

        # settings button
        if BUTTONS["settings"]["button"].run(mouse_pos, left_mouse_down):
            if play_test:
                play_settings(pause=False, play_test=True)
            else:
                play_settings(pause=False, play_test=False)
            game_state = 'play level'
            print(game_state)
            if target_game_state != '':  # got absolute target state
                if game_state != target_game_state:  # reach destination
                    running = False
                    break

        display_transition()

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()
        clock.tick(60)


def editor_level_select(level_select_page):
    global number_of_levels, game_state, target_game_state, level_names, current_level, transition, music_on
    game_state = 'editor level select'
    print(game_state)
    level_name_full_rect = pygame.Rect(0, 0, 0, 0)
    rename = False
    left_mouse_down_pos = (0, 0)
    new_level_name = ''
    rename_cursor_index = 0
    rename_cursor_tick = 0

    running = True  # use this method for all menus other than the outermost main menu, so that you can break the loop and exit
    while running:  # game loop
        left_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if rename:
                    # adding letters
                    # print(level_name_full_rect.width)
                    if len(new_level_name) < MAX_NAME_LENGTH:
                        for key in KEY_MAP.keys():
                            # if event.key == key and len(level_names[current_level]) < level_name_max_char:
                            if event.key == key:
                                if pygame.key.get_mods() & pygame.KMOD_CAPS:  # if caps_lock is ON
                                    added_key = KEY_MAP[key].upper()
                                else:
                                    added_key = KEY_MAP[key].lower()

                                # split word into two sections, 1 in front and 1 behind cursor, then inserting letter in between
                                level_name_front = new_level_name[:rename_cursor_index]
                                level_name_back = new_level_name[rename_cursor_index:]
                                new_level_name = level_name_front + added_key + level_name_back
                                rename_cursor_index += 1

                    if event.key == pygame.K_BACKSPACE:
                        if len(new_level_name) > 0:
                            level_name_front = new_level_name[:rename_cursor_index - 1]
                            level_name_back = new_level_name[rename_cursor_index:]
                            new_level_name = level_name_front + level_name_back  # remove last char
                            rename_cursor_index -= 1

                    # modifying rename cursor index
                    if event.key == pygame.K_LEFT:
                        if rename_cursor_index > 0:
                            rename_cursor_index -= 1
                    if event.key == pygame.K_RIGHT:
                        if rename_cursor_index < len(new_level_name):
                            rename_cursor_index += 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                # print(event.button)
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True

        # filling background colour every frame to refresh prev frame
        # screen.fill(bg_colour)
        screen.blit(bg_img, (0, 0))

        # back button
        if BUTTONS["back"]["button"].run(mouse_pos, left_mouse_down):
            transition = 2
            main_menu_img_rect.right = 0
        if transition == 2 and main_menu_img_rect.right == SCREEN_WIDTH:
            # reset back to no transition
            transition = 0
            screen.blit(main_menu_img, main_menu_img_rect)
            target_game_state = ''  # back to main menu
            running = False
            break

        display_text(screen, "SELECT LEVEL", False, TITLE_FONT, 50, "white", center=(SCREEN_WIDTH / 2, 70))

        # displaying all level tiles with delete and edit button
        number_of_pages = math.ceil(number_of_levels / (number_of_rows * number_of_cols))
        for row in range(number_of_rows):
            for col in range(number_of_cols):
                level_num = level_select_page * (number_of_rows * number_of_cols) + row * number_of_cols + (col + 1)  # start from 1
                # only display for existing levels
                if level_num <= number_of_levels and len(level_names) == number_of_levels and len(os.listdir('resources/pics/levels')) == number_of_levels:
                    level_tile_centerx = (col + 1) * (SCREEN_WIDTH / (number_of_cols + 1))
                    level_tile_centery = (row + 1) * (SCREEN_HEIGHT / (number_of_rows + 1))
                    btn_num = row * number_of_cols + (col + 1)
                    # display level bg tile
                    # level_tile_rect = display_img(screen, "level_tile.png", transform_type="scale", size=(140, 250),
                    #                               center=(level_tile_centerx, level_tile_centery))
                    screen.blit(level_tile_img, (level_tile_centerx - level_tile_img.get_width() / 2,
                                                 level_tile_centery - level_tile_img.get_height() / 2))

                    # display level name
                    font_size = LEVEL_SELECT_NAME_FONT_SIZE
                    name_rect = display_text(screen, f"{level_names[level_num - 1]}", False, TITLE_FONT, font_size, "white", return_rect_only=True,
                                             center=(level_tile_centerx, level_tile_centery-100))
                    # keep checking if level name fits inside box
                    # while name_rect.width > level_tile_rect.width-10:
                    while name_rect.width > level_tile_img.get_width() - 10:
                        font_size -= 1
                        name_rect = display_text(screen, f"{level_names[level_num - 1]}", False, TITLE_FONT,
                                                 font_size, "white", return_rect_only=True,
                                                 center=(level_tile_centerx, level_tile_centery - 100))
                    display_text(screen, f"{level_names[level_num - 1]}", False, TITLE_FONT, font_size, "white",
                                 center=(level_tile_centerx, level_tile_centery - 100))

                    # display level pic
                    # display_img(screen, f"level{level_num}.png", folder="pics/levels", transform_type="rotozoom", scale=0.28,
                    #             center=(level_tile_centerx, level_tile_centery-10))
                    screen.blit(level_images[level_num - 1], (
                        level_tile_centerx - level_images[level_num - 1].get_width() / 2,
                        level_tile_centery - 10 - level_images[level_num - 1].get_height() / 2))

                    # edit level button
                    if BUTTONS[f'level-tile-{btn_num}-view']["button"].run(mouse_pos, left_mouse_down):
                        # setting transition
                        transition = 3
                        sheep_bg_img_rect.left = SCREEN_WIDTH
                        current_level = level_num - 1

                    # delete level button
                    if BUTTONS[f'level-tile-{btn_num}-delete']["button"].run(mouse_pos, left_mouse_down,
                                                                             number_of_levels > 1):
                        number_of_levels, level_names = remove_level(level_num - 1, number_of_levels, level_names)
                        # print(level_names)
                        number_of_pages = math.ceil(number_of_levels / (number_of_rows * number_of_cols))
                        if level_select_page > number_of_pages - 1:
                            level_select_page = number_of_pages - 1

        if transition == 3 and sheep_bg_img_rect.centerx < SCREEN_WIDTH / 2:  # center of image pass center of screen
            level_editor(level=current_level+1)
            game_state = 'editor level select'
            print(game_state)
            if target_game_state != '':  # got absolute target state
                if game_state != target_game_state:  # reach destination
                    running = False
                    break

        # prev page button
        if BUTTONS["level-left"]["button"].run(mouse_pos, left_mouse_down, level_select_page > 0):
            level_select_page -= 1

        # next page button
        if BUTTONS["level-right"]["button"].run(mouse_pos, left_mouse_down, level_select_page < number_of_pages - 1):
            level_select_page += 1

        # display page number
        pygame.draw.rect(screen, COLOURS['SHADOW'], PAGE_NUMBER_RECT, border_radius=10)
        display_text(screen, f'{level_select_page + 1}/{number_of_pages}', False, WORD_FONT, 30, 'white',
                     center=(PAGE_NUMBER_RECT.centerx, PAGE_NUMBER_RECT.centery - 5))

        # music on/off toggle
        if music_on:
            music_on_rect = display_img(screen, 'music_on.png', transform_type='scale', size=(30, 30),
                                        return_rect_only=True, center=(30, SCREEN_HEIGHT - 30))
            if music_on_rect.collidepoint(mouse_pos):
                display_img(screen, 'music_on.png', transform_type='scale', size=(35, 35),
                            center=(30, SCREEN_HEIGHT - 30))
                if left_mouse_down:
                    music_on = False
                    stop_music()
            else:
                display_img(screen, 'music_on.png', transform_type='scale', size=(30, 30),
                            center=(30, SCREEN_HEIGHT - 30))
        else:
            music_off_rect = display_img(screen, 'music_off.png', transform_type='scale', size=(40, 40),
                                         return_rect_only=True, center=(30, SCREEN_HEIGHT - 30))
            if music_off_rect.collidepoint(mouse_pos):
                display_img(screen, 'music_off.png', transform_type='scale', size=(45, 45),
                            center=(30, SCREEN_HEIGHT - 30))
                if left_mouse_down:
                    music_on = True
                    resume_music()
            else:
                display_img(screen, 'music_off.png', transform_type='scale', size=(40, 40),
                            center=(30, SCREEN_HEIGHT - 30))

        # press new level button, start rename new level, add new level at end
        if BUTTONS["new-level"]["button"].run(mouse_pos, left_mouse_down, number_of_levels < MAX_LEVELS):
            new_level_name = ''
            rename = True
            # set default start pos of cursor at end of name
            rename_cursor_index = len(new_level_name)
            rename_cursor_tick = copy.deepcopy(rename_cursor_tick_max)

        # rename level
        # draw rect
        if rename:  # in rename stage
            # draw 50% transparent for whole game screen to blu everything behind
            surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 200))
            screen.blit(surf, (0, 0))

            # draw bg
            pygame.draw.rect(screen, COLOURS['DARK PURPLE'], RENAME_NEW_LEVEL_BG_RECT, border_radius=8)
            pygame.draw.rect(screen, 'white', RENAME_NEW_LEVEL_BG_RECT, width=2, border_radius=8)

            # draw 50% transparent box
            surf = pygame.Surface(RENAME_NEW_LEVEL_RECT.size, pygame.SRCALPHA)
            surf.fill((0, 0, 0, 128))
            screen.blit(surf, RENAME_NEW_LEVEL_RECT.topleft)
            # draw box outline
            pygame.draw.rect(screen, (255, 255, 255, 255), RENAME_NEW_LEVEL_RECT, 2)

            # display blinking cursor
            # reduce cursor tick timer
            rename_cursor_tick -= 1
            if rename_cursor_tick < 0:  # reset loop
                rename_cursor_tick = copy.deepcopy(rename_cursor_tick_max)
            # finding where to place cursor
            level_name_full_rect = display_text(screen, new_level_name, False, TITLE_FONT, font_size=NEW_LEVEL_RENAME_FONT_SIZE,
                                                text_colour="white", return_rect_only=True,
                                                center=RENAME_NEW_LEVEL_RECT.center)
            level_name_front_rect = display_text(screen, new_level_name[:rename_cursor_index], False, TITLE_FONT,
                                                 font_size=NEW_LEVEL_RENAME_FONT_SIZE, text_colour="white",
                                                 return_rect_only=True,
                                                 center=RENAME_NEW_LEVEL_RECT.center)
            rename_cursor_x = level_name_full_rect.left + level_name_front_rect.width
            if rename_cursor_tick > rename_cursor_tick_max // 2:  # draw cursor only half of the time of tick
                pygame.draw.line(screen, rename_cursor_colour,
                                 (rename_cursor_x, RENAME_NEW_LEVEL_RECT.centery - CURSOR_HEIGHT / 2),
                                 (rename_cursor_x, RENAME_NEW_LEVEL_RECT.centery + CURSOR_HEIGHT / 2), 2)

            # display level name
            if new_level_name == '':  # haven't typed anything or no name
                display_text(screen, 'NEW LEVEL NAME', False, TITLE_FONT, font_size=NEW_LEVEL_RENAME_FONT_SIZE, text_colour="white", alpha=128,
                             center=(RENAME_NEW_LEVEL_RECT.centerx, RENAME_NEW_LEVEL_RECT.centery+5))
            else:  # if got something typed
                display_text(screen, new_level_name, False, TITLE_FONT, font_size=NEW_LEVEL_RENAME_FONT_SIZE, text_colour="white",
                             center=(RENAME_NEW_LEVEL_RECT.centerx, RENAME_NEW_LEVEL_RECT.centery+5))

            # display done renaming button
            if BUTTONS["create-new-level"]["button"].run(mouse_pos, left_mouse_down, new_level_name != ''):
                rename = False
                level_editor(new_level_name=new_level_name)
                game_state = 'editor level select'
                print(game_state)
                if target_game_state != '':  # got absolute target state
                    if game_state != target_game_state:  # reach destination
                        running = False
                        break

            # display back button
            if BUTTONS["rename-new-level-back"]["button"].run(mouse_pos, left_mouse_down):
                rename = False

        display_transition()

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()  # update game display
        clock.tick(60)  # run game at 60 fps


def level_editor(level=-1, new_level_name=None):
    global map, stacks, number_of_tiles, current_layer, number_of_layers, current_level, number_of_levels, level_names, \
        level_select_page, layer_dragging, layer_selected, right_mouse_down, add, stack_setting, edit_tile, \
        cursor_img_no, stack_dir, stack_x, stack_y, stack_row, stack_col, music_on, \
        tile_count_pos, tile_count_warning, tile_count_dir, tile_count_rounds, \
        display_gridbox, game_state, target_game_state
    game_state = 'level editor'
    print(game_state)
    rename = False
    rename_cursor_index = 0
    rename_cursor_tick = 0
    left_mouse_down = False
    right_mouse_down = False
    settings = False
    hover_msg_tick = HOVER_MSG_TICK_START
    left_valid = right_valid = up_valid = down_valid = False

    play_music('in_game.mp3')

    # setting up map and stacks
    if level == -1:  # create new level
        level_names.append(new_level_name)
        map, stacks, number_of_tiles, current_layer, number_of_layers, layer_disp_list, current_level, \
            number_of_levels = add_level(number_of_levels)
    else:  # load existing level
        current_level = level - 1
        map, stacks, number_of_tiles, number_of_layers, current_layer, layer_disp_list = \
            load_level_complete(current_level)

    running = True
    while running:
        # print(pygame.mouse.get_rel())
        mouse_pos = pygame.mouse.get_pos()
        left_mouse_down_pos = (0, 0)
        right_mouse_up_pos = (0, 0)
        scroll_up = False
        scroll_down = False
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                tile_count_warning, tile_count_rounds, tile_count_dir = save_level(level_names, number_of_tiles,
                                                                                   tile_count_warning,
                                                                                   tile_count_rounds,
                                                                                   tile_count_dir,
                                                                                   current_level + 1, map,
                                                                                   stacks)  # save map in case window closes abruptly
                if not tile_count_warning:
                    # store main components of level editor in temp first before being altered in preview by update top layer()
                    temp_map = copy.deepcopy(map)
                    temp_stacks = copy.deepcopy(stacks)
                    temp_number_of_tiles = copy.deepcopy(number_of_tiles)

                    preview_level(ss_only=True)

                    # return back stored temp editor components into original place
                    map = copy.deepcopy(temp_map)
                    stacks = copy.deepcopy(temp_stacks)
                    number_of_tiles = copy.deepcopy(temp_number_of_tiles)

                    pygame.quit()
                    sys.exit()
                else:  # tile count invalid, don't exit yet
                    pass

            if event.type == pygame.KEYDOWN:
                if rename:
                    # adding letters
                    # print(level_name_full_rect.width)
                    if len(level_names[current_level]) < MAX_NAME_LENGTH:  # haven't crossed max word limit
                        for key in KEY_MAP.keys():
                            # if event.key == key and len(level_names[current_level]) < level_name_max_char:
                            if event.key == key:
                                if pygame.key.get_mods() & pygame.KMOD_CAPS:  # caps_lock is ON
                                    added_key = KEY_MAP[key].upper()
                                else:
                                    added_key = KEY_MAP[key].lower()

                                # split word into two sections, 1 in front and 1 behind cursor, then inserting letter in between
                                level_name_front = level_names[current_level][:rename_cursor_index]
                                level_name_back = level_names[current_level][rename_cursor_index:]
                                level_names[current_level] = level_name_front + added_key + level_name_back
                                rename_cursor_index += 1

                    if event.key == pygame.K_RETURN:
                        rename = False

                    if event.key == pygame.K_BACKSPACE:
                        if len(level_names[current_level]) > 0:
                            level_name_front = level_names[current_level][:rename_cursor_index - 1]
                            level_name_back = level_names[current_level][rename_cursor_index:]
                            level_names[current_level] = level_name_front + level_name_back  # remove last char
                            rename_cursor_index -= 1

                    # modifying rename cursor index
                    if event.key == pygame.K_LEFT:
                        if rename_cursor_index > 0:
                            rename_cursor_index -= 1
                    if event.key == pygame.K_RIGHT:
                        if rename_cursor_index < len(level_names[current_level]):
                            rename_cursor_index += 1

                if event.key == pygame.K_ESCAPE:
                    level_editor_settings(pause=True)
                    game_state = 'level editor'
                    print(game_state)
                    if target_game_state != '':  # got absolute target state
                        if game_state != target_game_state:  # reach destination
                            running = False
                            break

            if event.type == pygame.MOUSEBUTTONDOWN:
                # print(event.button)
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True
                    left_mouse_down_pos = event.pos  # update left mouse position
                if event.button == 3:  # right mouse button
                    right_mouse_down = True
                    right_mouse_down_pos = event.pos  # update right mouse position
                    # print(right_mouse_down_pos)
                if event.button == 4:  # scroll up
                    scroll_up = True
                if event.button == 5:  # scroll down
                    scroll_down = True
                # print(scroll_up, scroll_down)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # left mouse button
                    left_mouse_down = False
                    left_mouse_up_pos = event.pos  # update left mouse position
                if event.button == 3:  # right mouse button
                    right_mouse_down = False  # update right mouse position
                    right_mouse_up_pos = event.pos

        # filling background colour every frame to refresh prev frame
        screen.blit(bg_img, (0, 0))

        # preview button
        if BUTTONS["preview-on"]["button"].run(mouse_pos, left_mouse_down, not stack_setting and not rename):
            # store main components of level editor in temp first before being altered in preview by update top layer()
            temp_map = copy.deepcopy(map)
            temp_stacks = copy.deepcopy(stacks)
            temp_number_of_tiles = copy.deepcopy(number_of_tiles)

            preview_level()

            # return back stored temp editor components into original place
            map = copy.deepcopy(temp_map)
            stacks = copy.deepcopy(temp_stacks)
            number_of_tiles = copy.deepcopy(temp_number_of_tiles)

            # preview level func will exit and cont here
            game_state = 'level editor'
            print(game_state)
            if target_game_state != '':  # got absolute target state
                if game_state != target_game_state:  # reach destination
                    running = False
                    break

        # play test button
        if BUTTONS["test-play"]["button"].run(mouse_pos, left_mouse_down, not stack_setting and not rename):
            tile_count_warning, tile_count_rounds, tile_count_dir = save_level(level_names, number_of_tiles,
                                                                               tile_count_warning, tile_count_rounds,
                                                                               tile_count_dir, current_level + 1, map,
                                                                               stacks)
            if not tile_count_warning:
                # store main components of level editor in temp first before altering in play test mode
                temp_map = copy.deepcopy(map)
                temp_stacks = copy.deepcopy(stacks)
                temp_number_of_tiles = copy.deepcopy(number_of_tiles)

                play_level(current_level, play_test=True)

                # return back stored temp editor components into original place
                map = copy.deepcopy(temp_map)
                stacks = copy.deepcopy(temp_stacks)
                number_of_tiles = copy.deepcopy(temp_number_of_tiles)

                game_state = 'level editor'
                print(game_state)
                if target_game_state != '':  # got absolute target state
                    if game_state != target_game_state:  # reach destination
                        running = False
                        break

        # display level name and rename button
        if not rename:
            # draw bg
            pygame.draw.rect(screen, COLOURS['DARK PURPLE'], RENAME_LEVEL_BG_RECT, border_radius=15)
            # pygame.draw.rect(screen, 'white', RENAME_LEVEL_BG_RECT, width=2, border_radius=15)

            # display level name
            # print(current_level)
            display_text(screen, level_names[current_level], False, TITLE_FONT, font_size=LEVEL_NAME_FONT_SIZE,
                         text_colour="white",
                         center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery + 5))

            if not settings:
                if BUTTONS["rename"]["button"].run(mouse_pos, left_mouse_down):
                    rename = True
                    # set default start pos of cursor at end of name
                    rename_cursor_index = len(level_names[current_level])
                    rename_cursor_tick = copy.deepcopy(rename_cursor_tick_max)

        # delete level button
        if BUTTONS["delete-level"]["button"].run(mouse_pos, left_mouse_down,
                                                 number_of_levels > 1 and not rename and not settings and not stack_setting):  # at least 2 levels
            number_of_levels, level_names = remove_level(current_level, number_of_levels, level_names)
            # print(level_names)
            number_of_pages = math.ceil(number_of_levels / (number_of_rows * number_of_cols))
            if level_select_page > number_of_pages - 1:
                level_select_page = number_of_pages - 1
            target_game_state = 'editor level select'
            play_music('intro.mp3')
            running = False
            break  # after removing avoid anything below

        # save button
        if BUTTONS["save"]["button"].run(mouse_pos, left_mouse_down, not rename and not settings and not stack_setting):
            tile_count_warning, tile_count_rounds, tile_count_dir = save_level(level_names, number_of_tiles,
                                                                               tile_count_warning, tile_count_rounds,
                                                                               tile_count_dir, current_level + 1, map,
                                                                               stacks)
            if not tile_count_warning:
                # store main components of level editor in temp first before being altered in preview by update top layer()
                temp_map = copy.deepcopy(map)
                temp_stacks = copy.deepcopy(stacks)
                temp_number_of_tiles = copy.deepcopy(number_of_tiles)

                preview_level(ss_only=True)

                # return back stored temp editor components into original place
                map = copy.deepcopy(temp_map)
                stacks = copy.deepcopy(temp_stacks)
                number_of_tiles = copy.deepcopy(temp_number_of_tiles)

                game_state = 'level editor'
                print(game_state)
                if target_game_state != '':  # got absolute target state
                    if game_state != target_game_state:  # reach destination
                        running = False
                        break

        # draw left and right side bar
        # left top
        pygame.draw.rect(screen, left_sidebar_colour, LEFT_TOP_BG_RECT, border_radius=15)
        # left bottom
        pygame.draw.rect(screen, left_sidebar_colour, LEFT_BOTTOM_BG_RECT, border_radius=20)
        # right
        pygame.draw.rect(screen, right_sidebar_colour, RIGHT_BG_RECT, border_radius=20)

        # add layer button
        if BUTTONS["add-layer"]["button"].run(mouse_pos, left_mouse_down,
                                              number_of_layers < MAX_LAYERS and not rename and not settings and not stack_setting):  # layer cap
            map.insert(current_layer + 1, copy.deepcopy(MAP_BLANK_LEVEL))
            layer_disp_list.insert(current_layer + 1, 2)  # current layer shifts 1 down
            number_of_layers += 1
            current_layer += 1
            layer_disp_list[current_layer - 1] = 1  # darken prev layer
            # print(current_layer, number_of_layers-1)

        # delete layer button
        if BUTTONS["delete-layer"]["button"].run(mouse_pos, left_mouse_down,
                                                 number_of_layers > 1 and not rename and not settings and not stack_setting):
            map.pop(current_layer)
            layer_disp_list.pop(current_layer)
            # only at the last layer, there is nothing behind the current layer to move into its place, so it will be invalid layer
            if current_layer == number_of_layers - 1:
                current_layer -= 1  # move to the new last layer
            else:
                pass  # remain the same layer as before
            layer_disp_list[current_layer] = 2  # light up current layer
            number_of_layers -= 1

        # display layer number
        display_text(screen, f"{number_of_layers}", True, None, font_size=25, text_colour=(255, 255, 255),
                     center=(22, MAP_BOUNDARY_RECT.top+50))

        # display all layers on sidebar
        LEFT_BOTTOM_BOUNDARY_RECT = pygame.Rect(3, MAP_BOUNDARY_RECT.top+120, LAYER_RECT_WIDTH, number_of_layers * LAYER_RECT_HEIGHT)
        for layer in range(number_of_layers):
            if layer_disp_list[layer] == 1:
                display_img(screen, 'dark_layer.png', transform_type="scale", size=(35, 35),
                            midtop=(20, LEFT_BOTTOM_BOUNDARY_RECT.top + layer * LAYER_RECT_HEIGHT))
            elif layer_disp_list[layer] == 2:
                display_img(screen, 'layer.png', transform_type="scale", size=(35, 35),
                            midtop=(20, LEFT_BOTTOM_BOUNDARY_RECT.top + layer * LAYER_RECT_HEIGHT))

        # pygame.draw.rect(screen, "purple", layer_boundary_rect, 1)
        # swapping layers by drag and drop
        if not rename and not settings and not stack_setting:
            if not layer_dragging:
                if LEFT_BOTTOM_BOUNDARY_RECT.collidepoint(mouse_pos):
                    # just hovering over layer
                    layer_cursor = math.floor((mouse_pos[1] - LEFT_BOTTOM_BOUNDARY_RECT.top) / LAYER_RECT_HEIGHT)
                    if layer_disp_list[layer_cursor] == 1:
                        display_img(screen, 'dark_layer.png', transform_type="scale", size=(45, 45),
                                    center=(20, LEFT_BOTTOM_BOUNDARY_RECT.top + layer_cursor * LAYER_RECT_HEIGHT + LAYER_RECT_HEIGHT / 2))
                    elif layer_disp_list[layer_cursor] == 2:
                        display_img(screen, 'layer.png', transform_type="scale", size=(45, 45),
                                    center=(20, LEFT_BOTTOM_BOUNDARY_RECT.top + layer_cursor * LAYER_RECT_HEIGHT + LAYER_RECT_HEIGHT / 2))

                    # pressed down on layer, start dragging
                    if left_mouse_down:
                        play_sound('click.wav')
                        layer_selected = math.floor((left_mouse_down_pos[1] - 220) / LAYER_RECT_HEIGHT)
                        if layer_selected >= 0:
                            layer_dragging = True
                            layer_disp_list[layer_selected] = 0
            else:
                # upper and lower drag limits
                cursor_img_center_y = mouse_pos[1]
                if cursor_img_center_y - LAYER_RECT_HEIGHT / 2 < 220:
                    cursor_img_center_y = LEFT_BOTTOM_BOUNDARY_RECT.top + LAYER_RECT_HEIGHT / 2
                if cursor_img_center_y + LAYER_RECT_HEIGHT / 2 > 220 + number_of_layers * LAYER_RECT_HEIGHT:
                    cursor_img_center_y = LEFT_BOTTOM_BOUNDARY_RECT.top + number_of_layers * LAYER_RECT_HEIGHT - LAYER_RECT_HEIGHT / 2

                # display cursor image
                if layer_selected == current_layer:
                    display_img(screen, 'layer.png', transform_type="scale", size=(45, 45),
                                center=(20, cursor_img_center_y))
                else:
                    display_img(screen, 'dark_layer.png', transform_type="scale", size=(45, 45),
                                center=(20, cursor_img_center_y))

                if math.floor((mouse_pos[1] - LEFT_BOTTOM_BOUNDARY_RECT.top) / LAYER_RECT_HEIGHT) < number_of_layers:
                    # updating which layer box should be empty
                    layer_hovering = math.floor((mouse_pos[1] - LEFT_BOTTOM_BOUNDARY_RECT.top) / LAYER_RECT_HEIGHT)
                    if layer_hovering < 0:
                        layer_hovering = 0
                    if layer_hovering > number_of_layers - 1:
                        layer_hovering = number_of_layers - 1
                    layer_disp_list.remove(0)
                    layer_disp_list.insert(layer_hovering, 0)

                    # drop the dragging layer if left mouse is released
                    if not left_mouse_down and LEFT_BOTTOM_BOUNDARY_RECT.top < mouse_pos[
                        1] < LEFT_BOTTOM_BOUNDARY_RECT.bottom:
                        play_sound('click.wav')
                        # rearrange the map layers
                        temp = copy.deepcopy(map[layer_selected])
                        map.pop(layer_selected)
                        map.insert(layer_hovering, temp)
                        layer_dragging = False

                        # correcting current layer and reverting back 0 in disp list to selected number
                        if layer_selected == current_layer:
                            layer_disp_list[layer_hovering] = 2
                            current_layer = layer_hovering
                        else:
                            layer_disp_list[layer_hovering] = 1
                            current_layer = layer_disp_list.index(2)

        # reset whole level from fresh button
        if BUTTONS["reset-level"]["button"].run(mouse_pos, left_mouse_down, not rename and not settings and not stack_setting):
            map = [copy.deepcopy(MAP_BLANK_LEVEL)]
            stacks = []
            current_layer = 0
            number_of_layers = 1
            layer_disp_list = [2]
            # reset tile count
            number_of_tiles = 0

        # switching between layers by scrolling
        if not rename and not settings and not (stack_setting and not edit_tile):
            if scroll_up:
                current_layer -= 1  # go 1 layer above
                if current_layer < 0:  # lower limit
                    current_layer = 0
                layer_disp_list[current_layer] = 2
                if number_of_layers > 1:
                    layer_disp_list[current_layer + 1] = 1
                # print(current_layer, number_of_layers - 1)
            if scroll_down:
                current_layer += 1  # go 1 layer below
                if current_layer > number_of_layers - 1:
                    current_layer = number_of_layers - 1
                layer_disp_list[current_layer] = 2
                if number_of_layers > 1:
                    layer_disp_list[current_layer - 1] = 1
                # print(current_layer, number_of_layers - 1)

        # change mode (add tile/add stack/delete)
        if BUTTONS["add-tiles"]["button"].run(mouse_pos, left_mouse_down, not rename and not settings and not stack_setting):  # add tiles
            edit_tile = True
            add = True
        if BUTTONS["add-stacks"]["button"].run(mouse_pos, left_mouse_down, not rename and not settings and not stack_setting):  # add stacks
            edit_tile = False
            add = True
        if BUTTONS["delete-tiles"]["button"].run(mouse_pos, left_mouse_down,
                                                 not rename and not settings and not stack_setting):  # delete tiles
            edit_tile = True
            add = False

        # indentation on tile mode buttons
        if add:
            if edit_tile:
                screen.blit(BUTTONS['add-tiles']['button'].image_pressed, BUTTONS['add-tiles']['button'].rect)
            else:
                screen.blit(BUTTONS['add-stacks']['button'].image_pressed, BUTTONS['add-stacks']['button'].rect)
        else:
            screen.blit(BUTTONS['delete-tiles']['button'].image_pressed, BUTTONS['delete-tiles']['button'].rect)

        # display boundary and grid lines
        if display_gridbox:
            # pygame.draw.rect(screen, grid_line_colour, MAP_BOUNDARY_RECT, width=1)
            # displaying vertical grid lines
            for i in range(15):
                x_start = x_end = MAP_BOUNDARY_RECT.left + i * 25
                y_start = MAP_BOUNDARY_RECT.top
                y_end = y_start + 20*25 - 1
                pygame.draw.line(screen, grid_line_colour, (x_start, y_start), (x_end, y_end))
            # displaying horizontal grid lines
            for j in range(21):
                x_start = MAP_BOUNDARY_RECT.left
                x_end = x_start + 14*25 - 1
                y_start = y_end = MAP_BOUNDARY_RECT.top + j * 25
                pygame.draw.line(screen, grid_line_colour, (x_start, y_start), (x_end, y_end))

        # drawing placed tiles on screen
        # print(current_layer)
        for i in range(len(map[current_layer])):
            for j in range(len(map[current_layer][i])):
                if map[current_layer][i][j] > 0:  # only if grid point contains top left corner of tile
                    if map[current_layer][i][j] < 100:  # for ordinary layout tiles
                        tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2)
                        tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                        img = tile_images[map[current_layer][i][j]]
                        tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                        screen.blit(img, tile_rect)
                    else:  # stack
                        dir = int(str(map[current_layer][i][j])[1])  # dir: 1-up, 2-down, 3-left, 4-right
                        stack_id = int(str(map[current_layer][i][j])[2])

                        for k, stack_tile in enumerate(stacks[stack_id]):
                            # get tile position
                            if dir == 1:  # up
                                tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2)
                                tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2) - k * 6
                            elif dir == 2:  # down
                                tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2)
                                tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2) + k * 6
                            elif dir == 3:  # left
                                tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2) - k * 6
                                tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                            elif dir == 4:  # right
                                tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2) + k * 6
                                tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                            # draw transluscent mask for tiles that are not visible
                            if k < len(stacks[stack_id]) - 1:  # below top layer
                                img = tile_images[0]  # blank tile
                                tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                                screen.blit(img, tile_rect)
                                dark_surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
                                dark_surf.set_alpha(128)  # 50 % opacity
                                dark_surf.fill('#2F1443')  # dark purple
                                screen.blit(dark_surf, tile_rect)
                            else:
                                img = tile_images[stack_tile]
                                tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                                screen.blit(img, tile_rect)

        # everything happening in center display area
        if MAP_BOUNDARY_RECT.collidepoint(
                mouse_pos) and not layer_dragging and not rename and not settings:  # cursor is within available zone for placing tile
            map_col = math.floor((mouse_pos[0] - MAP_BOUNDARY_RECT.left) / 25)
            map_row = math.floor((mouse_pos[1] - MAP_BOUNDARY_RECT.top) / 25)
            if not right_mouse_down:  # right mouse btn not clicked
                # print(edit_tile, add)
                if add:  # add mode
                    # draw indicators for placing tiles
                    if map_col <= 12 and map_row <= 18:  # excluding last row and column
                        if not (stack_setting and not edit_tile):
                            # draw cursor tile image
                            preview_x = MAP_BOUNDARY_RECT.left + map_col * (TILE_WIDTH / 2)
                            preview_y = MAP_BOUNDARY_RECT.top + map_row * (TILE_HEIGHT / 2)
                            preview_rect = display_img(screen, f'{cursor_img_no}.png', topleft=(preview_x, preview_y))

                            # check if cursor tile is valid or not
                            valid = check_collision(map, stacks, preview_rect, current_layer)

                            # if layer is not top layer, disallow placement of stack
                            if not edit_tile and current_layer > 0:
                                valid = False

                            if not edit_tile:
                                # generate predicted stack rect with only 2 tiles in all 4 directions
                                left_preview_rect = pygame.Rect((preview_x-6, preview_y), (TILE_WIDTH+6, TILE_HEIGHT))
                                left_valid = check_collision(map, stacks, left_preview_rect, current_layer)
                                right_preview_rect = pygame.Rect((preview_x, preview_y), (TILE_WIDTH+6, TILE_HEIGHT))
                                right_valid = check_collision(map, stacks, right_preview_rect, current_layer)
                                up_preview_rect = pygame.Rect((preview_x, preview_y-6), (TILE_WIDTH, TILE_HEIGHT+6))
                                up_valid = check_collision(map, stacks, up_preview_rect, current_layer)
                                down_preview_rect = pygame.Rect((preview_x, preview_y), (TILE_WIDTH, TILE_HEIGHT+6))
                                down_valid = check_collision(map, stacks, down_preview_rect, current_layer)

                                # disallow placement if neither directions of stack are valid
                                if not left_valid and not right_valid and not up_valid and not down_valid:
                                    valid = False

                            # transluscent mask
                            preview_surf = pygame.Surface((50, 50))
                            preview_surf.set_alpha(150)
                            if valid:
                                preview_surf.fill((129, 212, 102))  # green
                            else:
                                preview_surf.fill((176, 49, 49))  # red
                            screen.blit(preview_surf, (preview_x, preview_y))
                            # print((map_col, map_row))

                            # print(number_of_tiles)
                            # place tile if clicked and its not obstructed by other tiles
                            if valid and (left_mouse_down_pos[0] > 0 or left_mouse_down_pos[
                                1] > 0):  # don't care position, as long as got click, position covered by mouse_down
                                play_sound('click.wav')
                                if edit_tile:
                                    map[current_layer][map_row][
                                        map_col] = cursor_img_no  # randomly choose 1 tile type just for variety
                                    cursor_img_no = random.choice(tile_types)
                                else:
                                    if not stack_setting:
                                        map[current_layer][map_row][
                                            map_col] = cursor_img_no  # randomly put a front tile first
                                        stacks.append([cursor_img_no])
                                        stack_row = copy.deepcopy(map_row)
                                        stack_col = copy.deepcopy(map_col)
                                        stack_x = copy.deepcopy(preview_x)
                                        stack_y = copy.deepcopy(preview_y)
                                        stack_dir = 0
                                        stack_setting = True
                                        cursor_img_no = random.choice(tile_types)

                    # setting stacks direction and number after placing first tile
                    if stack_setting and not edit_tile:
                        if stack_dir == 0:  # direction choosing stage
                            # display arrow and add/delete buttons
                            img_center_x = stack_x + TILE_WIDTH / 2
                            img_center_y = stack_y + TILE_HEIGHT / 2
                            if up_valid:
                                BUTTONS['stack-up']['button'].rect.center = (img_center_x, img_center_y - MAP_BOUNDARY_RECT.left)
                                if BUTTONS['stack-up']['button'].run(mouse_pos, left_mouse_down):
                                    play_sound('click.wav')
                                    stack_dir = 1
                                    # force add 1 tile at the start to make sure the stack min 2 tiles
                                    stacks[-1].insert(0, 1)  # the back tiles don't matter, so just put tile type 1

                            if down_valid:
                                BUTTONS['stack-down']['button'].rect.center = (
                                    img_center_x, img_center_y + MAP_BOUNDARY_RECT.left)
                                if BUTTONS['stack-down']['button'].run(mouse_pos, left_mouse_down):
                                    play_sound('click.wav')
                                    stack_dir = 2
                                    stacks[-1].insert(0, 1)  # the back tiles don't matter, so just put tile type 1

                            if left_valid:
                                BUTTONS['stack-left']['button'].rect.center = (
                                    img_center_x - MAP_BOUNDARY_RECT.left, img_center_y)
                                if BUTTONS['stack-left']['button'].run(mouse_pos, left_mouse_down):
                                    play_sound('click.wav')
                                    stack_dir = 3
                                    stacks[-1].insert(0, 1)  # the back tiles don't matter, so just put tile type 1

                            if right_valid:
                                BUTTONS['stack-right']['button'].rect.center = (
                                    img_center_x + MAP_BOUNDARY_RECT.left, img_center_y)
                                if BUTTONS['stack-right']['button'].run(mouse_pos, left_mouse_down):
                                    play_sound('click.wav')
                                    stack_dir = 4
                                    stacks[-1].insert(0, 1)  # the back tiles don't matter, so just put tile type 1

                            # print(stack_dir)
                        else:  # chose direction already
                            # getting top tile center point coord
                            img_center_x = stack_x + TILE_WIDTH / 2
                            if stack_dir == 3:
                                img_center_x = stack_x - (len(stacks[-1]) - 1) * 6 + TILE_WIDTH / 2
                            elif stack_dir == 4:
                                img_center_x = stack_x + (len(stacks[-1]) - 1) * 6 + TILE_WIDTH / 2

                            img_center_y = stack_y + TILE_HEIGHT / 2
                            if stack_dir == 1:
                                img_center_y = stack_y - (len(stacks[-1]) - 1) * 6 + TILE_HEIGHT / 2
                            elif stack_dir == 2:
                                img_center_y = stack_y + (len(stacks[-1]) - 1) * 6 + TILE_HEIGHT / 2

                            # getting rect if stack extends further
                            if stack_dir == 1:  # up
                                preview_rect = pygame.Rect(img_center_x - TILE_WIDTH/2, img_center_y - TILE_HEIGHT/2 - 6, \
                                                           TILE_WIDTH, (len(stacks[-1]) - 1) * 6 + TILE_HEIGHT + 6)
                            elif stack_dir == 2:  # down
                                preview_rect = pygame.Rect(stack_x, stack_y, TILE_WIDTH,
                                                           (len(stacks[-1]) - 1) * 6 + TILE_HEIGHT + 6)
                            elif stack_dir == 3:  # left
                                preview_rect = pygame.Rect(img_center_x - TILE_WIDTH/2 - 6, img_center_y - TILE_HEIGHT/2,
                                                           TILE_WIDTH + (len(stacks[-1]) - 1) * 6 + 6, TILE_HEIGHT)
                            elif stack_dir == 4:  # right
                                preview_rect = pygame.Rect(stack_x, stack_y,
                                                           TILE_WIDTH + (len(stacks[-1]) - 1) * 6 + 6, TILE_HEIGHT)
                            # check if extended stack is valid or not
                            valid = check_collision(map, stacks, preview_rect, current_layer, ignore_ij=[stack_row, stack_col])

                            # adding and deleting tiles in stacks
                            BUTTONS['add-stack-tile']['button'].rect.center = (img_center_x + 12, img_center_y+12)
                            if BUTTONS['add-stack-tile']['button'].run(mouse_pos, left_mouse_down, len(stacks[-1]) < MAX_STACK_COUNT and valid):
                                play_sound('click.wav')
                                stacks[-1].insert(0, 1)  # the back tiles don't matter, so just put tile type 1

                            BUTTONS['delete-stack-tile']['button'].rect.center = (img_center_x - 12, img_center_y+12)
                            if BUTTONS['delete-stack-tile']['button'].run(mouse_pos, left_mouse_down,
                                                                          len(stacks[-1]) > MIN_STACK_COUNT):
                                play_sound('click.wav')
                                stacks[-1].pop(0)  # remove last tile

                            map[current_layer][stack_row][stack_col] = 100 + stack_dir * 10 + (len(stacks) - 1)

                            # display stack count
                            pygame.draw.circle(screen, COLOURS['DARK PURPLE'], (img_center_x-TILE_WIDTH/2, img_center_y-TILE_HEIGHT/2), 12)
                            pygame.draw.circle(screen, 'black', (img_center_x-TILE_WIDTH/2, img_center_y-TILE_HEIGHT/2), 12, 1)
                            display_text(screen, f'{len(stacks[-1])}', False, None, 23, center=(img_center_x-TILE_WIDTH/2, img_center_y-TILE_HEIGHT/2))

                            # confirming stack count
                            BUTTONS['confirm-stack']['button'].rect.center = (img_center_x + TILE_WIDTH / 2, img_center_y - TILE_HEIGHT / 2)
                            if BUTTONS['confirm-stack']['button'].run(mouse_pos, left_mouse_down):
                                play_sound('click.wav')
                                stack_setting = False

                else:  # delete mode  (works for both tiles and stacks)
                    # finding correct tile coordinate to delete
                    [delete_row, delete_col], delete_rect = check_point_collision(map, stacks, mouse_pos, current_layer)

                    if delete_rect is not None:
                        # transluscent dark mask
                        dark_surf = pygame.Surface((delete_rect.width, delete_rect.height))
                        dark_surf.set_alpha(128)  # 50 % opacity
                        dark_surf.fill((0, 0, 0))  # black
                        screen.blit(dark_surf, delete_rect)

                        # draw delete icon
                        display_img(screen, 'minus.png', transform_type='scale', size=(20, 20),
                                    center=delete_rect.topleft)

                        # if clicked, delete selected tile from map and it won't be displayed anymore
                        if left_mouse_down_pos[0] + left_mouse_down_pos[1] > 0:
                            play_sound('click.wav')
                            if map[current_layer][delete_row][delete_col] < 100:  # tiles
                                map[current_layer][delete_row][
                                    delete_col] = 0  # only deletes tile from map, doesn't delete stack
                            else:  # stacks
                                delete_stack_id = int(str(map[current_layer][delete_row][delete_col])[2])
                                stacks.pop(delete_stack_id)  # remove deleted stack from stack list
                                map[current_layer][delete_row][delete_col] = 0  # remove stack from map

                                # relabel the id of remaining stacks in map
                                for i in range(len(map[current_layer])):
                                    for j in range(len(map[current_layer][i])):
                                        if map[current_layer][i][j] >= 100:
                                            old_dir = int(str(map[current_layer][i][j])[1]) # dir: 1-up, 2-down, 3-left, 4-right
                                            old_stack_id = int(str(map[current_layer][i][j])[2])
                                            if old_stack_id > delete_stack_id:
                                                new_stack_id = old_stack_id - 1
                                                map[current_layer][i][j] = 100 + old_dir * 10 + new_stack_id

        # rename level
        if rename:  # in rename stage
            # draw 50% transparent for whole game screen to blur everything behind
            surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT-RENAME_LEVEL_BG_RECT.top), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 200))
            screen.blit(surf, (0, RENAME_LEVEL_BG_RECT.top))

            # draw bg
            pygame.draw.rect(screen, COLOURS['DARK PURPLE'], RENAME_LEVEL_BG_RECT, border_radius=15)
            # pygame.draw.rect(screen, 'white', RENAME_LEVEL_BG_RECT, width=2, border_radius=15)

            # draw 50% transparent box for renaming level
            surf = pygame.Surface(LEVEL_NAME_RECT.size, pygame.SRCALPHA)
            surf.fill((0, 0, 0, 128))
            screen.blit(surf, LEVEL_NAME_RECT.topleft)
            # pygame.draw.circle(screen, (255,0,0,50), (20,20), 20)
            pygame.draw.rect(screen, (255, 255, 255, 255), LEVEL_NAME_RECT, 2)

            if BUTTONS["rename-done"]["button"].run(mouse_pos, left_mouse_down):
                rename = False

            # display blinking cursor
            # reduce cursor tick timer
            rename_cursor_tick -= 1
            if rename_cursor_tick < 0:  # reset loop
                rename_cursor_tick = copy.deepcopy(rename_cursor_tick_max)
            # finding where to place cursor
            level_name_full_rect = display_text(screen, level_names[current_level], False, TITLE_FONT, font_size=LEVEL_NAME_FONT_SIZE,
                                                text_colour="white", return_rect_only=True,
                                                center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery+5))
            level_name_front_rect = display_text(screen,
                                                 level_names[current_level][:rename_cursor_index], False, TITLE_FONT,
                                                 font_size=LEVEL_NAME_FONT_SIZE, text_colour="white",
                                                 return_rect_only=True,
                                                 center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery+5))
            rename_cursor_x = level_name_full_rect.left + level_name_front_rect.width
            if rename_cursor_tick > rename_cursor_tick_max // 2:  # draw cursor only half of the time of tick
                pygame.draw.line(screen, rename_cursor_colour,
                                 (rename_cursor_x, LEVEL_NAME_RECT.centery - CURSOR_HEIGHT / 2),
                                 (rename_cursor_x, LEVEL_NAME_RECT.centery + CURSOR_HEIGHT / 2), 2)

            # display level name
            if level_names[current_level] == '':  # haven't typed anything or no name
                display_text(screen, 'LEVEL NAME HERE', False, TITLE_FONT, font_size=LEVEL_NAME_FONT_SIZE,
                             text_colour="white", alpha=128,
                             center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery+5))
            else:  # if got something typed
                display_text(screen, level_names[current_level], False, TITLE_FONT, font_size=LEVEL_NAME_FONT_SIZE,
                             text_colour="white",
                             center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery+5))

        # settings button
        if BUTTONS["settings"]["button"].run(mouse_pos, left_mouse_down, not rename and not settings and not stack_setting):
            # settings = True
            level_editor_settings()
            game_state = 'level editor'
            print(game_state)
            if target_game_state != '':  # got absolute target state
                if game_state != target_game_state:  # reach destination
                    running = False
                    break

        # display number of tiles
        # display tile number bg
        display_img(screen, 'tile_count.png', transform_type="scale", size=(30, 30),
                    center=tile_count_pos)
        # display tiles count remaining to be valid or check mark for valid
        if number_of_tiles % 3 > 0:  # got tiles remaining
            tiles_left = 3 - number_of_tiles % 3
            text_colour = (255, 255, 255)
            display_text(screen, f"{tiles_left}", True, None, font_size=25, text_colour=text_colour,
                         center=tile_count_pos)
        else:
            tiles_left = 0
            # display tick to indicate valid
            display_img(screen, 'tick.png', transform_type="scale", size=(15, 15),
                        center=tile_count_pos)
        # tile shaking animation
        if not tile_count_warning:
            if tile_count_pos == tile_count_pos_ori:
                text_colour = (255, 255, 255)
            else:
                # last stretch of shake animation
                if tile_count_dir == 1:  # right
                    tile_count_pos[0] += tile_count_speed
                    if tile_count_pos[0] > tile_count_pos_ori[0]:
                        tile_count_pos = copy.deepcopy(tile_count_pos_ori)
                elif tile_count_dir == -1:  # left
                    tile_count_pos[0] -= tile_count_speed
                    if tile_count_pos[0] < tile_count_pos_ori[0]:
                        tile_count_pos = copy.deepcopy(tile_count_pos_ori)

                # tile count warning popup box
                if tile_count_pos[0] == tile_count_pos_ori[0]:  # finished last step of shaking
                    tile_count_warning_popup()
        else:  # shaking animation for warning
            if tile_count_dir == 1:  # right
                tile_count_pos[0] += tile_count_speed
                if tile_count_pos[0] >= tile_count_upper_bound:
                    tile_count_dir = -1
                    tile_count_rounds += 1
                    if tile_count_rounds >= tile_count_rounds_max:
                        tile_count_warning = False
            elif tile_count_dir == -1:  # left
                tile_count_pos[0] -= tile_count_speed
                if tile_count_pos[0] <= tile_count_lower_bound:
                    tile_count_dir = 1
                    tile_count_rounds += 1
                    if tile_count_rounds >= tile_count_rounds_max:
                        tile_count_warning = False

        # draw black transluscent mask over remaining unblurred buttons when renaming
        if rename:
            # draw 50% transparent for whole game screen to blur everything behind
            surf = pygame.Surface((SCREEN_WIDTH, RENAME_LEVEL_BG_RECT.top), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 200))
            screen.blit(surf, (0, 0))

        # hover messages
        # updating hovering countdown timer
        if sum(pygame.mouse.get_rel()) == 0:  # mouse stationary
            hover_msg_tick -= 1  # countdown timer if mouse is stationary over button
            if hover_msg_tick < 0:
                hover_msg_tick = 0
        else:  # mouse moving
            # reset countdown to display msg
            hover_msg_tick = HOVER_MSG_TICK_START

        # display messages if hovering any of these buttons after a period of time
        if hover_msg_tick == 0:
            if BUTTONS['add-layer']['button'].state == "hovering":
                msg = 'Add layer'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.bottomleft = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['delete-layer']['button'].state == "hovering":
                msg = 'Delete layer'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.bottomleft = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['reset-level']['button'].state == "hovering":
                msg = 'Clear level'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['delete-level']['button'].state == "hovering":
                msg = 'Delete level'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['save']['button'].state == "hovering":
                msg = 'Save'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['settings']['button'].state == "hovering":
                msg = 'Settings'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['rename']['button'].state == "hovering":
                msg = 'Rename level'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['add-tiles']['button'].state == "hovering":
                msg = 'Add tiles'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['add-stacks']['button'].state == "hovering":
                msg = 'Add stacks'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['delete-tiles']['button'].state == "hovering":
                msg = 'Delete tiles/stacks'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0,0), (msg_rect.width+10, msg_rect.height+10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)

            # hovering over layer to swap
            if not rename and not settings:
                if not layer_dragging:
                    if LEFT_BOTTOM_BOUNDARY_RECT.collidepoint(mouse_pos):
                        msg = 'Scroll to view other layers. Drag layer to swap position.'
                        msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white',
                                                return_rect_only=True, bottomleft=mouse_pos)
                        msg_rect = pygame.Rect((0, 0), (msg_rect.width + 10, msg_rect.height + 10))
                        msg_rect.bottomleft = mouse_pos
                        pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                        pygame.draw.rect(screen, 'white', msg_rect, width=1)
                        display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)

        # recalculate number of tiles after everything done in 1 frame
        number_of_tiles = update_number_of_tiles(map, stacks)

        display_transition()

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()  # update game display
        clock.tick(60)  # run game at 60 fps


def preview_level(ss_only=False):
    global map, stacks, number_of_tiles, current_layer, number_of_layers, current_level, number_of_levels, level_names, \
        level_select_page, display_gridbox, music_on, rename_cursor_tick, level_name_full_rect, \
        tile_count_pos, tile_count_warning, tile_count_dir, tile_count_rounds, \
        game_state, target_game_state, hover_msg_tick
    game_state = 'preview level'
    print(game_state)

    rename = False
    rename_cursor_index = 0
    new_level_name = ''
    left_mouse_down = False
    settings = False
    take_ss = False
    SS_TICK_MAX = 2
    ss_tick = 0
    if ss_only:
        ss_tick = SS_TICK_MAX
        take_ss = True

    # bring all visible tiles from bottom layers to top
    map = update_top_layer(map)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        left_mouse_down = False

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                tile_count_warning, tile_count_rounds, tile_count_dir = save_level(level_names, number_of_tiles,
                                                                                   tile_count_warning,
                                                                                   tile_count_rounds,
                                                                                   tile_count_dir,
                                                                                   current_level + 1, map,
                                                                                   stacks)  # save map in case window closes abruptly
                if not tile_count_warning:
                    # store main components of level editor in temp first before being altered in preview by update top layer()
                    temp_map = copy.deepcopy(map)
                    temp_stacks = copy.deepcopy(stacks)
                    temp_number_of_tiles = copy.deepcopy(number_of_tiles)

                    preview_level(ss_only=True)

                    # return back stored temp editor components into original place
                    map = copy.deepcopy(temp_map)
                    stacks = copy.deepcopy(temp_stacks)
                    number_of_tiles = copy.deepcopy(temp_number_of_tiles)

                    pygame.quit()
                    sys.exit()
                else:  # tile count invalid
                    pass

            if event.type == pygame.KEYDOWN:
                if rename:
                    # adding letters
                    # print(level_name_full_rect.width)
                    if len(level_names[current_level]) < MAX_NAME_LENGTH:
                        for key in KEY_MAP.keys():
                            # if event.key == key and len(level_names[current_level]) < level_name_max_char:
                            if event.key == key:
                                if pygame.key.get_mods() & pygame.KMOD_CAPS:
                                    added_key = KEY_MAP[key].upper()
                                else:
                                    added_key = KEY_MAP[key].lower()

                                # split word into two sections, 1 in front and 1 behind cursor, then inserting letter in between
                                level_name_front = level_names[current_level][:rename_cursor_index]
                                level_name_back = level_names[current_level][rename_cursor_index:]
                                level_names[current_level] = level_name_front + added_key + level_name_back
                                rename_cursor_index += 1

                    if event.key == pygame.K_RETURN:
                        rename = False

                    if event.key == pygame.K_BACKSPACE:
                        if len(level_names[current_level]) > 0:
                            level_name_front = level_names[current_level][:rename_cursor_index - 1]
                            level_name_back = level_names[current_level][rename_cursor_index:]
                            level_names[current_level] = level_name_front + level_name_back  # remove last char
                            rename_cursor_index -= 1

                    # modifying rename cursor index
                    if event.key == pygame.K_LEFT:
                        if rename_cursor_index > 0:
                            rename_cursor_index -= 1
                    if event.key == pygame.K_RIGHT:
                        if rename_cursor_index < len(level_names[current_level]):
                            rename_cursor_index += 1

                if event.key == pygame.K_ESCAPE:
                    level_editor_settings(pause=True)
                    game_state = 'preview level'
                    print(game_state)
                    if target_game_state != '':  # got absolute target state
                        if game_state != target_game_state:  # reach destination
                            running = False
                            break

            if event.type == pygame.MOUSEBUTTONDOWN:
                # print(event.button)
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True

        # filling background colour every frame to refresh prev frame
        # screen.fill(bg_colour)
        screen.blit(bg_img, (0, 0))

        # hide preview button
        if BUTTONS["preview-off"]["button"].run(mouse_pos, left_mouse_down):
            target_game_state = 'level editor'
            running = False
            break

        # play test button
        if BUTTONS["test-play"]["button"].run(mouse_pos, left_mouse_down):
            tile_count_warning, tile_count_rounds, tile_count_dir = save_level(level_names, number_of_tiles,
                                                                               tile_count_warning,
                                                                               tile_count_rounds,
                                                                               tile_count_dir, current_level + 1,
                                                                               map,
                                                                               stacks)
            if not tile_count_warning:
                # store main components of level editor in temp first before altering in play test mode
                temp_map = copy.deepcopy(map)
                temp_stacks = copy.deepcopy(stacks)
                temp_number_of_tiles = copy.deepcopy(number_of_tiles)

                play_level(current_level, play_test=True)

                # return back stored temp editor components into original place
                map = copy.deepcopy(temp_map)
                stacks = copy.deepcopy(temp_stacks)
                number_of_tiles = copy.deepcopy(temp_number_of_tiles)

                game_state = 'preview level'
                print(game_state)
                if target_game_state != '':  # got absolute target state
                    if game_state != target_game_state:  # reach destination
                        running = False
                        break

        # delete level button
        # print(BUTTONS)
        if BUTTONS["delete-level"]["button"].run(mouse_pos, left_mouse_down,
                                           number_of_levels > 1 and not rename and not settings):  # at least 2 levels
            number_of_levels, level_names = remove_level(current_level, number_of_levels, level_names)
            # print(level_names)
            number_of_pages = math.ceil(number_of_levels / (number_of_rows * number_of_cols))
            if level_select_page > number_of_pages - 1:
                level_select_page = number_of_pages - 1
            target_game_state = 'editor level select'
            play_music('intro.mp3')
            running = False
            break  # after removing avoid anything below

        # save button
        if BUTTONS["save"]["button"].run(mouse_pos, left_mouse_down, not rename and not settings):
            tile_count_warning, tile_count_rounds, tile_count_dir = save_level(level_names,
                                                                               number_of_tiles, tile_count_warning,
                                                                               tile_count_rounds, tile_count_dir,
                                                                               current_level + 1, map, stacks)
            if not tile_count_warning:
                ss_tick = SS_TICK_MAX
                take_ss = True

        # reset whole level from fresh button
        if BUTTONS["reset-level"]["button"].run(mouse_pos, left_mouse_down, not rename and not settings):
            map = [copy.deepcopy(MAP_BLANK_LEVEL)]
            stacks = []
            current_layer = 0
            number_of_layers = 1
            layer_disp_list = [2]
            # reset tile count
            number_of_tiles_map = 0
            number_of_tiles_stacks = 0
            number_of_tiles = 0

        # preview tiles
        for layer in range(len(map) - 1, -1, -1):  # from bottom to top
            for i in range(len(map[layer])):  # for each row
                for j in range(len(map[layer][i])):  # for each column
                    if map[layer][i][j] > 0:  # only if grid point contains top left corner of tile
                        if map[layer][i][j] < 100:  # for ordinary layout tiles
                            tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2)
                            tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                            img = tile_images[map[layer][i][j]]
                            tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                            screen.blit(img, tile_rect)
                            # draw transluscent mask for tiles that are not visible
                            if layer > 0:
                                dark_surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
                                dark_surf.set_alpha(128)  # 50 % opacity
                                dark_surf.fill('#2F1443')  # dark purple
                                screen.blit(dark_surf, tile_rect)
                        else:  # stack
                            dir = int(str(map[layer][i][j])[1])  # dir: 1-up, 2-down, 3-left, 4-right
                            stack_id = int(str(map[layer][i][j])[2])

                            for k, stack_tile in enumerate(stacks[stack_id]):
                                # get tile position
                                if dir == 1:  # up
                                    tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2)
                                    tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2) - k * 6
                                elif dir == 2:  # down
                                    tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2)
                                    tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2) + k * 6
                                elif dir == 3:  # left
                                    tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2) - k * 6
                                    tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                                elif dir == 4:  # right
                                    tile_x_pos = MAP_BOUNDARY_RECT.left + j * (TILE_WIDTH / 2) + k * 6
                                    tile_y_pos = MAP_BOUNDARY_RECT.top + i * (TILE_HEIGHT / 2)
                                # draw transluscent mask for tiles that are not visible
                                if k < len(stacks[stack_id]) - 1:  # below top layer
                                    img = tile_images[0]  # blank tile
                                    tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                                    screen.blit(img, tile_rect)
                                    dark_surf = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
                                    dark_surf.set_alpha(128)  # 50 % opacity
                                    dark_surf.fill('#2F1443')  # dark purple
                                    screen.blit(dark_surf, tile_rect)
                                else:
                                    img = tile_images[stack_tile]
                                    tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                                    screen.blit(img, tile_rect)

        # # rename level
        # if rename:  # in rename stage
        #     # draw 50% transparent for whole game screen to blu everything behind
        #     surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        #     surf.fill((0, 0, 0, 200))
        #     screen.blit(surf, (0, 0))
        #
        #     # draw bg
        #     pygame.draw.rect(screen, COLOURS['DARK PURPLE'], RENAME_LEVEL_BG_RECT, border_radius=15)
        #     # pygame.draw.rect(screen, 'white', RENAME_LEVEL_BG_RECT, width=2, border_radius=15)
        #
        #     # draw 50% transparent box
        #     surf = pygame.Surface(LEVEL_NAME_RECT.size, pygame.SRCALPHA)
        #     surf.fill((0, 0, 0, 128))
        #     screen.blit(surf, LEVEL_NAME_RECT.topleft)
        #     # pygame.draw.circle(screen, (255,0,0,50), (20,20), 20)
        #     pygame.draw.rect(screen, (255, 255, 255, 255), LEVEL_NAME_RECT, 2)
        #
        #     if BUTTONS["rename-done"]["button"].run(mouse_pos, left_mouse_down):
        #         rename = False
        #
        #     # display blinking cursor
        #     # reduce cursor tick timer
        #     rename_cursor_tick -= 1
        #     if rename_cursor_tick < 0:  # reset loop
        #         rename_cursor_tick = copy.deepcopy(rename_cursor_tick_max)
        #     # finding where to place cursor
        #     level_name_full_rect = display_text(screen, level_names[current_level], False, TITLE_FONT,
        #                                         font_size=LEVEL_NAME_FONT_SIZE,
        #                                         text_colour="white", return_rect_only=True,
        #                                         center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery+5))
        #     level_name_front_rect = display_text(screen,
        #                                          level_names[current_level][:rename_cursor_index], False, TITLE_FONT,
        #                                          font_size=LEVEL_NAME_FONT_SIZE, text_colour="white",
        #                                          return_rect_only=True,
        #                                          center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery+5))
        #     rename_cursor_x = level_name_full_rect.left + level_name_front_rect.width
        #     if rename_cursor_tick > rename_cursor_tick_max // 2:  # draw cursor only half of the time of tick
        #         pygame.draw.line(screen, rename_cursor_colour,
        #                          (rename_cursor_x, LEVEL_NAME_RECT.centery - CURSOR_HEIGHT / 2),
        #                          (rename_cursor_x, LEVEL_NAME_RECT.centery + CURSOR_HEIGHT / 2), 2)
        #
        #     # display level name
        #     if level_names[current_level] == '':  # haven't typed anything or no name
        #         display_text(screen, 'LEVEL NAME HERE', False, TITLE_FONT, font_size=LEVEL_NAME_FONT_SIZE,
        #                      text_colour="white", alpha=128,
        #                      center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery+5))
        #     else:  # if got something typed
        #         display_text(screen, level_names[current_level], False, TITLE_FONT, font_size=LEVEL_NAME_FONT_SIZE,
        #                      text_colour="white",center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery+5))
        # else:
        #     if not settings:
        #         # draw bg
        #         pygame.draw.rect(screen, COLOURS['DARK PURPLE'], RENAME_LEVEL_BG_RECT, border_radius=15)
        #         # pygame.draw.rect(screen, 'white', RENAME_LEVEL_BG_RECT, width=2, border_radius=15)
        #
        #         if BUTTONS["rename"]["button"].run(mouse_pos, left_mouse_down):
        #             rename = True
        #             # set default start pos of cursor at end of name
        #             rename_cursor_index = len(level_names[current_level])
        #             rename_cursor_tick = copy.deepcopy(rename_cursor_tick_max)
        #
        #         # display level name
        #         print(current_level)
        #         display_text(screen, level_names[current_level], False, TITLE_FONT, font_size=LEVEL_NAME_FONT_SIZE,
        #                      text_colour="white",
        #                      center=(LEVEL_NAME_RECT.centerx, LEVEL_NAME_RECT.centery+5))

        # settings button
        if BUTTONS["settings"]["button"].run(mouse_pos, left_mouse_down, not rename and not settings):
            level_editor_settings(from_preview=True)
            game_state = 'preview level'
            print(game_state)
            if target_game_state != '':  # got absolute target state
                if game_state != target_game_state:  # reach destination
                    running = False
                    break

        # display number of tiles
        # display tile number bg
        display_img(screen, 'tile_count.png', transform_type="scale", size=(30, 30),
                    center=tile_count_pos)
        # display tiles count remaining to be valid or check mark for valid
        if number_of_tiles % 3 > 0:  # got tiles remaining
            tiles_left = 3 - number_of_tiles % 3
            text_colour = (255, 255, 255)
            display_text(screen, f"{tiles_left}", True, None, font_size=25, text_colour=text_colour,
                         center=tile_count_pos)
        else:
            tiles_left = 0
            # display tick to indicate valid
            display_img(screen, 'tick.png', transform_type="scale", size=(15, 15),
                        center=tile_count_pos)
        # tile shaking animation
        if not tile_count_warning:
            if tile_count_pos == tile_count_pos_ori:
                text_colour = (255, 255, 255)
            else:
                # last stretch of shake animation
                if tile_count_dir == 1:  # right
                    tile_count_pos[0] += tile_count_speed
                    if tile_count_pos[0] > tile_count_pos_ori[0]:
                        tile_count_pos = copy.deepcopy(tile_count_pos_ori)
                elif tile_count_dir == -1:  # left
                    tile_count_pos[0] -= tile_count_speed
                    if tile_count_pos[0] < tile_count_pos_ori[0]:
                        tile_count_pos = copy.deepcopy(tile_count_pos_ori)

                # tile count warning popup box
                if tile_count_pos[0] == tile_count_pos_ori[0]:  # finished last step of shaking
                    tile_count_warning_popup()
        else:  # shaking animation for warning
            if tile_count_dir == 1:  # right
                tile_count_pos[0] += tile_count_speed
                if tile_count_pos[0] >= tile_count_upper_bound:
                    tile_count_dir = -1
                    tile_count_rounds += 1
                    if tile_count_rounds >= tile_count_rounds_max:
                        tile_count_warning = False
            elif tile_count_dir == -1:  # left
                tile_count_pos[0] -= tile_count_speed
                if tile_count_pos[0] <= tile_count_lower_bound:
                    tile_count_dir = 1
                    tile_count_rounds += 1
                    if tile_count_rounds >= tile_count_rounds_max:
                        tile_count_warning = False

        # take screenshot of game area for level select pic
        if take_ss:
            window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
            pygame.display.update()  # update all tiles in preview mode for 1 frame to snap pic
            if f'level{current_level + 1}.png' not in os.listdir('resources/pics/levels'):
                # adding screenshot of level into folder + level images
                ss_rect = pygame.Rect((0,0), (MAP_BOUNDARY_RECT.width + 40, MAP_BOUNDARY_RECT.height + 40))
                ss_rect.center = MAP_BOUNDARY_RECT.center
                screenshot_surf = screen.subsurface(ss_rect)
                pygame.image.save(screenshot_surf, f'resources/pics/levels/level{current_level+1}.png')
                img = pygame.image.load(f'resources/pics/levels/level{current_level+1}.png').convert_alpha()
                img = pygame.transform.smoothscale(img, (350 * 0.28, 500 * 0.28))
                level_images.insert(current_level, img)
            else:
                # replacing existing screenshot of level in folder + level images with new one
                ss_rect = pygame.Rect((0, 0), (MAP_BOUNDARY_RECT.width + 40, MAP_BOUNDARY_RECT.height + 40))
                ss_rect.center = MAP_BOUNDARY_RECT.center
                screenshot_surf = screen.subsurface(ss_rect)
                pygame.image.save(screenshot_surf, f'resources/pics/levels/level{current_level + 1}.png')
                img = pygame.image.load(f'resources/pics/levels/level{current_level + 1}.png').convert_alpha()
                img = pygame.transform.smoothscale(img, (350 * 0.28, 500 * 0.28))
                level_images[current_level] = img
            take_ss = False
            if ss_only:  # came from edit level function
                target_game_state = 'level editor'
                running = False  # exit back to edit level function
                break

        # hover messages
        # updating hovering countdown timer
        if sum(pygame.mouse.get_rel()) == 0:  # mouse stationary
            hover_msg_tick -= 1  # countdown timer if mouse is stationary over button
            if hover_msg_tick < 0:
                hover_msg_tick = 0
        else:  # mouse moving
            # reset countdown to display msg
            hover_msg_tick = HOVER_MSG_TICK_START

        # display messages if hovering any of these buttons after a period of time
        if hover_msg_tick == 0:
            if BUTTONS['reset-level']['button'].state == "hovering":
                msg = 'Clear level'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white',
                                        return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0, 0), (msg_rect.width + 10, msg_rect.height + 10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['delete-level']['button'].state == "hovering":
                msg = 'Delete level'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white',
                                        return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0, 0), (msg_rect.width + 10, msg_rect.height + 10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['save']['button'].state == "hovering":
                msg = 'Save'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white',
                                        return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0, 0), (msg_rect.width + 10, msg_rect.height + 10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['settings']['button'].state == "hovering":
                msg = 'Settings'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white',
                                        return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0, 0), (msg_rect.width + 10, msg_rect.height + 10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)
            elif BUTTONS['rename']['button'].state == "hovering":
                msg = 'Rename level'
                msg_rect = display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white',
                                        return_rect_only=True, bottomleft=mouse_pos)
                msg_rect = pygame.Rect((0, 0), (msg_rect.width + 10, msg_rect.height + 10))
                msg_rect.topright = mouse_pos
                pygame.draw.rect(screen, COLOURS['DARK PURPLE'], msg_rect)
                pygame.draw.rect(screen, 'white', msg_rect, width=1)
                display_text(screen, msg, True, None, HOVER_MSG_FONT_SIZE, 'white', center=msg_rect.center)

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()
        clock.tick(60)


def level_editor_settings(pause=False, from_preview=False):
    global music_on, display_gridbox, game_state, target_game_state, tile_count_warning, tile_count_dir, tile_count_rounds, transition, \
        number_of_tiles, map, stacks
    game_state = 'level editor settings'
    print(game_state)

    # draw 50% transparent for whole game screen to blur everything behind once at the start
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 200))
    screen.blit(surf, (0, 0))
    window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
    pygame.display.update()  # update whole game screen

    running = True
    while running:
        left_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                tile_count_warning, tile_count_rounds, tile_count_dir = save_level(level_names, number_of_tiles,
                                                                                   tile_count_warning,
                                                                                   tile_count_rounds,
                                                                                   tile_count_dir,
                                                                                   current_level + 1, map,
                                                                                   stacks)  # save map in case window closes abruptly
                if not tile_count_warning:
                    # store main components of level editor in temp first before being altered in preview by update top layer()
                    temp_map = copy.deepcopy(map)
                    temp_stacks = copy.deepcopy(stacks)
                    temp_number_of_tiles = copy.deepcopy(number_of_tiles)

                    preview_level(ss_only=True)

                    # return back stored temp editor components into original place
                    map = copy.deepcopy(temp_map)
                    stacks = copy.deepcopy(temp_stacks)
                    number_of_tiles = copy.deepcopy(temp_number_of_tiles)

                    pygame.quit()
                    sys.exit()
                else:  # tile count invalid
                    target_game_state = 'level editor'  # after it goes here tile count warning appears
                    running = False
                    break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    target_game_state = ''
                    running = False
                    break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True

        # draw bg
        pygame.draw.rect(screen, settings_bg_colour, SETTINGS_RECT, border_radius=15)
        pygame.draw.rect(screen, 'white', SETTINGS_RECT, width=2, border_radius=15)

        # display settings title
        screen_title = "SETTINGS"
        if pause:
            screen_title = "PAUSED"
        display_text(screen, screen_title, False, TITLE_FONT, font_size=DIALOG_BOX_TITLE_FONT_SIZE, text_colour="white",
                     midtop=(SETTINGS_RECT.centerx, SETTINGS_RECT.top + 20))

        # draw sheep
        display_img(screen, 'sheep3.png', transform_type='scale', size=(611 * 0.18, 512 * 0.18),
                    midbottom=(SETTINGS_RECT.centerx, SETTINGS_RECT.centery - 30))

        # resume editing
        if BUTTONS["resume"]["button"].run(mouse_pos, left_mouse_down):
            target_game_state = ''
            running = False
            break

        # gridlines
        if BUTTONS["settings-checkbox-1"]["button"].run(mouse_pos, left_mouse_down):
            display_gridbox = not display_gridbox
        # draw tick mark
        if display_gridbox:
            display_img(screen, 'tick.png', transform_type="scale", size=(12, 12),
                        center=BUTTONS["settings-checkbox-1"]["pos"])
        display_text(screen, "Show Gridlines", False, 'resources/fonts/2PeasDramaQueen-pgny.ttf', font_size=DIALOG_BOX_CONTENT_FONT_SIZE,
                     text_colour="white",
                     center=(SETTINGS_RECT.centerx, SETTINGS_RECT.centery + 40))

        # music and sounds
        if BUTTONS["settings-checkbox-2"]["button"].run(mouse_pos, left_mouse_down):
            music_on = not music_on
            if music_on:
                resume_music()
            else:
                stop_music()
                # stop_sound()
        # draw tick mark
        if music_on:
            display_img(screen, 'tick.png', transform_type="scale", size=(12, 12),
                        center=BUTTONS["settings-checkbox-2"]["pos"])
        display_text(screen, "Music", False, 'resources/fonts/2PeasDramaQueen-pgny.ttf', font_size=DIALOG_BOX_CONTENT_FONT_SIZE,
                     text_colour="white",
                     center=(SETTINGS_RECT.centerx, SETTINGS_RECT.centery + 80))

        # back to editor level select
        if BUTTONS["back-to-level-select"]["button"].run(mouse_pos, left_mouse_down):
            tile_count_warning, tile_count_rounds, tile_count_dir = \
                save_level(level_names, number_of_tiles,tile_count_warning,tile_count_rounds,tile_count_dir,
                           current_level + 1, map, stacks)  # save map in case window closes abruptly
            if not tile_count_warning:
                # store main components of level editor in temp first before being altered in preview by update top layer()
                temp_map = copy.deepcopy(map)
                temp_stacks = copy.deepcopy(stacks)
                temp_number_of_tiles = copy.deepcopy(number_of_tiles)

                preview_level(ss_only=True)  # take level pic

                # return back stored temp editor components into original place
                map = copy.deepcopy(temp_map)
                stacks = copy.deepcopy(temp_stacks)
                number_of_tiles = copy.deepcopy(temp_number_of_tiles)

                # setting transition
                transition = 4
                sheep_bg_img_rect.left = SCREEN_WIDTH
            else:  # tile count invalid
                if from_preview:
                    target_game_state = 'preview level'
                else:
                    target_game_state = 'level editor'  # after it goes here tile count warning appears
                running = False
                break
        if transition == 4 and sheep_bg_img_rect.centerx < SCREEN_WIDTH / 2:  # center of image pass center of screen
            target_game_state = "editor level select"
            play_music('intro.mp3')
            running = False
            break


        # back to main menu
        if BUTTONS["back-to-main-menu"]["button"].run(mouse_pos, left_mouse_down):
            tile_count_warning, tile_count_rounds, tile_count_dir = save_level(level_names, number_of_tiles,
                                                                               tile_count_warning,
                                                                               tile_count_rounds,
                                                                               tile_count_dir,
                                                                               current_level + 1, map,
                                                                               stacks)  # save map in case window closes abruptly
            if not tile_count_warning:
                # store main components of level editor in temp first before being altered in preview by update top layer()
                temp_map = copy.deepcopy(map)
                temp_stacks = copy.deepcopy(stacks)
                temp_number_of_tiles = copy.deepcopy(number_of_tiles)

                preview_level(ss_only=True)

                # return back stored temp editor components into original place
                map = copy.deepcopy(temp_map)
                stacks = copy.deepcopy(temp_stacks)
                number_of_tiles = copy.deepcopy(temp_number_of_tiles)

                # set transition
                transition = 2
                main_menu_img_rect.right = 0
            else:  # tile count invalid
                if from_preview:
                    target_game_state = 'preview level'
                else:
                    target_game_state = 'level editor'  # after it goes here tile count warning appears
                running = False
                break

        if transition == 2 and main_menu_img_rect.right == SCREEN_WIDTH:
            transition = 0
            screen.blit(main_menu_img, main_menu_img_rect)
            target_game_state = "main menu"
            play_music('intro.mp3')
            running = False
            break

        display_transition()

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()
        clock.tick(60)


def play_settings(pause=False, play_test=False):
    global map, stacks, number_of_tiles, collected_tiles, play_state, left_mouse_down_pos, left_mouse_down, \
        tile_count_warning, tile_count_dir, tile_count_dir, tile_count_rounds, settings, \
        music_on, display_gridbox, game_state, target_game_state, \
        map_undo_list, stacks_undo_list, collected_tiles_undo_list, undo_used, extra_collected_tiles, extend_used, shuffle_used, \
        transition, progress, progress_sheep_x, progress_sheep_x_target, extra_collected_tiles_undo_list, map_prev
    game_state = 'play settings'
    print(game_state)

    # draw 50% transparent for whole game screen to blur everything behind once at the start
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 200))
    screen.blit(surf, (0, 0))
    window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
    pygame.display.update()  # update whole game screen

    running = True
    while running:
        left_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    target_game_state = ''
                    running = False
                    break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True

        # draw bg
        pygame.draw.rect(screen, settings_bg_colour, SETTINGS_RECT, border_radius=15)
        pygame.draw.rect(screen, 'white', SETTINGS_RECT, width=2, border_radius=15)

        # display settings title
        screen_title = "SETTINGS"
        if pause:
            screen_title = "PAUSED"
        display_text(screen, screen_title, False, TITLE_FONT, font_size=DIALOG_BOX_TITLE_FONT_SIZE, text_colour="white",
                     midtop=(SETTINGS_RECT.centerx, SETTINGS_RECT.top + 20))

        # draw sheep
        display_img(screen, 'sheep3.png', transform_type='scale', size=(611 * 0.18, 512 * 0.18),
                    midbottom=(SETTINGS_RECT.centerx, SETTINGS_RECT.centery - 30))

        # resume editing
        if BUTTONS["resume"]["button"].run(mouse_pos, left_mouse_down):
            target_game_state = ''
            running = False
            break

        # give up and restart
        if BUTTONS["give-up"]["button"].run(mouse_pos, left_mouse_down):
            map, stacks, number_of_tiles, collected_tiles, play_state, left_mouse_down_pos, left_mouse_down, \
            tile_count_warning, tile_count_dir, tile_count_dir, tile_count_rounds, settings, undo_used,\
            map_undo_list, stacks_undo_list, collected_tiles_undo_list, extra_collected_tiles, extend_used, shuffle_used, \
            progress, progress_sheep_x, progress_sheep_x_target, extra_collected_tiles_undo_list, map_prev = \
                restart_level(current_level, MAX_NUM_OF_TYPES)
            play_music('in_game.mp3')
            target_game_state = "play level"
            running = False
            break

        # music and sounds
        if BUTTONS["settings-checkbox-2"]["button"].run(mouse_pos, left_mouse_down):
            music_on = not music_on
            if music_on:
                resume_music()
            else:
                stop_music()
        # draw tick mark
        if music_on:
            display_img(screen, 'tick.png', transform_type="scale", size=(12, 12),
                        center=BUTTONS["settings-checkbox-2"]["pos"])
        display_text(screen, "Music", False, 'resources/fonts/2PeasDramaQueen-pgny.ttf', font_size=DIALOG_BOX_CONTENT_FONT_SIZE,
                     text_colour="white",
                     center=(SETTINGS_RECT.centerx, SETTINGS_RECT.centery + 80))

        # back to play level select
        if BUTTONS["back-to-level-select"]["button"].run(mouse_pos, left_mouse_down):
            # setting transition
            transition = 4
            sheep_bg_img_rect.left = SCREEN_WIDTH
        if transition == 4 and sheep_bg_img_rect.centerx < SCREEN_WIDTH / 2:  # center of image pass center of screen
            if play_test:
                target_game_state = "editor level select"
            else:
                target_game_state = "play level select"
            play_music('intro.mp3')
            running = False
            break

        # back to main menu
        if BUTTONS["back-to-main-menu"]["button"].run(mouse_pos, left_mouse_down):
            # set transition
            transition = 2
            main_menu_img_rect.right = 0
        if transition == 2 and main_menu_img_rect.right == SCREEN_WIDTH:
            transition = 0
            screen.blit(main_menu_img, main_menu_img_rect)
            target_game_state = "main menu"
            play_music('intro.mp3')
            running = False
            break

        display_transition()

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()
        clock.tick(60)


def shuffle():
    tiles = []
    tiles_pos_old = []
    tiles_coord_old = []
    for layer_id, layer in enumerate(map):
        for row_id, row in enumerate(layer):
            for col_id, tile in enumerate(row):
                if tile > 0:  # legit tile
                    if tile < 100:  # single tile, not stack
                        tiles.append(tile)
                        tiles_pos_old.append([layer_id, row_id, col_id])
                        tile_x_coord = MAP_BOUNDARY_RECT.x + col_id * (TILE_WIDTH / 2)
                        tile_y_coord = MAP_BOUNDARY_RECT.y + row_id * (TILE_HEIGHT / 2)
                        tiles_coord_old.append([tile_x_coord, tile_y_coord])
                    else:  # stack
                        stack_str = str(tile)  # cvt to str so easier to extract individual nums, ex: '103'
                        stack_dir = int(stack_str[1])
                        stack_id = int(stack_str[2])
                        stack_base_x = MAP_BOUNDARY_RECT.x + col_id * (TILE_WIDTH / 2)
                        stack_base_y = MAP_BOUNDARY_RECT.y + row_id * (TILE_HEIGHT / 2)

                        # add tiles within stacks into tiles list and pos list, not the 3 digit stack num
                        for stack_tile_id, stack_tile in reversed(list(enumerate(stacks[stack_id]))):
                            tiles.append(stack_tile)
                            tiles_pos_old.append([int(stack_str[0]), stack_dir, stack_id, stack_tile_id])

                            if stack_dir == 1:  # up
                                tile_x_coord = stack_base_x
                                tile_y_coord = stack_base_y - stack_tile_id * 6
                            elif stack_dir == 2:  # down
                                tile_x_coord = stack_base_x
                                tile_y_coord = stack_base_y + stack_tile_id * 6
                            elif stack_dir == 3:  # left
                                tile_x_coord = stack_base_x - stack_tile_id * 6
                                tile_y_coord = stack_base_y
                            elif stack_dir == 4:  # right
                                tile_x_coord = stack_base_x + stack_tile_id * 6
                                tile_y_coord = stack_base_y

                            tiles_coord_old.append([tile_x_coord, tile_y_coord])
    # print(f'tiles: {tiles}')

    # shuffle ids
    tiles_id = list(range(len(tiles)))
    # print(f'tiles id old: {tiles_id}')
    random.shuffle(tiles_id)
    # print(f'tiles id new: {tiles_id}')

    # generate new tile grid pos and coords from shuffled ids
    tiles_pos_new = []
    tiles_coord_new = []
    for index in tiles_id:
        tiles_pos_new.append(copy.deepcopy(tiles_pos_old[index]))
        tiles_coord_new.append(copy.deepcopy(tiles_coord_old[index]))

    # print(f'tiles pos old: {tiles_pos_old}')
    # print(f'tiles pos new: {tiles_pos_new}')
    # print(f'tiles coord old: {tiles_coord_old}')
    # print(f'tiles coord new: {tiles_coord_new}')

    # determine animation velocities of each tile
    tile_velocities = []
    NUMBER_OF_FRAMES = 60*3  # 60 fps * 3s duration
    for index, _ in enumerate(tiles_coord_old):
        tile_x_vel = round((tiles_coord_new[index][0] - tiles_coord_old[index][0])/NUMBER_OF_FRAMES, 6)
        tile_y_vel = round((tiles_coord_new[index][1] - tiles_coord_old[index][1])/NUMBER_OF_FRAMES, 6)
        tile_velocities.append([tile_x_vel, tile_y_vel])

    # print(f'tile velocities: {tile_velocities}')


    # generate shuffled map and stacks
    for index, tile in enumerate(tiles):
        if len(tiles_pos_new[index]) == 3:  # single tile  [0,0,2]
            map[tiles_pos_new[index][0]][tiles_pos_new[index][1]][tiles_pos_new[index][2]] = tile
        elif len(tiles_pos_new[index]) == 4:  # stacks  [1,0,4,2]
            stacks[tiles_pos_new[index][2]][tiles_pos_new[index][3]] = tile

    shuffle_tick = NUMBER_OF_FRAMES
    tiles_coord = copy.deepcopy(tiles_coord_old)  # constantly changing tile coords from old to new
    while shuffle_tick > 0:
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # filling background colour every frame to refresh prev frame
        screen.blit(bg_img, (0,0))

        # drawing each remaining tile on the game screen
        for index in range(len(tiles) - 1, -1, -1):  # draw tiles from bottom to top
            # update tile coordinates for animation movement
            tiles_coord[index][0] += tile_velocities[index][0]  # add velocity x comp
            tiles_coord[index][1] += tile_velocities[index][1]  # add velocity y comp

            # draw tile
            img = tile_images[tiles[index]]
            tile_rect = img.get_rect(topleft=(tiles_coord[index][0], tiles_coord[index][1]))
            screen.blit(img, tile_rect)

        # countdown shuffle tick to end loop
        shuffle_tick -= 1

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update(MAP_BOUNDARY_RECT)  # don't update any areas outside map tiles
        clock.tick(60)

    # filling background colour every frame to refresh prev frame
    screen.blit(bg_img, (0, 0))

    # drawing each remaining tile on the game screen
    for index in range(len(tiles) - 1, -1, -1):  # draw tiles from bottom to top
        # update tile coordinates for animation movement
        tiles_coord[index][0] += tile_velocities[index][0]  # add velocity x comp
        tiles_coord[index][1] += tile_velocities[index][1]  # add velocity y comp

        # draw tile
        img = tile_images[tiles[index]]
        tile_rect = img.get_rect(topleft=(tiles_coord[index][0], tiles_coord[index][1]))
        screen.blit(img, tile_rect)



def win_screen(play_test):
    state = 1
    WIN_SCREEN_TOP_RECT = pygame.Rect((0, 0), (300, 150))
    WIN_SCREEN_TOP_RECT.midbottom = (SCREEN_WIDTH/2, -10)
    STAR_START_SIZE = 5
    STAR_END_SIZE = 60
    STAR_SIZE_INCREMENT = 2
    star_sizes = [STAR_START_SIZE,STAR_START_SIZE,STAR_START_SIZE]
    SHEEP_START_SIZE = 5
    SHEEP_END_SIZE = 350
    SHEEP_SIZE_INCREMENT = 20
    sheep_size = SHEEP_START_SIZE
    sheep_img = pygame.image.load(f'resources/pics/win_sheep.png').convert_alpha()
    WIN_SCREEN_BOTTOM_RECT = pygame.Rect((0,0), (380, 65))
    WIN_SCREEN_BOTTOM_RECT.midtop = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + SHEEP_END_SIZE/2 -30)
    RETRY_START_HEIGHT = 5
    RETRY_END_HEIGHT = 50
    RETRY_HEIGHT_INCREMENT = 2
    retry_height = RETRY_START_HEIGHT
    retry_img = pygame.image.load('resources/pics/buttons/retry_1.png').convert_alpha()
    BTLS_START_HEIGHT = 5
    BTLS_END_HEIGHT = 50
    BTLS_HEIGHT_INCREMENT = 2
    btls_height = BTLS_START_HEIGHT
    btls_img = pygame.image.load('resources/pics/buttons/back-to-level-select_1.png').convert_alpha()
    BTE_START_HEIGHT = 5
    BTE_END_HEIGHT = 50
    BTE_HEIGHT_INCREMENT = 2
    bte_height = BTE_START_HEIGHT
    bte_img = pygame.image.load('resources/pics/buttons/back-to-editing_1.png').convert_alpha()

    global map, stacks, number_of_tiles, collected_tiles, play_state, left_mouse_down_pos, left_mouse_down, \
                tile_count_warning, tile_count_dir, tile_count_dir, tile_count_rounds, settings, undo_used, \
                map_undo_list, stacks_undo_list, collected_tiles_undo_list, extra_collected_tiles, extend_used, shuffle_used, \
                target_game_state, progress, progress_sheep_x, progress_sheep_x_target

    play_music('win.wav')

    running = True
    while running:
        left_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # print(event.button)
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True

        # filling background colour every frame to refresh prev frame
        screen.blit(bg_img, (0,0))

        # display message in box
        if state >= 1:
            if WIN_SCREEN_TOP_RECT.top < 60:  # haven't reached final state
                WIN_SCREEN_TOP_RECT.y += 10  # move message box downwards
            else:  # ady reached final pos
                if state == 1:
                    state = 2  # go onto next state

            # draw top message box
            # draw box
            pygame.draw.rect(screen, COLOURS['DARK PURPLE'], WIN_SCREEN_TOP_RECT, border_radius=8)
            # pygame.draw.rect(screen, 'white', WIN_SCREEN_TOP_RECT, width=2, border_radius=8)
            # draw text
            display_text(screen, "CONGRATULATIONS!", False, TITLE_FONT, 28, "white",
                         center=(WIN_SCREEN_TOP_RECT.centerx, WIN_SCREEN_TOP_RECT.top + 40))
            display_text(screen, "                   !", False, 'resources/fonts/2PeasDramaQueen-pgny.ttf', 45, "white",
                         center=(WIN_SCREEN_TOP_RECT.centerx, WIN_SCREEN_TOP_RECT.top + 30))

        # draw left star
        if state >= 2:
            if star_sizes[0] < STAR_END_SIZE:  # haven't reached final size
                star_sizes[0] += STAR_SIZE_INCREMENT
            else:  # ady reached final size
                if state == 2:
                    state = 3

            display_img(screen, 'star.png', transform_type='scale', size=(star_sizes[0],star_sizes[0]),
                        midbottom=(WIN_SCREEN_TOP_RECT.centerx-70, WIN_SCREEN_TOP_RECT.bottom-20))

        # draw middle star
        if state >= 3:
            if star_sizes[1] < STAR_END_SIZE:  # haven't reached final size
                star_sizes[1] += STAR_SIZE_INCREMENT
            else:  # ady reached final size
                if state == 3:
                    state = 4

            display_img(screen, 'star.png', transform_type='scale', size=(star_sizes[1],star_sizes[1]),
                        midbottom=(WIN_SCREEN_TOP_RECT.centerx, WIN_SCREEN_TOP_RECT.bottom-20))

        # draw right star
        if state >= 4:
            if star_sizes[2] < STAR_END_SIZE:  # haven't reached final size
                star_sizes[2] += STAR_SIZE_INCREMENT
            else:  # ady reached final size
                if state == 4:
                    state = 5

            display_img(screen, 'star.png', transform_type='scale', size=(star_sizes[2], star_sizes[2]),
                        midbottom=(WIN_SCREEN_TOP_RECT.centerx+70, WIN_SCREEN_TOP_RECT.bottom - 20))

        # draw sheep
        if state >= 5:
            if sheep_size < SHEEP_END_SIZE:  # haven't reached final size
                sheep_size += SHEEP_SIZE_INCREMENT
            else:  # ady reached final size
                if state == 5:
                    state = 6

            sheep_img_scaled = pygame.transform.smoothscale(sheep_img, (sheep_size, sheep_size))
            sheep_img_rect = sheep_img_scaled.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(sheep_img_scaled, sheep_img_rect)
            # display_img(screen, 'win_sheep.png', transform_type='scale', size=(sheep_size, sheep_size),
            #             center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

        # draw bottom message
        if state >= 6:
            if state == 6:
                state = 7

            # draw top message box
            # draw box
            pygame.draw.rect(screen, COLOURS['DARK PURPLE'], WIN_SCREEN_BOTTOM_RECT, border_radius=8)
            # draw message
            display_text(screen, "You have an IQ of 999 and beat 99.99%", False,
                         TITLE_FONT, 20, "white",
                         midtop=(WIN_SCREEN_BOTTOM_RECT.centerx, WIN_SCREEN_BOTTOM_RECT.top + 10))
            display_text(screen, "                                           %", False, 'resources/fonts/2PeasDramaQueen-pgny.ttf',
                         30, "white", midtop=(WIN_SCREEN_BOTTOM_RECT.centerx, WIN_SCREEN_BOTTOM_RECT.top-5))
            display_text(screen, "of players in the world!", False,
                         TITLE_FONT, 20, "white",
                         midtop=(WIN_SCREEN_BOTTOM_RECT.centerx, WIN_SCREEN_BOTTOM_RECT.top + 35))
            display_text(screen, "                          !", False, 'resources/fonts/2PeasDramaQueen-pgny.ttf',
                         30, "white", midtop=(WIN_SCREEN_BOTTOM_RECT.centerx, WIN_SCREEN_BOTTOM_RECT.top + 22))

        # draw button images
        if state >= 7:
            if retry_height < RETRY_END_HEIGHT:  # haven't reached final size
                retry_height += RETRY_HEIGHT_INCREMENT
                if play_test:
                    bte_height += BTE_HEIGHT_INCREMENT
                else:
                    btls_height += BTLS_HEIGHT_INCREMENT
            else:  # reached final size
                if state == 7:
                    state = 8

            # retry image
            retry_img_scaled = pygame.transform.smoothscale(retry_img, ((retry_img.get_width()/retry_img.get_height())*retry_height, retry_height))
            retry_img_rect = retry_img_scaled.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT-120))
            screen.blit(retry_img_scaled, retry_img_rect)

            if play_test:
                # bte image
                bte_img_scaled = pygame.transform.smoothscale(bte_img, ((bte_img.get_width() / bte_img.get_height()) * bte_height, bte_height))
                bte_img_rect = bte_img_scaled.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60))
                screen.blit(bte_img_scaled, bte_img_rect)
            else:
                # btls image
                btls_img_scaled = pygame.transform.smoothscale(btls_img, ((btls_img.get_width() / btls_img.get_height()) * btls_height, btls_height))
                btls_img_rect = btls_img_scaled.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60))
                screen.blit(btls_img_scaled, btls_img_rect)

        # draw buttons
        if state >= 8:
            # retry
            if BUTTONS["end-retry"]["button"].run(mouse_pos, left_mouse_down):
                map, stacks, number_of_tiles, collected_tiles, play_state, left_mouse_down_pos, left_mouse_down, \
                tile_count_warning, tile_count_dir, tile_count_dir, tile_count_rounds, settings, undo_used, \
                map_undo_list, stacks_undo_list, collected_tiles_undo_list, extra_collected_tiles, extend_used, shuffle_used, \
                progress, progress_sheep_x, progress_sheep_x_target, extra_collected_tiles_undo_list, map_prev = \
                    restart_level(current_level, MAX_NUM_OF_TYPES)
                play_music('in_game.mp3')
                target_game_state = "play level"
                running = False
                break

            if play_test:
                # back to editing
                if BUTTONS["end-back-to-editing"]["button"].run(mouse_pos, left_mouse_down):
                    target_game_state = "level editor"
                    play_music('in_game.mp3')
                    running = False
                    break
            else:
                # back to play level select
                if BUTTONS["end-back-to-level-select"]["button"].run(mouse_pos, left_mouse_down):
                    target_game_state = "play level select"
                    play_music('intro.mp3')
                    running = False
                    break

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()
        clock.tick(60)


def lose_screen(play_test):
    state = 1
    LOSE_SCREEN_TOP_RECT = pygame.Rect((0, 0), (320, 120))
    LOSE_SCREEN_TOP_RECT.midbottom = (SCREEN_WIDTH/2, -10)
    SHEEP_START_SIZE = 5
    SHEEP_END_SIZE = 350
    SHEEP_SIZE_INCREMENT = 20
    sheep_size = SHEEP_START_SIZE
    sheep_img = pygame.image.load(f'resources/pics/lose_sheep_1.png').convert_alpha()
    LOSE_SCREEN_BOTTOM_RECT = pygame.Rect((0,0), (380, 65))
    LOSE_SCREEN_BOTTOM_RECT.midtop = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + SHEEP_END_SIZE/2 -30)
    cake_x = SCREEN_WIDTH + 10
    CAKE_X_END = SCREEN_WIDTH/2 + 100
    sheep_img_2 = pygame.image.load(f'resources/pics/lose_sheep_2.png').convert_alpha()
    sheep_img_2 = pygame.transform.scale(sheep_img_2, (SHEEP_END_SIZE, SHEEP_END_SIZE))
    sheep_img_2_rect = sheep_img_2.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    RETRY_START_HEIGHT = 5
    RETRY_END_HEIGHT = 50
    RETRY_HEIGHT_INCREMENT = 2
    retry_height = RETRY_START_HEIGHT
    retry_img = pygame.image.load('resources/pics/buttons/retry_1.png').convert_alpha()
    BTLS_START_HEIGHT = 5
    BTLS_END_HEIGHT = 50
    BTLS_HEIGHT_INCREMENT = 2
    btls_height = BTLS_START_HEIGHT
    btls_img = pygame.image.load('resources/pics/buttons/back-to-level-select_1.png').convert_alpha()
    tick_1 = 60*3  # after bottom message appears, wait for 3s for cake to slide in
    tick_2 = 60*2  # after cake slides in, wait for 2s for sheep to be happy
    BTE_START_HEIGHT = 5
    BTE_END_HEIGHT = 50
    BTE_HEIGHT_INCREMENT = 2
    bte_height = BTE_START_HEIGHT
    bte_img = pygame.image.load('resources/pics/buttons/back-to-editing_1.png').convert_alpha()

    global map, stacks, number_of_tiles, collected_tiles, play_state, left_mouse_down_pos, left_mouse_down, \
                tile_count_warning, tile_count_dir, tile_count_dir, tile_count_rounds, settings, undo_used, \
                map_undo_list, stacks_undo_list, collected_tiles_undo_list, extra_collected_tiles, extend_used, shuffle_used, \
                target_game_state, progress, progress_sheep_x, progress_sheep_x_target

    play_music('lose.wav')

    running = True
    while running:
        left_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # print(event.button)
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True

        # filling background colour every frame to refresh prev frame
        screen.blit(bg_img, (0,0))

        # display message in box
        if state >= 1:
            if LOSE_SCREEN_TOP_RECT.top < 60:  # haven't reached final state
                LOSE_SCREEN_TOP_RECT.y += 10  # move message box downwards
            else:  # ady reached final pos
                if state == 1:
                    state = 2  # go onto next state

            # draw top message box
            # draw box
            pygame.draw.rect(screen, COLOURS['DARK PURPLE'], LOSE_SCREEN_TOP_RECT, border_radius=8)
            # pygame.draw.rect(screen, 'white', WIN_SCREEN_TOP_RECT, width=2, border_radius=8)
            # draw text
            display_text(screen, "GAME OVER!", False, TITLE_FONT, 50, "white",
                         center=(LOSE_SCREEN_TOP_RECT.centerx, LOSE_SCREEN_TOP_RECT.top + 50))
            display_text(screen, "              !", False, 'resources/fonts/2PeasDramaQueen-pgny.ttf', 70, "white",
                         center=(LOSE_SCREEN_TOP_RECT.centerx, LOSE_SCREEN_TOP_RECT.top + 33))
            display_text(screen, "TOO BAA-AA-AAD", False, TITLE_FONT, 35, "white",
                         center=(LOSE_SCREEN_TOP_RECT.centerx, LOSE_SCREEN_TOP_RECT.top + 90))

        # draw sad sheep
        if state >= 2:
            if sheep_size < SHEEP_END_SIZE:  # haven't reached final size
                sheep_size += SHEEP_SIZE_INCREMENT
                if sheep_size > SHEEP_END_SIZE:
                    sheep_size = SHEEP_END_SIZE
            else:  # ady reached final size
                if state == 2:
                    state = 3

            sheep_img_scaled = pygame.transform.smoothscale(sheep_img, (sheep_size, sheep_size))
            sheep_img_rect = sheep_img_scaled.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(sheep_img_scaled, sheep_img_rect)

        # draw happy sheep
        if state >= 9:
            screen.blit(sheep_img_2, sheep_img_2_rect)

        # draw bottom message
        if state >= 3:
            # draw top message box
            # draw box
            pygame.draw.rect(screen, COLOURS['DARK PURPLE'], LOSE_SCREEN_BOTTOM_RECT, border_radius=8)
            # draw message
            display_text(screen, "Not to worry, here is some leftover", False,
                         TITLE_FONT, 20, "white",
                         midtop=(LOSE_SCREEN_BOTTOM_RECT.centerx, LOSE_SCREEN_BOTTOM_RECT.top + 10))
            display_text(screen, "cake for you to cheer you up", False,
                         TITLE_FONT, 20, "white",
                         midtop=(LOSE_SCREEN_BOTTOM_RECT.centerx, LOSE_SCREEN_BOTTOM_RECT.top + 35))

            if state == 3:
                state = 4

        # draw button images
        if state >= 4:
            if retry_height < RETRY_END_HEIGHT:  # haven't reached final size
                retry_height += RETRY_HEIGHT_INCREMENT
                if play_test:
                    bte_height += BTE_HEIGHT_INCREMENT
                else:
                    btls_height += BTLS_HEIGHT_INCREMENT
            else:  # reached final size
                if state == 4:
                    state = 5

            # retry image
            retry_img_scaled = pygame.transform.smoothscale(retry_img, ((retry_img.get_width()/retry_img.get_height())*retry_height, retry_height))
            retry_img_rect = retry_img_scaled.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT-120))
            screen.blit(retry_img_scaled, retry_img_rect)

            if play_test:
                # bte image
                bte_img_scaled = pygame.transform.smoothscale(bte_img, ((bte_img.get_width() / bte_img.get_height()) * bte_height, bte_height))
                bte_img_rect = bte_img_scaled.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60))
                screen.blit(bte_img_scaled, bte_img_rect)
            else:
                # btls image
                btls_img_scaled = pygame.transform.smoothscale(btls_img, ((btls_img.get_width() / btls_img.get_height()) * btls_height, btls_height))
                btls_img_rect = btls_img_scaled.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60))
                screen.blit(btls_img_scaled, btls_img_rect)

        # draw buttons
        if state >= 5:
            # retry
            if BUTTONS["end-retry"]["button"].run(mouse_pos, left_mouse_down):
                map, stacks, number_of_tiles, collected_tiles, play_state, left_mouse_down_pos, left_mouse_down, \
                tile_count_warning, tile_count_dir, tile_count_dir, tile_count_rounds, settings, undo_used, \
                map_undo_list, stacks_undo_list, collected_tiles_undo_list, extra_collected_tiles, extend_used, shuffle_used, \
                progress, progress_sheep_x, progress_sheep_x_target, extra_collected_tiles_undo_list, map_prev = \
                    restart_level(current_level, MAX_NUM_OF_TYPES)
                play_music('in_game.mp3')
                target_game_state = "play level"
                running = False
                break

            if play_test:
                # back to editing
                if BUTTONS["end-back-to-editing"]["button"].run(mouse_pos, left_mouse_down):
                    target_game_state = "level editor"
                    play_music('in_game.mp3')
                    running = False
                    break
            else:
                # back to play level select
                if BUTTONS["end-back-to-level-select"]["button"].run(mouse_pos, left_mouse_down):
                    target_game_state = "play level select"
                    play_music('intro.mp3')
                    running = False
                    break

            if state == 5:
                state = 6

        # timer 1 countdown
        if state == 6:
            if tick_1 > 0:
                tick_1 -= 1
            else:
                state = 7

        # draw cake sliding in
        if state >= 7:
            if cake_x > CAKE_X_END:  # haven't reached final state
                cake_x -= 5  # move message box downwards
            else:  # ady reached final pos
                if state == 7:
                    state = 8  # go onto next state

            # draw cake
            display_img(screen, 'cake.png', transform_type='scale', size=(40, 40),
                        bottomleft=(cake_x, LOSE_SCREEN_BOTTOM_RECT.top - 10))

        # timer 2 countdown
        if state == 8:
            if tick_2 > 0:
                tick_2 -= 1
            else:
                state = 9



        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()
        clock.tick(60)


def tile_count_warning_popup():
    global target_game_state

    running = True
    while running:
        left_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # print(event.button)
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down = True

        # draw bg rect
        pygame.draw.rect(screen, COLOURS['DARK PURPLE'], TILE_COUNT_WARNING_RECT, border_radius=15)
        # pygame.draw.rect(screen, COLOURS['DARK PURPLE'], TILE_COUNT_WARNING_RECT, border_radius=15)

        rect1 = display_text(screen, f"Number of tiles is invalid.", False, WORD_FONT, 35, "white",
                             midtop=(TILE_COUNT_WARNING_RECT.centerx, TILE_COUNT_WARNING_RECT.top + 10))
        rect2 = display_text(screen, f"Please add {3 - number_of_tiles % 3} more tiles", False, WORD_FONT, 35, "white",
                             midtop=(rect1.centerx, rect1.centery + 10))
        rect3 = display_text(screen, f"to your level.", False, WORD_FONT, 35,
                             "white", midtop=(rect2.centerx, rect2.centery + 10))

        # draw okay button
        if BUTTONS["okay"]["button"].run(mouse_pos, left_mouse_down):
            target_game_state = ""
            # play_music('intro.mp3')
            running = False
            break

        window.blit(screen, (0, 0))  # stick the alpha channel surface onto game window
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    # pygame.time.delay(3000)
    main_menu()

















import pygame, sys  # file > settings > Project:SpaceInvader > Project Interpreter > "+" > Pygame > Install package
from pygame.locals import *  # import some global constants from pygame lib
import random
import math
import numpy as np
from modules import *
from config import *

# initialize pygame
pygame.init()
clock = pygame.time.Clock()

# setup game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def play(current_level):
    ############################ CHANGE THIS ###################################
    # tile map, first layer is top layer
    # stacked tiles, left to right -> bottom to top, dir: 1-up, 2-down, 3-left, 4-right
    map, stacks, _, _, _, _ = \
        load_level_complete(current_level)
    number_of_tiles_map, number_of_tiles_stacks, number_of_tiles = update_number_of_tiles(map, stacks, return_map_and_stacks=True)
    ###########################################################################################

    # TILE MAP RANDOM PIC GENERATOR BASED ON INPUT
    ##################################### CHANGE THIS ###################################
    number_of_types = int(number_of_tiles/3)
    if number_of_types > MAX_NUM_OF_TYPES:
        number_of_types = MAX_NUM_OF_TYPES
    tile_types = list(range(1,number_of_types+1))  # list of pics to be used in map
    #######################################################################################
    if len(tile_types) < int(number_of_tiles/3):  # number of tile pics not enough to fill all sets
        # 1. add sets to fit the max no of sets
        sets_to_add = int(number_of_tiles/3) - len(tile_types)
        for i in range(sets_to_add):
            tile_types.append(random.choice(tile_types))
    # 2. duplicate the array to fit number of tiles
    tile_types = tile_types*3
    # 3. shuffle the tile types 5 times
    for i in range(5):
        random.shuffle(tile_types)
    print(tile_types)

    counter = 0
    complete = False  # completed generating for map, not stacks
    # 4. fill up map
    for layer,_ in enumerate(map):
        for row,_ in enumerate(map[layer]):
            for col,_ in enumerate(map[layer][row]):
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
    for stack,_ in enumerate(stacks):
        for tile,_ in enumerate(stacks[stack]):
            stacks[stack][tile] = tile_types[counter]
            counter += 1

    # 6. bring any exposed tiles from bottom layers of tile map that have been missed out to the top layer
    map = update_top_layer(map)
    # print(tile_map)

    # initialize variables
    collected_tiles = []  # [1,3,2,4,3,4,2]  type
    wait_frame = 0
    game_state = "playing"  # playing, game won, game lost
    left_mouse_down_pos = (0,0)

    # game loop
    while True:
        left_mouse_down_pos = (0,0)
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # only if left mouse button clicked
                    left_mouse_down_pos = event.pos  # update mouse position

        # mouse testing functions
        # print(pygame.mouse.get_focused())
        # print(pygame.mouse.get_pos())
        # print(pygame.mouse.get_pressed()[0]) # left click

        # filling background colour every frame to refresh prev frame
        screen.fill(bg_colour)

        if game_state == "playing":
            # drawing each remaining tile on the game screen
            for layer in range(len(map)-1,-1,-1):  # from bottom to top
                for i in range(len(map[layer])):  # for each row
                    for j in range(len(map[layer][i])):  # for each column
                        if map[layer][i][j] > 0:  # only if grid point contains top left corner of tile
                            if map[layer][i][j] < 100: # for ordinary layout tiles
                                img_name = str(map[layer][i][j]) + '.png'
                                if layer > 0:  # not visible tiles
                                    img_name = str(map[layer][i][j]) + '_dark.png'  # dark version
                                img = pygame.image.load('pics/' + img_name)
                                tile_x_pos = 45 + j * (TILE_WIDTH / 2)
                                tile_y_pos = 100 + i * (TILE_HEIGHT / 2)
                                tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                                screen.blit(img, tile_rect)
                            else:  # stack
                                dir = math.floor(map[layer][i][j]%100/10)   # dir: 1-up, 2-down, 3-left, 4-right
                                stack_id = (map[layer][i][j]%100) - dir*10

                                for k, stack_tile in enumerate(stacks[stack_id]):
                                    img_name = str(stack_tile) + '.png'
                                    if k < len(stacks[stack_id])-1:  # below top layer
                                        img_name = 'tile_dark.png'  # dark version
                                    img = pygame.image.load('pics/' + img_name)
                                    if dir == 1:  # up
                                        tile_x_pos = 45 + j * (TILE_WIDTH / 2)
                                        tile_y_pos = 100 + i * (TILE_HEIGHT / 2) - k * 6
                                    elif dir == 2:  # down
                                        tile_x_pos = 45 + j * (TILE_WIDTH / 2)
                                        tile_y_pos = 100 + i * (TILE_HEIGHT / 2) + k * 6
                                    elif dir == 3:  # left
                                        tile_x_pos = 45 + j * (TILE_WIDTH / 2) - k * 6
                                        tile_y_pos = 100 + i * (TILE_HEIGHT / 2)
                                    elif dir == 4:  # right
                                        tile_x_pos = 45 + j * (TILE_WIDTH / 2) + k * 6
                                        tile_y_pos = 100 + i * (TILE_HEIGHT / 2)
                                    tile_rect = img.get_rect(topleft=(tile_x_pos, tile_y_pos))
                                    screen.blit(img, tile_rect)

                            # game mechanics
                            if layer == 0:  # only for top layer (visible tiles)
                                # remove tile from top if clicked on and move to collected tiles(items bar) list only if tile is on top layer
                                if tile_rect.collidepoint(left_mouse_down_pos):
                                    if map[layer][i][j] < 100: # for ordinary layout tiles
                                        clicked_tile = map[layer][i][j]
                                    else: # stack
                                        clicked_tile = stacks[stack_id][-1]  # append top most tile in stack
                                    collected_tiles.append(clicked_tile)

                                    # items bar explodes
                                    if len(collected_tiles) == 7 and collected_tiles.count(clicked_tile) < 3:
                                        game_state = "game lost"

                                    ############################## ADD ANIMATION HERE ##############################
                                    # if got 3x combo in items bar, reduce the number of tiles left
                                    if collected_tiles.count(clicked_tile) >= 3:
                                        number_of_tiles -= 3
                                        collected_tiles = [tile for tile in collected_tiles if tile != clicked_tile]  # discard 3x combo tiles from items bar
                                        if number_of_tiles <= 0:  # no more tiles remaining
                                            game_state = "game won"
                                    # print("number of tiles:", number_of_tiles)
                                    # print(collected_tiles)

                                    # remove tiles from map and won't be displayed anymore
                                    if map[layer][i][j] < 100:  # for ordinary layout tiles
                                        map[0][i][j] = 0  # remove clicked tile from game screen
                                    else:  # stack
                                        stacks[stack_id].pop()  # remove clicked tile from top of stack
                                    left_mouse_down_pos = (0, 0)  # once a tile has been removed, reset pos of mouse to prevent detection of more than 1 tile clicked

            # bring all exposed tiles from layers beneath after removing tile onto top layer to be considered visible
            map = update_top_layer(map)

            # items bar background
            items_surf = pygame.Surface((ITEM_BAR_WIDTH, ITEM_BAR_HEIGHT))
            # items_surf.fill("#8f6f45")
            items_surf.fill("#D95585")
            items_rect = items_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT-100))
            screen.blit(items_surf, items_rect)

            # displaying collected tiles in items bar
            for index, tile in enumerate(collected_tiles):  # tile = tile_type
                img = pygame.image.load('pics/' + str(tile) + '.png')
                tile_x_pos = SCREEN_WIDTH/2-ITEM_BAR_WIDTH/2+ITEM_GAP+index*(TILE_WIDTH+ITEM_GAP)
                tile_y_pos = SCREEN_HEIGHT-100
                tile_rect = img.get_rect(midleft=(tile_x_pos,tile_y_pos))
                screen.blit(img, tile_rect)

        elif game_state == "game lost":
            print("GAME OVER! YOU LOST!")

        elif game_state == "game won":
            print("YOU WIN!")

        pygame.display.update()  # update game display
        clock.tick(60)  # run game at 60 fps



play(0)
















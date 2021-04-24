import pygame, sys, random

from pygame.locals import *

pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Arial', 30)

# Screen settings
clock = pygame.time.Clock()
WINDOW_SIZE = (600, 400)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
DISPLAY_WIDTH = 300
DISPLAY_HEIGHT = 200
display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))  # used as the surface for rendering, which is scaled
pygame.display.set_caption('Jumper')
CHUNK_SIZE = 8

# Player
player_image = pygame.image.load('player.png').convert()
player_image.set_colorkey((255, 255, 255))
player_location = [70, 20]
player_momentum = 0
player_rect = pygame.Rect(player_location[0], player_location[1], player_image.get_width(), player_image.get_height())
player_action = 'idle'  # At first the player is idle
player_frame = 0
player_flip = False  # Player is facing right
background_objects = [[0.25, [120, -80, 70, 400]], [0.25, [280, -40, 40, 400]], [0.5, [30, 0, 40, 400]],
                      [0.5, [100, 90, 100, 400]], [0.5, [230, 80, 120, 400]]]
moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0
true_scroll = [0, 0]
grass_timer = 0
y_lower = -3
y_upper = 4


def loadchunk(path):                #Load a chunk of tiles from path
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')  # Split data by new line (into rows)
    file_chunk = []
    for row in data:
        file_chunk.append(list(row))  # Turn row(string) into an iterable object(list)
    return file_chunk


# Map
game_map = {}  # {} - dictionary
dirt1_img = pygame.image.load('dirt2.png')  # Load images
plant_img = pygame.image.load('plant.png').convert()
wave_img = pygame.image.load('wave.png')
water_img = pygame.image.load('water.png')
fire_img = pygame.image.load('fire.png').convert()
jumper_img = pygame.image.load('jumper.png').convert()
dirt1_img.set_colorkey((255, 255, 255))
plant_img.set_colorkey((255, 255, 255))
wave_img.set_colorkey((255, 255, 255))
fire_img.set_colorkey((255, 255, 255))
jumper_img.set_colorkey((255, 255, 255))
tile_index = {1: dirt1_img,
              3: plant_img,
              4: water_img,
              5: wave_img,
              6: fire_img,
              7: jumper_img}
fire_objects = []                          #Fire list
jumper_objects = []                        #Jumper list


def collision_test(rect, tiles):            #Test rect object for collisions
    collide_list = []
    for tile in tiles:
        if rect.colliderect(tile):          #if rect collides with a tile
            collide_list.append(tile)       #add it to list
    return collide_list


def generate_chunk(x, y):               #Generate random chunks of tiles
    chunk_data = []
    chunk = loadchunk('chunk' + str(random.randint(1, 4)))
    for chunk_x in range(CHUNK_SIZE):
        plant_tile = 0
        for chunk_y in range(CHUNK_SIZE):
            true_x = (x * CHUNK_SIZE) + chunk_x         # true_y, true_x - relative to the map
            true_y = (y * CHUNK_SIZE) + chunk_y
            random_val = random.randint(1, 10)

            tile_type = 0       #Air
            if true_y == 10:
                tile_type = 5  # Wave
            elif true_y > 10:
                tile_type = 4  # Water
            else:
                if chunk[chunk_x][chunk_y] == '1':
                    if random_val <= 6 or plant_tile == 1:
                        tile_type = 1  # Dirt
                        plant_tile = 0
                    elif 6 < random_val <= 8 and plant_tile == 0:
                        tile_type = 6    #Fire
                    elif random_val > 8 and plant_tile == 0:
                        tile_type = 7   #Jumper
                elif chunk[chunk_x][chunk_y] == '2' and random_val > 5:
                    tile_type = 3  # Plant
                    plant_tile = 1
            if tile_type != 0:
                chunk_data.append([[true_x, true_y], tile_type])
    return chunk_data


class fire_obj():               #Fire object class
    def __init__(self, loc):
        self.loc = loc

    def render(self, surface, scroll):
        surface.blit(fire_img, (self.loc[0] - scroll[0], self.loc[1] - scroll[1]))

    def get_rect(self):
        return pygame.Rect(self.loc[0], self.loc[1], 8, 16)

    def collision_test(self, rect):
        fire_rect = self.get_rect()
        return fire_rect.colliderect(rect)


class jumper_obj():            #Jumper object class
    def __init__(self, loc):
        self.loc = loc

    def render(self, surface, scroll):
        surface.blit(jumper_img, (self.loc[0] - scroll[0], self.loc[1] - scroll[1]))

    def get_rect(self):
        return pygame.Rect(self.loc[0], self.loc[1], 8, 16)

    def collision_test(self, rect):
        jumper_rect = self.get_rect()
        return jumper_rect.colliderect(rect)


def move(rect, movement, tiles):                #Move player and test for collisions
    collision_side = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    collide_list = collision_test(rect, tiles)
    for tile in collide_list:
        if movement[0] > 0:         #bump into tile from right side
            rect.right = tile.left
            collision_side['right'] = True
        elif movement[0] < 0:        #... left side
            rect.left = tile.right
            collision_side['left'] = True
    rect.y += movement[1]
    collide_list = collision_test(rect, tiles)
    for tile in collide_list:
        if movement[1] > 0:         #...bottom
            rect.bottom = tile.top
            collision_side['bottom'] = True
        elif movement[1] < 0:       #...top
            rect.top = tile.bottom
            collision_side['top'] = True
    return rect, collision_side


def die():          #Game Over screen
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        textsurface = myfont.render('Game Over', False, (0, 0, 0))
        display.blit(textsurface, (DISPLAY_WIDTH // 2 - 75, DISPLAY_HEIGHT // 2 - 25))
        display.blit(pygame.transform.flip(player_image, player_flip, False),
                     (player_rect.x - true_scroll[0], player_rect.y - true_scroll[1]))      # Render player
        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))                 # Scale the screen
        pygame.display.update()
        clock.tick(60)


while True:          # Game loop

    display.fill((146, 244, 255))  # Background color
    true_scroll[0] = 0              #x axis camera scrolling
    true_scroll[1] += (player_rect.y - true_scroll[1] - (DISPLAY_HEIGHT / 2 + 6)) / 20  #y axis camera scrolling
    scroll = true_scroll.copy()
    scroll[1] = int(scroll[1])

    for background_object in background_objects:                    #Paralax effect
        object = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                             background_object[1][1] - scroll[1] * background_object[0], background_object[1][2],
                             background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (165, 204, 9), object)
        else:
            pygame.draw.rect(display, (0, 86, 35), object)

    tile_rects = []                   # Draw map
    for y in range(y_lower, y_upper):
        for x in range(4):
            true_x = x - 1 + int(round(scroll[0] / (CHUNK_SIZE * 16)))
            true_y = y - 1 + int(round(scroll[1] / (CHUNK_SIZE * 16)))
            target_chunk = str(true_x) + ';' + str(true_y)
            if target_chunk not in game_map:        #If chunk is a new chunk
                game_map[target_chunk] = generate_chunk(true_x, true_y)
            for tile in game_map[target_chunk]:
                display.blit(tile_index[tile[1]],           #display the tile
                            (tile[0][0] * 16 - scroll[0], tile[0][1] * 8 - scroll[1]))  #blit(tile_type, (x_pos, y_pos))
                if tile[1] in [1, 4]:           #dirt/water tile
                    tile_rects.append(pygame.Rect(tile[0][0] * 16, tile[0][1] * 8, 16, 8))
                elif tile[1] == 6:              #Fire tile
                    fire_objects.append(fire_obj((tile[0][0] * 16, tile[0][1] * 8)))
                elif tile[1] == 7:              #Jumper tile
                    jumper_objects.append(jumper_obj((tile[0][0] * 16, tile[0][1] * 8)))

    for fire in fire_objects:       #test for fire collision
        if fire.collision_test(player_rect):        #if player collides with fire...
            die()                                   #...they die

    for jumper in jumper_objects:       #test for jumper collision
        if jumper.collision_test(player_rect):      #if player collides with jumper...
            vertical_momentum = -8                  #...they receive a jump boost

    if len(fire_objects) > 50:              #memory optimisation
        fire_objects = []

    if len(jumper_objects) > 50:
        jumper_objects = []

    if player_rect.y % 100 == 0:  # this method is suboptimal
        y_lower -= 1

    player_movement = [0, 0]

    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2

    player_movement[1] += vertical_momentum  # Gravity
    vertical_momentum += 0.2
    if vertical_momentum > 3:
        vertical_momentum = 3

    player_rect, collisions = move(player_rect, player_movement, tile_rects)  # Move player and test for collisions

    if collisions['bottom'] == True:  # Case when player is on the ground
        air_timer = 0
        vertical_momentum = 0
    else:                     # Case when player is in the air
        air_timer += 1

    if player_movement[0] > 0:  # Set player image orientation
        player_flip = False
    elif player_movement[0] < 0:
        player_flip = True

    display.blit(pygame.transform.flip(player_image, player_flip, False),
                 (player_rect.x - true_scroll[0], player_rect.y - true_scroll[1]))  # Render player
                                                                # flip if needed and offset position by scroll value
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:  # Key is pressed
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    vertical_momentum = -5
        if event.type == KEYUP:     # Key is released
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))  # Scale the screen
    pygame.display.update()
    clock.tick(60)

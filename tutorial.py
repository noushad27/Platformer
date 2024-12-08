import os
import pygame
import math
import random
from os import listdir, name, path
from os.path import join, isfile
from pygame.sprite import Group

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Game By NOUSHAD")

# Constants
BG_COLOR = (177, 177, 177)
WIDTH, HEIGHT = 1600, 900
FPS = 60
GRAVITY = 1
GROUND_LEVEL = HEIGHT - 200
PLAYER_VELOCITY = 5.5

# Set up the game window
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)

# Utility Functions
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)  # Relative path to assets folder
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    print(f"Loading sprites from: {path}")
    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    print(f"Loaded sprites: {all_sprites}")
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")  # Relative path to Terrain
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    print(f"Resolved path: {path}")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_background(name):
    path = join("assets", "Background", name)  # Relative path to Background
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    image = pygame.image.load(path)
    __, __, width, height = image.get_rect()
    tiles = []
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)
    print(f"Background tiles: {tiles}")
    return tiles, image

# Classes
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)  # Relative path
    ANIMATION_DELAY = 1
    MAX_JUMP_COUNT = 2

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.Fall_count = 0
        self.on_ground = False
        self.sprite = None
        self.sprite = self.SPRITES["idle_left"][0]
        self.update_sprite()

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
    
    def jump(self):
        if self.jump_count < self.MAX_JUMP_COUNT:
            self.y_vel = -15
            self.jump_count += 1
            self.on_ground = False

    def landed(self):
        self.Fall_count = 0
        self.y_vel = 0
        self.jump_count = 0 

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
            self.sprite = self.SPRITES["idle_left"][0]

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
            self.sprite = self.SPRITES["idle_right"][0]

    def jump(self, vel=7):
        if self.on_ground:
            self.y_vel = -vel
            self.jump_count += 1
            self.on_ground = False
        elif self.jump_count == 1:  # Double jump logic
            self.y_vel = -vel  # Double jump velocity
            self.jump_count += 1
        self.update_sprite()

    def apply_gravity(self, objects):
        self.y_vel += GRAVITY
        self.rect.y += self.y_vel

        for obj in objects:
            if pygame.sprite.collide_mask(self, obj):
                if self.y_vel > 0:  # Falling down
                    self.rect.bottom = obj.rect.top
                    self.landed()
                elif self.y_vel < 0:  # Jumping up
                    self.rect.top = obj.rect.bottom
                    self.hit_head()

        if self.rect.top > HEIGHT:  # Below screen
            self.rect.y = GROUND_LEVEL - self.rect.height  # Reset to ground
            self.landed()

    def stop_moving(self):
        self.x_vel = 0

    def loop(self, fps, objects):
        self.move(self.x_vel, self.y_vel)
        self.Fall_count += 1
        self.apply_gravity(objects)
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
        self.on_ground = True  

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self, sprite_group=None):
        if self.y_vel < 0:  # Jumping (upward motion)
            if self.x_vel > 0:  # Moving right (forward)
                sprite_sheet_name = f"front_flip_right"  # Front flip animation
            elif self.x_vel < 0:  # Moving left (backward)
                sprite_sheet_name = f"back_flip_left"  # Back flip animation
            else:  # Not moving horizontally, just jumping
                sprite_sheet_name = f"jump_{self.direction}"
        elif self.y_vel > GRAVITY * 2:  # Falling (downward motion)
            sprite_sheet_name = f"fall_{self.direction}"
        elif self.x_vel != 0:  # Running left or right
            sprite_sheet_name = f"run_{self.direction}"
        else:  # Idle
            sprite_sheet_name = f"idle_{self.direction}"

        sprites = self.SPRITES.get(sprite_sheet_name)
        if sprites is not None:
            if sprite_group is not None:
                sprite_group.add(self)
            self.animation_count += 1
            if self.animation_count >= len(sprites) * self.ANIMATION_DELAY:
                self.animation_count = 0
            self.sprite = sprites[self.animation_count // self.ANIMATION_DELAY]
        else:
            self.sprite = self.SPRITES.get(f"idle_{self.direction}", [None])[0]
    
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

# Main Game Functions
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tuple(tile))
    for obj in objects:
        obj.draw(window, offset_x)
    player.draw(window, offset_x)
    pygame.display.update()

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        player.move_left(PLAYER_VELOCITY)
    if keys[pygame.K_d]:
        player.move_right(PLAYER_VELOCITY)
    if keys[pygame.K_w]:
        player.jump()

def main():
    clock = pygame.time.Clock()

    # Create Game Objects
    background_tiles, bg_image = get_background("blue.png")
    player = Player(300, GROUND_LEVEL - 100, 50, 70)

    all_objects = pygame.sprite.Group()

    # Add blocks to the scene
    for i in range(0, WIDTH, 50):
        block = Block(i, GROUND_LEVEL - 50, 50)
        all_objects.add(block)

    # Game loop
    running = True
    while running:
        clock.tick(FPS)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        handle_move(player, all_objects)
        player.loop(FPS, all_objects)
        draw(window, background_tiles, bg_image, player, all_objects, player.rect.x)

    pygame.quit()

if __name__ == "__main__":
    main()

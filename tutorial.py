import pygame
import os

os.chdir("C:/Users/sknou/OneDrive/Desktop/game/Python-Platformer-main")

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -10
WHITE = (255, 255, 255)

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game")

# Load images
def get_background(name):
    path = os.path.join("assets", "Background", name)  # Correct relative path construction
    try:
        image = pygame.image.load(path)  # Load the image
        tiles = image.get_rect()  # Get the rectangle of the image for positioning
        return tiles, image
    except pygame.error:
        raise FileNotFoundError(f"File not found: {path}")

# Call the function with just the file name
background_tiles, background_image = get_background("Blue.png")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 128, 255))  # Player color
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - 150  # Starting position
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False

    def update(self, blocks):
        keys = pygame.key.get_pressed()

        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.velocity_x = -5
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = 5
        else:
            self.velocity_x = 0

        # Apply gravity
        if not self.on_ground:
            self.velocity_y += GRAVITY
        else:
            self.velocity_y = 0

        # Update player position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Check for collisions with blocks (platforms)
        self.on_ground = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                # Check if falling and colliding with the top of the block
                if self.velocity_y > 0 and self.rect.bottom <= block.rect.top + 10:
                    self.rect.bottom = block.rect.top
                    self.on_ground = True

        # Keep player within screen bounds
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > WIDTH - self.rect.width:
            self.rect.x = WIDTH - self.rect.width
        if self.rect.y > HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH

# Block class for platforms
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0))  # Red color for block
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Function to create blocks/platforms
def create_blocks():
    block1 = Block(200, HEIGHT - 100, 150, 20)  # Platform 1
    block2 = Block(400, HEIGHT - 200, 150, 20)  # Platform 2
    block3 = Block(600, HEIGHT - 300, 150, 20)  # Platform 3
    return [block1, block2, block3]

# Main game loop
def main():
    # Use the globally initialized background image
    global background_image

    # Create the player and blocks
    player = Player()
    blocks = pygame.sprite.Group(*create_blocks())
    all_sprites = pygame.sprite.Group(player, *blocks)

    clock = pygame.time.Clock()

    # Main loop
    running = True
    while running:
        screen.fill(WHITE)

        # Draw the background
        screen.blit(background_image, (0, 0))  # Use the globally initialized background_image

        # Check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        # Update the player separately
        player.update(blocks)

        # Update other sprites (without arguments)
        for sprite in blocks:
            sprite.update()

        # Draw everything
        all_sprites.draw(screen)

        # Refresh the screen
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()

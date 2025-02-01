import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Echoes of the Arena")

# Clock for controlling the frame rate
clock = pygame.time.Clock()
FPS = 60

# Font
font = pygame.font.Font(None, 36)

# Load assets
player_img = pygame.Surface((50, 50))
player_img.fill(GREEN)

enemy_img = pygame.Surface((50, 50))
enemy_img.fill(RED)

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.health = 100
        self.speed = 5
        self.attack_cooldown = 0

    def update(self, keys):
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

        # Prevent player from moving off-screen
        self.rect.clamp_ip(screen.get_rect())

        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self):
        if self.attack_cooldown == 0:
            self.attack_cooldown = 30
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = 50
        self.speed = 2

    def update(self, player):
        # Move towards the player
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed

        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.speed

        # Prevent enemy from moving off-screen
        self.rect.clamp_ip(screen.get_rect())

# Initialize player and enemies
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

enemies = pygame.sprite.Group()
for _ in range(3):
    x, y = random.randint(400, 700), random.randint(100, 500)
    enemy = Enemy(x, y)
    all_sprites.add(enemy)
    enemies.add(enemy)

# Health bars
def draw_health_bar(surface, x, y, health, max_health):
    pygame.draw.rect(surface, RED, (x, y, 100, 10))
    pygame.draw.rect(surface, GREEN, (x, y, max(0, int(100 * health / max_health)), 10))

# Main game loop
running = True
win = False
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key presses
    keys = pygame.key.get_pressed()

    # Player actions
    player.update(keys)

    # Enemy actions
    for enemy in enemies:
        enemy.update(player)

    # Attack handling
    if keys[pygame.K_SPACE] and player.attack():
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                enemy.health -= 20
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    all_sprites.remove(enemy)

    # Check for win condition
    if len(enemies) == 0:
        win = True
        running = False

    # Check for game over
    for enemy in enemies:
        if enemy.rect.colliderect(player.rect):
            player.health -= 1
            if player.health <= 0:
                running = False

    # Drawing
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Draw health bars
    draw_health_bar(screen, player.rect.x, player.rect.y - 15, player.health, 100)
    for enemy in enemies:
        draw_health_bar(screen, enemy.rect.x, enemy.rect.y - 15, enemy.health, 50)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# End screen
screen.fill(WHITE)
if win:
    text = font.render("Victory! You defeated all enemies.", True, BLACK)
else:
    text = font.render("Game Over. You were defeated.", True, BLACK)
screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
pygame.display.flip()

# Wait before quitting
pygame.time.wait(3000)

# Quit Pygame
pygame.quit()

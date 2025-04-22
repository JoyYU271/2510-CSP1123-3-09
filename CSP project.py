import pygame
import sys

# Init
pygame.init()
clock = pygame.time.Clock()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Doctor Test")

# Doctor class (insert the full class here)
# Use the class I gave earlier ↑↑↑

class Doctor(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.stand_img = pygame.image.load('picture/Character QQ/Doctor idle.png').convert_alpha()
        self.image = self.stand_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.flip = False
        self.direction = 1
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        for i in range(1, 5):
            walk_img = pygame.image.load(f'picture/Doctor Walking/walk {i}.png').convert_alpha()
            self.animation_list.append(walk_img)

    def move(self):
        keys = pygame.key.get_pressed()
        dx = 0
        moving = False

        if keys[pygame.K_a]:
            dx = -self.speed
            self.flip = True
            self.direction = -1
            moving = True
        elif keys[pygame.K_d]:
            dx = self.speed
            self.flip = False
            self.direction = 1
            moving = True

        self.rect.x += dx

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

        return moving

    def update_animation(self, moving):
        if moving:
            ANIMATION_COOLDOWN = 150
            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.animation_list):
                    self.frame_index = 0
            self.image = self.animation_list[self.frame_index]
        else:
            self.image = self.stand_img

    def update(self):
        is_moving = self.move()
        self.update_animation(is_moving)

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

# Create the doctor instance
player = Doctor(x=400, y=300, speed=4.5)

# Game loop
run = True
while run:
    screen.fill((100, 100, 255))  # sky blue background

    # Event check (for ESC / quit)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    # Update player
    player.update()

    # Draw player
    player.draw(screen)

    # Update display
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()

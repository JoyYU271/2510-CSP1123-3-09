import pygame, sys
from random import randint

#create class for obstacle sprite, and player sprite
class Block(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('/Python game/GUI 1.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)

class Fire(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('/Python game/pfp.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.direction = pygame.math.Vector2()
        self.speed = 5
    
    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction_y = -1
        elif keys[pygame.K_DOWN]:
            self.direction_y = 1
        else:
            self.direction_y = 0

        if keys[pygame.K_RIGHT]:
            self.direction_x = 1
        elif keys[pygame.K_LEFT]:
            self.direction_x = -1
        else:
            self.direction_x = 0

    def update(self):
        self.input()
        self.rect.center += self.direction * self.speed

pygame.init()
screen = pygame.display.set_mode((1280,720))
#To show on white bar above, we'll be in fullscreen so may not be needed
#   pygame.display.set_caption('Game_name or what have you')
clock = pygame.time.Clock() #limit game frame rate

#set up
#sprite group?
camera_group = pygame.sprite.Group()
Fire((640, 360), camera_group)

for i in range(20):
    random_x = randint(0, 1000)
    random_y = randint(0,1000)
    Block((random_x,random_y), camera_group)

#Game loop begins
while True:
    # to End game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    screen.fill('Blue')

    camera_group.update()
    camera_group.draw(screen)

    pygame.display.update()
    clock.tick(60)





import pygame, sys
from random import randint

#create class for obstacle sprite, and player sprite
class Fire(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('Projects/Python game/pfp.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,group):
        super().__init__(group)
        self.image = pygame.image.load('Projects/Python game/sonic.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.direction = pygame.math.Vector2()
        self.speed = 5
    
    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self):
        self.input()
        self.rect.center += self.direction * self.speed

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
    
    #camera offset
        self.offset = pygame.math.Vector2

    def custom_draw(self):
        for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery): #.sprites is where all our imported sprites are stored in pygame
            self.display_surface.blit(sprite.image,sprite.rect)
 
    #box camera 
        self.camera_borders = {'left':200, 'right':200, 'top':100, 'bottom':100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l,t,w,h)
    
    

pygame.init()
screen = pygame.display.set_mode((1280,720))
#To show on white bar above, we'll be in fullscreen so may not be needed
#   pygame.display.set_caption('Game_name or what have you')
clock = pygame.time.Clock() #limit game frame rate

#set up
#sprite group?
camera_group = CameraGroup() #missing the bracket gives me AbstractGroup.add_internal() missing 1 required positional argument: 'sprite' error... maybe because I didn't actually called it?
Player((640, 360), camera_group)

for i in range(20):
    random_x = randint(0, 1000)
    random_y = randint(0,1000)
    Fire((random_x,random_y), camera_group)

#Game loop begins
while True:
    # to End game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    screen.fill('#71ddee')

    camera_group.update()
    camera_group.custom_draw()

    pygame.display.update()
    clock.tick(60)





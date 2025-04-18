import pygame, sys,ctypes
from random import randint
#Help on built-in function set_mode in module pygame.display:



#create class for obstacle sprite, and player sprite
class Fire(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.image.load('pfp.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,group):
        super().__init__(group)
        self.image = pygame.image.load('sonic.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.flip = False
    
    def input(self):
        keys = pygame.key.get_pressed()

        #if keys[pygame.K_UP]:
        #    self.direction.y = -1
        #elif keys[pygame.K_DOWN]:
        #    self.direction.y = 1
        #else:
        #    self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.flip = False
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.flip = True
        else:
            self.direction.x = 0

    def update(self):
        self.input()
        self.rect.center += self.direction * self.speed

    def move(self,moving_left,moving_right):
     #reset movement variables
       dx = 0

     #assign movement variables (left or right)
       if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
       if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
    #update position
       self.rect.x += dx 

    def draw(self):
        screen.blit (pygame.transform.flip(self.image,self.flip,False),self.rect)


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        
        #camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        #box camera 
        self.camera_borders = {'left':200, 'right':200, 'top':100, 'bottom':100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l,t,w,h)

        #ground
        self.ground_surf = pygame.image.load('GUI 1.png').convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(topleft = (0,0))

    def center_target_camera(self,target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def box_target_camera(self,target):

        if target.rect.left < self.camera_rect.left:
           self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
           self.camera_rect.right = target.rect.right 

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    def custom_draw(self,player):

        #self.center_target_camera(player)
        self.box_target_camera(player)

        #ground
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surf,ground_offset)

        #active elements
        for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.center): #.sprites is where all our imported sprites are stored in pygame
            #note to study more about 'sorted'
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image,offset_pos)
            

pygame.init()

#to get real resolution
#ctypes.windll.user32.SetProcessDPIAware() #make sure the Python program gets the actual screen resolution, not scaled one
#screen_width = ctypes.windll.user32.GetSystemMetrics(0) #ask the real screen width in pixels
#screen_height = ctypes.windll.user32.GetSystemMetrics(1) #ask the real screen height in pixels


screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE) #Right here! :D


#To show on white bar above, we'll be in fullscreen so may not be needed
#   pygame.display.set_caption('Game_name or what have you')
clock = pygame.time.Clock() #limit game frame rate

#set up
#sprite group?
camera_group = CameraGroup() #missing the bracket gives me AbstractGroup.add_internal() missing 1 required positional argument: 'sprite' error... maybe because I didn't actually called it?
player = Player((640, 360), camera_group)

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

        if event.type == pygame.VIDEORESIZE:
                # There's some code to add back window content here.
                surface = pygame.display.set_mode((event.w, event.h),pygame.RESIZABLE)
        
    screen.fill('#71ddee')

    camera_group.update()
    camera_group.custom_draw(player)
    

    pygame.display.update()
    clock.tick(60)





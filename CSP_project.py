import pygame, sys
from random import randint
#Help on built-in function set_mode in module pygame.display:
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
world_width = 2488
world_height = 720

class doctor(pygame.sprite.Sprite):  
    def __init__(self,x,y,group):
        super().__init__(group)   #auto find the sprite（pygame.sprite.Sprite）
        self.stand_img = pygame.image.load('picture/Character QQ/Doctor idle.png').convert_alpha()
        self.image =  self.stand_img
        self.rect = self.image.get_rect() #get the rectangle area of image to locate the character
        self.rect.center = (x,y) #set player on screen on origin location
        self.speed = 4.5
        self.direction = 1
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        for i in range(1,5):
            doctorwalk = pygame.image.load(f'picture/Doctor Walking/walk {i}.png').convert_alpha()
            self.animation_list.append(doctorwalk)

    def move(self):
        keys = pygame.key.get_pressed()
        dx = 0
        moving = False

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
            self.flip = True
            self.direction = -1
            moving = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
            self.flip = False
            self.direction = 1
            moving = True

        self.rect.x += dx

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > world_width:
            self.rect.right = world_width

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

        # #ground
        # ground_offset = self.ground_rect.topleft - self.offset
        # self.display_surface.blit(self.ground_surf,ground_offset)

        #player?
        for sprite in self.sprites():
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
player = doctor(400, 500, camera_group)

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
        
    #screen.fill('#71ddee')

    camera_group.update()
    camera_group.custom_draw(player)
    

    pygame.display.update()
    clock.tick(60)





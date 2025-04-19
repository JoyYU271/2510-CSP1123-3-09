import pygame
import sys
import ctypes #library for full screen
from pygame.locals import *

pygame.init()

#to get real resolution
#ctypes.windll.user32.SetProcessDPIAware() #make sure the Python program gets the actual screen resolution, not scaled one
#screen_width = ctypes.windll.user32.GetSystemMetrics(0) #ask the real screen width in pixels
#screen_height = ctypes.windll.user32.GetSystemMetrics(1) #ask the real screen height in pixels

screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define background color
BG = (255,255,255)

# only white bg 
# for bg img  need to use 'screen.blit(background_image, (0, 0)) '
def draw_bg():
  screen.fill(BG)

class doctor(pygame.sprite.Sprite):
    def __init__(self,x,y,speed):
        super().__init__()   #auto find the sprite（pygame.sprite.Sprite）
        self.stand_img = pygame.image.load('picture/stand.png').convert_alpha()
        self.image =  self.stand_img
        #get the rectangle area of image
        self.rect = self.image.get_rect()
        #set player on screen on origin location
        self.rect.center = (x,y)
        self.speed = speed
        self.direction = 1

        # flip picture
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
    
        for i in range(1,5):
            doctorwalk = pygame.image.load(f'picture/walking/walk {i}.png').convert_alpha()
            self.animation_list.append(doctorwalk)

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

    # let player cannot get out of screen
       if self.rect.left < 0 :
           self.rect.left = 0
       if self.rect.right > screen_width:
           self.rect.right = screen_width
       return moving_left or moving_right

    def update_animation(self,is_moving):
        if is_moving:

            #control animation speed 
            ANIMATION_COOLDOWN = 150

            #control change of animation
            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                 self.update_time = pygame.time.get_ticks()
                 self.frame_index += 1

                 if self.frame_index >= len(self.animation_list):
                    self.frame_index = 0

            self.image = self.animation_list[self.frame_index]
        else:
            self.image = self.stand_img


    def draw(self):
        screen.blit (pygame.transform.flip(self.image,self.flip,False),self.rect)


player = doctor(400,500,4.5)    #coordinate screen, speed

#define player action variables
moving_left = False
moving_right = False

is_moving = player.move(moving_left,moving_right)

run = True 

while run :
    
    draw_bg()
    is_moving = player.move(moving_left,moving_right)
    player.update_animation(is_moving)
    player.draw()
  
    for event in pygame.event.get():
        

        if event.type == pygame.QUIT:
           run = False

        # Keyboard button pressed
        if event.type == KEYDOWN :
            if event.key == K_a:
                moving_left = True
            if event.key == K_d:
                moving_right = True

        # keyboard button released
        if event.type == KEYUP :
            if event.key == K_a:
                moving_left = False
            if event.key == K_d:
                moving_right = False
            if event.key == K_ESCAPE:
                run = False
        
    
   

    # uodate display of screen
    pygame.display.update()

    # control game frames
    clock.tick(FPS)    
           
         
pygame.quit()
sys.exit()
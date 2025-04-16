import pygame
import sys
from pygame.locals import *

pygame.init()


screen_width = 1535
screen_height = 775

screen = pygame.display.set_mode((screen_width,screen_height))
#set framerate帧率
clock = pygame.time.Clock()

#define background color
BG = (255,255,255)

#清空画面 only white bg 
# for 复杂的背景就要用screen.blit(background_image, (0, 0)) 
def draw_bg():
  screen.fill(BG)

class doctor(pygame.sprite.Sprite):
    def __init__(self,x,y,speed):
        super().__init__()   #auto find the sprite 自动找到当前类的父类（pygame.sprite.Sprite）
        self.image =  pygame.image.load('picture/images.png')
        #得到图片的矩形区域
        self.rect = self.image.get_rect()
        #set player on screen on origin location
        self.rect.center = (x,y)
        self.speed = speed
        self.direction = 1
        #翻转图片 flip picture
        self.flip = False

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

    def draw(self):
        screen.blit (pygame.transform.flip(self.image,self.flip,False),self.rect)


player = doctor(500,550,5)    #coordinate screen, speed

#define player action variables
moving_left = False
moving_right = False



run = True 

while run :

    draw_bg()
    player.move( moving_left, moving_right )
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
        
    
   
    
    # 更新屏幕
    pygame.display.update()

    # 控制游戏帧率
    clock.tick(60)    
           
         
pygame.quit()
sys.exit()
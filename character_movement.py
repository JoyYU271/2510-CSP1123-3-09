import pygame
import sys
from pygame.locals import *

pygame.init()



#=======screen setting==========
screen_width = 1280
screen_height = 720
#set framerate
FPS = 60
#define background color
BG = (255,255,255)


def init_game():
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    clock = pygame.time.Clock() #control framerate
    player = doctor(400,500,4.5)    #coordinate screen, speed
    return screen,clock,player

# only white bg 
# for bg img  need to use 'screen.blit(background_image, (0, 0)) '
def draw_bg(screen):
  screen.fill(BG)

class doctor(pygame.sprite.Sprite):
    def __init__(self,x,y,speed):
        super().__init__()   #auto find the sprite（pygame.sprite.Sprite）
        self.stand_img = pygame.image.load('picture/Character QQ/Doctor idle.png').convert_alpha()
        self.image =  self.stand_img
        self.rect = self.image.get_rect() #get the rectangle area of image to locate the character
        self.rect.center = (x,y) #set player on screen on origin location
        self.speed = speed
        self.direction = 1
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
    
        for i in range(1,5):
            doctorwalk = pygame.image.load(f'picture/Doctor Walking/walk {i}.png').convert_alpha()
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


    def draw(self,screen):
        screen.blit (pygame.transform.flip(self.image,self.flip,False),self.rect)

def keyboard_input(moving_left, moving_right, run) :
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
        return moving_left,moving_right,run



def main():
    screen,clock,player = init_game()

#define player action variables
    moving_left = False
    moving_right = False
    run = True

    while run :
    
          draw_bg(screen)

          is_moving = player.move(moving_left,moving_right)

          player.update_animation(is_moving)

          player.draw(screen)

          moving_left,moving_right,run =  keyboard_input(moving_left, moving_right, run)


         # uodate display of screen
          pygame.display.update()

         # control game frames
          clock.tick(FPS)    
           
         
    pygame.quit()
    sys.exit()

#the code will run when the main run ，if anyone import my code to use ，they will get function they want but the main program  will not run
if __name__ =="__main__":
    main()
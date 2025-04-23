import pygame
import sys
from pygame.locals import *
from character_movement import *

pygame.init()

screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
clock = pygame.time.Clock()
FPS = 60

player = doctor(400,500,4.5) 
moving_left = False
moving_right = False

run = True
while run:
          draw_bg(screen)
          is_moving = player.move(moving_left,moving_right)
          player.update_animation(is_moving)
          player.draw(screen)
          moving_left,moving_right,run =  keyboard_input(moving_left, moving_right, run)

          pygame.display.update()
          clock.tick(FPS)    
           
pygame.quit()
sys.exit()

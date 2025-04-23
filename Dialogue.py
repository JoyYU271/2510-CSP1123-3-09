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


font = pygame.font.SysFont('Comic Sans MS',50)
index = -1
space_released = True # control the dialog will not happen continuously when press key space


#============dialog box =============
class dialog:
    def __init__(self,npc,player):
        super().__init__()
        self.dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog box.png").convert_alpha()
        self.portrait = pygame.image.load("picture/Character Dialogue/Nurse.png").convert_alpha()
        self.player = player
        self.npc = npc
        self.step = 0 # present current line
        self.text = ["Hi","halo","Cute"]
        self.talking = False

    def update(self,key):
         if self.player.rect.colliderect(self.npc.rect):
              if key and not self.talking:
                   self.talking = True #start dialog
                   self.step =0

              elif key and self.talking:
                   self.step += 1
                   if self.step >= len(self.text) :
                        self.talking = False #stop dialog
                        self.step = 0
         else:
              self.talking = False
    
    def draw(self,screen):
        if self.talking and self.step < len(self.text):
           
           dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
           dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20

           screen.blit(self.dialog_box_img,(dialog_x,dialog_y))

            # NPC portrait
           portrait_x = dialog_x + 850
           portrait_y = dialog_y - 400
           screen.blit(self.portrait,(portrait_x,portrait_y))

           
           #Npc name 
           draw_text(screen,self.npc.name,40,(0,0,0),dialog_x + 200 , dialog_y + 20)

           draw_text(screen,self.text[self.step],30,(0,0,0),dialog_x + self.dialog_box_img.get_width()//2,dialog_y + self.dialog_box_img.get_height()//2,center = True)
 
          

           

# =============text setting================
def draw_text(surface,text,size,color,x,y,center = False):
    font = pygame.font.SysFont('Comic Sans MS', size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
         text_rect.center = (x,y)
    else:
         text_rect.topleft =(x,y)
    surface.blit(text_surface, text_rect)


      
#===========Nuva==============

class NPC(pygame.sprite.Sprite):
    def __init__(self,x,y,name = "Nuva"):
        super().__init__()
        self.image = pygame.image.load('picture/Character QQ/Nurse idle.png').convert_alpha()
        self.world_pos = pygame.Vector2(x,y) #for world coordinate
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.name = name
        
npc = NPC(600,500)
dialogue = dialog(npc,player)


run = True
while run:
          
          draw_bg(screen)
          is_moving = player.move(moving_left,moving_right)
          player.update_animation(is_moving)
          screen.blit(npc.image,npc.rect)
          player.draw(screen)
          
          moving_left,moving_right,run =  keyboard_input(moving_left, moving_right, run)

          #=====space======
          keys = pygame.key.get_pressed()
          if npc.rect.colliderect(player.rect) and dialogue.step>=0 :
            
           if keys[pygame.K_SPACE] and space_released:
               space_released = False
               dialogue.update(True)
           else:
                dialogue.update(False)

           if not keys[pygame.K_SPACE]:
                space_released = True
          else :
               dialogue.update(False)


          dialogue.draw(screen)
          
          pygame.display.update()
          clock.tick(FPS)    
          

pygame.quit()
sys.exit()

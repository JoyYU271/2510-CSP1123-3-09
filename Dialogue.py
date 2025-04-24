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
player.name = "You" # remember to put in class doctor
moving_left = False
moving_right = False


font = pygame.font.SysFont('Comic Sans MS',50)
space_released = True # control the dialog will not happen continuously when press key space


#============dialog box =============
class dialog:
    def __init__(self,npc,player):
        super().__init__()
        self.dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog box.png").convert_alpha()
        self.dialog_box_img.set_alpha(200)
        self.portrait = pygame.image.load("picture/Character Dialogue/Nurse.png").convert_alpha()
        self.player_portrait = pygame.image.load("picture/Character Dialogue/Doctor.png").convert_alpha()

        self.player = player
        self.npc = npc

        self.step = 0 # present current sentence

        self.text = [("npc","HI"),("player","hello"),("npc","You are so cute"),("player","Thank you......")]
        
        self.talking = False # is it talking

        # for present sentences effect
        self.displayed_text = "" #display current word
        self.letter_index = 0  #display current which words
        self.last_time = pygame.time.get_ticks()
        self.letter_delay = 45

      # update dialog status
    def update(self,key): 
         if self.player.rect.colliderect(self.npc.rect):
              if key and not self.talking:
                   self.talking = True #start dialog
                   self.step =0
                   self.reset_typing()
              
               #start talking n reset status
              elif key and self.talking:
                   if self.letter_index <len(self.text[self.step]):
                        return
                   
                   #if the sentences haven't finish print out,cannot jump to next sentences
                   self.step += 1
                   if self.step >= len(self.text) :
                        self.talking = False #stop dialog
                        self.step = 0

                    # if not skip to next sentences
                   else:
                        self.reset_typing()
                        
          # if player is not around the npc, dialog end
         else:
              self.talking = False

    def reset_typing(self):
         self.displayed_text = ""
         self.letter_index = 0
         self.last_time = pygame.time.get_ticks()


 # =========draw for dialog box ,text ,character, word effect ======   
    def draw(self,screen):
        
        #only draw when in talking mode
        if self.talking and self.step < len(self.text):
           speaker,full_text = self.text[self.step]
           
           #let the dialog box on the center and put below
           dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
           dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20

           if speaker == "npc":
                portrait = self.portrait
                name = self.npc.name
                portrait_pos =(dialog_x + 800
           ,dialog_y - 400)
           else:
                portrait = self.player_portrait
                name = "You"
                portrait_pos = (dialog_x +20,dialog_y - 400)

           #draw Character portraits
           screen.blit(portrait,portrait_pos)

           #draw dialog box
           screen.blit(self.dialog_box_img,(dialog_x,dialog_y))

           


           #draw Npc name above the small dialog box
           name_to_display = self.npc.name if speaker == "npc" else self.player.name
           draw_text(screen,name_to_display,40,(0,0,0),dialog_x + 200 , dialog_y + 20)
           
           # words come out one by one effect
           current_time = pygame.time.get_ticks()
           speaker,full_text = self.text[self.step]
           if self.letter_index < len(full_text):
                if current_time - self.last_time > self.letter_delay:
                     self.displayed_text +=full_text[self.letter_index]
                     self.letter_index += 1
                     self.last_time = current_time
          

           draw_text(screen,self.displayed_text,30,(0,0,0),dialog_x + self.dialog_box_img.get_width()//2,dialog_y + self.dialog_box_img.get_height()//2,center = True)
 
          

           

# =============text setting================
def draw_text(surface,text,size,color,x,y,center = False):
    font = pygame.font.SysFont('Comic Sans MS', size)
    text_surface = font.render(text, True, color)

    # set the words location (in center)
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

import pygame
import sys
from pygame.locals import *
from character_movement import *
import json



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


font = pygame.font.SysFont('Comic Sans MS',40)
space_released = True # control the dialog will not happen continuously when press key space

with open('NPC_dialog/NPC.json','r',encoding = 'utf-8') as f:
     all_dialogues = json.load(f)

current_chapter = "chapter_1"

npc_list =["Nuva"]


#============dialog box =============
class dialog:
    def __init__(self,npc,player):
        super().__init__()
        self.dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog box.png").convert_alpha()
        self.dialog_box_img.set_alpha(200)
        self.portrait = pygame.image.load("picture/Character Dialogue/Nurse.png").convert_alpha()
        self.player_portrait = pygame.image.load("picture/Character Dialogue/Doctor.png").convert_alpha()

        self.player = player
        self.npc_name = npc.name
        self.npc = npc
        self.npc_data = all_dialogues.get(self.npc_name)

     #dialogue setting
        self.current_story = "chapter_1" #default chapter
        self.story_data = self.npc_data.get(self.current_story,[])
       

        self.step = 0 # present current sentence
        
        

        # for present sentences effect
        self.displayed_text = "" #display current word
        self.letter_index = 0  #display current which words
        self.last_time = pygame.time.get_ticks()
        self.letter_delay = 45

        self.options = []
        self.option_selected = 0
        self.talking = False # is it talking


      # update dialog status
    def update(self): 
        if self.talking and self.step < len(self.story_data):
             entry = self.story_data[self.step]
             text = entry.get("text","")

             if "choice" in entry :
              self.options = entry.get("choice",[])
             else:
                 self.options = []

             # words come out one by one effect
             current_time = pygame.time.get_ticks()
             if self.letter_index < len(text):
                if current_time - self.last_time > self.letter_delay:
                     self.displayed_text += text[self.letter_index]
                     self.letter_index += 1
                     self.last_time = current_time

    def reset_typing(self):
         self.displayed_text = ""
         self.letter_index = 0
         self.last_time = pygame.time.get_ticks()


 # =========draw for dialog box ,text ,character, word effect ======   
    def draw(self,screen):
        
        #only draw when in talking mode
        if self.talking and self.step < len(self.story_data):
           entry = self.story_data[self.step]

           text = entry.get("text","")
           speaker = entry.get("speaker","npc")
                

            #let the dialog box on the center and put below
           dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
           dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20


           #calculate max midth for text inside
           #adjust values based on dialog box size
           text_max_width = self.dialog_box_img.get_width() - 150 #50 pixel padding each side

           if "choice" in entry:
             max_options_display = 3

             dialog_center_x = dialog_x + self.dialog_box_img.get_width()// 2

          
             
             for i , option in enumerate(entry["choice"][:max_options_display]):
                     color = (255,0,0) if i == self.option_selected else (0,0,0)
                     option_y =  dialog_y+ 60 + i * 60
                     if option_y < screen.get_height() - 40:
                      draw_text(screen, option["option"],30,color,dialog_center_x,option_y,center= True)


           else:
           
             if speaker == "npc":
                portrait = self.portrait
                name_to_display = self.npc.name
                portrait_pos =(dialog_x + 800,dialog_y - 400)
             else:
                portrait = self.player_portrait
                name_to_display = "You"
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
           if self.letter_index < len(text):
                if current_time - self.last_time > self.letter_delay:
                     self.displayed_text += text[self.letter_index]
                     self.letter_index += 1
                     self.last_time = current_time
          

           draw_text(screen,self.displayed_text,30,(0,0,0),dialog_x + self.dialog_box_img.get_width()//2 - 20 ,dialog_y + self.dialog_box_img.get_height()//2 ,center = True,max_width=text_max_width)


    def handle_option_selection(self,keys):
        if (self.talking and self.options and self.step <len(self.story_data) and self.letter_index >= len(self.story_data[self.step].get("text",""))):
                   option_key_pressed = False
                   if keys[pygame.K_w]:
                      self.option_selected = (self.option_selected - 1) % len(self.options)
                      option_key_pressed = True
                    
                   if keys[pygame.K_s]:
                      self.option_selected = (self.option_selected + 1) % len(self.options)
                      option_key_pressed = True
                   if keys[pygame.K_e]:
                      selected_option = self.options[self.option_selected]
                      next_target = selected_option["next"]

                      if isinstance(next_target,int):
                         self.step = next_target
                      else:
                         self.story_data = self.npc_data.get(next_target,[])
                         self.step = 0

                      self.options =[]
                      self.reset_typing()
                   if option_key_pressed:
                       pygame.time.delay(50)

    def handle_space(self,keys):
         if not self.talking:
              self.talking = True
              self.step = 0
              self.reset_typing()
              return
         
         if self.step <len(self.story_data):
              entry = self.story_data[self.step]
              text = entry.get("text","")

              if self.letter_index <len (text):
                   self.letter_index = len(text)
                   self.displayed_text = text

              else:
                   if self.options:
                     pass
                  
           
                   else:
                    if "next" in entry:
                      next_target = entry["next"]

                      if isinstance(next_target,int):
                          
                          self.step = next_target
                      else:
                          self.story_data = self.npc_data.get(next_target,[])
                          self.step = 0
                      self.reset_typing()

                    else:
                        self.step += 1
                        if self.step >= len(self.story_data):
                            self.talking = False
                            self.step = 0
                        else:
                           self.reset_typing()
                

         

# =============text setting================
def draw_text(surface,text,size,color,x,y,center = False,max_width = None):
    font = pygame.font.SysFont('Comic Sans MS', size)
    text_surface = font.render(text, True, color)

    # If no max width is specified or text is short, render it normally
    if max_width is None or font.size(text)[0] <= max_width:
        text_surface = font.render(text,True,color)
        text_rect = text_surface.get_rect()# set the words location (in center)
        if center:
            text_rect.center = (x,y)
        else:
            text_rect.topleft =(x,y)
        surface.blit(text_surface, text_rect)
        return y + text_rect.height #return the y position after the text
    
    #word wrap implementation
    words = text.split(' ')
    current_line = ""
    line_y = y
    line_height = font.size('Tg')[1]#height of a typical line

    for word in words:
        test_line = current_line + word + " "
        # test if this line woy=uld be too wide
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            #render the current line
            if current_line:
                line_surface = font.render(current_line,True,color)
                line_rect = line_surface.get_rect()
                if center:
                    line_rect.midtop = (x,line_y)
                    surface.blit(line_surface,line_rect)
                    line_y += line_height
                #start a new line with the current word
                current_line = word + " "

    if current_line:
        line_surface = font.render(current_line,True,color)
        line_rect = line_surface.get_rect()
        if center:
            line_rect.midtop =(x,line_y)
        else:
            line_rect.topleft = (x,line_y)
        surface.blit(line_surface, line_rect)

    return line_y + line_height#return the y position after all text
    
   


      
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
          if npc.rect.colliderect(player.rect) or dialogue.talking:
            
           if keys[pygame.K_SPACE] and space_released:
               space_released = False
               dialogue.handle_space(keys)

           dialogue.handle_option_selection(keys)
          

           if not keys[pygame.K_SPACE]:
                space_released = True
          else :
               dialogue.talking = False
               dialogue.options =[]


          if dialogue.talking:
              dialogue.update()
              dialogue.draw(screen)
          
          pygame.display.update()
          clock.tick(FPS)    
          

pygame.quit()
sys.exit()
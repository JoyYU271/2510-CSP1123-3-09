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



npc_list =["Nuva"]
shown_dialogues = {}
selected_options = {}

#============ Dialogue System =============
class dialog:
    def __init__(self,npc,player):
        super().__init__()

        #load dialog box img n set transparency
        self.dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()
        self.dialog_box_img.set_alpha(200)

        # character portrait selection based on NPC name
        if npc.name == "Nuva":
             self.portrait = pygame.image.load("picture/Character Dialogue/Nurse.png").convert_alpha()
        elif npc.name == "Dean":
            self.portrait = pygame.image.load("picture/Character Dialogue/Dean.png").convert_alpha()
        elif npc.name == "Zheng":
            self.portrait = pygame.image.load("picture/Character Dialogue/Patient1.png").convert_alpha()
        elif npc.name == "Emma":
            self.portrait = pygame.image.load("picture/Character Dialogue/Patient2.png").convert_alpha()
        elif npc.name == "player":
            self.player_portrait = pygame.image.load("picture/Character Dialogue/Doctor.png").convert_alpha()

        # always load player portrait
        self.player_portrait = pygame.image.load("picture/Character Dialogue/Doctor.png").convert_alpha()

        self.player = player
        self.npc_name = npc.name
        self.npc = npc
        self.dialogue_trigger_distance = 50

        #get NPC's dialogue data from Json
        self.npc_data = all_dialogues.get(self.npc_name)

         #dialogue state variacbles
        self.current_story = "chapter_3" #default chapter
        self.story_data = self.npc_data.get(self.current_story,[])
        self.step = 0 # present current sentence
        global shown_dialogues
        self.shown_dialogues = shown_dialogues #track dialogues that have been shown

        # sentences typing effect
        self.displayed_text = "" #display current word
        self.letter_index = 0  #current letter position in text
        self.last_time = pygame.time.get_ticks() #time tracking for typing speed
        self.letter_delay = 45

        self.options = [] #dialogue options when choices present
        self.option_selected = 0 #current selected option index
        self.talking = False # is it talking
        self.first_time_done  = False

        self.key_w_released = True
        self.key_s_released = True
        self.key_e_released = True

        self.cg_images = []
        self.cg_index = 0
        self.showing_cg = False

        self.entry = None
        self.chapter_end = False
        self.cg_shown = False

        if self.current_story in self.npc.shown_options and self.npc.shown_options[self.current_story]:
            self.current_story = "repeat_only"
       
             

    def update(self,event_list): 

        if self.showing_cg:
             for event in event_list:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                     self.fade(screen,fade_in=False,cg_list=self.cg_images)

                     self.cg_index += 1

                     if self.cg_index >= len(self.cg_images):
                         self.showing_cg = False
                         self.end = True
                     else:
                         self.fade(screen,fade_in=True,cg_list=self.cg_images)

        #only update if in dialogue n not at the end
        if self.talking and self.step < len(self.story_data):
             self.entry = self.story_data[self.step] # current dialogue entry
             

             if isinstance(self.entry,dict) and "cg" in self.entry:
                 
                 self.cg_images = []
                 self.cg_index = 0
                 self.showing_cg = False

                 self.cg_images = [pygame.image.load(path).convert() for path in self.entry["cg"]]
                 self.cg_index = 0
                 self.showing_cg = True
                 self.fade(screen,fade_in = True,cg_list=self.cg_images)
                 self.step += 1
                 return

             text = self.entry.get("text","") #get text
             
             #check if this is a choice entry

             if "choice" in self.entry :
              self.options = self.entry.get("choice",[])
             else:
                 self.options = []
                 

             # text typing effect
             current_time = pygame.time.get_ticks()
             if self.letter_index < len(text):
                if current_time - self.last_time > self.letter_delay:
                     self.displayed_text += text[self.letter_index]
                     self.letter_index += 1
                     self.last_time = current_time

        
        if isinstance(self.entry,dict) and self.entry.get("type") == "ending":
            self.chapter_end = True    

    def reset_typing(self):
         #reset text displayed for a new line 
         self.displayed_text = ""
         self.letter_index = 0
         self.last_time = pygame.time.get_ticks()


    def draw(self,screen):

        # calculate the distance between player n NPC
        player_pos = pygame.Vector2(self.player.rect.center)
        npc_pos = pygame.Vector2(self.npc.rect.center)
        distance = player_pos.distance_to(npc_pos)

        if distance < 50 and  not self.talking and self.step >= len(self.story_data):
            key_hint_font = pygame.font.SysFont('Comic Sans MS',20)
            key_hint_text = key_hint_font.render("Press Space to talk", True,(0,0,0))
            key_hint_rect = key_hint_text.get_rect(center=(self.npc.rect.centerx,self.npc.rect.top - 30))
            screen.blit(key_hint_text,key_hint_rect)

        if self.showing_cg:
               
               if self.cg_index < len(self.cg_images):
                   screen.blit(self.cg_images[self.cg_index],(0,0))
               else:
                   self.showing_cg = False
                   self.cg_index = 0
                   self.cg_images = []
 
        
        #only draw when in talking mode n not finished talk
        if self.talking and self.step < len(self.story_data):
           entry = self.story_data[self.step]

           text = entry.get("text","")
           speaker = entry.get("speaker","npc") # default speaker is NPc
                
           #let the dialog box on the center and put below
           dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
           dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20

           #calculate text width with limit for wrapping
           text_max_width = self.dialog_box_img.get_width() - 300 #pixel padding each side

           # choose portrait n position based on speaker
           if speaker == "narrator":
               name_to_display = " "
               screen.blit(self.dialog_box_img, (dialog_x, dialog_y))
               
           elif speaker == "npc":
                   portrait = self.portrait
                   name_to_display = self.npc.name
                   portrait_pos =(dialog_x + 800,dialog_y - 400) #right side
                   screen.blit(portrait,portrait_pos)
           else:
                   portrait = self.player_portrait
                   name_to_display = "You"
                   portrait_pos = (dialog_x +20,dialog_y - 400) #left side
                   screen.blit(portrait,portrait_pos)

            #draw Character portraits n dialog box
          
           screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

           #draw speaker name
           if name_to_display :
               draw_text(screen,name_to_display,40,(0,0,0),dialog_x + 150, dialog_y + 5)

           #draw choice options if present
           if self.options:
             max_options_display = 3 #display at most 3 options

             dialog_center_x = dialog_x + self.dialog_box_img.get_width()// 2

             for i , option in enumerate(entry["choice"][:max_options_display]):
                     # red for selected option, black for others
                     color = (255,0,0) if i == self.option_selected else (0,0,0)
                     option_y =  dialog_y+ 60 + i * 45

                     if option_y < screen.get_height() - 10: #ensure option is on screen
                        draw_text(screen, option["option"],30,color,dialog_center_x,option_y,center= True)

             key_hint_font = pygame.font.SysFont('Comic Sans MS', 20)
             key_hint_text1 = key_hint_font.render("Press W/S to select,",True,(0,0,0))
             key_hint_rect1 = key_hint_text1.get_rect(bottomright=(dialog_x + self.dialog_box_img.get_width() - 90,  dialog_y + self.dialog_box_img.get_height() - 40))
             key_hint_text2 = key_hint_font.render("  E to comfirm",True,(0,0,0))
             key_hint_rect2 = key_hint_text2.get_rect(bottomright=(dialog_x + self.dialog_box_img.get_width() - 90,  dialog_y + self.dialog_box_img.get_height() - 20))

             screen.blit(key_hint_text1,key_hint_rect1)
             screen.blit(key_hint_text2,key_hint_rect2)
          
           # draw dialogue text 
           draw_text(screen,self.displayed_text,30,(0,0,0),dialog_x + self.dialog_box_img.get_width()//2  ,dialog_y + self.dialog_box_img.get_height()//2 - 38,center = True,max_width=text_max_width)

           #only show space hint if no options are present 
           if not self.options:
               hint_font = pygame.font.SysFont('Comic Sans MS', 20)
               hint_text = hint_font.render("Press SPACE to continue", True, (0,0,0))
               hint_rect = hint_text.get_rect(bottomright=(dialog_x + self.dialog_box_img.get_width() - 90,  dialog_y + self.dialog_box_img.get_height() - 20))
               screen.blit(hint_text, hint_rect)
    

    def fade (self,screen,cg_list,fade_in =True):
        
        for original_image in cg_list:
         
            cg_image = pygame.transform.scale(original_image ,(screen.get_width(),screen.get_height()))

            if fade_in:       #fade in
             for alpha in range (0,255,10):
                screen.fill((0,0,0))
                cg_image.set_alpha(alpha)
                screen.blit(cg_image,(0,0))
                pygame.display.update()
                pygame.time.delay(30)

          
            else:#fade out 
             for alpha in range(255,0,-10):
                screen.fill((0,0,0))
                cg_image.set_alpha(alpha)
                screen.blit(cg_image,(0,0))
                pygame.display.update()
                pygame.time.delay(30)

    def get_current_cg(self):
        path = self.cg_images[self.cg_index]
        image = pygame.image.load(path).convert()
        return pygame.transform.scale(image,(screen.get_width(),screen.get_height(  )))

        

    def handle_option_selection(self,keys):

        # only handle if in dialogue with options n text is full displayed
        if (self.talking and self.options and self.step <len(self.story_data) and self.letter_index >= len(self.story_data[self.step].get("text",""))):
                  
                   # move up in options list with W key
                   if keys[pygame.K_w] and self.key_w_released:
                      self.option_selected = (self.option_selected - 1) % len(self.options)
                      self.key_w_released = False
                   if not keys[pygame.K_w]:
                       self.key_w_released = True
                    
                    #Move down in options list with S key
                   if keys[pygame.K_s] and self.key_s_released:
                      self.option_selected = (self.option_selected + 1) % len(self.options)
                      self.key_s_released = False
                   if not keys[pygame.K_s]:
                       self.key_s_released = True
                       
                    # comfirm selection with E Key
                   if keys[pygame.K_e] and self.key_e_released:
                      selected_option = self.options[self.option_selected]
                      self.npc.shown_options[self.current_story] = True
                      next_target = selected_option["next"]

                      if next_target == "back_reality":
                          self.load_back_reality()
                      elif next_target == "check_sub_end":
                          self.check_sub_end_conditions()
                      elif next_target.startswith("sub_end_"):
                          self.load_sub_ending(next_target) #display sub ending
                      elif next_target.startswith("end_"):
                          self.load_ending(next_target) #display main ending
                      else:
                          self.load_dialogue(self.npc_name,next_target)

                      self.options =[]
                      self.reset_typing()
                      self.key_e_released = False
                   if not keys[pygame.K_e]:
                       self.key_e_released = True


    def load_back_reality(self):
        self.displayed_text = ""
        self.letter_index = 0
        self.check_sub_end_conditions()
        pygame.display.update()

      

    def handle_space(self,keys):
         
         #start dialogue if not talked
         if not self.talking:
              self.talking = True
              self.load_dialogue(self.npc_name,self.current_story)
              return
         
         #process current dialogue step
         if self.step <len(self.story_data):
              entry = self.story_data[self.step]
              text = entry.get("text","")

              #mark dialogue as shown if needed
              if "shown" in entry and entry["shown"] == False:
                  dialogue_id = f"{self.npc_name}_{self.current_story}_{self.step}"
                  self.shown_dialogues[dialogue_id] = True

              if "chapter_ending" in entry:
             #save which ending was chosen
                  global player_choices, showing_chapter_ending, ending_start_time, ending_complete_callback
                  player_choices["chapter_1_ending"] = entry["chapter_ending"]
                  
             #set up the ending screen
                  showing_chapter_ending = True
                  ending_start_time = pygame.time.get_ticks()

             #set next chapter after ending
                  next_chapter = entry["next_chapter"]

             #run when ending screen done
                  def ending_complete():
                      global start_chapter 
                      start_chapter(next_chapter, True)

                  ending_complete_callback = ending_complete
                  self.talking = False
                  return

              # if test is typing, complete it immdiately
              if self.letter_index <len (text):
                   self.letter_index = len(text)
                   self.displayed_text = text
              else:
                   
                   #if have options ,nothing to do( option selection is at other part of code)
                   if self.options:
                     self.options = []
                  
                   else:
                    if "next" in entry:
                      next_target = entry["next"]

                      if isinstance(next_target,int):
                          
                          #if next_target = integer, jump to that step within same chapter
                          self.step = next_target
                      else:
                         #if next_target = string,it's the name of new chapter to load
                          self.current_story = next_target
                          self.story_data = self.npc_data.get(next_target,[])
                          self.step = 0
                          self.load_dialogue(self.npc_name, next_target)
                          

                    else:
                        #if there is no "next",proceed to the next dialogue step
                        self.step += 1
                        if self.step >= len(self.story_data):
                            #end the dialogue if reached the end
                            self.talking = False
                            self.step = 0
                        else:
                           #reset typing effect for the next dialogue entry
                           self.reset_typing()
    

    def load_dialogue(self,npc_name,chapter):

        self.options = []
        #update NPC detials
        self.npc_name = npc_name
        self.npc_data = all_dialogues.get(self.npc_name,{})
        self.current_story = chapter
        self.story_data = self.npc_data.get(self.current_story,[])
        filtered_story_data = []

        # filter out already shown dialogues marked with "shown":false ( in json)
        
        for i,entry in enumerate(self.story_data):
            dialogue_id = f"{self.npc_name}_{self.current_story}_{i}"

            if ("shown" not in entry or entry["shown"] != False) or (dialogue_id not in self.shown_dialogues):
                filtered_story_data.append(entry)

            elif self.npc_name == "Nuva" and self.current_story == "chapter_1_common" and entry.get("text") == "She is waiting in your office,you can head over when you are ready":
                if dialogue_id not in self.shown_dialogues:
                    filtered_story_data.append(entry)
   
        # set filtered dialogue n reset state
        self.story_data = filtered_story_data
        self.step = 0
        self.reset_typing()

        if filtered_story_data:
            first_entry = filtered_story_data[0]

            if "cg" in first_entry:
                paths = first_entry["cg"] if isinstance(first_entry["cg"], list) else [first_entry["cg"]]
                self.cg_images = [pygame.image.load(path) for path in paths]
                self.cg_index = 0
                self.showing_cg = True
             

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
    

#===========NPCs==============
class NPC(pygame.sprite.Sprite):
    def __init__(self,x,y,name,image_path = None):
        super().__init__()

        if image_path is None:
            if name == "Nuva":
                image_path = 'picture/Character QQ/Nurse idle.png'
            elif name == "Dean":
                image_path = 'picture/Character QQ/Dean idle.png'
            elif name == "Zheng":
                image_path = 'picture/Character QQ/Zheng idle.png'
            elif name =="Emma":
                image_path = 'picture/Character QQ/Emma idle.png'
            elif name == "John":
                image_path = 'picture/Character QQ/John idle.png'
            elif name =="Police":
                image_path = 'picture/Character QQ/Police idle.png'
        
        
        self.image = pygame.image.load(image_path).convert_alpha()
        self.world_pos = pygame.Vector2(x,y) #for world coordinate
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.name = name
        self.dialog = None
        self.shown_options = {}

# to manage multiples NPCs
class NPCManager:
    def __init__(self):
        self.npcs = []

    def add_npc(self,npc):
        self.npcs.append(npc)
    
    def get_nearest_npc(self,player):
        nearest_npc = None
        min_distance = float('inf')

        for npc in self.npcs:

            if npc.rect.colliderect(player.rect):

                dx = npc.rect.centerx - player.rect.centerx
                dy = npc.rect.centery - player.rect.centery
                distance = (dx**2 + dy**2)**0.5

                if distance< min_distance:
                    min_distance = distance
                    nearest_npc = npc
        return nearest_npc



npc_manager = NPCManager()

nuva = NPC(600,500,"Nuva")
dean = NPC(800,500,"Dean")
patient1 = NPC(1000,500,"Zheng")
patient2 = NPC(400,500,"Emma")

current_dialogue = None

npc_manager.add_npc(nuva)
npc_manager.add_npc(dean)
npc_manager.add_npc(patient1)
npc_manager.add_npc(patient2)

current_dialogue = None
show_cg = False
cg_image = None
cg_loaded = False



run = True
while run:
          
          draw_bg(screen)

          if not current_dialogue or not current_dialogue.talking:
               is_moving = player.move(moving_left,moving_right)
               player.update_animation(is_moving)
          else:
              is_moving = False
              player.update_animation(is_moving)
          
          for npc in npc_manager.npcs:
              screen.blit(npc.image,npc.rect)
              player_pos = pygame.Vector2(player.rect.center)
              npc_pos = pygame.Vector2(npc.rect.center)
              if player_pos.distance_to(npc_pos) < 100 :
                    font = pygame.font.SysFont('Comic Sans MS', 20)
                    hint_text = font.render("Press SPACE to talk", True, (0, 0, 0))
                    hint_rect = hint_text.get_rect(center=(npc.rect.centerx, npc.rect.top - 20))
                    screen.blit(hint_text, hint_rect)


              if npc.dialog:
                  npc.dialog.draw(screen)

          player.draw(screen)
          
          moving_left,moving_right,run =  keyboard_input(moving_left, moving_right, run)

          nearest_npc = npc_manager.get_nearest_npc(player)

          #=====space======
          keys = pygame.key.get_pressed()
          if nearest_npc or (current_dialogue and current_dialogue.talking):
              if nearest_npc and (current_dialogue is None or current_dialogue.npc != nearest_npc):
                  current_dialogue = dialog(nearest_npc,player)
            
              if keys[pygame.K_SPACE] and space_released:
                  space_released = False
                  if current_dialogue:
                     current_dialogue.handle_space(keys)

              if current_dialogue:
                 current_dialogue.handle_option_selection(keys)
          

              if not keys[pygame.K_SPACE]:
                  space_released = True

          elif current_dialogue:
               current_dialogue.talking = False
               current_dialogue.options = []

            
          if current_dialogue and current_dialogue.talking:
              current_dialogue.update(pygame.event.get())
              current_dialogue.draw(screen)

          if current_dialogue and current_dialogue.chapter_end and not cg_loaded :
              if "cg" in current_dialogue.entry:
                  cg_image = pygame.image.load(current_dialogue.entry["cg"])
                  show_cg = True
                  cg_loaded = True


          if show_cg and cg_image:
              screen.blit(cg_image,(0,0))
   
          pygame.display.update()
          clock.tick(FPS)    
          

pygame.quit()
sys.exit()
import pygame
import sys
from pygame.locals import *
from character_movement import *
import json
from ui_components import Button, get_font

current_text_size = 30
click_sound = pygame.mixer.Sound("main page/click1.wav") 

current_dialogue_instance = None

def run_dialogue(text_size=None,language="EN",bgm_vol=0.5,sfx_vol=0.5):
    global current_dialogue_instance

    pygame.init()

    screen_width = 1280
    screen_height = 720

    pygame.mixer.music.set_volume(bgm_vol)
    pygame.mixer.music.load("bgm/intro.mp3")
    pygame.mixer.music.set_volume(bgm_vol)
    pygame.mixer.music.play(-1)

    backmain_img = pygame.image.load("backmain.png").convert_alpha()
    backmain_button = Button(backmain_img, (1100, 80), scale=0.2)

    global current_text_size
    if text_size is not None:
        current_text_size = text_size

    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    FPS = 60

    player = doctor(400,500,4.5) 
    player.name = "You" # remember to put in class doctor
    moving_left = False
    moving_right = False


    font = pygame.font.SysFont('Comic Sans MS',30)
    space_released = True # control the dialog will not happen continuously when press key space


    if language == "CN":
        dialogue_file = 'NPC_dialog/NPC_CN.json'
    else:
        dialogue_file = 'NPC_dialog/NPC.json'

    with open(dialogue_file, 'r', encoding='utf-8') as f:
        all_dialogues = json.load(f)

    current_chapter = "chapter_1"

    npc_list =["Nuva"]

    npc_manager = NPCManager()

    nuva = NPC(600,500,"Nuva")
    dean = NPC(800,500,"Dean")

    current_dialogue = None

    npc_manager.add_npc(nuva)
    npc_manager.add_npc(dean)

    current_dialogue = None


    run = True
    while run:

            draw_bg(screen)
            backmain_button.draw(screen)          

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                   pygame.quit()
                   sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if backmain_button.checkForInput(pygame.mouse.get_pos()):
                       click_sound.play()
                       pygame.mixer.music.stop()
                       return

            is_moving = player.move(moving_left,moving_right)
            player.update_animation(is_moving)
        
            for npc in npc_manager.npcs:
                screen.blit(npc.image,npc.rect)

            player.draw(screen)
            
            moving_left,moving_right,run =  keyboard_input(moving_left, moving_right, run)


            nearest_npc = npc_manager.get_nearest_npc(player)

            #=====space======
            keys = pygame.key.get_pressed()
            if nearest_npc or (current_dialogue and current_dialogue.talking):
                if nearest_npc and (current_dialogue is None or current_dialogue.npc != nearest_npc):
                    current_dialogue = dialog(nearest_npc, player, all_dialogues, sfx_vol)
                    current_dialogue_instance = current_dialogue
                
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
                current_dialogue.update()
                current_dialogue.draw(screen)
            

            pygame.display.update()
            clock.tick(FPS)





#============dialog box =============
class dialog:
    def __init__(self,npc,player,all_dialogues,sfx_vol=0.5):
        super().__init__()


        self.sounds = {
            "phone_typing": pygame.mixer.Sound("sfx/phone_typing.wav"),
            "footsteps": pygame.mixer.Sound("sfx/footsteps.wav"),
        }

        self.sfx_vol = sfx_vol

        for sound in self.sounds.values():
            sound.set_volume(sfx_vol)


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
        elif npc.name == "John":
            self.portrait = pygame.image.load("picture/Character Dialogue/Patient3.png").convert_alpha()
        elif npc.name == "Police":
            self.portrait = pygame.image.load("picture/Character Dialogue/Police.png").convert_alpha()

        # always load player portrait
        self.player_portrait = pygame.image.load("picture/Character Dialogue/Doctor.png").convert_alpha()

        self.player = player
        self.npc_name = npc.name
        self.npc = npc

        #get NPC's dialogue data from Json
        self.all_dialogues = all_dialogues
        self.npc_data = self.all_dialogues.get(self.npc_name)

         #dialogue state variacbles
        self.current_story = "chapter_1" #default chapter
        self.story_data = self.npc_data.get(self.current_story,[])
        self.step = 0 # present current sentence
        self.shown_dialogues = {} #track dialogues that have been shown
        
        

        # sentences typing effect
        self.displayed_text = "" #display current word
        self.letter_index = 0  #current letter position in text
        self.last_time = pygame.time.get_ticks() #time tracking for typing speed
        self.letter_delay = 45

        self.options = [] #dialogue options when choices present
        self.option_selected = 0 #current selected option index
        self.talking = False # is it talking

        self.key_w_released = True
        self.key_s_released = True
        self.key_e_released = True
        
        self.currently_playing_sfx = None
        self.sound_played_for_current_step = False

    
    def update_sfx_volume(self, new_volume):
        self.sfx_vol = new_volume
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_vol)
            
  
    def stop_all_sfx(self):
        for sound in self.sounds.values():
            sound.stop()
        self.currently_playing_sfx = None
    


#================ Update ============
    def update(self): 
        #only update if in dialogue n not at the end
        if self.talking and self.step < len(self.story_data):
             entry = self.story_data[self.step] # current dialogue entry

             text = entry.get("text","") #get text

             if entry.get("sound_stop"):
                self.stop_all_sfx()

             if "sound" in entry and not self.sound_played_for_current_step:
                sound_name = entry["sound"]
                if sound_name in self.sounds:
                    self.sounds[sound_name].play()
                    self.currently_playing_sfx = sound_name
                self.sound_played_for_current_step = True
             



             #check if this is a choice entry
             if "choice" in entry :
              self.options = entry.get("choice",[])
             else:
                 self.options = []

             # text typing effect
             current_time = pygame.time.get_ticks()
             if self.letter_index < len(text):
                if current_time - self.last_time > self.letter_delay:
                     self.displayed_text += text[self.letter_index]
                     self.letter_index += 1
                     self.last_time = current_time

    def reset_typing(self):
         #reset text displayed for a new line 
         self.displayed_text = ""
         self.letter_index = 0
         self.last_time = pygame.time.get_ticks()

         self.sound_played_for_current_step = False 

 # ================ Draw ======================
    def draw(self,screen):
        
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
           if speaker == "npc":
                portrait = self.portrait
                name_to_display = self.npc.name
                portrait_pos =(dialog_x + 800,dialog_y - 400) #right side
           else:
                portrait = self.player_portrait
                name_to_display = "You"
                portrait_pos = (dialog_x +20,dialog_y - 400) #left side

            #draw Character portraits n dialog box
           screen.blit(portrait,portrait_pos)
           screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

           #draw speaker name
           name_to_display = self.npc.name if speaker == "npc" else self.player.name
           draw_text(screen, name_to_display, None, (0,0,0), dialog_x + 200, dialog_y + 10)

           #draw choice options if present
           if "choice" in entry:
             max_options_display = 3 #display at most 3 options

             dialog_center_x = dialog_x + self.dialog_box_img.get_width()// 2

             for i , option in enumerate(entry["choice"][:max_options_display]):
                     # red for selected option, black for others
                     color = (255,0,0) if i == self.option_selected else (0,0,0)
                     option_y =  dialog_y+ 60 + i * 60
                     if option_y < screen.get_height() - 40:
                      draw_text(screen, option["option"], None, color, dialog_center_x, option_y, center=True)

          
           # words come out one by one effect
           current_time = pygame.time.get_ticks()
           if self.letter_index < len(text):
                if current_time - self.last_time > self.letter_delay:
                     self.displayed_text += text[self.letter_index]
                     self.letter_index += 1
                     self.last_time = current_time
          


           draw_text(screen, self.displayed_text, None, (0,0,0), dialog_x + self.dialog_box_img.get_width()//2, dialog_y + self.dialog_box_img.get_height()//2 - 15, center=True, max_width=text_max_width)


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
                      next_target = selected_option["next"]

                      #handle value jumps n chapter change
                      if isinstance(next_target,int):
                         self.step = next_target
                      else:
                         self.load_dialogue(self.npc_name, next_target)

                      self.options =[]
                      self.reset_typing()
                      self.key_e_released = False
                   if not keys[pygame.K_e]:
                       self.key_e_released = True
                       

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

              # if test is typing, complete it immdiately
              if self.letter_index <len (text):
                   self.letter_index = len(text)
                   self.displayed_text = text
              else:
                   
                   #if have options ,nothing to do( option selection is at other part of code)
                   if self.options:
                     pass
                  
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
                          self.reset_typing()

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
        #update NPC detials
        self.npc_name = npc_name
        self.npc_data = self.all_dialogues.get(self.npc_name, {})
        self.current_story = chapter
        self.story_data = self.npc_data.get(self.current_story,[])

        # filter out already shown dialogues marked with "shown":false ( in json)
        filtered_story_data = []
        for i,entry in enumerate(self.story_data):
            dialogue_id = f"{self.npc_name}_{self.current_story}_{i}"

            if "shown" not in entry or entry["shown"] != False or dialogue_id not in self.shown_dialogues:
                filtered_story_data.append(entry)

        # set filtered dialogue n reset state
        self.story_data = filtered_story_data
        self.step = 0
        self.reset_typing()

        self.sound_played_for_current_step = False 

    def update_font_size(self, new_size):
        global current_font_size
        current_font_size = new_size            

         

# =============text setting================
def draw_text(surface, text, size=None, color=(0,0,0), x=0, y=0, center=False, max_width=None):
    global current_text_size
    font_size = size if size is not None else current_text_size
    font = pygame.font.Font('fonts/NotoSansSC-Regular.ttf', font_size)


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
  


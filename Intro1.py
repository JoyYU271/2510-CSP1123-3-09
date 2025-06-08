import pygame
import sys
from pygame.locals import *
import json
import character_movement
import shared
from shared import CameraGroup


# Load object data
with open("objects.json", "r") as f:
    object_data = json.load(f)

with open("object_dialogue.json") as f:
    object_dialogue = json.load(f)

pygame.init()

# Set up display
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Chapter Intro Test")
shared.screen = screen
clock = pygame.time.Clock()
FPS = 60

# Load JSON data
with open('NPC_dialog/NPC.json', 'r', encoding='utf-8') as f:
        all_dialogues = json.load(f)

dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()

moving_left = False
moving_right = False

npc_list =["Nuva"]
shown_dialogues = {}
selected_options = {}

cutscene_active = False
cutscene_speed = 3 #pixel per frame



class dialog:
    def __init__(self,npc,player):
        #Remove super().__init__()

        #load dialog box img n set transparency
        self.dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()
        self.dialog_box_img.set_alpha(200)

        # character portrait selection based on NPC name
        potrait_paths = {
            "Nuva": "picture/Character Dialogue/Nurse.png",
            "Dean": "picture/Character Dialogue/Dean.png",
            "Zheng": "picture/Character Dialogue/Patient1.png",
            "Emma": "picture/Character Dialogue/Patient2.png",
        }

        # always load player portrait
        portrait_path = potrait_paths.get(npc.name)
        if portrait_path:
            self.portrait = pygame.image.load(portrait_path).convert_alpha()
        else:
            self.portrait = pygame.Surface((1,1)) #fallback or error handling

        self.player_portrait = pygame.image.load("picture/Character Dialogue/Doctor.png").convert_alpha()

        self.player = player
        self.npc_name = npc.name
        self.npc = npc

        #get NPC's dialogue data from Json
        self.npc_data = all_dialogues.get(self.npc_name)

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


    def update(self): 
        #only update if in dialogue n not at the end
        if self.talking and self.step < len(self.story_data):
             entry = self.story_data[self.step] # current dialogue entry

             text = entry.get("text","") #get text
             
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
           name_to_display if speaker == "npc" else self.player.name #change here
           draw_text(screen,name_to_display,40,(0,0,0),dialog_x + 200, dialog_y + 10)

           #draw choice options if present
           if "choice" in entry:
             max_options_display = 3 #display at most 3 options

             dialog_center_x = dialog_x + self.dialog_box_img.get_width()// 2

             for i , option in enumerate(entry["choice"][:max_options_display]):
                     # red for selected option, black for others
                     color = (255,0,0) if i == self.option_selected else (0,0,0)
                     option_y =  dialog_y+ 60 + i * 60

                     if option_y < screen.get_height() - 40: #ensure option is on screen
                        draw_text(screen, option["option"],30,color,dialog_center_x,option_y,center= True)
          
           # draw dialogue text 
           draw_text(screen,self.displayed_text,30,(0,0,0),dialog_x + self.dialog_box_img.get_width()//2  ,dialog_y + self.dialog_box_img.get_height()//2 - 15 ,center = True,max_width=text_max_width)


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
        self.npc_data = all_dialogues.get(self.npc_name,{})
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

        if self.current_story in self.shown_dialogues:
            self.story_data = []
        else:
            self.shown_dialogues[self.current_story] = True
        

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

        self.flip = False

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

class SimpleChapterIntro:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.active = False
        self.background = None
        self.dialogue = []
        self.step = 0
        self.last_time = 0
        self.delay = 3000  # 3 seconds between lines
        self.typing_index = 0
        self.displayed_text = ""
        self.typing_delay = 45
        self.typing_last_time = 0
        self.fade_alpha = 0
        self.fade_speed = 5
        self.fading_in = True
        self.fading_out = False
        self.completed_callback = None
        self.space_released = True
    
    def start(self, chapter):
        print(f"Starting intro for chapter: {chapter}")
        self.active = True
        
        # Load background
        try:
            self.background = pygame.image.load("picture/Map Art/outside.png").convert()
            print("Background loaded successfully")
        except Exception as e:
            print(f"Error loading background: {e}")
        
        # Get dialogue from JSON
        self.dialogue = all_dialogues.get("intro", {}).get(chapter, [])
        if not self.dialogue:
            self.dialogue = [{"speaker": "narrator", "text": f"Chapter {chapter} begins..."}]
       
        
        # Reset state
        self.step = 0
        self.last_time = pygame.time.get_ticks()
        self.typing_index = 0
        self.displayed_text = ""
        self.typing_last_time = pygame.time.get_ticks()
        self.fade_alpha = 0
        self.fading_in = True
        self.fading_out = False
    
    def update(self, keys):
        if not self.active:
            return False
        
        # Handle fading in
        if self.fading_in:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fading_in = False
            return True
        
        # Handle fading out
        if self.fading_out:
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                self.active = False
                if self.completed_callback:
                    self.completed_callback()
                return False
            return True
        
        # Check if intro is complete
        if self.step >= len(self.dialogue):
            self.fading_out = True
            return True
        
        # Handle space key
        if keys[pygame.K_SPACE] and self.space_released:
            self.space_released = False
            
            # If still typing, complete the text immediately
            if self.typing_index < len(self.dialogue[self.step].get("text", "")):
                self.typing_index = len(self.dialogue[self.step].get("text", ""))
                self.displayed_text = self.dialogue[self.step].get("text", "")
            else:
                # Move to next dialogue line
                self.step += 1
                self.typing_index = 0
                self.displayed_text = ""
                self.last_time = pygame.time.get_ticks()
        
        if not keys[pygame.K_SPACE]:
            self.space_released = True
        
        # Process current dialogue
        if self.step < len(self.dialogue):
            entry = self.dialogue[self.step]
            current_text = entry.get("text", "")
            
            # Auto-advance after delay
            current_time = pygame.time.get_ticks()
            if (self.typing_index >= len(current_text) and 
                current_time - self.last_time > self.delay):
                self.step += 1
                self.typing_index = 0
                self.displayed_text = ""
                self.last_time = current_time
            
            # Typing effect
            if self.typing_index < len(current_text):
                if current_time - self.typing_last_time > self.typing_delay:
                    self.displayed_text += current_text[self.typing_index]
                    self.typing_index += 1
                    self.typing_last_time = current_time
        
        return True
    
    def draw(self, screen):
        if not self.active:
            return
        
        # Draw background with fade
        screen_rect = screen.get_rect()
        bg_rect = self.background.get_rect(center=screen_rect.center)
        
        # Fill with black first
        screen.fill((0, 0, 0))
        
        # Create copy with adjusted alpha
        temp_bg = self.background.copy()
        temp_bg.set_alpha(self.fade_alpha)
        screen.blit(temp_bg, bg_rect)
        
        # Don't draw text during transitions
        if self.fading_in or self.fading_out:
            return
        
        # Draw text box if we have dialogue
        if self.step < len(self.dialogue):
            # Create semitransparent text box
           global dialog_box_img

           dialog_x = screen.get_width()//2 - dialog_box_img.get_width()//2
           dialog_y = screen.get_height() - dialog_box_img.get_height() - 20
           
           screen.blit(dialog_box_img,(dialog_x,dialog_y))
           text_max_width = dialog_box_img.get_width() - 80

           draw_text(screen,self.displayed_text,30,
                (0, 0, 0),  # Black text
                dialog_x + dialog_box_img.get_width()//2,
                dialog_y + dialog_box_img.get_height()//2,
                center=True,
                max_width=text_max_width
            )
                        # Draw hint
           hint_font = pygame.font.SysFont('Comic Sans MS', 20)
           hint_text = hint_font.render("Press SPACE to continue", True, (0,0,0))
           hint_rect = hint_text.get_rect(bottomright=(dialog_x + dialog_box_img.get_width() - 90,  dialog_y + dialog_box_img.get_height() - 20))

           screen.blit(hint_text, hint_rect)

    def run(self):
        keys = pygame.key.get_pressed()
        self.update(keys)
        self.draw(self.display)

npc_manager = NPCManager()

player = character_movement.doctor(100,521,4.5) 
player.name = "You" # remember to put in class doctor

camera_group = CameraGroup(player, npc_manager, screen)
shared.camera_group = camera_group

player.camera_group = camera_group

#patient1 = NPC(1000,500,"Zheng")
#patient2 = NPC(400,500,"Emma")

#current_dialogue = None

#npc_manager.add_npc(patient1)
#npc_manager.add_npc(patient2)

image_path = {
            "Table": "Table.png",
            "Door01": "Door01.png"
        }

class InteractableObject(pygame.sprite.Sprite):
    def __init__(self, name, position, dialogue_id, start_node, image_path=None, active=True, text=None):
        super().__init__()

        self.name = name
        self.dialogue_id = dialogue_id
        self.start_node = start_node
        self.active = active
        self.text = text

        self.image = pygame.image.load(image_path).convert_alpha() if image_path else None
        self.rect = self.image.get_rect(topleft=position)
        self.flip = False #so CameraGroup won't flip items with player
        

    def draw(self, surface, offset):
        if self.image:
            offset_rect = self.rect.move(-offset[0], -offset[1])
        
            pygame.draw.rect(surface, (0, 255, 0), offset_rect, 2) 
        
            padded_rect = player.rect.inflate(10,10)
            near_obj = check_object_interaction(padded_rect, interactable_objects)
            if near_obj:
                font = pygame.font.Font(None, 24)
                text = font.render("Press Q to interact", True, (0, 0, 0), (255, 255, 255))
                for obj in near_obj:
                    screen_pos = obj.rect.move(-offset[0], -offset[1])
                    surface.blit(text, (screen_pos.centerx - text.get_width() // 2, screen_pos.top - 20))
                    
    def interaction(self):
        if self.dialogue_id:
            self.interacted = True
            # Run object dialogue
            global current_dialog
            current_dialog = ObjectDialogue(self.dialogue_id, self.start_node)
            current_dialog.start()
        elif self.text:
            print(f"{self.name}:{self.text}")
        else:
            print(f"You see {self.name}.")

interactable_objects = []

for obj_id, obj_info in object_data.items():
    name=obj_info["name"]
    pos = obj_info["position"]
    image = obj_info.get("image")
    image_path_str=image_path.get(image, None)
    dialogue_id=obj_info["dialogue_id"]
    start_node=obj_info["start_node"]
    active=obj_info.get("active", True)
    text = obj_info.get("text")

    obj = InteractableObject(name, pos, dialogue_id, start_node, image_path=image_path_str, active=active, text=text)
    interactable_objects.append(obj)

def check_object_interaction(player_rect, interactable_objects):
    return [obj for obj in interactable_objects if obj.active and player_rect.colliderect(obj.rect)]

class ObjectDialogue:
    def __init__(self, obj_info, game_ref):
        self.obj_info = obj_info
        self.dialogue_id = obj_info.dialogue_id
        self.start_node = obj_info.start_node
        self.current_node = obj_info.start_node
        self.dialogue_data = object_dialogue.get(self.dialogue_id, {})
        #self.current_dialogue_ref = current_dialogue_ref
        self.talking = False
        self.game_ref = game_ref

        self.dialogue_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()
        self.dialogue_box_img.set_alpha(200)

        self.displayed_text = ""
        self.letter_index = 0
        self.last_time = pygame.time.get_ticks()
        self.letter_delay = 45

        self.current_line = 0
        self.lines = []

    def start(self):
        self.talking = True
        self.displayed_text = ""
        self.letter_index = 0
        self.last_time = pygame.time.get_ticks()
        self.current_node = self.start_node

    def update(self):
        if self.talking:
            node = self.dialogue_data.get(self.current_node, {})
            text = node.get("text", "")

            current_time = pygame.time.get_ticks()
            if self.letter_index < len(text):
                if current_time - self.last_time > self.letter_delay:
                    self.displayed_text += text[self.letter_index]
                    self.letter_index += 1
                    self.last_time = current_time

    def draw(self, screen):
        if self.talking:
            x = screen.get_width() // 2 - self.dialogue_box_img.get_width() // 2
            y = screen.get_height() - self.dialogue_box_img.get_height() - 20
            screen.blit(self.dialogue_box_img, (x, y))

            # Padding inside the dialogue box
            text_x = x + 150
            text_y = y + 60
            max_text_width = self.dialogue_box_img.get_width() - 200  # 40 padding on each side

            draw_text(screen, self.displayed_text, size=30, color=(0, 0, 0), x=text_x, y=text_y, center=False, max_width=max_text_width)

    def handle_space(self):
        node = self.dialogue_data[self.current_node]
        full_text = node.get("text", "")

        # 1) complete typing if in middle
        if self.letter_index < len(full_text):
            self.displayed_text = full_text
            self.letter_index = len(full_text)
            return
        
        # 2) if there's a "next" in JSON, go there
        next_node = node.get("next")
        if next_node:
            self.current_node = next_node
            self.displayed_text = ""
            self.letter_index = 0
            self.last_time = pygame.time.get_ticks()
            return
        
        # 3) otherwise, we've reached the end of the dialogue
        self.talking = False

        # 4) now trigger transition, if any
        next_room = self.obj_info.get("next_room")
        if next_room:
            #if first time, show dialogue next time; else start fade
            if self.dialogue_id in self.game_ref.visited_doors:
                self.game_ref.start_fade_to(next_room)
            else:
                self.game_ref.visited_doors.add(self.dialogue_id)
        # done


        # if not self.talking:
        #     self.start()
        #     self.talking = True
            
        #     # Only show dialogue if door is first time
        #     if self.dialogue_id not in self.current_dialogue_ref.visited_doors:
        #         self.lines = ["Your office."]
        #         self.current_line = 0
        #         self.displayed_text = ""
        #     else:
        #         self.lines = []
        #         self.current_line = 0
        #     return
        
        # node = self.dialogue_data.get(self.current_node, {})
        # text = node.get("text", "")
        # if self.letter_index < len(text):
        #     self.displayed_text = text
        #     self.letter_index = len(text)
        #     return

        # self.current_line += 1
        # if self.current_line >= len(self.lines):
        #     self.talking = False
        #     if self.dialogue_id == "door01_dialogue":
        #         if self.dialogue_id not in self.current_dialogue_ref.visited_doors:
        #             self.current_dialogue_ref.visited_doors.add(self.dialogue_id)
        #         else:
        #             self.current_dialogue_ref.states['level'].fading = True
        #     return
    
        # self.displayed_text = ""
        # self.letter_index = 0
        # self.last_time = pygame.time.get_ticks()


class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.player = player
        self.npc_manager = NPCManager()
        self.current_dialogue = None
        self.visited_doors = set()
        self._pending_room = None
        self._fading = False
        self._fade_alpha = 0

        self.gameStateManager = GameStateManager('start')
        self.intro = SimpleChapterIntro(self.screen, self.gameStateManager)
        self.start = Start(self.screen, self.gameStateManager, self.intro)
        self.level = Rooms(self.screen, self.gameStateManager, self.player, self.npc_manager, self.screen, self)
        
        self.intro.completed_callback = lambda: self.gameStateManager.set_state('level')

        self.states = {'intro':self.intro, 'start':self.start, 'level':self.level}
    
        nuva = NPC(840,520,"Nuva")
        dean = NPC(400,520,"Dean")
        self.npc_manager.add_npc(nuva)
        self.npc_manager.add_npc(dean)

        camera_group.add(self.player)
        camera_group.add(nuva)
        camera_group.add(dean)

    def start_fade_to(self, room_name):
        """Called by ObjectDialogue when it’s time to switch rooms."""
        self._pending_room = room_name
        self._fading = True
        self._fade_alpha = 0

    def _do_fade_and_switch(self):
        self._fade_alpha = min(255, self._fade_alpha + 5)
        fade_surf = pygame.Surface(self.screen.get_size())
        fade_surf.fill((0,0,0))
        fade_surf.set_alpha(self._fade_alpha)
        self.screen.blit(fade_surf, (0,0))
        if self._fade_alpha >= 255:
            # actually switch rooms
            self.level.load_room(self._pending_room)
            self._fading = False
            self._pending_room = None
            # you could also re-spawn NPCs/interactables here

    def run(self):
        running = True
        moving_left = False
        moving_right = False
        run = True

        while running:
            events = pygame.event.get()

            # handle input once for everyone
            moving_left, moving_right, run = character_movement.keyboard_input(events, moving_left, moving_right, run)

            currentState = self.gameStateManager.get_state()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    screen_width, screen_height = event.w, event.h
                    # Optional: tell the camera group about the new size
                    camera_group.display_surface = screen
                    camera_group.half_w = screen_width // 2
                    camera_group.half_h = screen_height // 2

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        if self.current_dialogue and self.current_dialogue.talking:
                            # Ignore Q if dialogue is already ongoing
                            if isinstance(self.current_dialogue, ObjectDialogue):
                                self.current_dialogue.handle_space()
                        else:
                            interacted_obj = check_object_interaction(player.rect, interactable_objects)
                            if interacted_obj:
                                obj = interacted_obj[0]
                                self.current_dialogue = ObjectDialogue(obj, self)
                                self.current_dialogue.start()

            if currentState == 'level':
                dean = next(npc for npc in self.npc_manager.npcs if npc.name == "Dean")
                if dean:
                    self.states['level'].run(moving_left, moving_right, run, dean)
            else:
                self.states[currentState].run()

            for obj in interactable_objects:
                obj.draw(self.screen, camera_group.offset)

            screen_pos = player.rect.move(-camera_group.offset.x, -camera_group.offset.y)
            pygame.draw.rect(self.screen, (255, 0, 0), screen_pos, 2)  # red box = player

            if self.current_dialogue:
                self.current_dialogue.update()
                self.current_dialogue.draw(self.screen)

            if self._fading:
                self._do_fade_and_switch()



            pygame.display.update()
            self.clock.tick(FPS)

class Start:    #try to call back SimpleChapterIntro
    def __init__(self, display, gameStateManager, intro):
        self.display = display
        self.gameStateManager = gameStateManager
        self.intro = intro

    def run(self):
        self.display.fill('blue')
        keys = pygame.key.get_pressed()
        if keys[pygame.K_i]:
            self.intro.start("chapter_1")
            self.gameStateManager.set_state('intro')
        if keys[pygame.K_l]:
            self.gameStateManager.set_state('level')

            
#make plan to change by colliderect/position of player.rect

class Rooms:    # class Level in tutorial
    def __init__(self, display, gameStateManager, player, npc_manager, screen, current_dialogue_ref):
        self.display = display
        self.gameStateManager = gameStateManager
        self.background = pygame.image.load("picture/Map Art/Map clinic.png").convert_alpha()
        camera_group.set_background(self.background)

        self.player = player
        self.npc_manager = npc_manager
        self.screen = screen
        
        self.current_dialogue_ref = current_dialogue_ref
        self.space_released = True
        self.cutscene_active = False

        self.dean_exiting = False

        self.last_npc_name = None
        self.last_story = None

        self.visited_doors = set()  #keep track of doors used
        self.current_room = "room01"
        self.fading = False
        self.fade_alpha = 0

    def load_room(self, room_name):
        if room_name == "room2":
            self.background = pygame.image.load("picture/Map Art/Player room.png").convert_alpha()
            camera_group.set_background(self.background)
            self.player.rect.topleft = (100, 500)  # reset player position
            
            room_width, room_height = self.background.get_size()
            camera_group.set_limits(room_width, room_height)

            # Optionally clear/reload interactables or NPCs

    def run(self, moving_left, moving_right, run, dean):
        entry = {}
        self.dean = dean
        keys = pygame.key.get_pressed()

        # --- Movement ---
        if not self.current_dialogue_ref.current_dialogue or not self.current_dialogue_ref.current_dialogue.talking:
              is_moving = self.player.move(moving_left,moving_right)
        else:
              is_moving = False
        self.player.update_animation(is_moving)
          
        # --- Dialogue logic ---
        nearest_npc = self.npc_manager.get_nearest_npc(self.player)

        #=====space======
        if nearest_npc or self.current_dialogue_ref.current_dialogue:
            if nearest_npc: 
                if self.current_dialogue_ref.current_dialogue is None or not self.current_dialogue_ref.current_dialogue.talking:
                    self.current_dialogue_ref.current_dialogue = dialog(nearest_npc,self.player)
                elif isinstance(self.current_dialogue_ref.current_dialogue, ObjectDialogue):
                    pass
            
            if keys[pygame.K_SPACE] and self.space_released:
                self.space_released = False
                if self.current_dialogue_ref.current_dialogue:
                    dialogue = self.current_dialogue_ref.current_dialogue
                    
                    if isinstance(dialogue, ObjectDialogue):
                        dialogue.handle_space()
                    else:
                        dialogue.handle_space(keys)

            if isinstance(self.current_dialogue_ref.current_dialogue, dialog):
               self.current_dialogue_ref.current_dialogue.handle_option_selection(keys)
        

            if isinstance(self.current_dialogue_ref.current_dialogue, dialog):
                self.npc_name = self.current_dialogue_ref.current_dialogue.npc.name
                self.current_story = getattr(self.current_dialogue_ref.current_dialogue, "current_story", "chapter_1")

                # Only update story_data if the NPC or story changed
                if (self.last_npc_name != self.npc_name) or (self.last_story != self.current_story):
                    self.npc_data = all_dialogues.get(self.npc_name, {})
                    self.story_data = self.npc_data.get(self.current_story, [])
                    self.last_npc_name = self.npc_name
                    self.last_story = self.current_story

                self.step = self.current_dialogue_ref.current_dialogue.step

                if not self.current_dialogue_ref.current_dialogue.talking:
                    self.current_dialogue_ref.current_dialogue = None
                    entry = {}
                else:
                    entry = self.story_data[self.step]
            else:
                # 👇 This runs for ObjectDialogue — we don't use npc/story/step
                if not self.current_dialogue_ref.current_dialogue.talking:
                    self.current_dialogue_ref.current_dialogue = None
                    entry = {}
                else:
                    entry = {}

            
        if not keys[pygame.K_SPACE]:
            self.space_released = True
        
        camera_group.custom_draw(self.player)
        
        # --- Draw dialogue if active ---
        if self.current_dialogue_ref.current_dialogue:
            self.current_dialogue_ref.current_dialogue.update()
            self.current_dialogue_ref.current_dialogue.draw(self.display)
    
        # --- Handle fade-to-black transition ---
        if self.fading:
            self.fade_alpha += 5
            fade_surface = pygame.Surface((screen_width, screen_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            self.display.blit(fade_surface, (0, 0))

            if self.fade_alpha >= 255:
                # Transition complete — change room state
                self.current_room = "room2"   # e.g., swap to room2
                self.load_room("room2")       # call a method to load new map/positions
                self.fading = False
                self.fade_alpha = 0

        # --- Trigger cutscene --- 
        if self.current_dialogue_ref.current_dialogue and self.current_dialogue_ref.current_dialogue.talking:
            
            if isinstance(self.current_dialogue_ref.current_dialogue, dialog):
                current_npc_name = self.current_dialogue_ref.current_dialogue.npc.name

                if current_npc_name == "Dean":
                    if not self.cutscene_active:
                        self.cutscene_active = True

                else:
                    self.cutscene_active = False
    
        if self.cutscene_active and entry.get("event") == "dean_exits":
            self.dean_exiting = True
        
        if self.dean_exiting:
            self.dean.rect.x -= 3
            if self.dean.rect.x < -self.dean.image.get_width():
                        self.dean_exiting = False
                        self.cutscene_active = False

        # --- Back to start screen ---
        if keys[pygame.K_t]:
            self.gameStateManager.set_state('start')

            
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState
    def get_state(self):
        return self.currentState
    def set_state(self, state):
        self.currentState = state

if __name__== '__main__':
    game = Game()
    game.run()


#     #thisdict = {
# #   "world": ["Outside", "Inside", "PlayerOff", "DeanOff", "Basement", "Store"],
# #   "sub_worlds": {"chapter1":["work", "class", "office", "lab?"], "chapter2":["runway ad", "dressing", "home", "bedroom", "clinic?"]}
# # }

# #print(thisdict)
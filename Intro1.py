import pygame
import sys
from pygame.locals import *
import json
import character_movement
import shared
from shared import CameraGroup
import os
from ui_components import Button, get_font
from save_system import save_checkpoint, load_checkpoint


screen = None

current_text_size = 30
click_sound = pygame.mixer.Sound("main page/click1.wav") 

current_dialogue_instance = None
shown_dialogues = {}
selected_options = {}

game_chapter = 1

BG =(255,255,255)

def draw_bg(screen):
    screen.fill(BG)


def fade_to_main(surface ,speed = 5):
    fade = pygame.Surface((screen_width,screen_height))
    fade.fill((0,0,0))
    for alpha in range(0,255,speed):
        fade.set_alpha(alpha)
        draw_bg(surface)
        surface.blit(fade,(0,0))
        pygame.display.update()
        pygame.time.delay(30)
    pygame.quit()
    import subprocess
    import sys
    subprocess.Popen([sys.executable,"main_page.py"])
    

    
        

player_choices = {}

flags = {}

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

print("\n--- DEBUG: After loading all_dialogues ---")
print(f"Type of all_dialogues: {type(all_dialogues)}")
print(f"Keys in all_dialogues: {list(all_dialogues.keys())}") # See what top-level keys actually exist

if "Zheng" in all_dialogues:
    print("SUCCESS: 'Zheng' key found in all_dialogues.")
    # Print a snippet of Zheng's dialogue to confirm it's not empty/malformed
    print(f"Zheng dialogue structure (first 200 chars): {str(all_dialogues['Zheng'])[:200]}...")
else:
    print("ERROR: 'Zheng' key NOT found in all_dialogues. Please check NPC_dialog/NPC.json for exact key name and casing.")
print("-------------------------------------------\n")

with open("objects.json", "r") as f:
    object_data = json.load(f)

with open("object_dialogue.json") as f:
    object_dialogue = json.load(f)

with open("NPC_data.json") as f:
    npc_data = json.load(f)

dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()

moving_left = False
moving_right = False

#npc_list =["Nuva"]
selected_options = {}

cutscene_active = False
cutscene_speed = 3 #pixel per frame

room_settings = {
    "Player_room": {
        "background_path": "picture/Map Art/Player room.png",
        "player_start_pos": (1100, 420)
    },
    "room01": {
        "background_path": "picture/Map Art/Map clinic.png",
        "player_start_pos": (640, 420) # Default player start pos for room01
    },
    "subc.Z_01": {
        "background_path": "picture/Map Art/P11.png",
        "player_start_pos": (640, 420)
    },
    "subc.Z_02": {
        "background_path": "picture/Map Art/P12.png",
        "player_start_pos": (640, 420)
    },
    "subc.Z_03": {
        "background_path": "picture/Map Art/P13.png",
        "player_start_pos": (640, 400)
    },
    "subc.Z_04": {
        "background_path": "picture/Map Art/P14.png",
        "player_start_pos": (640, 420) # Assuming a default if not specified
    },
    "out_clinic": {
        "background_path": "picture/Map Art/Outside.png",
        "player_start_pos": (640, 420) # Assuming a default if not specified
    }
}

#============ Dialogue System =============
class dialog:
    def __init__(self,npc,player,full_dialogue_tree, start_node_id, rooms_instance,bgm_vol=0.5,sfx_vol=0.5, text_size=30, shown_dialogues=None, npc_manager=None):
        super().__init__()
        
        self.sounds = {
            "phone_typing": pygame.mixer.Sound("sfx/phone_typing.wav"),
            "footsteps": pygame.mixer.Sound("sfx/footsteps.wav"),
            "camera": pygame.mixer.Sound("sfx/camera.wav"),
            "car_crash": pygame.mixer.Sound("sfx/car_crash.wav"),
            "claps": pygame.mixer.Sound("sfx/claps.wav"),
            "crash": pygame.mixer.Sound("sfx/crash.wav"),
            "crowd": pygame.mixer.Sound("sfx/crowd.wav"),
            "gavel": pygame.mixer.Sound("sfx/gavel.wav"),
            "horror": pygame.mixer.Sound("sfx/horror.wav"),
            "people_talking": pygame.mixer.Sound("sfx/people_talking.wav"),
            "rain": pygame.mixer.Sound("sfx/rain.wav"),
            "wine_glass": pygame.mixer.Sound("sfx/wine_glass.wav"),
            "write_pen": pygame.mixer.Sound("sfx/write_pen.wav"),
        }

        self.sfx_vol = sfx_vol
        for sound in self.sounds.values():
            sound.set_volume(sfx_vol)

        self.player = player
        self.npc_name = npc.name
        self.npc = npc
        self.full_dialogue_tree = full_dialogue_tree # e.g., the entire {"Nuva": {...}} or {"System_Narrative": {...}}
        self.rooms_instance = rooms_instance # Reference to Rooms for event triggering

        self.current_node_id = start_node_id # e.g., "chapter_1", "not_a_doctor", "after_puzzle_sequence", "intro"
        self.current_dialogue_list = self._get_dialogue_list_from_node_id(self.current_node_id)

        self.current_story = f"chapter_{rooms_instance.current_day}"

        self.current_line_index = 0
        self.talking = True
        self.typing_complete = False
        self.text_display_timer = 0
        self.typing_speed = 2 # Adjust as needed
        self.current_text_display = ""
        self.choices_active = False
        self.current_choices = []
        self.selected_choice_index = 0 # Track selected choice for visual feedback

        # Initialize the first line for typing
        self.reset_typing()
        
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
        self.all_dialogues = all_dialogues
       # self.npc_data = self.all_dialogues.get(self.npc_name)

         #dialogue state variacbles
       # self.current_story = f"chapter_{game_chapter}" #default chapter
       # self.story_data = self.npc_data.get(self.current_story,[])
       # self.step = 0 # present current sentence

       # self.shown_dialogues = shown_dialogues #track dialogues that have been shown

        # # sentences typing effect
        # self.displayed_text = "" #display current word
        # self.letter_index = 0  #current letter position in text
        # self.last_time = pygame.time.get_ticks() #time tracking for typing speed
        # self.letter_delay = 45

       # self.options = [] #dialogue options when choices present
       # self.option_selected = 0 #current selected option index
       # self.talking = False # is it talking
        self.first_time_done  = False

        self.cg_images = []
        self.cg_index = 0
        self.showing_cg = None

        self.entry = None
        self.chapter_end = False
        self.finished = True

        self.cg_shown = False
        self.ready_to_quit = False
       

        if self.current_story in self.npc.shown_options and self.npc.shown_options[self.current_story]:
            self.current_story = "repeat_only"

       # self.key_w_released = True
       # self.key_s_released = True
       # self.key_e_released = True
        
        self.currently_playing_sfx = None
        self.sound_played_for_current_step = False
        self.current_bgm = None
        self.bgm_volume = bgm_vol

        self.npc_manager = npc_manager

        self.text_size = text_size

        self.cutscene_speed = 3

        self.dean_cutscene_triggered = False

        if not self.current_dialogue_list:
            print(f"Error: Initial dialogue list for node '{self.current_node_id}' not found. Ending dialogue.")
            self.talking = False
            self.current_text_display = "(Dialogue error or missing text)" # Display an error message

    def _get_dialogue_list_from_node_id(self, node_id):
        # e.g., if node_id is "intro", it will find "intro" -> "chapter_X" based on current_day.
        current_data = self.full_dialogue_tree

        # If node_id points to a structure that is a dictionary (like "intro"),
        # then it's a "meta-node" that contains chapter_X. Find the chapter_X inside it.
        if node_id in current_data and isinstance(current_data[node_id], dict):
            chapter_key = f"chapter_{self.rooms_instance.current_day}" # Get current day from Rooms
            dialogue_list = current_data[node_id].get(chapter_key)
            if dialogue_list:
                return dialogue_list
            else:
                print(f"Warning: No chapter dialogue '{chapter_key}' found for '{node_id}'.")
                return [] # No specific chapter dialogue
        # Otherwise, assume node_id directly points to a list of dialogue entries
        return current_data.get(node_id, [])

    def reset_typing(self):
        self.current_text_display = ""
        self.typing_complete = False
        self.text_display_timer = 0    

    
    

    def change_bgm(self, bgm_path):
        if bgm_path != self.current_bgm:
            self.current_bgm = bgm_path
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.set_volume(self.bgm_volume)
            pygame.mixer.music.play(-1)
    
    def update_bgm_volume(self, new_volume):
        self.bgm_volume = new_volume
        pygame.mixer.music.set_volume(new_volume)

    def update_sfx_volume(self, new_volume):
        self.sfx_vol = new_volume
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_vol)
            
    def stop_all_sfx(self):
        for sound in self.sounds.values():
            sound.stop()
        self.currently_playing_sfx = None
    
    

    def update(self,events=None): 

        if events is None:
            events = []

        if self.showing_cg:
           for event in events:
               if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                print("Space pressed during CG showing")
           
               #change to next CG
                self.cg_index += 1

                if self.cg_index >= len(self.cg_images):
                    #when all cg displayed, quit CG
                    self.cg_index = len(self.cg_images) - 1  # stay on last frame instead of blank
                   
                else:
                    #fade in to next cg
                    self.fade(screen, fade_in = True, cg_list=[self.cg_images[self.cg_index]])
                return
       
        #update dialogue content
      #  if self.talking and self.step < len(self.story_data):
      #       self.entry = self.story_data[self.step] # current dialogue entry
            
        entry = self.story_data[self.step] # current dialogue entry

        if isinstance(self.entry,dict) and "cg" in self.entry:
                 self.cg_images = [pygame.image.load(path).convert_alpha() for path in self.entry["cg"]]
                 self.cg_index = 0
                 self.showing_cg = True

                 self.fade(screen,fade_in = True,cg_list=self.cg_images)
                 self.step += 1
               

      #       text = self.entry.get("text","") #get text

        if self.entry.get("sound_stop"):
                self.stop_all_sfx()

        if "sound" in self.entry and not self.sound_played_for_current_step:
                sound_name = self.entry["sound"]
                if sound_name in self.sounds:
                    self.sounds[sound_name].play()
                    self.currently_playing_sfx = sound_name
                self.sound_played_for_current_step = True

        if "bgm" in self.entry:
                 self.change_bgm(self.entry["bgm"])
        elif "bgm_stop" in self.entry:
                   pygame.mixer.music.stop()
                   self.current_bgm = None

             #check if this is a choice entry
            # if "choice" in self.entry :
            #  self.options = self.entry.get("choice",[])
            # else:
            #     self.options = []

        if "event" in entry:
                if entry["event"] == "dean_exit_cutscene":
                    flags["dean_cutscene_played"] = True
                    self.dean_cutscene_triggered = True  

                    # save
                    save_checkpoint(
                        npc_name=self.npc_name,
                        chapter=self.current_story,
                        step=self.step,
                        player_choices=player_choices,
                        flags=flags,
                        shown_dialogues=self.shown_dialogues
                    )


                #   if self.npc_manager:
                #    for npc in self.npc_manager.npcs:
                #        if npc.name == "Dean":
                #           npc.rect.x -= self.cutscene_speed
                #           break

             # text typing effect
            # current_time = pygame.time.get_ticks()
            # if self.letter_index < len(text):
            #    if current_time - self.last_time > self.letter_delay:
            #         self.displayed_text += text[self.letter_index]
            #         self.letter_index += 1
            #         self.last_time = current_time

        if not self.talking or self.choices_active: # Don't update text animation if choices are active
            return

        # Ensure we have a valid line to display
        if self.current_line_index >= len(self.current_dialogue_list):
            self.typing_complete = True
            self.current_text_display = "" # Clear if no text
            return # No more text to type

        current_line_data = self.current_dialogue_list[self.current_line_index]
        text_to_display = current_line_data.get("text", "")

        if not self.typing_complete:
            self.text_display_timer += 1 
            chars_to_display = self.text_display_timer // self.typing_speed

            if chars_to_display > len(text_to_display):
                chars_to_display = len(text_to_display)

            self.current_text_display = text_to_display[:chars_to_display]
            
            if chars_to_display >= len(text_to_display):
                self.typing_complete = True     

        if isinstance(self.entry,dict) and self.entry.get("type") == "ending":
            self.chapter_end = True   

            global game_chapter
            # final chapter 
            if game_chapter >= 3:   
                self.ready_to_quit = True
                print(f"Main ending reached! ready_to_quit set to True") 
            else:
                # next chapter
                self.fade(screen , fade_in=True)
                game_chapter += 1
                self.step = 0 
                self.talking = False
                self.chapter_end = False
                self.current_story = f"chapter_{game_chapter}"
                self.story_data = self.npc_data.get(self.current_story,[])
                print(f"Moving to chapter {game_chapter}") 
                
            ending_key = self.current_story 
            flags[f"ending_unlocked_{ending_key}"] = True

            # save unlocked state
            save_checkpoint(
                npc_name=self.npc_name,
                chapter=self.current_story,
                step=self.step,
                player_choices=player_choices,
                flags=flags,
                shown_dialogues=self.shown_dialogues
            ) 
            


    def reset_typing(self):
         #reset text displayed for a new line 
         self.displayed_text = ""
         self.letter_index = 0
         self.last_time = pygame.time.get_ticks()

         self.sound_played_for_current_step = False 

    def draw(self,screen):

        if not self.talking:
            return

        # calculate the distance between player n NPC
        player_pos = pygame.Vector2(self.player.rect.center)
        npc_pos = pygame.Vector2(self.npc.rect.center)
        distance = player_pos.distance_to(npc_pos)

        if distance < 50 and  not self.talking and self.step >= len(self.story_data):
            key_hint_font = pygame.font.SysFont('Comic Sans MS',20)
            key_hint_text = key_hint_font.render("Press Space to talk", True,(0,0,0))
            key_hint_rect = key_hint_text.get_rect(center=(self.npc.rect.centerx,self.npc.rect.top - 30))
            screen.blit(key_hint_text,key_hint_rect)

    
        if self.showing_cg and self.cg_index < len(self.cg_images):
                   screen.blit(self.cg_images[self.cg_index],(0,0))
        else:
                   self.showing_cg = False
                   self.cg_index = 0
                   self.cg_images = []
 
        
         #calculate text width with limit for wrapping
        text_max_width = self.dialog_box_img.get_width() - 300 #pixel padding each side

        if not self.typing_complete:
            self.text_display_timer += 1 
            chars_to_display = self.text_display_timer // self.typing_speed

            if chars_to_display > len(text_to_display):
                chars_to_display = len(text_to_display)

            self.current_text_display = text_to_display[:chars_to_display]    


        # #only draw when in talking mode n not finished talk
        # if self.talking and self.step < len(self.story_data):
        #    entry = self.story_data[self.step]

        #    text = entry.get("text","")
        #    speaker = entry.get("speaker","npc") # default speaker is NPc
                
           #let the dialog box on the center and put below
        dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
        dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20
        screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

        #calculate text width with limit for wrapping
        text_max_width = self.dialog_box_img.get_width() - 300 #pixel padding each side

        current_line_data = self.get_current_line_data()
        if current_line_data:
            speaker_type = current_line_data.get("speaker", "narrator")

            # --- Choose portrait and position based on speaker ---
            portrait = None
            name_to_display = ""
            portrait_pos = (0, 0)

            if speaker_type == "npc":
                portrait = self.portrait
                name_to_display = self.npc.name # Use the name of the NPC object
                portrait_pos = (dialog_x + 800, dialog_y - 400) # Right side
            elif speaker_type == "player":
                portrait = self.player_portrait
                name_to_display = "You" # Player's name as 'You'
                portrait_pos = (dialog_x + 20, dialog_y - 400) # Left side
            else: # narrator (or any other speaker type without a portrait)
                portrait = None # No portrait for narrator
                name_to_display = "Narrator" # Default narrator name
                portrait_pos = (0, 0) # Not used, but set for consistency
            
            # --- Draw Character portraits and dialog box ---
            if portrait: # Only blit if a portrait image exists
                screen.blit(portrait, portrait_pos)
            screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

            # --- Draw speaker name ---
            # You had dialog_x + 200 for speaker name
            draw_text(screen, name_to_display, 40, (0, 0, 0), dialog_x + 200, dialog_y + 10, center=False) # Black text


            if self.choices_active:
                # --- Draw choice options if present ---
                max_options_display = 3 # display at most 3 options (from your old code)
                dialog_center_x = dialog_x + self.dialog_box_img.get_width() // 2

                for i, option in enumerate(self.current_choices[:max_options_display]):
                    # Red for selected option, black for others (from your old code)
                    color = (255, 0, 0) if i == self.selected_choice_index else (0, 0, 0)
                    
                    # Position choices relative to dialog box and center
                    option_y = dialog_y + 60 + i * 60 # From your old code
                    
                    # Ensure option is on screen (from your old code)
                    if option_y < screen.get_height() - 40: 
                        draw_text(screen, option["option"], 30, color, dialog_center_x, option_y, center=True)
            else: # --- Draw normal dialogue text ---
                text_to_display = self.current_text_display
                
                # Draw dialogue text, centered in the dialogue box (from your old code)
                draw_text(screen, text_to_display, self.text_size, (0, 0, 0), 
                          dialog_x + self.dialog_box_img.get_width() // 2, 
                          dialog_y + self.dialog_box_img.get_height() // 2 - 15, 
                          center=True, max_width=text_max_width)

           #only show space hint if no options are present 
        #   if not self.options:
        #       hint_font = pygame.font.SysFont('Comic Sans MS', 20)
        #       hint_text = hint_font.render("Press SPACE to continue", True, (0,0,0))
        #       hint_rect = hint_text.get_rect(bottomright=(dialog_x + self.dialog_box_img.get_width() - 90,  dialog_y + self.dialog_box_img.get_height() - 20))
        #       screen.blit(hint_text, hint_rect)
    

    def fade ( self, screen, cg_list, fade_in =True ):
        print(f"fade called with fade_in={fade_in}")
        for original_image in cg_list:
            cg_image = pygame.transform.scale(original_image ,(screen.get_width(),screen.get_height())).convert_alpha()

            if fade_in:       #fade in
              for alpha in range (0,255,10):
                screen.fill((0,0,0))
                cg_image.set_alpha(alpha)
                screen.blit(cg_image,(0,0))
                pygame.display.update()
                pygame.time.delay(30)
          
            else:             #fade out 
              print("Fading out image...")
              for alpha in range(255,-1,-10):
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

                      #======not really function========
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

    # not really function , need to combine codes mini games n modify
    def load_back_reality(self):
        self.displayed_text = ""
        self.letter_index = 0
        self.check_sub_end_conditions()
        pygame.display.update()


    def handle_space(self,keys):
         global save_message_timer  
         #start dialogue if not talked
         if not self.talking:
              self.talking = True
              self.load_dialogue(self.npc_name,self.current_story)
              return
         

         if self.npc_name == "Nuva" and self.current_story == "repeat_only":
            dialogue_id = f"{self.npc_name}_{self.current_story}_{self.step}"
            if dialogue_id in self.shown_dialogues:
                self.talking = False
                return


         #process current dialogue step
         if self.step <len(self.story_data):
              entry = self.story_data[self.step]
              text = entry.get("text","")

              dialogue_id = f"{self.npc_name}_{self.current_story}_{self.step}"
              self.shown_dialogues[dialogue_id] = True



      #========not really fonction , need to combine others codes n modify======
          #    if "chapter_ending" in entry:
             #save which ending was chosen
          #        global player_choices, showing_chapter_ending, ending_start_time, ending_complete_callback
          #        player_choices["chapter_1_ending"] = entry["chapter_ending"]
                  
             #set up the ending screen
          #        showing_chapter_ending = True
          #        ending_start_time = pygame.time.get_ticks()
            
            

         if not self.talking:
            return

         if self.choices_active:
            # Choice selection handled by arrow keys + Enter, not space
            print("Choices are active. Use arrow keys to select, Enter to confirm.")
            return

         if not self.typing_complete:
            # If text is still typing, complete it instantly
            if self.current_line_index < len(self.current_dialogue_list):
                current_line_data = self.current_dialogue_list[self.current_line_index]
                self.current_text_display = current_line_data.get("text", "")
            self.typing_complete = True
            return

        # Typing is complete, advance to the next line or handle node transition/event
         self.current_line_index += 1

         if self.current_line_index < len(self.current_dialogue_list):
            next_entry_data = self.current_dialogue_list[self.current_line_index]

            # 1. Check for 'choice'
            if "choice" in next_entry_data:
                self.current_choices = next_entry_data["choice"]
                self.choices_active = True
                self.selected_choice_index = 0 # Reset selection
                self.reset_typing()
                print(f"Choices activated: {self.current_choices}")
                return

            # 2. Check for 'next' node jump (e.g., "not_a_doctor", "chapter_1_common", "back_reality")
            if "next" in next_entry_data:
                next_node_id = next_entry_data["next"]
                self._transition_to_node(next_node_id)
                return

            # 3. Check for 'event' (e.g., "patient_zheng_talked_to", "day_end_and_intro_next_day")
            if "event" in next_entry_data:
                event_name = next_entry_data["event"]
                print(f"Triggering event: {event_name}")
                self.rooms_instance.handle_dialogue_event(event_name) # Assuming event doesn't need extra data
                
                # Events typically end dialogue or transition
                self.talking = False 
                self.rooms_instance.current_dialogue_ref.current_dialogue = None # Clear reference
                return

            # If it's a regular text line, reset for typing
            self.reset_typing()

         else: # End of current dialogue list
            # If we reached the end and didn't jump to 'next' or trigger an 'event'
            self.talking = False
            self.rooms_instance.current_dialogue_ref.current_dialogue = None
            print("NPC Dialogue ended.")

    # def handle_option_selection(self,keys):

    #     # only handle if in dialogue with options n text is full displayed
    #     if (self.talking and self.options and self.step <len(self.story_data) and self.letter_index >= len(self.story_data[self.step].get("text",""))):
                  
    #                # move up in options list with W key
    #                if keys[pygame.K_w] and self.key_w_released:
    #                   self.option_selected = (self.option_selected - 1) % len(self.options)
    #                   self.key_w_released = False
    #                if not keys[pygame.K_w]:
    #                    self.key_w_released = True
                    
    #                 #Move down in options list with S key
    #                if keys[pygame.K_s] and self.key_s_released:
    #                   self.option_selected = (self.option_selected + 1) % len(self.options)
    #                   self.key_s_released = False
    #                if not keys[pygame.K_s]:
    #                    self.key_s_released = True
                       
    #                 # comfirm selection with E Key
    #                if keys[pygame.K_e] and self.key_e_released:
    #                   selected_option = self.options[self.option_selected]
    #                   next_target = selected_option["next"]

    #                   #handle value jumps n chapter change
    #                   if isinstance(next_target,int):
    #                      self.step = next_target
    #                   else:
    #                      self.load_dialogue(self.npc_name, next_target)

    #                   self.options =[]
    #                   self.reset_typing()
    #                   self.key_e_released = False
    #                if not keys[pygame.K_e]:
    #                    self.key_e_released = True
                       

    # def handle_space(self, keys):
        #  #start dialogue if not talked
        #  if not self.talking:
        #       self.talking = True
        #       self.load_dialogue(self.npc_name,self.current_story)
        #       return
         
        #  #process current dialogue step
        #  if self.step <len(self.story_data):
        #       entry = self.story_data[self.step]
        #       text = entry.get("text","")

        #       #mark dialogue as shown if needed
        #       if "shown" in entry and entry["shown"] == False:
        #           dialogue_id = f"{self.npc_name}_{self.current_story}_{self.step}"
        #           self.shown_dialogues[dialogue_id] = True

        #       if "chapter_ending" in entry:
        #      #save which ending was chosen
        #           global player_choices, showing_chapter_ending, ending_start_time, ending_complete_callback
        #           player_choices["chapter_1_ending"] = entry["chapter_ending"]

        #      #set up the ending screen
        #           showing_chapter_ending = True
        #           ending_start_time = pygame.time.get_ticks()

        #      #set next chapter after ending
        #           next_chapter = entry["next_chapter"]

        #      #run when ending screen done
        #           def ending_complete():
        #               global start_chapter 
        #               start_chapter(next_chapter, True)

        #           ending_complete_callback = ending_complete

        #           self.talking = False
        #           return

        #       # if test is typing, complete it immdiately
        #       if self.letter_index <len (text):
        #            self.letter_index = len(text)
        #            self.displayed_text = text
        #       else:
                   
        #            #if have options ,nothing to do( option selection is at other part of code)
        #            if self.options:
        #              pass
                  
        #            else:
        #             if "next" in entry:
        #               next_target = entry["next"]

        #               if isinstance(next_target,int):
                          
        #                   #if next_target = integer, jump to that step within same chapter
        #                   self.step = next_target
        #               else:
        #                  #if next_target = string,it's the name of new chapter to load
        #                   self.current_story = next_target
        #                   self.story_data = self.npc_data.get(next_target,[])
        #                   self.step = 0
        #                   self.load_dialogue(self.npc_name, next_target)
        #                   self.reset_typing()

        #             else:
        #                 #if there is no "next",proceed to the next dialogue step
        #                 self.step += 1
        #                 if self.step >= len(self.story_data):
        #                     #end the dialogue if reached the end
        #                     self.talking = False
        #                     self.step = 0
        #                 else:
        #                    #reset typing effect for the next dialogue entry
        #                    self.reset_typing()

    def _transition_to_node(self, node_id):
        new_dialogue_list = self._get_dialogue_list_from_node_id(node_id)
        
        if new_dialogue_list: # Check if the list is not empty
            self.current_node_id = node_id
            self.current_dialogue_list = new_dialogue_list
            self.current_line_index = 0
            self.reset_typing()
            self.choices_active = False # Ensure choices are reset
            self.selected_choice_index = 0
        else:
            print(f"Warning: Next node '{node_id}' not found or invalid format. Ending dialogue.")
            self.talking = False
            self.rooms_instance.current_dialogue_ref.current_dialogue = None

    def select_choice(self, choice_index):
        if self.choices_active and 0 <= choice_index < len(self.current_choices):
            selected_option = self.current_choices[choice_index]
            next_node_id = selected_option["next"]
            self.choices_active = False
            self._transition_to_node(next_node_id)
        else:
            print("Invalid choice selection or no choices active.")

    def get_current_line_data(self):
        if self.talking and not self.choices_active and self.current_line_index < len(self.current_dialogue_list):
            return self.current_dialogue_list[self.current_line_index]
        return None

    def draw(self,screen):
        if not self.talking:
            return
        # #only draw when in talking mode n not finished talk
        # if self.talking and self.step < len(self.story_data):
        #    entry = self.story_data[self.step]

        #    text = entry.get("text","")
        #    speaker = entry.get("speaker","npc") # default speaker is NPc
                
           #let the dialog box on the center and put below
        dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
        dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20
        screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

        #calculate text width with limit for wrapping
        text_max_width = self.dialog_box_img.get_width() - 300 #pixel padding each side

        current_line_data = self.get_current_line_data()
        if current_line_data:
            speaker_type = current_line_data.get("speaker", "narrator")

            # --- Choose portrait and position based on speaker ---
            portrait = None
            name_to_display = ""
            portrait_pos = (0, 0)

            if speaker_type == "npc":
                portrait = self.portrait
                name_to_display = self.npc.name # Use the name of the NPC object
                portrait_pos = (dialog_x + 800, dialog_y - 400) # Right side
            elif speaker_type == "player":
                portrait = self.player_portrait
                name_to_display = "You" # Player's name as 'You'
                portrait_pos = (dialog_x + 20, dialog_y - 400) # Left side
            else: # narrator (or any other speaker type without a portrait)
                portrait = None # No portrait for narrator
                name_to_display = "Narrator" # Default narrator name
                portrait_pos = (0, 0) # Not used, but set for consistency
            
            # --- Draw Character portraits and dialog box ---
            if portrait: # Only blit if a portrait image exists
                screen.blit(portrait, portrait_pos)
            screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

            # --- Draw speaker name ---
            # You had dialog_x + 200 for speaker name
            draw_text(screen, name_to_display, 40, (0, 0, 0), dialog_x + 200, dialog_y + 10, center=False) # Black text


            if self.choices_active:
                # --- Draw choice options if present ---
                max_options_display = 3 # display at most 3 options (from your old code)
                dialog_center_x = dialog_x + self.dialog_box_img.get_width() // 2

                for i, option in enumerate(self.current_choices[:max_options_display]):
                    # Red for selected option, black for others (from your old code)
                    color = (255, 0, 0) if i == self.selected_choice_index else (0, 0, 0)
                    
                    # Position choices relative to dialog box and center
                    option_y = dialog_y + 60 + i * 60 # From your old code
                    
                    # Ensure option is on screen (from your old code)
                    if option_y < screen.get_height() - 40: 
                        draw_text(screen, option["option"], 30, color, dialog_center_x, option_y, center=True)
            else: # --- Draw normal dialogue text ---
                text_to_display = self.current_text_display
                
                # Draw dialogue text, centered in the dialogue box (from your old code)
                draw_text(screen, text_to_display, 30, (0, 0, 0), 
                          dialog_x + self.dialog_box_img.get_width() // 2, 
                          dialog_y + self.dialog_box_img.get_height() // 2 - 15, 
                          center=True, max_width=text_max_width)
                
                # print(f"Drawing dialogue: [{speaker}] {text_to_display}") # Debug print
        #    # choose portrait n position based on speaker
        #    if speaker == "npc":
        #         portrait = self.portrait
        #         name_to_display = self.npc.name
        #         portrait_pos =(dialog_x + 800,dialog_y - 400) #right side
        #    else:
        #         portrait = self.player_portrait
        #         name_to_display = "You"
        #         portrait_pos = (dialog_x +20,dialog_y - 400) #left side

        #     #draw Character portraits n dialog box
        #    screen.blit(portrait,portrait_pos)
        #    screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

        #    #draw speaker name
        #    name_to_display if speaker == "npc" else self.player.name #change here
        #    draw_text(screen,name_to_display,40,(0,0,0),dialog_x + 200, dialog_y + 10)

        #    #draw choice options if present
        #    if "choice" in entry:
        #      max_options_display = 3 #display at most 3 options

        #      dialog_center_x = dialog_x + self.dialog_box_img.get_width()// 2

        #      for i , option in enumerate(entry["choice"][:max_options_display]):
        #              # red for selected option, black for others
        #              color = (255,0,0) if i == self.option_selected else (0,0,0)
        #              option_y =  dialog_y+ 60 + i * 60

        #              if option_y < screen.get_height() - 40: #ensure option is on screen
        #                 draw_text(screen, option["option"],30,color,dialog_center_x,option_y,center= True)
          
        # draw dialogue text 
        # draw_text(screen,self.displayed_text,30,(0,0,0),dialog_x + self.dialog_box_img.get_width()//2  ,dialog_y + self.dialog_box_img.get_height()//2 - 15 ,center = True,max_width=text_max_width)

    def load_dialogue(self,npc_name,chapter):
        #update NPC detials
        self.npc_name = npc_name
        self.npc_data = self.all_dialogues.get(self.npc_name, {})
        self.current_story = chapter
        self.story_data = self.npc_data.get(self.current_story,[])
        
        if self.npc_name == "Nuva" and self.current_story == "repeat_only":
            self.story_data = self.npc_data.get("repeat_only", [])
            self.step = 0
            self.reset_typing()
            return
            
        raw_story_data = self.npc_data.get(self.current_story, [])
        filtered_story_data = []
        self.step_map = []
        
        for i, entry in enumerate(raw_story_data):
            dialogue_id = f"{self.npc_name}_{self.current_story}_{i}"
            
            if ("shown" not in entry or entry["shown"] != False) or (dialogue_id not in self.shown_dialogues):
                filtered_story_data.append(entry)

            elif self.npc_name == "Nuva" and self.current_story == "chapter_1_common" and entry.get("text") == "She is waiting in your office,you can head over when you are ready":
                if dialogue_id not in self.shown_dialogues:
                    filtered_story_data.append(entry)
   
        # set filtered dialogue n reset state
                self.step_map.append(i)
        
        self.story_data = filtered_story_data
        
        # if start_step in self.step_map:
        #    self.step = self.step_map.index(start_step)
        # else:
        #    self.step = 0
        
        self.reset_typing()


        if filtered_story_data:
            first_entry = filtered_story_data[0]

            if "cg" in first_entry:
                paths = first_entry["cg"] if isinstance(first_entry["cg"], list) else [first_entry["cg"]]
                self.cg_images = [pygame.image.load(path) for path in paths]
                self.cg_index = 0
                self.showing_cg = True
             

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
    def __init__(self,x,y,name,image_path = None, dialogue_id=""):
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
        self.dialogue_id = dialogue_id
        self.world_pos = pygame.Vector2(x,y) #for world coordinate
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.name = name
        self.dialog = None
        self.shown_options = {}

        self.flip = False 
        

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
    def __init__(self, display, gameStateManager,text_size=None,language="EN",bgm_vol=0.5,sfx_vol=0.5,resume_from=None):
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
        self.finished = False


        self.language = language
        self.text_size = text_size
        self.bgm_vol = bgm_vol
        self.sfx_vol = sfx_vol

    
    def start(self, chapter,completed_callback=None):
        print(f"Starting intro for chapter: {chapter}")

        pygame.mixer.music.set_volume(self.bgm_vol)
        current_bgm = "bgm/intro.mp3"
        pygame.mixer.music.load(current_bgm)
        pygame.mixer.music.play(-1)

        self.active = True
        self.completed_callback = completed_callback
        
        # Load background
        try:
            self.background = pygame.image.load("picture/Map Art/outside.png").convert()
            print("Background loaded successfully")
        except Exception as e:
            print(f"Error loading background: {e}")
        
        # Get dialogue from JSON
        if self.language == "CN":
            dialogue_file = "NPC_dialog/NPC_CN.json"
        else:
            dialogue_file = "NPC_dialog/NPC.json"

        try:
            with open(dialogue_file, 'r', encoding='utf-8') as f:
                language_dialogues = json.load(f)
                self.dialogue = language_dialogues.get("intro", {}).get(chapter, [])
        except Exception as e:
            print(f"Error loading dialogue file {dialogue_file}: {e}")
            self.dialogue = []

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
            self.finished = True
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
    
    def next(self):
        if self.finished :
            return self.next_chapter
        return None
    
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

           draw_text(screen,self.displayed_text, self.text_size or 30,
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
        is_running = self.update(keys)
        self.draw(self.display)


npc_manager = NPCManager()
     
class Chapter:
    def __init__(self,chapter_num):
        self.chapter_num = chapter_num   
        self.setup_chapter()

    def setup_chapter (self):
        if self.chapter_num == 1:
            print("chapter 1 setup completed")

    def setup_chapter(self):
        if self.chapter_num == 1:
            self.map = pygame.image.load("picture/Map Art/Map clinic.png")

            
def start_chapter_1():
    print("start chapter 1 ......")
    chapter = Chapter(1)
    chapter.setup_chapter()

# Create intro object
showing_intro = True
#chapter_intro = SimpleChapterIntro()
#chapter_intro.start("chapter_1",completed_callback=start_chapter_1)

player = character_movement.doctor(100,521,4.5) 
player.name = "You" # remember to put in class doctor

camera_group = CameraGroup(player, npc_manager, screen)
shared.camera_group = camera_group

player.camera_group = camera_group

#patient1 = NPC(1000,500,"Zheng")
#patient2 = NPC(400,500,"Emma")l

#current_dialogue = None

#npc_manager.add_npc(patient1)
#npc_manager.add_npc(patient2)

image_path = {
            "Table": "Object_image/Table.png",
            "Door01": "Object_image/Door01.png",
            "Board": "Object_image/Board.png",
            "Machine": "Object_image/Machine.png",
            "Computer": "Object_image/exit_Z01.png",
            "Whiteboard": "Object_image/exit_Z02.png",
            "Office_door": "Object_image/exit_Z03.png",
            "Boxes?": "Object_image/exit_Z04.png",
            "intro_to_clinic": "Object_image/temp_enter.png",
            "Office_comps": "Object_image/Z01_Key1.png",
            "Printer": "Object_image/Z01_Lock.png",
            "Water_cooler": "Object_image/Z01_Random.png",
            "Student_desk": "Object_image/Z02_Key1.png",
            "Trash_bin": "Object_image/Z02_Key2.png",
            "Window_sill": "Object_image/Z03_Key1.png",
            "Trophies": "OBject_image/Z03_Key2.png",
            "Drawer": "Object_image/Z03_Lock.png",
            "Monitor": "Object_image/Z04_Random.png"
        }

class InteractableObject(pygame.sprite.Sprite):
    def __init__(self, name, position, dialogue_id, start_node, image_path=None, active=True, text=None, next_room=None, unlocked=True, conditional_dialogue_flag=None, node_if_locked=None, node_if_unlocked=None, day_specific_nodes=None, draw_layer="mid_layer"):
        super().__init__()

        self.name = name
        self.dialogue_id = dialogue_id
        self.start_node = start_node
        self.active = active
        self.text = text
        self.next_room = next_room

        self.image = pygame.image.load(image_path).convert_alpha() if image_path else None
        self.rect = self.image.get_rect(topleft=position)
        self.flip = False #so CameraGroup won't flip items with player
        
        self.unlocked = unlocked
        self.conditional_dialogue_flag = conditional_dialogue_flag
        self.node_if_locked = node_if_locked
        self.node_if_unlocked = node_if_unlocked
        self.day_specific_nodes = day_specific_nodes if day_specific_nodes is not None else {}
        self.draw_layer = draw_layer

    #     print(f"Initializing object: {name} at {position} with image: {image_path}")

    # def draw(self, surface, offset):
    #     if self.image:
    #         offset_rect = self.rect.move(-offset[0], -offset[1])
    #         surface.blit(self.image, offset_rect)
    #         pygame.draw.rect(surface, (0, 255, 0), offset_rect, 2) 
        
    #         padded_rect = player.rect.inflate(10,10)
    #         near_obj = check_object_interaction(padded_rect, interactable_objects)
    #         if near_obj:
    #             font = pygame.font.Font(None, 24)
    #             text = font.render("Press Q to interact", True, (0, 0, 0), (255, 255, 255))
    #             for obj in near_obj:
    #                 screen_pos = obj.rect.move(-offset[0], -offset[1])
    #                 surface.blit(text, (screen_pos.centerx - text.get_width() // 2, screen_pos.top - 20))
    #     print(f"Drawing {self.name} at {self.rect.topleft} with offset {offset}. Image exists: {self.image is not None}")
                    
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

def check_object_interaction(player_rect, interactable_objects):
    return [obj for obj in interactable_objects if obj.active and player_rect.colliderect(obj.rect)]

class ObjectDialogue:  # very confused
    def __init__(self, obj_info, current_dialogue_ref, rooms_instance, start_node_id="start",text_size=30, language="EN"):
        self.obj_info = obj_info
        self.current_dialogue_ref = current_dialogue_ref
        self.rooms_instance = rooms_instance
        self.dialogue_id = obj_info.dialogue_id
        self.dialogue_data = object_dialogue.get(self.dialogue_id, {})
        self.current_node_id = start_node_id
        self.current_node = self.dialogue_data.get(self.current_node_id, {})
        self.talking = False
        
        # --- ADDED: Initialization for typing animation variables ---
        self.current_text_index = 0 # Index for the current line within a node's text list
        self.talking = True # Dialogue starts talking immediately
        self.current_text_display = "" # The text currently displayed characters by characters
        self.typing_speed = 3 # Characters per frame, adjust as needed
        self.text_display_timer = 0
        self.typing_complete = False # Flag indicating if the current line has finished typing

        self.text_size = text_size
        self.language = language

        self.displayed_text = ""
        self.letter_index = 0

        self.dialogue_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()
        self.dialogue_box_img.set_alpha(200)

        self.reset_typing()
        # self.lines = []

    def reset_typing(self):
        # This method is crucial to set up the typing animation for a new line/node
        self.text_display_timer = 0
        self.typing_complete = False
        self.current_text_display = ""
        # Ensure we have a valid text list and current index
        node_text_list = self.current_node.get("text", [""])
        if not isinstance(node_text_list, list): # Ensure it's always a list for indexing
            node_text_list = [node_text_list]
        if self.current_text_index >= len(node_text_list):
            self.typing_complete = True

    # def start(self):
    #     self.talking = True
    #     self.current_node = self.start_node
    #     self.current_line = 0
    #     self.displayed_text = ""
    #     self.letter_index = 0
    #     self.last_time = pygame.time.get_ticks()
        
    def update(self):
        if self.talking and not self.rooms_instance.fading:
            # Get the current full text for the line we are displaying
            node_text_list = self.current_node.get("text", [""])
            if not isinstance(node_text_list, list): # Ensure it's always a list
                node_text_list = [node_text_list]

            # Check if current_text_index is valid for the current node's text
            if self.current_text_index >= len(node_text_list):
                self.typing_complete = True
                self.current_text_display = ""
                return # Nothing to type if no text
            
            current_full_text = node_text_list[self.current_text_index]

            if not self.typing_complete:
                self.text_display_timer += 1
                chars_to_display = self.text_display_timer // self.typing_speed
                # Ensure we don't try to display more characters than available
                if chars_to_display > len(current_full_text):
                    chars_to_display = len(current_full_text)
                
                self.current_text_display = current_full_text[:chars_to_display]
                
                if chars_to_display >= len(current_full_text):
                    self.typing_complete = True
            
    def draw(self, screen):
        if not self.talking: return

        x = screen.get_width() // 2 - self.dialogue_box_img.get_width() // 2
        y = screen.get_height() - self.dialogue_box_img.get_height() - 20
        screen.blit(self.dialogue_box_img, (x, y))

        # Padding inside the dialogue box
        text_x = x + 150
        text_y = y + 60
        max_text_width = self.dialogue_box_img.get_width() - 200  # 40 padding on each side

        draw_text(screen, self.current_text_display, size=30, color=(0, 0, 0), x=text_x, y=text_y, center=False, max_width=max_text_width)

    def handle_space(self):
        if not self.typing_complete:
            node_text_list = self.current_node.get("text", [""])
            if not isinstance(node_text_list, list): node_text_list = [node_text_list]
            if self.current_text_index < len(node_text_list):
                self.current_text_display = node_text_list[self.current_text_index]
            self.typing_complete = True
            return
        node_text_list = self.current_node.get("text", [""])
        if not isinstance(node_text_list, list): node_text_list = [node_text_list]
        if self.current_text_index + 1 < len(node_text_list):
            self.current_text_index += 1
            self.reset_typing()
            return
        next_node_id = self.current_node.get("next_node")
        event_name = self.current_node.get("event")
        if event_name:
            event_data = {}
            if hasattr(self.obj_info, 'next_room') and self.obj_info.next_room: # Pass next_room if it exists on the object
                event_data["target_room"] = self.obj_info.next_room
            self.rooms_instance.handle_dialogue_event(event_name, event_data)
            self.talking = False
            return
        if next_node_id == "end" or not next_node_id:
            self.talking = False
        else:
            self.current_node_id = next_node_id
            self.current_node = self.dialogue_data.get(self.current_node_id, {})
            if not self.current_node:
                print(f"Warning: next_node '{self.current_node_id}' not found. Ending dialogue.")
                self.talking = False
                return
            self.current_text_index = 0
            self.reset_typing()
        if not self.talking:
            self.current_dialogue_ref.current_dialogue = None
        # node = self.current_node    # self.dialogue_data[self.current_node]

        # raw_text = node.get("text", "")

        # if not isinstance(raw_text, list):
        #     text_lines_in_node = [raw_text]
        # else:
        #     text_lines_in_node = raw_text

        # # full_text = node.get("text", "")

        # # 1) complete typing if in middle
        # if not self.typing_complete:
        #     self.typing_complete = True
        #     # Force the display to show full text for the current line
        #     self.current_text_display = text_lines_in_node[self.current_text_index]
        #     return # Don't advance dialogue yet, just complete typing
        
        # # Go to next line
        # if self.current_text_index + 1 < len(text_lines_in_node):
        #     self.current_text_index += 1
        #     self.reset_typing()
        #     return
        
        # # 2) if there's a "next" in JSON, go there
        # next_node_id = node.get("next")
        # if next_node_id:
        #     # Update current node ID and retrieve the new node's data
        #     self.current_node_id = next_node_id
        #     self.current_node = self.dialogue_data.get(self.current_node_id, {"text": ["Error: Node not found!"], "end_dialogue": True})
        #     self.current_text_index = 0
        #     self.reset_typing()
        #     return
      
        # # Special case for locked door
        # if self.obj_info.name == "Dean_room":
        #         if not self.obj_info.unlocked:
        #             self.dialogue_data = {
        #                "locked":{"text": "It's locked.", "end_dialogue": True}
        #             }
        #             self.current_node_id = "locked"
        #             self.current_node = self.dialogue_data["locked"]
        #             self.current_text_index = 0
        #             self.reset_typing()
        #             self.talking = True
        #             return

        # # 3) otherwise, we've reached the end of the dialogue
        # self.talking = False
        # self.current_text_display = ""

        # # 4) now trigger transition, if any
        # next_room = self.obj_info.next_room
        # if next_room and self.obj_info.unlocked:
        #     # Start fade whether it's first time or not
        #     self.rooms_instance.next_room_after_transition = next_room
        #     self.rooms_instance.fading = True
        #     # self.game_ref.start_fade_to(next_room)
            
        #     # Optional: record door visit so next time you can skip the dialogue entirely
        #     # self.game_ref.visited_doors.add(self.dialogue_id)

        # # --- Trigger event in Rooms if defined in the current node ---
        # if "event" in self.current_node:
        #     # Pass the event name to the Rooms instance's handler
        #     self.rooms_instance.handle_dialogue_event(self.current_node["event"])

        


class Game:
    def __init__(self,text_size=None,language="EN",bgm_vol=0.5,sfx_vol=0.5,resume_from=None):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = screen
        self.player = player
        self.npc_manager = NPCManager()
        self.current_dialogue = None
        self.visited_doors = set()
        self._pending_room = None
        self._fading = False
        self._fade_alpha = 0

        self.language = language
        self.text_size = text_size
        self.bgm_vol = bgm_vol
        self.sfx_vol = sfx_vol

        self.current_dialogue_ref = self  # or an empty helper class if preferred
        self.current_dialogue = None

        # self.all_dialogues_data = all_dialogues

        self.gameStateManager = GameStateManager('start')

        self.gameStateManager.game_instance = self
        
        self.intro = SimpleChapterIntro(self.screen, self.gameStateManager,language=language,
                                        text_size=text_size,
                                        bgm_vol=bgm_vol,
                                        sfx_vol=sfx_vol)
        self.start = Start(self.screen, self.gameStateManager, self.intro,language = language,text_size = text_size,bgm_vol = bgm_vol,sfx_vol = sfx_vol)
        self.level = Rooms(self.screen, self.gameStateManager, self.player, self.npc_manager, self, self.screen, self.current_dialogue_ref,
                           language=self.language,
                           text_size=self.text_size,
                           bgm_vol=self.bgm_vol,
                           sfx_vol=self.sfx_vol
                           )
        
        
        #self.intro.completed_callback = lambda: self.gameStateManager.set_state('level')

        self.states = {'intro':self.intro, 'start':self.start, 'level':self.level}
    
        nuva = NPC(840,520,"Nuva")
        dean = NPC(400,520,"Dean")
        self.npc_manager.add_npc(nuva)
        self.npc_manager.add_npc(dean)

        camera_group.add(self.player)
        camera_group.add(nuva)
        camera_group.add(dean)

    def start_fade_to(self, room_name):
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
            
    def run(self):
        running = True
        moving_left = False
        moving_right = False
        run = True

        while running:
            events = pygame.event.get()

            # handle input once for everyone
            moving_left, moving_right, run = character_movement.keyboard_input(events, moving_left, moving_right, run)

            if not run:
                running = False

            currentState = self.gameStateManager.get_state()

            

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    global screen_width, screen_height  # Update global constants?
                    screen_width, screen_height = event.w, event.h
                    self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)  #Re-set screen
                    
                    # Optional: tell the camera group about the new size
                    camera_group.display_surface = self.screen
                    camera_group.half_w = screen_width // 2
                    camera_group.half_h = screen_height // 2

                # elif event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_q:
                #         if self.current_dialogue and self.current_dialogue.talking:
                #             # Ignore Q if dialogue is already ongoing
                #             if isinstance(self.current_dialogue, ObjectDialogue):
                #                 self.current_dialogue.handle_space()
                #         else:
                #             interacted_obj = check_object_interaction(self.player.rect, interactable_objects)
                #             if interacted_obj:
                #                 obj = interacted_obj[0]
                #                 self.current_dialogue = ObjectDialogue(obj, self.player, all_dialogues, self, chosen_start_node)
                #                 self.current_dialogue.start()

            if currentState == 'level':
                self.states['level'].run(moving_left, moving_right,events)
            else:
                # 其他狀態也需要事件來響應，例如 intro 中的 space 按鍵
                self.states[currentState].run() # 您可能需要更新其他 state 的 run 方法以接受 events




            # for obj in interactable_objects:
            #     obj.draw(self.screen, camera_group.offset)

            screen_pos = player.rect.move(-camera_group.offset.x, -camera_group.offset.y)
            pygame.draw.rect(self.screen, (255, 0, 0), screen_pos, 2)  # red box = player

            if self.current_dialogue:

                if isinstance(self.current_dialogue, dialog):
                    self.current_dialogue.update(events)
                else:
                    self.current_dialogue.update()

                self.current_dialogue.draw(self.screen)

            if self._fading:
                self._do_fade_and_switch()

            pygame.display.update()
            self.clock.tick(FPS)

class Start:    #try to call back SimpleChapterIntro
    def __init__(self, display, gameStateManager, intro, language="EN", text_size=None, bgm_vol=0.5, sfx_vol=0.5):
        self.display = display
        self.gameStateManager = gameStateManager
        self.intro = intro

        self.language = language
        self.text_size = text_size
        self.bgm_vol = bgm_vol
        self.sfx_vol = sfx_vol
        

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
    def __init__(self, display, gameStateManager, player, npc_manager, game_ref,screen, current_dialogue_ref, language="EN", text_size=None, bgm_vol=0.5, sfx_vol=0.5):
        self.display = display
        self.gameStateManager = gameStateManager

        self.player = player
        self.npc_manager = npc_manager
        self.screen = screen
        
        self.current_dialogue_ref = current_dialogue_ref

        self.language = language
        self.text_size = text_size
        self.bgm_vol = bgm_vol
        self.sfx_vol = sfx_vol
        
        self.backmain_img = pygame.image.load("backmain.png").convert_alpha()
        self.backmain_button = Button(image=self.backmain_img, pos=(1100, 80), scale=0.2)
        

        if self.language == "CN":
            dialogue_file = "NPC_dialog/NPC_CN.json"
        else:
            dialogue_file = "NPC_dialog/NPC.json"

        with open(dialogue_file, 'r', encoding='utf-8') as f:
            self.all_dialogues = json.load(f)

        self.shown_dialogues = {}    

        camera_group = CameraGroup(self.player, self.npc_manager, display)
        camera_group.add(self.player)
        
        self.current_dialogue_ref = game_ref

        self.space_released = True
        self.q_released = True
        self.enter_released = True  # New: for choice selection confitmation
        
        self.cutscene_active = False

        self.cutscene_speed = 3

        self.dean_exiting = False
        self.patient_zheng_talked_to = False # Flag for machine unlock
        self.visited_doors = set()  #keep track of doors used

        self.current_room = "room01"
        self.current_day = 1    #Initialize the current day (Chapter 1)
        
        self.fading = False
        self.fade_alpha = 0
        self.next_room_after_transition = None    # Store the target room for fading transitions
        self.start_intro_after_fade = False # Flag to trigger intro after a fade transition
        
        # Initial background load in __init__ (using room_settings for consistency)
        initial_room_data = room_settings.get(self.current_room)
        if initial_room_data:
            self.background = pygame.image.load(initial_room_data["background_path"]).convert_alpha()
        else:
            print(f"Warning: Initial room '{self.current_room}' not found in room_settings. Using default background.")
            self.background = pygame.image.load("picture/Map Art/Map clinic.png").convert_alpha()
        
        camera_group.set_background(self.background)
        print(f"DEBUG: Rooms __init__ finished. self.camera_group ID: {id(camera_group)}")
        
        self.load_room(self.current_room)


    def advance_day(self):
        # Increments the current day and performs day-change actions
        self.current_day += 1
        print(f"--- Advancing to Day {self.current_day} (Chapter {self.current_day})---")
        # Reset NPC position and quest flags? here 
        # self.load_room(self.current_room) # To reload the room to refresh objects/NPC

        self.backmain_img = pygame.image.load("backmain.png").convert_alpha()

        self.backmain_button = Button(image=self.backmain_img, pos=(1100, 80), scale=0.2)


    def load_room(self, room_name, facing="left"):
        print(f"\n--- Entering load_room for {room_name} ---")
        print(f"DEBUG: In load_room, self.camera_group ID: {id(camera_group)}")

        camera_group.empty()
        camera_group.background_layer_sprites.empty()
        camera_group.foreground_layer_sprites.empty()
        print("DEBUG: All camera groups emptied.")

        camera_group.add(self.player)
        print(f"DEBUG: Player added to main camera_group. Current main group sprites: {[s.name if hasattr(s, 'name') else type(s).__name__ for s in camera_group.sprites()]}")

        # Remove NPCs from both npc_manager and camera_group
        for npc in self.npc_manager.npcs:
            camera_group.remove(npc)
        self.npc_manager.npcs.clear()
        print("DEBUG: NPC manager cleared.")

        for obj in interactable_objects:
            camera_group.remove(obj)
            camera_group.background_layer_sprites.remove(obj)
            camera_group.foreground_layer_sprites.remove(obj)
        interactable_objects.clear()
    
        print(f"Loading room: {room_name}")
        # --- Load background and set player position using room_settings dictionary ---
        room_data = room_settings.get(room_name)

        if room_data:
            background_path = room_data["background_path"]
            player_start_pos = room_data["player_start_pos"]
            self.background = pygame.image.load(background_path).convert_alpha()
            self.player.rect.topleft = player_start_pos
            print(f"Successfully loaded background from: {background_path}")
            print(f"Set player start position to: {player_start_pos}")
        else:
            print(f"Warning: Room '{room_name}' not found in room_settings. Using default fallback background and player position.")
            self.background = pygame.image.load("picture/Map Art/Map clinic.png").convert_alpha() # Default fallback
            self.player.rect.topleft = (640, 420) # Default player pos for fallback

        camera_group.set_background(self.background)

        self.current_room = room_name

        if facing == "left":
            self.player.flip = True
            self.player.direction = -1
        elif facing == "right":
            self.player.flip = False
            self.player.direction = 1

        for obj_id, obj_info in object_data.items():
            if room_name in obj_info.get("rooms", []):
                name = obj_info["name"]
                pos = obj_info["position"]
                image_key = obj_info.get("image")
                image_path_str=image_path.get(image_key, None)
                dialogue_id=obj_info["dialogue_id"]
                start_node=obj_info["start_node"]
                active=obj_info.get("active", True)
                text = obj_info.get("text")
                next_room = obj_info.get("next_room")
                unlocked=obj_info.get("unlocked", True)
                # New conditional dialogue attributes for InteractableObject
                conditional_dialogue_flag = obj_info.get("conditional_dialogue_flag")
                node_if_locked = obj_info.get("node_if_locked")
                node_if_unlocked = obj_info.get("node_if_unlocked")
                day_specific_nodes = obj_info.get("day_specific_nodes")
                
                draw_layer = obj_info.get("draw_layer", "mid_layer")

                if image_path_str:
                    obj = InteractableObject(name, pos, dialogue_id, start_node, 
                                             image_path=image_path_str, active=active, 
                                             text=text, next_room=next_room, 
                                             unlocked=unlocked, 
                                             conditional_dialogue_flag=conditional_dialogue_flag,
                                             node_if_locked=node_if_locked,
                                             node_if_unlocked=node_if_unlocked,
                                             day_specific_nodes=day_specific_nodes,
                                             draw_layer=draw_layer)
                    interactable_objects.append(obj)
                    
                # --- NEW: Add to the correct CameraGroup layer ---
                    if draw_layer == "background":
                        camera_group.background_layer_sprites.add(obj)
                        print(f"Added {name} to background layer.")
                    elif draw_layer == "foreground":
                        camera_group.foreground_layer_sprites.add(obj)
                        print(f"Added {name} to foreground layer.")
                    else: # Default or "mid_layer"
                        camera_group.add(obj) # Add to the main camera group for Y-sorting with characters
                        print(f"Added {name} to mid layer (main group).")
                else:
                    print(f"Warning: No image path found for object '{name}' (image_key: {image_key}). Not adding to game.")


                print(f"SUCCESS: Loaded object: {name} for room: {room_name}")
        
        print(f"Total interactable objects loaded for {room_name}: {len(interactable_objects)}")
        
        # --- Load and add NPCs for the current room using global npc_data ---
        for npc_id, npc_info in npc_data.items(): # <-- Access global npc_data
            if room_name in npc_info.get("rooms", []): 
                name = npc_info["name"]
                pos = npc_info["position"]
                dialogue_id = npc_info["dialogue_id"] 
                npc = NPC(pos[0], pos[1], name, dialogue_id=dialogue_id) # <--- Corrected: No image_path argument here
                
                self.npc_manager.add_npc(npc)
                camera_group.add(npc) 
                print(f"SUCCESS: Added NPC: {name} ({dialogue_id}) to room {room_name}.")    
        # if room_name == "Player_room":
        #     # Assuming you get Zheng's position from `object_data` or have it hardcoded.
        #     # If using object_data, it would look up "zheng_npc_id"
        #     zheng_data = self.object_data.get("zheng_npc_id") # Get Zheng's data from object_data.json
            
        #     if zheng_data and room_name in zheng_data.get("rooms", []): # Make sure Zheng is configured for this room
        #         # patient1 = NPC(800, 550, "Zheng") <-- OLD
        #         # Now, pass the dialogue_id as "Zheng"
        #         patient1 = NPC(zheng_data["position"][0], zheng_data["position"][1], 
        #                        zheng_data["name"], 
        #                        "Zheng") # <--- Explicitly pass "Zheng" as the dialogue_id
        #     self.npc_manager.add_npc(patient1)
        #     camera_group.add(patient1)
        
        room_width, room_height = self.background.get_size()
        camera_group.set_limits(room_width, room_height)
        
        # if room_name == "...":
            # new_npc = NPC(300, 500, "Someone")
            # self.npc_manager.add_npc(new_npc)
            # camera_group.add(new_npc)

    # --- METHOD TO HANDLE DIALOGUE EVENTS ---
    def handle_dialogue_event(self, event_name, event_data=None):
        event_data = event_data if event_data is not None else {}
        
        # Processes events triggered at the end of a dialogue node.
        if event_name == "patient_zheng_talked_to":
            self.patient_zheng_talked_to = True
            print("Patient Zheng's dialogue completed. Machine dialogue unlocked!")
        elif event_name == "machine_enter":
            target_room = event_data.get("target_room")
            if target_room:
                self.fading = True
                self.fade_alpha = 0 # Ensure fade starts from 0
                self.next_room_after_transition = target_room # Use the passed target room
                print(f"Machine triggered room transition to: {self.next_room_after_transition}")
            else:
                print("Warning: 'machine_enter' triggered without 'target_room'. Cannot transition.")
        elif event_name == "open_door_event": # For generic door transitions
            target_room = event_data.get("target_room")
            if target_room:
                self.fading = True
                self.fade_alpha = 0
                self.next_room_after_transition = target_room
                print(f"Door triggered room transition to: {self.next_room_after_transition}")
            else:
                print("Warning: 'open_door_event' triggered without 'target_room'. Cannot transition.")
        
        # NEW EVENT: Triggered after the 'Machine' interaction (after puzzle completion)
        elif event_name == "puzzle_complete":
            print("Event: Puzzle completed. Triggering 'after_puzzle' narrative.")
            # Initiate the "after_puzzle_sequence" dialogue.
            # Create a simple dummy object/NPC for System_Narrative dialogue.
            class NarratorDummy:
                def __init__(self, name="narrator", dialogue_id="System_Narrative"):
                    self.name = name
                    self.dialogue_id = dialogue_id
                    self.rect = pygame.Rect(0,0,1,1) # Dummy rect for consistency if 'dialog' needs it

            narrator_dummy_obj = NarratorDummy()
            system_narrative_tree = self.all_dialogues.get(narrator_dummy_obj.dialogue_id)
            if system_narrative_tree:
                self.current_dialogue_ref.current_dialogue = dialog(
                    narrator_dummy_obj, # Pass the dummy object
                    self.player,
                    self.all_dialogues.get(narrator_dummy_obj.dialogue_id), # Pass the whole System_Narrative tree
                    start_node_id="after_puzzle_sequence", # Start the specific sequence
                    rooms_instance=self
                )
                self.current_dialogue_ref.current_dialogue.talking = True # Ensure it begins talking
            else:
                print(f"Error: 'System_Narrative' dialogue data not found for event '{event_name}'.")

        # NEW EVENT: Triggered at the end of the 'back_reality' dialogue
        elif event_name == "day_end_and_intro_next_day":
            print("Event: Day end sequence triggered. Advancing day and starting next intro.")
            # Fade to black if not already fading
            if not self.fading:
                self.fading = True
                self.fade_alpha = 0

            # Advance the game day
            self.advance_day()

            self.start_intro_after_fade = True # New flag to tell the fade logic to start intro
            print(f"Set to fade to {self.next_room_after_transition} and start intro for Day {self.current_day}.")

    def run(self, moving_left, moving_right,events):
        entry = {}
        keys = pygame.key.get_pressed()

        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                if self.backmain_button.checkForInput(mouse_pos):
                    print("Back to main menu clicked!")
                    click_sound.play()
                    pygame.mixer.music.stop()
                    #self.gameStateManager.set_state('start')
                    return False  # This will exit the level loop

        if not keys[pygame.K_SPACE]:
            self.space_released = True
        if not keys[pygame.K_q]:
            self.q_released = True  #Release Q key debounce
        if not keys[pygame.K_RETURN]: # New debounce for Enter key
            self.enter_released = True

        # --- Movement ---
        if not self.current_dialogue_ref.current_dialogue or not self.current_dialogue_ref.current_dialogue.talking:
            is_moving = self.player.move(moving_left,moving_right)
        else:
            is_moving = False
        self.player.update_animation(is_moving)
          
        # --- Dialogue logic ---
        nearest_npc = self.npc_manager.get_nearest_npc(self.player)
        near_obj = check_object_interaction(self.player.rect.inflate(10,10), interactable_objects)
        # #=====space======
        # if nearest_npc or self.current_dialogue_ref.current_dialogue:
        #     if nearest_npc: 
        #         if self.current_dialogue_ref.current_dialogue is None or isinstance(self.current_dialogue_ref.current_dialogue, ObjectDialogue):     #not self.current_dialogue_ref.current_dialogue.talking:
        #             self.current_dialogue_ref.current_dialogue = dialog(nearest_npc,self.player)
        #         elif isinstance(self.current_dialogue_ref.current_dialogue, ObjectDialogue):
        #             pass

        #     if keys[pygame.K_SPACE] and self.space_released: # Only consider space to start new NPC dialogue
        #         self.space_released = False # Debounce
        #         if self.current_dialogue_ref.current_dialogue:
        #         #     print(f"Starting NPC dialogue with {nearest_npc.name}")
        #             dialogue = self.current_dialogue_ref.current_dialogue

        #             if isinstance(dialogue, ObjectDialogue):
        #                 dialogue.handle_space()
        #             else:
        #                 dialogue.handle_space(keys)

        # 1. Handle Object Interaction (Q key)
        if keys[pygame.K_q] and self.q_released:
            self.q_released = False # Debounce the 'Q' key
            if near_obj:
                obj_to_interact = near_obj[0] # Interact with the first detected object

                # Only initiate new dialogue if no current dialogue is active
                if self.current_dialogue_ref.current_dialogue is None or not self.current_dialogue_ref.current_dialogue.talking:
                    
                    # Determine initial node based on day and conditional flags
                    chosen_start_node = obj_to_interact.start_node

                    # Step 1: Check for day-specific node
                    day_specific_node_id = obj_to_interact.day_specific_nodes.get(str(self.current_day))
                    if day_specific_node_id:
                        chosen_start_node = day_specific_node_id
                        print(f"DEBUG: Object '{obj_to_interact.name}': Using day-specific node '{chosen_start_node}' for Day {self.current_day}.")
                    else:
                        print(f"DEBUG: Object '{obj_to_interact.name}': No day-specific node for Day {self.current_day}. Falling back to default/conditional.")

                    # Step 2: Apply conditional logic (locked/unlocked) - OVERRIDES day-specific if applicable
                    if obj_to_interact.conditional_dialogue_flag:
                        condition_met = getattr(self, obj_to_interact.conditional_dialogue_flag, False)

                        if condition_met: # If condition is True (unlocked)
                            if obj_to_interact.node_if_unlocked:
                                chosen_start_node = obj_to_interact.node_if_unlocked
                                print(f"DEBUG: Object '{obj_to_interact.name}': Condition '{obj_to_interact.conditional_dialogue_flag}' TRUE, using UNLOCKED node '{chosen_start_node}'.")
                        else: # If condition is False (locked)
                            if obj_to_interact.node_if_locked:
                                chosen_start_node = obj_to_interact.node_if_locked
                                print(f"DEBUG: Object '{obj_to_interact.name}': Condition '{obj_to_interact.conditional_dialogue_flag}' FALSE, using LOCKED node '{chosen_start_node}'.")
                    
                    # Create and start ObjectDialogue
                    self.current_dialogue_ref.current_dialogue = ObjectDialogue(
                        obj_to_interact, 
                        self.current_dialogue_ref, # Reference to main Game/Rooms for dialogue management
                        self, # Reference to self (Rooms instance) for event triggering
                        start_node_id=chosen_start_node # The determined start node
                    )
                    print(f"Interacting with {obj_to_interact.name}. Dialogue started from node: {chosen_start_node}")

        # 2. Handle NPC Interaction (Space Key to START new NPC dialogue)
        # This block only triggers if no dialogue is active OR the current dialogue is an ObjectDialogue
        # (meaning if an object dialogue is active, Space won't start an NPC dialogue unless it's finished or explicitly allowed)
        if nearest_npc and keys[pygame.K_SPACE] and self.space_released:
            # Check if there's no active dialogue or if the active one is an object dialogue (which should be cleared by now)
            if self.current_dialogue_ref.current_dialogue is None or not self.current_dialogue_ref.current_dialogue.talking or isinstance(self.current_dialogue_ref.current_dialogue, ObjectDialogue):
                self.space_released = False # Debounce
                
                # Get the base dialogue data for this NPC (e.g., the entire "Nuva" dictionary)
                npc_dialogue_tree = all_dialogues.get(nearest_npc.dialogue_id) # self.all_dialogues contains the whole JSON

                if npc_dialogue_tree:
                    # Determine NPC's starting story based on current day
                    chapter_key = f"chapter_{self.current_day}"
                    chosen_story_id = chapter_key # Default to the current chapter's main node

                    # Fallback to "repeat_only" or "start" if specific chapter is missing
                    if chapter_key not in npc_dialogue_tree:
                         if "repeat_only" in npc_dialogue_tree:
                             chosen_story_id = "repeat_only"
                         else:
                             chosen_story_id = "start" # General default if nothing else found
                    
                    print(f"DEBUG: Interacting with NPC {nearest_npc.name}. Chosen story: {chosen_story_id} on Day {self.current_day}.")
                    
                    # Initialize NPC dialogue
                    self.current_dialogue_ref.current_dialogue = dialog(
                        nearest_npc, # The NPC object
                        self.player,
                        npc_dialogue_tree, # Pass the entire NPC dialogue tree (e.g., {"Nuva": {...}})
                        start_node_id=chosen_story_id, # Tell the dialog class which chapter/story to start from
                        rooms_instance=self # Pass Rooms instance for event triggering
                    )
                    self.current_dialogue_ref.current_dialogue.talking = True # Ensure it begins talking
                else:
                    print(f"Warning: No dialogue data found for NPC '{nearest_npc.dialogue_id}'.")

                    # if obj_to_interact.name == "Machine":
                    #     # Dynamically choose start node for Machine dialogue based on patient_zheng_talked_to
                    #     if not self.patient_zheng_talked_to:
                    #         chosen_start_node = "before_patient"
                    #     else:
                    #         chosen_start_node = "after_patient"
                            
                    #     # Pass 'self' (the Rooms instance) to ObjectDialogue so it can trigger events
                    #     self.current_dialogue_ref.current_dialogue = ObjectDialogue(obj_to_interact, self.current_dialogue_ref, self, initial_start_node_id=chosen_start_node)
                    #     print(f"Interacting with Machine. Start node: {chosen_start_node}")

                    # elif obj_to_interact.next_room: # Handle doors (if they have next_room defined)
                    #     if obj_to_interact.unlocked:
                    #         self.next_room_after_transition = obj_to_interact.next_room
                    #         self.fading = True
                    #         print(f"Door '{obj_to_interact.name}' triggered fade to {obj_to_interact.next_room}")
                    #     else: # Door is locked, maybe show a dialogue
                    #         # Assuming locked doors also have dialogue set up in object_data
                    #         self.current_dialogue_ref.current_dialogue = ObjectDialogue(obj_to_interact, self.current_dialogue_ref, self)
                    #         print(f"Door '{obj_to_interact.name}' is locked or has other dialogue.")
                    
                    # elif obj_to_interact.active: # General object with dialogue
                    #     self.current_dialogue_ref.current_dialogue = ObjectDialogue(obj_to_interact, self.current_dialogue_ref, self)
                    #     print(f"Interacting with general object: {obj_to_interact.name}")

        # if keys[pygame.K_SPACE] and self.space_released:
        #     self.space_released = False
        #     if self.current_dialogue_ref.current_dialogue:
        #         dialogue = self.current_dialogue_ref.current_dialogue
        #         if isinstance(dialogue, ObjectDialogue):
        #             dialogue.handle_space()
        #         else:
        #             dialogue.handle_space(keys)

        # if isinstance(self.current_dialogue_ref.current_dialogue, dialog):
        #     self.current_dialogue_ref.current_dialogue.handle_option_selection(keys)
    
        # --- Dialogue State Update and Input Handling (Unified) ---
        if self.current_dialogue_ref.current_dialogue:
            dialogue = self.current_dialogue_ref.current_dialogue
            
            # Handle input specific to dialogue choices
            if isinstance(dialogue, dialog) and dialogue.choices_active:

                dialogue.update(events) 

                if keys[pygame.K_UP] and self.space_released: # Reusing space_released for debounce, consider a new flag
                    self.space_released = False
                    dialogue.selected_choice_index = max(0, dialogue.selected_choice_index - 1)
                    print(f"Selected choice: {dialogue.selected_choice_index}")
                elif keys[pygame.K_DOWN] and self.space_released: # Reusing space_released
                    self.space_released = False
                    dialogue.selected_choice_index = min(len(dialogue.current_choices) - 1, dialogue.selected_choice_index + 1)
                    print(f"Selected choice: {dialogue.selected_choice_index}")
                elif keys[pygame.K_RETURN] and self.enter_released: # Using new enter_released debounce
                    self.enter_released = False
                    dialogue.select_choice(dialogue.selected_choice_index)
                    print(f"Confirmed choice: {dialogue.selected_choice_index}")
            else: # Only update and handle space if choices are NOT active
                dialogue.update()
                
                # SPACE key logic for advancing regular dialogue
                if keys[pygame.K_SPACE] and self.space_released:
                    self.space_released = False
                    # if dialogue: # Check again if dialogue exists (it should, due to outer if)
                    if isinstance(dialogue, ObjectDialogue):
                        dialogue.handle_space()
                    elif isinstance(dialogue, dialog):# Assuming this is your 'dialog' class
                        dialogue.handle_space(keys) # Pass keys if dialog.handle_space needs it

            # Check if dialogue has just finished
            if not dialogue.talking:
                self.current_dialogue_ref.current_dialogue = None # Clear global reference to dialogue
                print("Rooms: Current dialogue reference cleared.")
                # You might need to reset 'entry' here if it's used for display after dialogue ends
                # entry = {} 
            #     # If NPC dialogue finished
            #     if isinstance(dialogue, dialog):
            #         # Check if the last node of the NPC dialogue had an event and trigger it
            #         npc_dialogue_data = all_dialogues.get(dialogue.npc.name, {}).get(dialogue.current_story, [])
            #         if dialogue.step < len(npc_dialogue_data): # Ensure step is valid
            #             last_node_data = npc_dialogue_data[dialogue.step]
            #             if "event" in last_node_data:
            #                 self.handle_dialogue_event(last_node_data["event"])
            #     # Dialogue finished, clear reference
            #     self.current_dialogue_ref.current_dialogue = None
            #     entry = {} # Reset entry for display
            # else: # Dialogue is still talking
            #     # For NPC dialogue, update entry for display
            #     if isinstance(self.current_dialogue_ref.current_dialogue, dialog):
            #         self.npc_name = self.current_dialogue_ref.current_dialogue.npc.name
            #         self.current_story = getattr(self.current_dialogue_ref.current_dialogue, "current_story", "start")  # Might have problem here

            #         self.npc_data = all_dialogues.get(self.npc_name, {})
            #         self.story_data = self.npc_data.get(self.current_story, [])

            #         self.step = dialogue.step
            #         entry = self.story_data[self.step]
            #     else:
                    # entry = {} # ObjectDialogue doesn't use npc/story/step in the same way

        # else: # No current dialogue active
        #     entry = {} # Ensure entry is always defined if no dialogue is active
        

        
        #     # Only update story_data if the NPC or story changed
        #     if (self.last_npc_name != self.npc_name) or (self.last_story != self.current_story):
        #         self.npc_data = all_dialogues.get(self.npc_name, {})
        #         self.story_data = self.npc_data.get(self.current_story, [])
        #         self.last_npc_name = self.npc_name
        #         self.last_story = self.current_story

        #     self.step = self.current_dialogue_ref.current_dialogue.step

        #     if not self.current_dialogue_ref.current_dialogue.talking:
        #         self.current_dialogue_ref.current_dialogue = None
        #         entry = {}
        #     else:
        #         entry = self.story_data[self.step]
        # else:
        #     # 👇 This runs for ObjectDialogue — we don't use npc/story/step
        #     if not self.current_dialogue_ref.current_dialogue.talking:
        #         self.current_dialogue_ref.current_dialogue = None
        #         entry = {}
        #     else:
        #         entry = {}

        
        camera_group.custom_draw(self.player)

        self.backmain_button.draw(self.display)
        
        # --- Display "Press Q to interact" text ---
        if near_obj:
            font = pygame.font.Font(None, 24)
            text_surf = font.render("Press Q to interact", True, (0, 0, 0), (255, 255, 255))
            for obj in near_obj:
                # Calculate screen position based on camera offset
                screen_pos = obj.rect.topleft - camera_group.offset # Use camera_group.offset
                self.display.blit(text_surf, (screen_pos.x - text_surf.get_width() // 2, screen_pos.y - 20))
        

        # --- Draw dialogue if active ---
        if self.current_dialogue_ref.current_dialogue:

            if isinstance(self.current_dialogue_ref.current_dialogue, dialog):
                self.current_dialogue_ref.current_dialogue.update(events)
            # else:
             #   self.current_dialogue_ref.current_dialogue.update()


            self.current_dialogue_ref.current_dialogue.draw(self.display)
    
        # --- Handle fade-to-black transition ---
        if self.fading:
            self.fade_alpha += 5
            fade_surface = pygame.Surface(self.display.get_size())
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            self.display.blit(fade_surface, (0, 0))

            if self.fade_alpha >= 255:
                # Transition complete — change room state
                if self.next_room_after_transition:
                    target_room = self.next_room_after_transition
                    self.next_room_after_transition = None # Reset after use
                else:
                    print("Warning: Fading complete but next_room_after_transition was not set.")
                    target_room = "room01" 

                self.load_room(target_room)       # call a method to load new map/positions
                
                # If the 'day_end_and_intro_next_day' event set this flag
                if hasattr(self, 'start_intro_after_fade') and self.start_intro_after_fade:
                    print("Fade finished, starting new day's intro dialogue.")
                    self.start_intro_after_fade = False # Reset flag
                    
                    # Create a NarratorDummy and start the intro dialogue for the new day
                    class NarratorDummy:
                        def __init__(self, name="narrator", dialogue_id="System_Narrative"):
                            self.name = name
                            self.dialogue_id = dialogue_id
                            self.rect = pygame.Rect(0,0,1,1) # Dummy rect

                    # Trigger the intro dialogue for the new day/chapter
                    narrator_dummy_obj = NarratorDummy() # Use the same dummy narrator
                    system_narrative_tree = self.all_dialogues.get(narrator_dummy_obj.dialogue_id)
                    if system_narrative_tree:
                        self.current_dialogue_ref.current_dialogue = dialog(
                            narrator_dummy_obj,
                            self.player,
                            self.all_dialogues.get(narrator_dummy_obj.dialogue_id),
                            start_node_id="intro", # This will now select chapter_X based on current_day
                            rooms_instance=self
                        )
                        self.current_dialogue_ref.current_dialogue.talking = True # Ensure it begins talking
                    else:
                        print("Error: 'System_Narrative' dialogue data not found for intro after fade.")
                
                self.fading = False
                self.fade_alpha = 0

        # --- Draw dialogue if active ---
        if self.current_dialogue_ref.current_dialogue:
            #self.current_dialogue_ref.current_dialogue.update()
            self.current_dialogue_ref.current_dialogue.draw(self.display)

        # --- Trigger cutscene --- 
        if self.current_dialogue_ref.current_dialogue and self.current_dialogue_ref.current_dialogue.talking:
            
            if isinstance(self.current_dialogue_ref.current_dialogue, dialog):
                current_npc_name = self.current_dialogue_ref.current_dialogue.npc.name

                if current_npc_name == "Dean":
                    if not self.cutscene_active:
                        self.cutscene_active = True

                else:
                    self.cutscene_active = False
    
        if self.cutscene_active:
            # Check if current dialogue has triggered the cutscene event
            if isinstance(self.current_dialogue_ref.current_dialogue, dialog):
                if self.current_dialogue_ref.current_dialogue.dean_cutscene_triggered:
                    self.dean_exiting = True

        
        if self.dean_exiting:
            dean = next((npc for npc in self.npc_manager.npcs if npc.name == "Dean"), None)
            if dean:
                dean.rect.x -= 3
                if dean.rect.x < -dean.image.get_width():
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

if __name__ == '__main__':
    game = Game()

    def start_chapter_1():
        print("intro done, enter game")

    game.intro.completed_callback = start_chapter_1
    game.intro.start("chapter_1")
    game.run()
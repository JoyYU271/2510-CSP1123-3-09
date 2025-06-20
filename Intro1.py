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

game_chapter = 1 # Global variable for game chapter

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

#with open('NPC_dialog/NPC.json', 'r', encoding='utf-8') as f:
 #   all_dialogues = json.load(f)


# print("\n--- DEBUG: After loading all_dialogues ---")
# print(f"Type of all_dialogues: {type(all_dialogues)}")
# print(f"Keys in all_dialogues: {list(all_dialogues.keys())}") # See what top-level keys actually exist

#if "Zheng" in all_dialogues:
#    print("SUCCESS: 'Zheng' key found in all_dialogues.")
    # Print a snippet of Zheng's dialogue to confirm it's not empty/malformed
#    print(f"Zheng dialogue structure (first 200 chars): {str(all_dialogues['Zheng'])[:200]}...")
#else:
#    print("ERROR: 'Zheng' key NOT found in all_dialogues. Please check NPC_dialog/NPC.json for exact key name and casing.")
#print("-------------------------------------------\n")

with open("objects.json", "r") as f:
    object_data = json.load(f)



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
    "Dean_room": {
        "background_path": "picture/Map Art/Dean room.png",
        "player_start_pos": (1100, 420)
    },
    "room01": {
        "background_path": "picture/Map Art/Map clinic.png",
        "player_start_pos": (200, 420) # Default player start pos for room01
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
    },
    "subc.E_01": {
        "background_path": "picture/Map Art/P21.png",
        "player_start_pos": (640, 420)
    },
    "subc.E_02": {
        "background_path": "picture/Map Art/P22.png",
        "player_start_pos": (640, 420)
    },
    "subc.E_03.1": {
        "background_path": "picture/Map Art/P23.png",
        "player_start_pos": (640, 420)
    },
    "subc.E_03.2": {
        "background_path": "picture/Map Art/P24.png",
        "player_start_pos": (1000, 420)
    },
    "subc.E_04": {
        "background_path": "picture/Map Art/P25.png",
        "player_start_pos": (640, 420)
    },
    "subc.E_05": {
        "background_path": "picture/Map Art/P26.png",
        "player_start_pos": (640, 420)
    },
    "basement": {
        "background_path": "picture/Map Art/Basement.png",
        "player_start_pos": (100, 420)
    }
}

#============ Dialogue System =============
class Dialog:
    def __init__(self,npc,player,full_dialogue_tree, start_node_id, rooms_instance,bgm_vol=0.5,sfx_vol=0.5, language="EN",text_size=30, shown_dialogues=None, npc_manager=None,screen_surface=None):
        super().__init__()
        
        self.screen = screen_surface
        self.current_day =3 
       

        self.sounds = {
            "phone_typing": pygame.mixer.Sound("sfx/phone_typing.wav"),
            "footsteps": pygame.mixer.Sound("sfx/footsteps.wav"),
            "camera": pygame.mixer.Sound("sfx/camera.wav"),
            "car_crash": pygame.mixer.Sound("sfx/car_crash.wav"),
            "claps": pygame.mixer.Sound("sfx/claps.wav"),
            "crash": pygame.mixer.Sound("sfx/crash.wav"),
            #"crowd": pygame.mixer.Sound("sfx/crowd.wav"),
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

        self.current_bgm = None
        self.bgm_volume = bgm_vol

        self.language = language

        # Core Game References
        self.player = player
        self.npc_name = npc.name
        self.npc = npc
        self.full_dialogue_tree = full_dialogue_tree 
        self.rooms_instance = rooms_instance
        self.shown_dialogues = shown_dialogues if shown_dialogues is not None else {}
        self.npc_manager = npc_manager

        # --- Initialize these attributes BEFORE calling other methods ---
        self.talking = True
        self.choices_active = False
        self.current_line_index = 0
        self.current_node_id = start_node_id
        
        # This will now correctly use the current_day from the rooms_instance
        self.current_dialogue_list = self._get_dialogue_list_from_node_id(self.current_node_id)
        self.current_line_data = self.get_current_line_data()
        
        self.typing_complete = False
        self.text_display_timer = 0
        self.typing_speed = 2 
        self.current_text_display = ""

        self.current_choices = []
        self.selected_choice_index = 0

        self.dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()
        self.dialog_box_img.set_alpha(200)

        # Character portrait selection
        self.portrait = None
        if npc.name == "Nuva":
            self.portrait = pygame.image.load("picture/Character Dialogue/Nurse.png").convert_alpha()
        elif npc.name == "Dean":
            self.portrait = pygame.image.load("picture/Character Dialogue/Dean.png").convert_alpha()
        elif npc.name == "Zheng":
            self.portrait = pygame.image.load("picture/Character Dialogue/Patient1.png").convert_alpha()
        elif npc.name == "Emma":
            self.portrait = pygame.image.load("picture/Character Dialogue/Patient2.png").convert_alpha()
        
        self.player_portrait = pygame.image.load("picture/Character Dialogue/Doctor.png").convert_alpha()

        self.currently_playing_sfx = None
        self.sound_played_for_current_step = False
        self.current_bgm = None
        self.bgm_volume = bgm_vol
        self.text_size = text_size


        self.dean_cutscene_triggered = False # For cutscene logic
        self.last_choice_move_time = 0
        self.choice_move_delay = 400

        # Attributes for chapter ending and CGs, initialized here

        self.chapter_end = False
        self.ready_to_quit = False
        self.showing_cg = False
        self.cg_images = []
        self.cg_index = 0

        self.fade_in_cg_pending = False
        self.next_cg_index = None
       # self.story_data = npc_data.get(f"chapter_{game_chapter}", []) # Assuming npc_data is accessible and contains story data
       # self.current_story = f"chapter_{game_chapter}"
        self.shown_dialogues = shown_dialogues if shown_dialogues is not None else {}
        self.npc_manager = npc_manager

        self.reset_typing()

        if not self.current_dialogue_list:
            print(f"Error: Initial dialogue list for node '{self.current_node_id}' not found. Ending dialogue.")
            self.talking = False
            self.current_text_display = "(Dialogue error or missing text)"

    def _get_dialogue_list_from_node_id(self, node_id):
        # This function now correctly navigates the NPC.json structure
        current_data = self.full_dialogue_tree
        raw_dialogue_list = []

        if  node_id in current_data and isinstance(current_data[node_id], dict):
            chapter_key = f"chapter_{self.rooms_instance.current_day}" if hasattr(self.rooms_instance, "current_day") else "default_chapter"
            raw_dialogue_list = current_data[node_id].get(chapter_key, [])
            print(f"DEBUG: Found {len(raw_dialogue_list)} lines in {chapter_key}")
        else:
            raw_dialogue_list = current_data.get(node_id, [])
            print(f"DEBUG: Found {len(raw_dialogue_list)} lines in direct node")

        # Debug: Print the raw dialogue and their shown status
        print(f"DEBUG: Raw dialogue list for {node_id}:")
        for i, line in enumerate(raw_dialogue_list):
            if isinstance(line, dict):
               shown_status = line.get("shown", False)
               text_preview = line.get("text", "No text")[:30] + "..." if len(line.get("text", "")) > 30 else line.get("text", "No text")
               print(f"  Line {i}: shown={shown_status}, text='{text_preview}'")
            else:
               print(f"  Line {i}: Not a dict - {line}")

            # Filter out dialogue lines that have "shown": true
        filtered_dialogue_list = []
        for i, line_data in enumerate(raw_dialogue_list):
            if isinstance(line_data, dict):
               shown_status = line_data.get("shown", False)
               if not shown_status:
                  filtered_dialogue_list.append(line_data)
                  print(f"DEBUG: Including line {i} (shown={shown_status})")
               else:
                  text_preview = line_data.get("text", "No text")[:50]
                  print(f"DEBUG: Skipping line {i} (shown={shown_status}): {text_preview}")
            else:
              filtered_dialogue_list.append(line_data)
              print(f"DEBUG: Including non-dict line {i}")

              print(f"DEBUG: After filtering, {len(filtered_dialogue_list)} lines remain")
    
        if not filtered_dialogue_list and raw_dialogue_list:
            print(f"WARNING: All dialogue in node '{node_id}' has been shown already.")
        # Return the repeat_only dialogue if it exists
            repeat_node = f"{node_id}_repeat" if f"{node_id}_repeat" in current_data else "repeat_only"
            if repeat_node in current_data:
               print(f"DEBUG: Using repeat dialogue from {repeat_node}")
               return current_data.get(repeat_node, [])
    
        return filtered_dialogue_list

    def reset_typing(self):
        self.current_text_display = ""
        self.typing_complete = False
        self.text_display_timer = 0
        self.sound_played_for_current_step = False
        
        if self.current_line_data: # Make sure there's valid data
            text_content = self.current_line_data.get("text", "")
            if not text_content: # If the current line has no 'text' key (e.g., it's a choice or event), complete typing instantly.
                self.typing_complete = True
                self.current_text_display = ""
        else: # If current_line_data somehow became None, also instantly complete.
            self.typing_complete = True
            self.current_text_display = ""

    def update(self,events=None):
        if not self.talking or self.choices_active:
            return
        
       
        if events is None:
            events = []
        
        #if self.rooms_instance.cutscene_active and self.rooms_instance.dean_exiting:
        #    return

        # Handle CG showing separately from normal dialogue progression
     #   if self.showing_cg:
            # CGs are advanced by handle_space, so no typing update needed here
     #       return

        if self.current_line_index >= len(self.current_dialogue_list):
            self.typing_complete = True
            return

        current_line_data = self.current_dialogue_list[self.current_line_index]
        
        # Handle BGM changes
        if "bgm" in current_line_data and current_line_data["bgm"] != self.current_bgm:
            self.change_bgm(current_line_data["bgm"])
        elif "bgm_stop" in current_line_data:
            pygame.mixer.music.stop()
            self.current_bgm = None

        # Handle SFX
        if "sound_stop" in current_line_data:
            self.stop_all_sfx()
        if "sound" in current_line_data and not self.sound_played_for_current_step:
            sound_name = current_line_data["sound"]
            if sound_name in self.sounds:
                self.sounds[sound_name].set_volume(self.sfx_vol)
                self.sounds[sound_name].play()
                self.currently_playing_sfx = sound_name
            self.sound_played_for_current_step = True
            
        # Handle typing effect
        text_to_display = current_line_data.get("text", "")
        if not self.typing_complete:
            self.text_display_timer += 1
            chars_to_display = self.text_display_timer // self.typing_speed
            if chars_to_display > len(text_to_display):
                chars_to_display = len(text_to_display)
            self.current_text_display = text_to_display[:chars_to_display]
            if chars_to_display >= len(text_to_display):
                self.typing_complete = True



    def handle_space(self, screen, keys=None):
        global game_chapter
        global flags # Assuming 'flags' is also a global variable modified here
        global player_choices # Assuming 'player_choices' is also a global variable modified here
        
      #  if self.showing_cg:

            # If a CG is showing, space advances the CG
       #     self.cg_index += 1
     #       if self.cg_index >= len(self.cg_images):
                # All CGs displayed, stop showing CGs and continue dialogue (if any)
       #         self.showing_cg = False
       #         self.cg_images = [] # Clear images
       #         self.cg_index = 0
                # Now check if there's more dialogue to proceed to after CGs
                # This will be handled by the normal dialogue advancement below
       #     else:
                # Fade to the next CG
       #         self.fade(screen, cg_list=[self.cg_images[self.cg_index]], fade_in=True)
       #         return # Consume space and don't advance dialogue yet

        if self.showing_cg:
            # If a CG is showing, space advances the CG
            if self.cg_index < len(self.cg_images) - 1:
                self.next_cg_index = self.cg_index + 1
                self.fade_in_cg_pending = True
                return        # 等玩家再按 SPACE

        if not self.talking or self.choices_active:
            return

        if not self.typing_complete:
            # Instantly complete the text of the current line
            if self.current_line_data: # Ensure current_line_data is valid
                self.current_text_display = self.current_line_data.get("text", "")
            self.typing_complete = True
            return
        
        # Mark current line as shown before advancing
        if self.current_line_data and isinstance(self.current_line_data, dict):
           self.current_line_data["shown"] = True
           print(f"Marked as shown: {self.current_line_data.get('text', 'No text')[:50]}...")

        if self.current_line_data and "cg" in self.current_line_data and not self.showing_cg:
            cg_paths = (self.current_line_data["cg"]
                        if isinstance(self.current_line_data["cg"], list)
                        else [self.current_line_data["cg"]])
            self.cg_images = [pygame.image.load(p).convert_alpha()
                            for p in cg_paths]
            self.cg_index = 0
            self.showing_cg = True
            self.fade(screen, cg_list=[self.cg_images[0]], fade_in=True)
            return
        
        # Advance to the next line
        self.current_line_index += 1
        self.current_line_data = self.get_current_line_data()

        if self.current_line_data:
            # Handle CG trigger if present
            if "cg" in self.current_line_data:

                cg_paths = self.current_line_data["cg"] if isinstance(self.current_line_data["cg"], list) else [self.current_line_data["cg"]]
                self.cg_images = [pygame.image.load(path).convert_alpha() for path in cg_paths]
                self.cg_index = 0
                self.showing_cg = True
                self.fade(screen, fade_in=True,cg_list=[self.cg_images[self.cg_index]])
                self.reset_typing() # Reset typing for the next potential dialogue after CG
                return # Consume space, CG will be handled


            if "choice" in self.current_line_data:
                self.current_choices = self.current_line_data["choice"]
                self.choices_active = True
                self.selected_choice_index = 0
                self.reset_typing()
                return
            
            if "next" in self.current_line_data:
                next_node_id = self.current_line_data["next"]
                self._transition_to_node(next_node_id)
                return
            
            if "event" in self.current_line_data:
                event_name = self.current_line_data["event"]
                # Handle specific events
                if event_name == "dean_exit_cutscene":
                    flags["dean_cutscene_played"] = True
                    self.dean_cutscene_triggered = True 

                    # Save checkpoint
                    save_checkpoint(
                        npc_name=self.npc_name,
                        chapter=f"chapter_{game_chapter}", # Use current global game_chapter
                        step=self.current_line_index,
                        player_choices=player_choices,
                        flags=flags,
                        shown_dialogues=self.shown_dialogues
                    )
                self.rooms_instance.handle_dialogue_event(event_name)
                self.reset_typing()     
                return
            
            # Handle "ending" type directly in handle_space
            if self.current_line_data.get("type") == "ending":
                print("DEBUG: Ending type detected!")
                self.ending_triggered = True

            if getattr(self, 'ending_triggered', False):
                print(f"DEBUG: Ending triggered! current_day = {self.current_day}") 
                self.ending_triggered = False 
                self.chapter_end = True   

                if self.current_day >= 3:   
                    self.ready_to_quit = True
                    fade_to_main(screen)
                    print(f"Main ending reached! ready_to_quit set to True") 
                else:
                    self.fade(screen , fade_in=True,cg_list=None) # Assuming 'screen' is accessible here
                    # Reset dialogue state for next chapter
                    self.current_line_index = 0 
                    self.talking = False # End current dialogue
                    self.chapter_end = False

                    self.current_story = f"chapter_{self.current_day}"
                    # Update story_data to reflect the new chapter's dialogue
                    self.story_data = npc_data.get(self.current_story,[]) 
                    # Re-initialize current_dialogue_list based on the new chapter's start node
                    # You might need a new mechanism to get the start_node_id for the next chapter
                    # For now, assuming it will be handled by the Rooms class transitioning to a new room/dialogue
                    self.current_day +=1
                    print(f"Moving to chapter {self.current_day}") 

                    

                    
                ending_key = f"chapter_{game_chapter}" # This ensures it's updated for saving
                flags[f"ending_unlocked_{ending_key}"] = True

                # save unlocked state
                save_checkpoint(
                    npc_name=self.npc_name,
                    chapter=f"chapter_{game_chapter}", # Use updated global chapter
                    step=self.current_line_index,
                    player_choices=player_choices,
                    flags=flags,
                    shown_dialogues=self.shown_dialogues
                )
                return # Consume space after handling ending

            # If it's just another line of text, reset typing for it
            self.reset_typing()
        else:
            # Reached the end of the dialogue list for this node
            self.talking = False
            print("NPC Dialogue ended (natural end of node).")

    

    def select_choice(self, choice_index,screen):
        if self.choices_active and 0 <= choice_index < len(self.current_choices):

            if self.current_line_data and isinstance(self.current_line_data, dict):
                self.current_line_data["shown"] = True
                print(f"Marked choice as shown: {self.current_line_data}")
                
            selected_option = self.current_choices[choice_index]
            next_node_id = selected_option["next"]
            self.choices_active = False
            

            if next_node_id == "back_reality":
                self.talking = False
                self.rooms_instance.current_dialogue_ref = None
                self.rooms_instance.handle_dialogue_event("back_to_reality")
            elif next_node_id.startswith("sub_end_"):
                self.rooms_instance.handle_dialogue_event(f"show_sub_ending_{next_node_id}")
                self.talking = False
            elif next_node_id.startswith("end_"):
                # Handle main ending display
                self.rooms_instance.handle_dialogue_event(f"show_main_ending_{next_node_id}")
                self.talking = False
            else:
                self._transition_to_node(next_node_id)

                if self.current_line_data and "cg" in self.current_line_data:
                   cg_paths = self.current_line_data["cg"] if isinstance(self.current_line_data["cg"], list) else [self.current_line_data["cg"]]
                   self.cg_images = [pygame.image.load(path).convert_alpha() for path in cg_paths]
                   self.cg_index = 0
                   self.showing_cg = True
                   self.fade(screen, fade_in=True, cg_list=[self.cg_images[self.cg_index]])
                   self.reset_typing()
            
        else:
            print("Invalid choice selection or no choices active.")

    def _transition_to_node(self, node_id):
        new_dialogue_list = self._get_dialogue_list_from_node_id(node_id)
        
        if new_dialogue_list:
            self.current_node_id = node_id
            self.current_dialogue_list = new_dialogue_list
            self.current_line_index = 0
            self.choices_active = False
            self.selected_choice_index = 0
            self.current_line_data = self.get_current_line_data() # Get data for the new line
            self.reset_typing()
        else:
            print(f"Warning: Next node '{node_id}' not found or invalid format. Ending dialogue.")
            self.talking = False
            if hasattr(self.rooms_instance, 'current_dialogue_ref'):
                self.rooms_instance.current_dialogue_ref = None

    def draw(self, screen):
        # Draws the dialogue box, portraits, speaker names, text, and choices.
        if not self.talking:
            return

        dialog_x = screen.get_width() // 2 - self.dialog_box_img.get_width() // 2
        dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20
        text_max_width = self.dialog_box_img.get_width() - 300

        # Always blit the dialog box first, regardless of choices or text
        screen.blit(self.dialog_box_img, (dialog_x, dialog_y))
        # print(f"DEBUG (dialog.draw): Drawing at dialog_x={dialog_x}, dialog_y={dialog_y}. Screen size: {screen.get_size()}")

        # --- Handle drawing based on dialogue type (choices vs. normal text) ---
        # THIS IS THE CRITICAL IF-ELSE BRANCH
        if self.choices_active: # <--- THIS MUST BE THE PRIMARY CHECK FOR CHOICES
            # print(f"DEBUG (dialog.draw): Choices are ACTIVE. Selected index: {self.selected_choice_index}")

            # Draw speaker name for choices (e.g., "You Decide")
            name_to_display = "" # Or customize this
            draw_text(screen, self.text_size, self.text_size, (0, 0, 0), dialog_x + 200, dialog_y + 10, center=False)

            max_options_display = 3
            dialog_center_x = dialog_x + self.dialog_box_img.get_width() // 2

            for i, option in enumerate(self.current_choices[:max_options_display]):
                color = (255, 0, 0) if i == self.selected_choice_index else (0, 0, 0)
                option_y = dialog_y + 60 + i * 40

                if option_y < screen.get_height() - 40:
                    draw_text(screen, option["option"], self.text_size, color, dialog_center_x, option_y, center=True)
                    print(f"DEBUG (dialog.draw): Choice {i}: '{option['option']}' blitted.") # Enable if needed

        else: # <--- THIS IS THE BRANCH FOR NORMAL TEXT DIALOGUE
            # Only fetch current_line_data if it's NOT a choice scene
            print(f"DEBUG (dialog.draw): Choices are NOT active. (Inside normal text branch)")
            current_line_data = self.current_line_data
            print(f"DEBUG (dialog.draw): current_line_data (normal text branch): {current_line_data}")

            if current_line_data: # Only draw normal text if current_line_data is valid
                speaker_type = current_line_data.get("speaker", "narrator")

                # --- Choose portrait and position based on speaker ---
                portrait = None
                name_to_display = ""
                portrait_pos = (0, 0)

                if speaker_type == "npc":
                    portrait = self.portrait
                    name_to_display = self.npc.name
                    portrait_pos = (dialog_x + 800, dialog_y - 400)
                elif speaker_type == "player":
                    portrait = self.player_portrait
                    name_to_display = "You"
                    portrait_pos = (dialog_x + 20, dialog_y - 400)
                else: # narrator
                    portrait = None
                    name_to_display = ""

                if portrait:
                    screen.blit(portrait, portrait_pos)

                # --- Draw speaker name ---
                draw_text(screen, name_to_display, 40, (0, 0, 0), dialog_x + 200, dialog_y + 15, center=False)

                text_to_display = self.current_text_display
                # print(f"DEBUG (dialog.draw): Drawing normal text: '{text_to_display}', Typing complete: {self.typing_complete}")

                draw_text(screen, text_to_display, self.text_size, (0, 0, 0),
                          dialog_x + self.dialog_box_img.get_width() // 2,
                          dialog_y + self.dialog_box_img.get_height() // 2 - 15,

                          center=True , max_width=text_max_width)


            else:
                # This print will appear if current_line_data somehow becomes None
                # when choices_active is False, indicating a problem with dialogue flow.
                print("DEBUG (dialog.draw): current_line_data is None for non-choice dialogue. Skipping drawing.")    
                

    def get_current_line_data(self):
        if self.talking and self.current_line_index < len(self.current_dialogue_list):
            return self.current_dialogue_list[self.current_line_index]
        return None
        
    def change_bgm(self, bgm_path):
        if bgm_path != self.current_bgm:
            self.current_bgm = bgm_path
            if self.bgm_volume > 0:
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


    def fade ( self, screen, cg_list, fade_in =True):
        fade = pygame.Surface((screen.get_width(),screen.get_height()))
        fade.fill((0,0,0))
        if cg_list:
            original_image =  cg_list[0]
        #for original_image in cg_list:
            cg_image_scaled = pygame.transform.scale(original_image ,(screen.get_width(),screen.get_height())).convert_alpha()
        else:
            cg_image_scaled = None

        if fade_in:
            #fade in
           for alpha in range (255, -1, -10):
                fade.set_alpha(alpha)
                
                if cg_image_scaled:
                    screen.blit(cg_image_scaled, (0,0))
                screen.blit(fade,(0,0))
                pygame.display.update()
                pygame.time.delay(30)
        else:
            #fade out
            for alpha in range (0,255,10):
                
                fade.set_alpha(alpha)
                if cg_image_scaled:
                    screen.blit(cg_image_scaled, (0,0))
                screen.blit(fade,(0,0))
                pygame.display.update()
                pygame.time.delay(30)
            

    def get_current_cg(self):
        if self.cg_images and self.cg_index < len(self.cg_images):
            # No need to load again, it's already a pygame.Surface
            return self.cg_images[self.cg_index]
        return None
    
    def draw(self,screen):
        if not self.talking:
            # print("DEBUG (dialog.draw): Not talking, returning early.")
            return
        
        if self.showing_cg:
           current_cg = self.get_current_cg()
           if current_cg:
              cg_scaled = pygame.transform.scale(current_cg, (screen.get_width(), screen.get_height()))
              screen.blit(cg_scaled, (0, 0))
        
        if hasattr(self, 'showing_cg') and self.showing_cg:
            cg_surface = self.get_current_cg()
            if cg_surface:
                screen.blit(pygame.transform.scale(cg_surface, screen.get_size()), (0, 0))

        #let the dialog box on the center and put below
        dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
        dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20
        screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

        #calculate text width with limit for wrapping
        text_max_width = self.dialog_box_img.get_width() - 300 #pixel padding each side

        # print(f"DEBUG (dialog.draw): Drawing at dialog_x={dialog_x}, dialog_y={dialog_y}. Screen size: {screen.get_size()}")

        current_line_data = self.get_current_line_data()
        # print(f"DEBUG (dialog.draw): current_line_data: {current_line_data}")

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
            # print(f"DEBUG (dialog.draw): Dialog box blitted. Position: ({dialog_x}, {dialog_y})")

            # --- Draw speaker name ---
            # You had dialog_x + 200 for speaker name
            draw_text(screen, name_to_display, 40, (0, 0, 0), dialog_x + 150, dialog_y + 5, center=False) # Black text
            # print(f"DEBUG (dialog.draw): Speaker name '{name_to_display}' blitted.")

            if self.choices_active:
                print(f"DEBUG (dialog.draw): Choices are active. Selected index: {self.selected_choice_index}")
                # --- Draw choice options if present ---
                max_options_display = 3 # display at most 3 options (from your old code)
                dialog_center_x = dialog_x + self.dialog_box_img.get_width() // 2

                key_hint_font = pygame.font.SysFont('Comic Sans MS', 20)
                key_hint_text1 = key_hint_font.render("Press W/S to select,",True,(0,0,0))
                key_hint_rect1 = key_hint_text1.get_rect(bottomright=(dialog_x + self.dialog_box_img.get_width() - 90,  dialog_y + self.dialog_box_img.get_height() - 40))
                key_hint_text2 = key_hint_font.render("  E to comfirm",True,(0,0,0))
                key_hint_rect2 = key_hint_text2.get_rect(bottomright=(dialog_x + self.dialog_box_img.get_width() - 90,  dialog_y + self.dialog_box_img.get_height() - 20))

                screen.blit(key_hint_text1,key_hint_rect1)
                screen.blit(key_hint_text2,key_hint_rect2)


                for i, option in enumerate(self.current_choices[:max_options_display]):
                    # Red for selected option, black for others (from your old code)
                    color = (255, 0, 0) if i == self.selected_choice_index else (0, 0, 0)
                    
                    # Position choices relative to dialog box and center
                    option_y = dialog_y + 60 + i * 40 # From your old code
                    
                    # Ensure option is on screen (from your old code)
                    if option_y < screen.get_height() - 40: 
                        draw_text(screen, option["option"], self.text_size, color, dialog_center_x, option_y, center=True)
            else: # --- Draw normal dialogue text ---
                text_to_display = self.current_text_display
                hint_font = pygame.font.SysFont('Comic Sans MS', 20)
                hint_text = hint_font.render("Press SPACE to continue", True, (0,0,0))
                hint_rect = hint_text.get_rect(bottomright=(dialog_x + self.dialog_box_img.get_width() - 90,  dialog_y + self.dialog_box_img.get_height() - 20))
                screen.blit(hint_text, hint_rect)
                # print(f"DEBUG (dialog.draw): Drawing normal text: '{text_to_display}', Typing complete: {self.typing_complete}")

                # Draw dialogue text, centered in the dialogue box (from your old code)
                draw_text(screen, text_to_display, self.text_size, (0, 0, 0), 
                          dialog_x + self.dialog_box_img.get_width() // 2, 
                          dialog_y + self.dialog_box_img.get_height() // 2 - 35 , 
                          center=True, max_width=text_max_width)
        else:
            print("DEBUG (dialog.draw): current_line_data is None. Skipping text/choice drawing.")
            
        


    #def handle_space(self):
       #  global save_message_timer  
       #  #start dialogue if not talked
      #   if not self.talking:
          #    self.talking = True
          #    self.load_dialogue(self.npc_name,self.current_story)
          #    return
         

       #  if self.npc_name == "Nuva" and self.current_node_id == "repeat_only":
         #   dialogue_id = f"{self.npc_name}_{self.current_story}_{self.step}"
         #   if dialogue_id in self.shown_dialogues:
         #       self.talking = False
          #      return


         #process current dialogue step
        # if self.step <len(self.story_data):
        #      entry = self.story_data[self.step]
        #      text = entry.get("text","")

        #      dialogue_id = f"{self.npc_name}_{self.current_story}_{self.step}"
        #      self.shown_dialogues[dialogue_id] = True


    def load_dialogue(self,npc_name,chapter):
        #update NPC detials
        self.npc_name = npc_name
        self.npc_data = self.all_dialogues.get(self.npc_name, {})
        self.current_story = chapter
        self.story_data = self.npc_data.get(self.current_story,[])

    def get_dialogue_list_from_node_id(self,node_id):
        current_data = self.full_dialogue_tree
        raw_dialogue_list = []

        if node_id in current_data and isinstance(current_data[node_id], dict):
        # For System_Narrative (intro)
           chapter_key = f"chapter_{self.rooms_instance.current_day}" if hasattr(self.rooms_instance, "current_day") else "default_chapter"
           raw_dialogue_list = current_data[node_id].get(chapter_key, [])
        else:
        # For regular NPC dialogue nodes
           raw_dialogue_list = current_data.get(node_id, [])

        filtered_dialogue_list = []
        for line_data in raw_dialogue_list:
             if isinstance(line_data, dict):
                 # Only include lines that haven't been shown yet
                if not line_data.get("shown", False):
                    filtered_dialogue_list.append(line_data)
                else:
                  print(f"Skipping already shown dialogue: {line_data.get('text', 'No text')[:50]}...")
             else:
            # If it's not a dict, include it (shouldn't happen in your structure)
                filtered_dialogue_list.append(line_data)
    
        if not filtered_dialogue_list and raw_dialogue_list:
           print(f"Warning: All dialogue in node '{node_id}' has been shown already.")
    
        return filtered_dialogue_list
    


     


    
        
    #     for i, entry in enumerate(raw_story_data):
    #         dialogue_id = f"{self.npc_name}_{self.current_story}_{i}"
            
    #         if ("shown" not in entry or entry["shown"] != False) or (dialogue_id not in self.shown_dialogues):
    #             filtered_story_data.append(entry)

    #         elif self.npc_name == "Nuva" and self.current_story == "chapter_1_common" and entry.get("text") == "She is waiting in your office,you can head over when you are ready":
    #             if dialogue_id not in self.shown_dialogues:
    #                 filtered_story_data.append(entry)
   
    #     # set filtered dialogue n reset state
    #             self.step_map.append(i)
        
    #     self.story_data = filtered_story_data
        
    #     # if start_step in self.step_map:
    #     #    self.step = self.step_map.index(start_step)
    #     # else:
    #     #    self.step = 0
        
    #     self.reset_typing()


    #     if filtered_story_data:
    #         first_entry = filtered_story_data[0]

    #         if "cg" in first_entry:
    #             paths = first_entry["cg"] if isinstance(first_entry["cg"], list) else [first_entry["cg"]]
    #             self.cg_images = [pygame.image.load(path) for path in paths]
    #             self.cg_index = 0
    #             self.showing_cg = True
             

    #     self.sound_played_for_current_step = False 

    def update_font_size(self, new_size):
        # Updates a global font size variable (if used by draw_text).
        global current_font_size # Assuming 'current_font_size' is a global variable
        if 'current_font_size' in globals(): # Safer check
            current_font_size = new_size 
        else:
            print("Warning: global 'current_font_size' not found. Font size update may not apply.")
            
# =============text setting================
def draw_text(surface, text, size=None, color=(0,0,0), x=0, y=0, center=False, max_width=None): 
    global current_text_size
    font_size = size if size is not None else current_text_size
    font = pygame.font.Font('fonts/NotoSansSC-Regular.ttf', font_size)

    line_y = y
    line_height = font.size('Tg')[1]#height of a typical line

    # If no max width is specified or text is short, render it normally
    if max_width is None :
        text_surface = font.render(text,True,color)
        text_rect = text_surface.get_rect()# set the words location (in center)
        if center:
            text_rect.center = (x,y)
        else:
            text_rect.topleft =(x,y)
        surface.blit(text_surface, text_rect)
        return y + text_rect.height #return the y position after the text
    
    
  
    current_line = ""
    

    for char in text:
        test_line = current_line + char 
        # test if this line woy=uld be too wide
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            #render the current line
            line_surface = font.render(current_line, True, color)
            line_rect = line_surface.get_rect()
            if center:
                    line_rect.midtop = (x,line_y)
            else:
                    line_rect.topleft = (x,line_y)
            surface.blit(line_surface,line_rect)
            line_y += line_height
                #start a new line with the current word
            current_line = char

    if current_line:
        line_surface = font.render(current_line,True,color)
        line_rect = line_surface.get_rect()
        if center:
            line_rect.midtop =(x,line_y)
        else:
            line_rect.topleft = (x,line_y)
        surface.blit(line_surface, line_rect)
        line_y += line_height

    return line_y #return the y position after all text
    

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
                self.dialogue = language_dialogues.get("System_Narrative", {}).get("intro", []).get(chapter, [])
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
            "Monitor": "Object_image/Z04_Random.png",
            "Chest": "Object_image/exit_E01.png",
            "Poster": "Object_image/E01_Lock.png",
            "Dresser": "Object_image/E01_Key1.png",
            "Paint_roller": "Object_image/E01_Key2.png",
            "Curtains": "Object_image/exit_E02.png",
            "Torn_dress": "Object_image/E02_Lock.png",
            "Vanity01": "Object_image/E02_Random.png",
            "Vanity02": "Object_image/E02_Key.png",
            "Car": "Object_image/exit_E03.png",
            "Welcome_mat": "Object_image/E03_path.png",
            "House_mat": "Object_image/E03_path_.png",
            "Clothes_rack": "Object_image/E03_Key.png",
            "Piano": "Object_image/E03_Random.png",
            "Dream_door": "Object_image/exit_E04.png",
            "Pill_bottle": "Object_image/E04_Lock.png",
            "Coat": "Object_image/E04_Key.png",
            "Mirror": "Object_image/exit_E05.png",
            "Medbed": "Object_image/E05_Random.png",
            "Dean_desk": "Object_image/D_Key.png",
            "Bookshelves": "Object_image/D_Lock.png",
            "Player_door": "Object_image/P_path.png",
            "base_path": "Object_image/base_path.png",
            "Dean_door": "Object_image/D_path.png"
        }

class InteractableObject(pygame.sprite.Sprite):
    def __init__(self, name, position, dialogue_id, start_node, image_path=None, active=True, text=None, next_room=None, unlocked=True, conditional_dialogue_flag=None, node_if_locked=None, node_if_unlocked=None, day_specific_nodes=None, draw_layer="mid_layer", has_dialogue=True, required_flags=None):
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
        self.has_dialogue = has_dialogue
        self.required_flags = required_flags
   
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

class ObjectDialogue: 
    def __init__(self, obj_info, current_dialogue_ref, rooms_instance,dialogue_data, start_node_id="start", text_size=30, language="EN"):
        self.obj_info = obj_info # The InteractableObject instance
        self.current_dialogue_ref = current_dialogue_ref # Reference to Rooms' current_dialogue_ref
        self.rooms_instance = rooms_instance # Reference to the Rooms instance
        self.dialogue_id = obj_info.dialogue_id # ID to fetch dialogue data from object_dialogue.json

        self.text_size = text_size
        self.language = language

        # Load all dialogue data for this object
        self.dialogue_data = dialogue_data.get(self.dialogue_id, {})
        
        # The actual starting node for THIS instance of dialogue (determined by Rooms or get_start_node_for_interaction)
        self.current_node_id = start_node_id 
        self.current_node = self.dialogue_data.get(self.current_node_id, []) # The list of dialogue lines for the current node
        
        # Typing animation variables
        self.current_text_index = 0 # Index for the current line within current_node
        self.current_line_data = {} # The dictionary for the current dialogue line

        self.talking = True # Dialogue starts talking immediately
        self.current_text_display = "" # The text currently displayed (character by character)
        self.typing_speed = 3 # Characters per frame, adjust as needed
        self.text_display_timer = 0
        self.typing_complete = False # Flag indicating if the current line has finished typing

        # For dialogue box rendering
        try:
            self.dialogue_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()
            self.dialogue_box_img.set_alpha(200) # Semi-transparent
        except pygame.error as e:
            print(f"FATAL ERROR (ObjectDialogue.__init__): Could not load dialog_box_img: {e}. Using dummy blue square.")
            self.dialogue_box_img = pygame.Surface((800, 200)) 
            self.dialogue_box_img.fill((0, 0, 255)) # Bright blue for error indication
            self.dialogue_box_img.set_alpha(255) 

        # Call reset_typing to prepare the first line
        self.reset_typing()

        # Debugging: check if the initial node was found
        if not self.current_node:
            print(f"Warning: ObjectDialogue initialized with empty or missing node '{self.current_node_id}' for dialogue_id '{self.dialogue_id}'. Dialogue might end immediately.")
        
    def _get_current_line_data(self):
        # """Helper to get the dictionary for the current line in the current_node list."""
        if self.current_text_index < len(self.current_node):
            return self.current_node[self.current_text_index]
        return None

    def reset_typing(self):
        # """
        # Resets the typing animation state for a new line of dialogue.
        # Marks as complete instantly if the line contains no text (e.g., only an event or 'next' pointer).
        # """
        self.text_display_timer = 0
        self.typing_complete = False
        self.current_text_display = ""
        
        # Get the data for the current line's dictionary AFTER index has been advanced/set
        self.current_line_data = self._get_current_line_data()

        if self.current_line_data:
            # If the current line has text, prepare for typing. Otherwise, it's an event/next, so skip typing.
            text_content = self.current_line_data.get("text", "")
            if not text_content: 
                self.typing_complete = True # Mark as complete instantly if no text
                self.current_text_display = ""
        else: 
            # This means current_text_index is out of bounds for current_node, or current_node is empty.
            # Signal completion, and handle_space will end the dialogue.
            self.typing_complete = True 
            self.current_text_display = ""
            print(f"DEBUG (ObjectDialogue.reset_typing): current_line_data is None. Setting typing_complete = True. Index: {self.current_text_index}, Node Length: {len(self.current_node)}")


    def update(self, events=None):
        # """Updates the dialogue typing animation."""
        if not self.talking or self.rooms_instance.fading: 
            return
        
        # Check if current_line_data is valid before attempting to type
        if self.current_line_data is None: 
            self.typing_complete = True
            self.current_text_display = ""
            return
        
        #stop all sounds if sound_stop is requested
        if "sound_stop" in self.current_line_data:
            pygame.mixer.stop()
            print("DEBUG: sound_stop triggered in ObjectDialogue.")


        if "sound" in self.current_line_data and not hasattr(self, 'sound_played_for_current_step'):
            self.sound_played_for_current_step = False
        if "sound" in self.current_line_data and not self.sound_played_for_current_step:
            sound_name = self.current_line_data["sound"]
            try:
                sfx = pygame.mixer.Sound(f"sfx/{sound_name}.wav")
                sfx.set_volume(self.rooms_instance.sfx_vol)
                sfx.play()
                self.sound_played_for_current_step = True
            except Exception as e:
                print(f"[SFX Error] Could not play sound '{sound_name}': {e}")

        text_to_type = self.current_line_data.get("text", "")
        
        if not self.typing_complete:
            self.text_display_timer += 1
            chars_to_display = self.text_display_timer // self.typing_speed
            chars_to_display = min(chars_to_display, len(text_to_type)) # Ensure no IndexError
            
            self.current_text_display = text_to_type[:chars_to_display]
            
            if chars_to_display >= len(text_to_type):
                self.typing_complete = True
    
    def _transition_to_node(self, node_id):
        # """Transitions dialogue to a new specified node ID within object_dialogue."""
        new_current_node = self.dialogue_data.get(node_id, [])
        
        if new_current_node:
            self.current_node_id = node_id
            self.current_node = new_current_node
            self.current_text_index = 0
            self.current_line_data = self._get_current_line_data() # Get the first line of the new node
            self.reset_typing() 
            print(f"ObjectDialogue: Transitioned to new dialogue node: {self.current_node_id}")
        else:
            print(f"Warning: ObjectDialogue: Next node '{node_id}' not found or invalid format. Ending dialogue.")
            self.talking = False
            # --- CRITICAL FIX: REMOVE THIS LINE ---
            # self.rooms_instance.current_dialogue_ref.current_dialogue = None # This causes race conditions

    def handle_q(self):
        # """Handles spacebar input to advance dialogue or complete typing."""
        if not self.talking:
            return

        if not self.typing_complete:
            # If text is still typing, complete it instantly
            if self.current_line_data: # Ensure current_line_data is valid
                self.current_text_display = self.current_line_data.get("text", "")
            self.typing_complete = True
            return

        # Typing is complete, advance to the next line or handle node transition/event
        self.current_text_index += 1
        self.current_line_data = self._get_current_line_data() # Get the data for the next line

        if self.current_line_data: # If there's a next line in the current node list
            # Check for 'next' node jump or 'event' within this line's dictionary
            if "next" in self.current_line_data:
                next_node_id = self.current_line_data["next"]
                self._transition_to_node(next_node_id)
                return

            if "event" in self.current_line_data:
                event_name = self.current_line_data["event"]
                
                # Get event_data from the current dialogue line itself
                event_data_from_json = self.current_line_data.get("event_data", {}) 
                event_data_to_pass = event_data_from_json.copy() 
                
                # Add target_room if present in obj_info (this is specific to the ObjectDialogue's object)
                if hasattr(self.obj_info, 'next_room') and self.obj_info.next_room:
                    event_data_to_pass["target_room"] = self.obj_info.next_room
                print(f"ObjectDialogue: Triggering event: {event_name} with data: {event_data_to_pass}")
                self.rooms_instance.handle_dialogue_event(event_name, event_data_to_pass) 
                self.talking = False # End this dialogue instance
                print("ObjectDialogue: Event handled, this dialogue instance is stopping.")
                return
            # If it's a regular text line (and no next/event), reset typing for it
            self.reset_typing() 
        else: # End of current dialogue list for this node (natural end of dialogue)
            self.talking = False
            print("ObjectDialogue ended (natural end of node).")
       
    def get_start_node_for_interaction(self):
        global flags
        chosen_node = self.obj_info.start_node # Default to the object's initial start_node

        # 1. Check for day-specific nodes first (highest priority)
        # Assumes day_specific_nodes is a dict like {"1": "node_id_day1", "2": "node_id_day2"}
        day_specific_node_id = None
        if self.obj_info.day_specific_nodes and isinstance(self.rooms_instance.current_day, (int, str)):
            day_specific_node_id = self.obj_info.day_specific_nodes.get(str(self.rooms_instance.current_day))
        
        if day_specific_node_id:
            print(f"DEBUG ({self.obj_info.name}): Using day-specific node: {day_specific_node_id}")
            return day_specific_node_id

        # 2. Check for REQUIRED_FLAGS (new, higher priority than single conditional_dialogue_flag)
        if self.obj_info.required_flags: # If required_flags list is not empty
            all_required_flags_met = True
            for flag_name in self.obj_info.required_flags:
                if not flags.get(flag_name, False): # If any required flag is False or missing
                    all_required_flags_met = False
                    break # No need to check further flags
            
            if all_required_flags_met:
                print(f"DEBUG ({self.obj_info.name}): All required flags {self.obj_info.required_flags} met. Directing to unlocked node.")
                return self.obj_info.node_if_unlocked if self.obj_info.node_if_unlocked else chosen_node
            else:
                print(f"DEBUG ({self.obj_info.name}): Required flags {self.obj_info.required_flags} NOT all met. Directing to locked node.")
                return self.obj_info.node_if_locked if self.obj_info.node_if_locked else chosen_node

        # 3. Fallback to GENERAL CONDITIONAL_DIALOGUE_FLAG (for objects using the old single flag system)
        elif self.obj_info.conditional_dialogue_flag: # If required_flags was empty/None, check conditional_dialogue_flag
            condition_met = flags.get(self.obj_info.conditional_dialogue_flag, False)
            if condition_met: 
                print(f"DEBUG ({self.obj_info.name}): Conditional flag '{self.obj_info.conditional_dialogue_flag}' met. Directing to unlocked node.")
                return self.obj_info.node_if_unlocked if self.obj_info.node_if_unlocked else chosen_node
            else: 
                print(f"DEBUG ({self.obj_info.name}): Conditional flag '{self.obj_info.conditional_dialogue_flag}' NOT met. Directing to locked node.")
                return self.obj_info.node_if_locked if self.obj_info.node_if_locked else chosen_node

        # --- FIX: New (or modified) block for inherent 'unlocked' status ---
        # This specifically checks the 'unlocked' status set by Rooms.load_room (e.g., from unlocked_day)
        if self.obj_info.unlocked: # If the object is marked as UNLOCKED (e.g., by unlocked_day on current day)
            print(f"DEBUG ({self.obj_info.name}): Object is currently UNLOCKED by its .unlocked status. Directing to UNLOCKED node.")
            return self.obj_info.node_if_unlocked if self.obj_info.node_if_unlocked else chosen_node
        elif not self.obj_info.unlocked: # If the object is currently LOCKED by its .unlocked status (e.g., not yet on unlocked_day)
            print(f"DEBUG ({self.obj_info.name}): Object is currently LOCKED by its .unlocked status. Directing to LOCKED node.")
            return self.obj_info.node_if_locked if self.obj_info.node_if_locked else chosen_node
        # --- END FIX ---

        print(f"DEBUG ({self.obj_info.name}): No special conditions met. Returning default start_node: {chosen_node}")
        return chosen_node

    def draw(self, screen):
        # Draws the dialogue box and text for the ObjectDialogue."""
        if not self.talking: return

        dialog_x = screen.get_width() // 2 - self.dialogue_box_img.get_width() // 2
        dialog_y = screen.get_height() - self.dialogue_box_img.get_height() - 20
        screen.blit(self.dialogue_box_img, (dialog_x, dialog_y))

        # Padding and text positioning
        text_x = dialog_x + self.dialogue_box_img.get_width() // 2
        text_y = dialog_y + self.dialogue_box_img.get_height() // 2 - 15
        max_text_width = self.dialogue_box_img.get_width() - 200 # Padding on each side
        text_color = (0, 0, 0) # Black text

        hint_font = pygame.font.SysFont('Comic Sans MS', 20)
        hint_text = hint_font.render("Press Q to continue", True, (0,0,0))
        hint_rect = hint_text.get_rect(bottomright=(dialog_x + dialog_box_img.get_width() - 90,  dialog_y + dialog_box_img.get_height() - 20))

        screen.blit(hint_text, hint_rect)

        # Draw dialogue text
        draw_text(screen, self.current_text_display, size=self.text_size, color=text_color, 
                    x=text_x, y=text_y, center=True, max_width=max_text_width)


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

        if self.language == "CN":
            with open('NPC_dialog/NPC_CN.json', 'r', encoding='utf-8') as f:
                self.all_dialogues = json.load(f)
        else:
            with open('NPC_dialog/NPC.json', 'r', encoding='utf-8') as f:
                self.all_dialogues = json.load(f)

        if self.language == "CN":
            with open("object_dialogue_cn.json", "r", encoding="utf-8") as f:
                self.object_dialogue = json.load(f)
        else:
            with open("object_dialogue.json", "r", encoding="utf-8") as f:
                self.object_dialogue = json.load(f)
        

        
        self.intro = SimpleChapterIntro(self.screen, self.gameStateManager,language=self.language,
                                        text_size=self.text_size,
                                        bgm_vol=self.bgm_vol,
                                        sfx_vol=self.sfx_vol)
        self.start = Start(self.screen, self.gameStateManager, self.intro,language = language,text_size = text_size,bgm_vol = bgm_vol,sfx_vol = sfx_vol)
        self.level = Rooms(self.screen,                 
                            self.gameStateManager,      
                            self.player,              
                            self.npc_manager,            
                            self,    
                            self,                   
                            self.screen,                  
                            self.current_dialogue_ref,  
                            language=self.language,
                            text_size=self.text_size,
                            bgm_vol=self.bgm_vol,
                            sfx_vol=self.sfx_vol
                            )
        
        
        #self.intro.completed_callback = lambda: self.gameStateManager.set_state('level')

        self.states = {'intro':self.intro, 'start':self.start, 'level':self.level}
    
        # nuva = NPC(840,520,"Nuva")
        # dean = NPC(400,520,"Dean")
        # self.npc_manager.add_npc(nuva)
        # self.npc_manager.add_npc(dean)

        camera_group.add(self.player)
        # camera_group.add(nuva)
        # camera_group.add(dean)

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

    # def advance_day(self):
    #     # Increments the current day and performs day-change actions
    #     self.rooms_instance.current_day += 1
    #     self.patient_zheng_talked_to = False
    #     print(f"--- Advancing to Day {self.rooms_instance.current_day} (Chapter {self.rooms_instance.current_day})---")
            
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
            #pygame.draw.rect(self.screen, (255, 0, 0), screen_pos, 2)  # red box = player

            if self.current_dialogue_ref.current_dialogue:
                # Update the current dialogue
                if isinstance(self.current_dialogue_ref.current_dialogue, Dialog):
                    self.current_dialogue_ref.current_dialogue.update()
                else:  # For ObjectDialogue
                    self.current_dialogue_ref.current_dialogue.update()

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
    def __init__(self, display, gameStateManager, player, npc_manager, game_instance, game_ref,screen, current_dialogue_ref, language="EN", text_size=None, bgm_vol=0.5, sfx_vol=0.5):
        
        self.space_released = True

        
        self.display = display
        self.gameStateManager = gameStateManager

        self.player = player
        self.npc_manager = npc_manager
 
        self.game_ref = game_instance

        self.screen = screen
        
        self.current_dialogue_ref = current_dialogue_ref

        self.language = language
        self.text_size = text_size
        self.bgm_vol = bgm_vol
        self.sfx_vol = sfx_vol
        
        #self.backmain_img = pygame.image.load("backmain.png").convert_alpha()
        #self.backmain_button = Button(image=self.backmain_img, pos=(1100, 80), scale=0.2)
        

        self.all_dialogues = game_ref.all_dialogues 


        self.shown_dialogues = {}    

        camera_group = CameraGroup(self.player, self.npc_manager, display)
        camera_group.add(self.player)
        
        self.current_dialogue_ref = game_ref

        self.cutscene_active = False

        self.cutscene_speed = 3

        self.dean_exiting = False
        self.patient_zheng_talked_to = False # Flag for machine unlock
        self.visited_doors = set()  #keep track of doors used

        self.current_room = "room01"
        self.current_day = 1 #Initialize the current day (Chapter 1)
        
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
        print(f"DEBUG: Rooms __init__ finished. camera_group ID: {id(camera_group)}")
        
        # self.npc_manager.npcs.clear()
        self.load_room(self.current_room)


    def advance_day(self):
        # Increments the current day and performs day-change actions
        self.current_day += 1
        self.patient_zheng_talked_to = False
    #     print(f"--- Advancing to Day {self.current_day} (Chapter {self.current_day})---")
        # Reset NPC position and quest flags? here 
        # self.load_room(self.current_room) # To reload the room to refresh objects/NPC

        #self.backmain_img = pygame.image.load("backmain.png").convert_alpha()

        #self.backmain_button = Button(image=self.backmain_img, pos=(1100, 80), scale=0.2)

    def load_room(self, room_name, facing="left"):
        print(f"\n--- Entering load_room for {room_name} ---")
        print(f"DEBUG: In load_room, camera_group ID: {id(camera_group)}") # Use self.camera_group
        print(f"DEBUG: Current Day: {self.current_day}") 

        camera_group.empty() # Use self.camera_group
        camera_group.background_layer_sprites.empty() # Use self.camera_group
        camera_group.foreground_layer_sprites.empty() # Use self.camera_group
        print("DEBUG: All camera groups emptied.")

        camera_group.add(self.player) # Use self.camera_group
        print(f"DEBUG: Player added to main camera_group. Current main group sprites: {[s.name if hasattr(s, 'name') else type(s).__name__ for s in camera_group.sprites()]}") # Use self.camera_group

        # Remove NPCs from both npc_manager and camera_group
        for npc in self.npc_manager.npcs:
            camera_group.remove(npc) # Use self.camera_group
        self.npc_manager.npcs.clear()
        print("DEBUG: NPC manager cleared.")

        # Remove interactable objects
        global interactable_objects 
        for obj in interactable_objects:
            camera_group.remove(obj) # Use self.camera_group
            camera_group.background_layer_sprites.remove(obj) # Use self.camera_group
            camera_group.foreground_layer_sprites.remove(obj) # Use self.camera_group
        interactable_objects.clear()
        print("DEBUG: Global interactable_objects list cleared and sprites removed from camera groups.")
    
        print(f"Loading room: {room_name}")
        # --- Load background and set player position using global room_settings ---
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

        camera_group.set_background(self.background) # Use self.camera_group

        self.current_room = room_name

        if facing == "left":
            self.player.flip = True
            self.player.direction = -1
        elif facing == "right":
            self.player.flip = False
            self.player.direction = 1

        # --- Load and add interactable objects for the current room ---
        for obj_id, obj_info in object_data.items(): # Access global object_data
            if room_name in obj_info.get("rooms", []):
                name = obj_info["name"]
                pos = obj_info["position"]
                image_key = obj_info.get("image")
                image_path_str = image_path.get(image_key, None)
                dialogue_id = obj_info["dialogue_id"]
                start_node = obj_info["start_node"]
                active = obj_info.get("active", True)
                text = obj_info.get("text")
                
                # Determine effective next_room based on current day
                effective_next_room = obj_info.get("next_room") 
                day_specific_next_room_map = obj_info.get("day_specific_next_room")
                if day_specific_next_room_map and str(self.current_day) in day_specific_next_room_map:
                    effective_next_room = day_specific_next_room_map[str(self.current_day)]
                    print(f"INFO: Object '{name}' using day-specific next_room for Day {self.current_day}: {effective_next_room}")
                
                # Determine effective 'unlocked' status based on current day
                is_unlocked_today = obj_info.get("unlocked", True) 
                unlocked_day_threshold = obj_info.get("unlocked_day")
                
                if unlocked_day_threshold is not None:
                    if self.current_day >= unlocked_day_threshold:
                        is_unlocked_today = True
                    else:
                        is_unlocked_today = False
                
                conditional_dialogue_flag = obj_info.get("conditional_dialogue_flag")
                node_if_locked = obj_info.get("node_if_locked")
                node_if_unlocked = obj_info.get("node_if_unlocked")
                day_specific_nodes = obj_info.get("day_specific_nodes")
                
                draw_layer = obj_info.get("draw_layer", "mid_layer")

                has_dialogue = obj_info.get("has_dialogue", True)

                required_flags = obj_info.get("required_flags") 

                if image_path_str:
                    obj = InteractableObject(name, pos, dialogue_id, start_node, 
                                             image_path=image_path_str, active=active, 
                                             text=text, 
                                             next_room=effective_next_room, 
                                             unlocked=is_unlocked_today, 
                                             conditional_dialogue_flag=conditional_dialogue_flag,
                                             node_if_locked=node_if_locked,
                                             node_if_unlocked=node_if_unlocked,
                                             day_specific_nodes=day_specific_nodes,
                                             draw_layer=draw_layer,
                                             has_dialogue=has_dialogue,
                                             required_flags=None) 
                    interactable_objects.append(obj)
                    
                    if draw_layer == "background":
                        camera_group.background_layer_sprites.add(obj) # Use self.camera_group
                    elif draw_layer == "foreground":
                        camera_group.foreground_layer_sprites.add(obj) # Use self.camera_group
                    else: 
                        camera_group.add(obj) # Use self.camera_group
                    print(f"SUCCESS: Loaded object: {name} for room: {room_name}")
                else:
                    print(f"Warning: No image path found for object '{name}' (image_key: {image_key}). Not adding to game.")
        
        print(f"Total interactable objects loaded for {room_name}: {len(interactable_objects)}")
        
        # --- Load and add NPCs for the current room using global npc_data ---
        for npc_id, npc_info in npc_data.items(): 
            name = npc_info["name"]
            dialogue_id = npc_info["dialogue_id"]

            # Step 1: Check if NPC is scheduled to appear on this day AT ALL
            npc_days = npc_info.get("days")
            if npc_days is not None and self.current_day not in npc_days:
                print(f"INFO: NPC {name} (dialogue_id: {dialogue_id}) will NOT appear on Day {self.current_day} (not in days list).")
                continue # Skip to next NPC if not scheduled for this day

            # Step 2: Determine NPC's specific location for THIS day
            current_day_str = str(self.current_day)
            day_specific_locations = npc_info.get("day_specific_locations")
            
            npc_appears_in_current_room_today = False
            effective_position = None

            if day_specific_locations and current_day_str in day_specific_locations:
                # If there's a day-specific location for today, use it
                location_data = day_specific_locations[current_day_str]
                target_room_for_today = location_data.get("room")
                effective_position = location_data.get("position")
                print(f"DEBUG ROOM COMPARE: current_room_name='{room_name}', target_room_for_today='{target_room_for_today}'")
                print(f"DEBUG ROOM COMPARE: types: current_room_name={type(room_name)}, target_room_for_today={type(target_room_for_today)}")
                
                if room_name == target_room_for_today:
                    npc_appears_in_current_room_today = True
                    print(f"DEBUG: {name} has day-specific location for Day {self.current_day}: Room={target_room_for_today}, Pos={effective_position}")
                else:
                    print(f"INFO: NPC {name} (dialogue_id: {dialogue_id}) will NOT appear in {room_name} on Day {self.current_day} (day-specific room mismatch).")
            else:
                # Fallback: use general 'rooms' list and 'position' if no day-specific location
                general_rooms = npc_info.get("rooms", [])
                if room_name in general_rooms:
                    npc_appears_in_current_room_today = True
                    effective_position = npc_info.get("position")
                    print(f"DEBUG: {name} using general location for Day {self.current_day}: Room={general_rooms}, Pos={effective_position}")
                else:
                    print(f"INFO: NPC {name} (dialogue_id: {dialogue_id}) will NOT appear in {room_name} (not in general room list).")

            # Step 3: Add NPC if determined to be in this room today
            if npc_appears_in_current_room_today and effective_position:
                npc = NPC(effective_position[0], effective_position[1], name, dialogue_id=dialogue_id) 
                self.npc_manager.add_npc(npc)
                camera_group.add(npc) 
                print(f"SUCCESS: Added NPC: {name} ({dialogue_id}) to room {room_name} at {effective_position} for Day {self.current_day}.")
            elif npc_appears_in_current_room_today and not effective_position:
                 print(f"ERROR: NPC {name} ({dialogue_id}) is supposed to be in {room_name} on Day {self.current_day}, but no valid position was found. Not adding.")

        room_width, room_height = self.background.get_size()
        camera_group.set_limits(room_width, room_height) 
        print(f"DEBUG: After all additions in load_room:")
        print(f"DEBUG:   Main camera_group sprites: {[s.name if hasattr(s, 'name') else type(s).__name__ for s in camera_group.sprites()]}") 
        print(f"DEBUG:   Background layer sprites: {[s.name if hasattr(s, 'name') else type(s).__name__ for s in camera_group.background_layer_sprites.sprites()]}") 
        print(f"DEBUG:   Foreground layer sprites: {[s.name if hasattr(s, 'name') else type(s).__name__ for s in camera_group.foreground_layer_sprites.sprites()]}") 
        print(f"--- Exiting load_room for {room_name} ---")

    # --- METHOD TO HANDLE DIALOGUE EVENTS ---
    def handle_dialogue_event(self, event_name, event_data=None):
        global flags
        event_data = event_data if event_data is not None else {}
        
        # Processes events triggered at the end of a dialogue node.
        if event_name == "patient_zheng_talked_to":
            if 'flags' not in globals():
                print("ERROR: Global 'flags' dictionary not found! Initializing an empty one.")
                globals()['flags'] = {} 

            flags["patient_zheng_talked_to"] = True
            print("Patient Zheng's dialogue completed. GLOBAL flag 'patient_zheng_talked_to' set to True!")
        
        elif event_name == "machine_enter" or event_name == "open_door_event": 
            target_room = event_data.get("target_room")
            if target_room:
                self.fading = True
                self.fade_alpha = 0 
                self.next_room_after_transition = target_room 
                print(f"Room transition triggered to: {self.next_room_after_transition} by '{event_name}'.")
            else:
                print(f"Warning: '{event_name}' triggered without 'target_room'. Cannot transition.")
        
        elif event_name == "puzzle_complete":
            print("Event: Puzzle completed. Triggering 'after_puzzle' narrative.")
            
            target_npc_dialogue_id = event_data.get("puzzle_owner_dialogue_id", "Zheng") 
            print(f"DEBUG (Rooms.handle_dialogue_event): Target NPC for after_puzzle: {target_npc_dialogue_id}")

            class DynamicNarrativeDummy:
                def __init__(self, name="narrator", dialogue_id="System_Narrative"):
                    self.name = name
                    self.dialogue_id = dialogue_id
                    self.rect = pygame.Rect(0,0,1,1)

            dummy_obj = DynamicNarrativeDummy()
            dialogue_tree_to_load = None

            if target_npc_dialogue_id in self.game_ref.all_dialogues:
                dummy_obj.name = target_npc_dialogue_id 
                dummy_obj.dialogue_id = target_npc_dialogue_id 
                dialogue_tree_to_load = self.game_ref.all_dialogues.get(target_npc_dialogue_id)
            else:
                print(f"Warning: Target NPC dialogue ID '{target_npc_dialogue_id}' not found in all_dialogues. Falling back to 'System_Narrative'.")
                dummy_obj.name = "narrator"
                dummy_obj.dialogue_id = "System_Narrative"
                dialogue_tree_to_load = all_dialogues.get("System_Narrative")

            if dialogue_tree_to_load:
                self.current_dialogue_ref.current_dialogue = Dialog(
                    dummy_obj, 
                    self.player,
                    dialogue_tree_to_load, 
                    start_node_id="after_puzzle_sequence", 
                    rooms_instance=self,
                    screen_surface=pygame.display.get_surface(),
                    language=self.language,
                    text_size=self.text_size,
                    bgm_vol=self.bgm_vol,
                    sfx_vol=self.sfx_vol
                )
                self.current_dialogue_ref.current_dialogue.talking = True 
                print(f"DEBUG: Initiated '{target_npc_dialogue_id}' 'after_puzzle_sequence' dialogue.")
            else:
                print(f"Error: Dialogue data for '{target_npc_dialogue_id}' (or System_Narrative) not found for puzzle_complete event.")

        elif event_name == "day_end_and_intro_next_day":
            print("Event: Day end sequence triggered. Advancing day and starting next intro.")
            if not self.fading:
                self.fading = True
                self.fade_alpha = 0

            self.advance_day()
            self.next_room_after_transition = "room01"
            self.start_intro_after_fade = True 
            print(f"Set to fade to {self.next_room_after_transition} and start intro for Day {self.current_day}.")

            class NarratorDummy: 
                def __init__(self, name="narrator", dialogue_id="System_Narrative"):
                    self.name = name
                    self.dialogue_id = dialogue_id
                    self.rect = pygame.Rect(0,0,1,1)

            narrator_dummy_obj = NarratorDummy()
            system_narrative_tree = self.all_dialogues.get(narrator_dummy_obj.dialogue_id)
            if system_narrative_tree:
                self.current_dialogue_ref.current_dialogue = Dialog(
                    narrator_dummy_obj,
                    self.player,
                    system_narrative_tree,
                    start_node_id="intro", 
                    rooms_instance=self,
                    screen_surface=pygame.display.get_surface(),
                    language=self.language,
                    text_size=self.text_size,
                    bgm_vol=self.bgm_vol,
                    sfx_vol=self.sfx_vol

                )
                self.current_dialogue_ref.current_dialogue.talking = True 
            else:
                print("Error: 'System_Narrative' dialogue data not found for intro after fade.")
            
        elif event_name == "set_flag": # Handle the "set_flag" event
            flag_name = event_data.get("flag_name")
            flag_value = event_data.get("flag_value", True) # Default to True if not specified
            if flag_name:
                if 'flags' not in globals():
                    print("ERROR: Global 'flags' dictionary not found! Initializing an empty one.")
                    globals()['flags'] = {}
                flags[flag_name] = flag_value
                print(f"Event: Flag '{flag_name}' set to {flag_value}.")
            else:
                print("Warning: 'set_flag' event triggered without 'flag_name' in event_data.")
            

    def run(self, moving_left, moving_right,events):
        entry = {}
        keys = pygame.key.get_pressed()

        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

           # if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
           #     if self.backmain_button.checkForInput(mouse_pos):
           #         print("Back to main menu clicked!")
           #         click_sound.play()
           #         pygame.mixer.music.stop()
                    #self.gameStateManager.set_state('start')
           #         return False  # This will exit the level loop

        if not keys[pygame.K_SPACE]:
            self.space_released = True
        if not keys[pygame.K_q]:
            self.q_interact_released = True  #Release Q key debounce
            self.q_advance_released = True
        if not keys[pygame.K_e]:
            self.e_released = True # For selecting choices in NPC dialogue
        if not keys[pygame.K_w]: # For navigating choices
            self.w_released = True
        if not keys[pygame.K_s]: # For navigating choices
            self.s_released = True

        # --- Movement ---
        if not self.current_dialogue_ref.current_dialogue or not self.current_dialogue_ref.current_dialogue.talking:
            is_moving = self.player.move(moving_left,moving_right)
        else:
            is_moving = False
        self.player.update_animation(is_moving)
          
        # --- Dialogue logic ---
        nearest_npc = self.npc_manager.get_nearest_npc(self.player)
        near_obj = check_object_interaction(self.player.rect.inflate(10,10), interactable_objects)
        
        # Cache the current dialogue instance for cleaner logic within this frame
        dialogue_instance_at_frame_start = self.current_dialogue_ref.current_dialogue

        # 1. Handle Object Interaction (Q key)
        if keys[pygame.K_q] and self.q_interact_released and not self.fading:
            self.q_interact_released = False # Debounce the 'Q' key
            if near_obj:
                obj_to_interact = near_obj[0] # Interact with the first detected object

                # --- Handle objects WITHOUT dialogue but with a next_room ---
                if not obj_to_interact.has_dialogue and obj_to_interact.next_room:
                    print(f"INFO: Object '{obj_to_interact.name}' has no dialogue but has a next_room. Triggering direct room transition.")
                    # Trigger the room transition directly, similar to how ObjectDialogue would
                    self.handle_dialogue_event("open_door_event", {"target_room": obj_to_interact.next_room})
                    return # Important: Consume the interaction and return

                # Check if the object has dialogue before creating ObjectDialogue ---
                if obj_to_interact.has_dialogue:
                    if self.current_dialogue_ref.current_dialogue is None or not self.current_dialogue_ref.current_dialogue.talking:
                        # --- Let ObjectDialogue determine its start node ---
                        temp_obj_dialogue = ObjectDialogue(
                            obj_to_interact, 
                            self.current_dialogue_ref, 
                            self, 
                            self.game_ref.object_dialogue,
                            text_size=self.text_size,
                            language=self.language,
                            start_node_id="dummy" # Pass a dummy for now, it will be overridden
                        )
                        chosen_start_node = temp_obj_dialogue.get_start_node_for_interaction()
                        
                        # Now create the actual ObjectDialogue with the determined start_node
                        self.current_dialogue_ref.current_dialogue = ObjectDialogue(
                            obj_to_interact, 
                            self.current_dialogue_ref, 
                            self, 
                            self.game_ref.object_dialogue,
                            text_size=self.text_size,
                            language=self.language,
                            start_node_id=chosen_start_node 
                        )
                        print(f"Interacting with {obj_to_interact.name}. Dialogue started from node: {chosen_start_node}")
                    else:
                        print(f"INFO: Object interaction (Q) ignored: Not near an object with dialogue/transition.")

            # Handle NPC Interaction (Space Key to START new NPC dialogue)
            # Handle NPC Interaction (SPACE key for both STARTING and ADVANCING)
        # This block now handles both starting a new NPC dialogue AND advancing an existing one.
        if keys[pygame.K_SPACE] and self.space_released: # Check space_released for initial press
            self.space_released = False # Debounce 'SPACE' for initial interaction/first advance
            
            # If an NPC Dialogue is already active, advance it (or handle choices).
            if isinstance(dialogue_instance_at_frame_start, Dialog) and dialogue_instance_at_frame_start.talking:
                if dialogue_instance_at_frame_start.choices_active:
                    # Choice navigation (W/S) and selection (E) are handled in separate elifs
                    # but should typically be outside this main SPACE handler or in a nested if.
                    # Given the request, we assume SPACE is only for *advancing* text,
                    # and W/S/E are still for choices.
                    # So, if choices are active, SPACE does nothing here, W/S/E handle it.
                    pass # SPACE does nothing if choices are active
                else: # NPC Dialogue (not choices) advances with SPACE
                    dialogue_instance_at_frame_start.handle_space(self.display, keys) # Call handle_space
            # Else, if no dialogue is active, try to start a new NPC dialogue.
            elif not dialogue_instance_at_frame_start or not dialogue_instance_at_frame_start.talking:
                if nearest_npc:
                    global all_dialogues # Ensure all_dialogues is accessible
                    npc_dialogue_tree = self.all_dialogues.get(nearest_npc.dialogue_id)

                    if npc_dialogue_tree: # Check if the NPC's dialogue content exists
                        # --- FIX: Refined NPC Dialogue Start Node Selection Logic ---
                        chosen_story_id = None
                        
                        # 1. Prioritize day-specific nodes if the NPC has them defined (from npc_data.json)
                        # This covers the "Dean" example with `day_specific_nodes`
                        if hasattr(nearest_npc, 'day_specific_nodes') and nearest_npc.day_specific_nodes:
                            # Note: npc_data.json has "day_specific_locations", not "day_specific_nodes" for NPCs generally.
                            # Re-checking your JSON, 'day_specific_locations' defines where an NPC IS, not what dialogue they SAY.
                            # So, we should *not* use day_specific_nodes from NPC here unless you intend to add that.
                            # For now, let's assume chapter_X is the main way to branch NPC dialogue by day.
                            pass # Removing this block to simplify based on current JSON.

                        # 2. Check for chapter-specific nodes (e.g., "chapter_1", "chapter_2") directly in the NPC's dialogue content.
                        # This covers the "Nuva" and "Dean" structure shown in all_dialogues.json.
                        chapter_key = f"chapter_{self.current_day}"
                        if chapter_key in npc_dialogue_tree:
                            chosen_story_id = chapter_key
                            print(f"DEBUG: NPC {nearest_npc.name} using chapter_key: {chosen_story_id} for Day {self.current_day}.")
                            
                        # 3. Fallback to "repeat_only" if it exists and no specific chapter dialogue for today
                        if chosen_story_id is None: 
                            if "repeat_only" in npc_dialogue_tree:
                                chosen_story_id = "repeat_only"
                                print(f"DEBUG: NPC {nearest_npc.name} falling back to 'repeat_only'.")

                        # 4. Final fallback to a generic "start" node
                        if chosen_story_id is None:
                            if "start" in npc_dialogue_tree:
                                chosen_story_id = "start"
                                print(f"DEBUG: NPC {nearest_npc.name} falling back to generic 'start' node.")
                            else:
                                print(f"Warning: NPC {nearest_npc.name} has no 'start', 'chapter_{self.current_day}', or 'repeat_only' node defined in dialogue JSON. Dialogue might be empty.")
                                chosen_story_id = "start" # Provide a default even if it's empty in JSON, to avoid crashes.

                        self.current_dialogue_ref.current_dialogue = Dialog(
                            nearest_npc,
                            self.player,
                            npc_dialogue_tree,
                            start_node_id=chosen_story_id,
                            rooms_instance=self,
                            screen_surface=self.display, # Pass the screen surface
                            language=self.language,
                            text_size=self.text_size,
                            bgm_vol=self.bgm_vol,
                            sfx_vol=self.sfx_vol
                        )
                        self.current_dialogue_ref.current_dialogue.talking = True
                        print(f"DEBUG: Started dialogue with NPC: {nearest_npc.name} from node: {chosen_story_id}")
                    else:
                        print(f"Warning: No dialogue tree found for NPC: {nearest_npc.name} (dialogue_id: {nearest_npc.dialogue_id})")
                else:
                    print(f"INFO: NPC interaction (SPACE) ignored: Not near an NPC.")

        # --- Dialogue State Update and Input Handling (Unified) ---
        # This is the dialogue instance that will be updated and have its input handled.
        dialogue_instance_at_frame_start = self.current_dialogue_ref.current_dialogue
        
        # PHASE 2: Handle Dialogue Advancement (ONLY if dialogue is already active)
        if dialogue_instance_at_frame_start and dialogue_instance_at_frame_start.talking:
            # Advance ObjectDialogue with Q
            if isinstance(dialogue_instance_at_frame_start, ObjectDialogue):
                if keys[pygame.K_q] and self.q_advance_released: # Use q_released for advancement
                    self.q_advance_released = False # Re-use the same debounce for advance
                    dialogue_instance_at_frame_start.handle_q() # Call handle_q (Q is used for ObjectDialogue) 

            # 2. Handle input for this dialogue (which might trigger events)
            # IMPORTANT: These calls (handle_space/select_choice) might change
            # self.current_dialogue_ref.current_dialogue if an event triggers a new dialogue.
            elif isinstance(dialogue_instance_at_frame_start, Dialog) and dialogue_instance_at_frame_start.choices_active:
                if keys[pygame.K_w] and self.w_released: 
                    self.w_released = False
                    dialogue_instance_at_frame_start.selected_choice_index = max(0, dialogue_instance_at_frame_start.selected_choice_index - 1)
                elif keys[pygame.K_s] and self.s_released: 
                    self.s_released = False
                    dialogue_instance_at_frame_start.selected_choice_index = min(len(dialogue_instance_at_frame_start.current_choices) - 1, dialogue_instance_at_frame_start.selected_choice_index + 1)
                elif keys[pygame.K_e] and self.e_released: 
                    self.e_released = False
                    dialogue_instance_at_frame_start.select_choice(dialogue_instance_at_frame_start.selected_choice_index,screen)
            else: # Handle SPACE key for advancing regular dialogue (when choices are NOT active)
               if keys[pygame.K_SPACE] and self.space_released:
                    self.space_released = False
                    dialogue_instance_at_frame_start.handle_space(self.display, keys) # Call handle_space (SPACE is used for NPC dialogue)
        
            # --- Dialogue Reference Management ---
            # if not dialogue_instance_at_frame_start.talking:
            #     if self.current_dialogue_ref.current_dialogue is dialogue_instance_at_frame_start:
            #         self.current_dialogue_ref.current_dialogue = None 
            if dialogue_instance_at_frame_start and not dialogue_instance_at_frame_start.talking:
                if self.current_dialogue_ref.current_dialogue is dialogue_instance_at_frame_start:
                    self.current_dialogue_ref.current_dialogue = None
                    print("Rooms: Current dialogue reference cleared (original dialogue finished and no new one set).")
                else:
                    # This case means a new dialogue was started by an event, so we don't clear it.
                    print("Rooms: Current dialogue reference NOT cleared because a new dialogue was initiated by an event.")
                
            # --- Drawing and Update Loop (Unified) ---
            # Update and draw current dialogue if active
            if self.current_dialogue_ref.current_dialogue and self.current_dialogue_ref.current_dialogue.talking:
                self.current_dialogue_ref.current_dialogue.update() # Only one update call here
                self.current_dialogue_ref.current_dialogue.draw(self.display)
                # print("DEBUG (Rooms.run): Drawing active dialogue:", type(self.current_dialogue_ref.current_dialogue).__name__)
            else:
                print("DEBUG (Rooms.run): No active dialogue to draw this frame (it might have just ended or been replaced by None).")

        camera_group.custom_draw(self.player)

       # self.backmain_button.draw(self.display)
        
        # --- Display "Press Q to interact" text ---
        if near_obj:
            font = pygame.font.Font(None, 24)
            text_surf = font.render("Press Q to interact", True, (0, 0, 0), (255, 255, 255))
            for obj in near_obj:
                # Calculate screen position based on camera offset
                screen_pos = obj.rect.topleft - camera_group.offset # Use camera_group.offset
                self.display.blit(text_surf, (screen_pos.x + text_surf.get_width() // 2, screen_pos.y - 20))
        
        # --- Draw dialogue if active ---
        if self.current_dialogue_ref.current_dialogue:

            if isinstance(self.current_dialogue_ref.current_dialogue, Dialog):
                self.current_dialogue_ref.current_dialogue.update()
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
                        self.current_dialogue_ref.current_dialogue = Dialog(
                            narrator_dummy_obj,
                            self.player,
                            self.all_dialogues.get(narrator_dummy_obj.dialogue_id),
                            start_node_id="intro", # This will now select chapter_X based on current_day
                            rooms_instance=self,
                            language=self.language,
                            text_size=self.text_size,
                            bgm_vol=self.bgm_vol,
                            sfx_vol=self.sfx_vol
                        )
                        self.current_dialogue_ref.current_dialogue.talking = True # Ensure it begins talking
                    else:
                        print("Error: 'System_Narrative' dialogue data not found for intro after fade.")
                
                self.fading = False
                self.fade_alpha = 0

        # --- Draw dialogue if active ---
        if self.current_dialogue_ref.current_dialogue:
            self.current_dialogue_ref.current_dialogue.draw(self.display)

        # --- Trigger cutscene --- 
        if self.current_dialogue_ref.current_dialogue and self.current_dialogue_ref.current_dialogue.talking:
            
            if isinstance(self.current_dialogue_ref.current_dialogue, Dialog):
                current_npc_name = self.current_dialogue_ref.current_dialogue.npc.name

                if current_npc_name == "Dean":
                    if not self.cutscene_active:
                        self.cutscene_active = True
                else:
                    self.cutscene_active = False
    
        if self.cutscene_active:
            # Check if current dialogue has triggered the cutscene event
            if isinstance(self.current_dialogue_ref.current_dialogue, Dialog):
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
        self.currentState  = state

if __name__ == '__main__':
    game = Game()

    def start_chapter_1():
        print("intro done, enter game")

    game.intro.completed_callback = start_chapter_1
    game.intro.start("chapter_1")
    game.run()
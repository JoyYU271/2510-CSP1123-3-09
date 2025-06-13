import pygame
import sys
from pygame.locals import *
import json
import character_movement
import shared
from shared import CameraGroup

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
shown_dialogues = {}
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

class dialog:
    def __init__(self, npc, player, full_dialogue_tree, start_node_id, rooms_instance):
        self.player = player
        self.npc_name = npc.name
        self.npc = npc
        self.full_dialogue_tree = full_dialogue_tree # e.g., the entire {"Nuva": {...}} or {"System_Narrative": {...}}
        self.rooms_instance = rooms_instance # Reference to Rooms for event triggering

        self.current_node_id = start_node_id # e.g., "chapter_1", "not_a_doctor", "after_puzzle_sequence", "intro"
        self.current_dialogue_list = self._get_dialogue_list_from_node_id(self.current_node_id)

        self.current_line_index = 0
        #self.current_line_data = {}
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

    def update(self): 
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

    def handle_space(self,keys):
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
                
                # --- CRITICAL FIX START (same as ObjectDialogue) ---
                self.rooms_instance.handle_dialogue_event(event_name) # Assuming event doesn't need extra data
                self.talking = False 
                print("NPC Dialogue: Event handled, this dialogue instance is stopping.")
                # --- CRITICAL FIX END ---
                return

            # If it's a regular text line, reset for typing
            self.reset_typing()

        else: # End of current dialogue list
            # If we reached the end and didn't jump to 'next' or trigger an 'event'
            self.talking = False
            print("NPC Dialogue ended (natural end of node).")

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
            print("DEBUG (dialog.draw): Not talking, returning early.")
            return

        #let the dialog box on the center and put below
        dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
        dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20
        screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

        #calculate text width with limit for wrapping
        text_max_width = self.dialog_box_img.get_width() - 300 #pixel padding each side
        
        print(f"DEBUG (dialog.draw): Drawing at dialog_x={dialog_x}, dialog_y={dialog_y}. Screen size: {screen.get_size()}")

        current_line_data = self.get_current_line_data()
        print(f"DEBUG (dialog.draw): current_line_data: {current_line_data}")

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
            print(f"DEBUG (dialog.draw): Dialog box blitted. Position: ({dialog_x}, {dialog_y})")

            # --- Draw speaker name ---
            # You had dialog_x + 200 for speaker name
            draw_text(screen, name_to_display, 40, (0, 0, 0), dialog_x + 200, dialog_y + 10, center=False) # Black text
            print(f"DEBUG (dialog.draw): Speaker name '{name_to_display}' blitted.")

            if self.choices_active:
                print(f"DEBUG (dialog.draw): Choices are active. Selected index: {self.selected_choice_index}")
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
                print(f"DEBUG (dialog.draw): Drawing normal text: '{text_to_display}', Typing complete: {self.typing_complete}")

                # Draw dialogue text, centered in the dialogue box (from your old code)
                draw_text(screen, text_to_display, 30, (0, 0, 0), 
                          dialog_x + self.dialog_box_img.get_width() // 2, 
                          dialog_y + self.dialog_box_img.get_height() // 2 - 15, 
                          center=True, max_width=text_max_width)
        else:
            print("DEBUG (dialog.draw): current_line_data is None. Skipping text/choice drawing.")

                
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
    def __init__(self,x,y,name,image_path = None, dialogue_id=""):
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
        self.dialogue_id = dialogue_id
        self.world_pos = pygame.Vector2(x,y) #for world coordinate
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.name = name

# to manage multiples NPCs
class NPCManager:
    def __init__(self):
        self.npcs = []

    def clear(self):
        self.npcs.clear()

    def add_npc(self,npc):
        self.npcs.append(npc)

    def update(self):
        for npc in self.npcs:
            npc.update()
            
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

class ObjectDialogue: 
    def __init__(self, obj_info, current_dialogue_ref, rooms_instance, start_node_id="start"):
        self.obj_info = obj_info
        self.current_dialogue_ref = current_dialogue_ref
        self.rooms_instance = rooms_instance
        self.dialogue_id = obj_info.dialogue_id

        self.dialogue_data = object_dialogue.get(self.dialogue_id, {})
        
        self.current_node_id = start_node_id
        self.current_node = self.dialogue_data.get(self.current_node_id, [])
        
        # --- ADDED: Initialization for typing animation variables ---
        self.current_text_index = 0 # Index for the current line within a node's text list
        self.current_line_data = {}

        self.talking = True # Dialogue starts talking immediately
        self.current_text_display = "" # The text currently displayed characters by characters
        self.typing_speed = 3 # Characters per frame, adjust as needed
        self.text_display_timer = 0
        self.typing_complete = False # Flag indicating if the current line has finished typing

        self.dialogue_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()
        self.dialogue_box_img.set_alpha(200)

        self.reset_typing()

    def _get_current_line_data(self):
        # Helper to get the dictionary for the current line in the current_dialogue_list.
        if self.current_text_index < len(self.current_node):
            return self.current_node[self.current_text_index]
        return None

    def reset_typing(self):
        # This method is crucial to set up the typing animation for a new line/node
        self.text_display_timer = 0
        self.typing_complete = False
        self.current_text_display = ""
        
        # Get the data for the current line's dictionary
        self.current_line_data = self._get_current_line_data()

        if self.current_line_data:
            # If the current line has text, prepare for typing. Otherwise, it's an event/choice, so skip typing.
            text_content = self.current_line_data.get("text", "")
            if not text_content: 
                self.typing_complete = True # Mark as complete instantly if no text
                self.current_text_display = ""
        else: 
            # This means the current_line_index is out of bounds for current_dialogue_list
            self.typing_complete = True # Signal completion
            self.current_text_display = ""
            # The handle_space method will then detect the end of the node list and transition/end dialogue.

    def update(self):
        if not self.talking or self.rooms_instance.fading: # Don't update if not talking or fading
            return
        
        if self.current_line_data is None: # No valid line data to display
            self.typing_complete = True
            self.current_text_display = ""
            return

        text_to_type = self.current_line_data.get("text", "")
            
        if not self.typing_complete:
            self.text_display_timer += 1
            chars_to_display = self.text_display_timer // self.typing_speed
            # Ensure we don't try to display more characters than available
            if chars_to_display > len(text_to_type):
                chars_to_display = len(text_to_type)
            
            self.current_text_display = text_to_type[:chars_to_display]
            
            if chars_to_display >= len(text_to_type):
                self.typing_complete = True
    
    def _transition_to_node(self, node_id):
        #Transitions dialogue to a new specified node ID within object_dialogue.
        new_current_node = self.dialogue_data.get(node_id, [])
        
        if new_current_node:
            self.current_node_id = node_id
            self.current_node = new_current_node
            self.current_text_index = 0
            self.reset_typing() # Reset typing for the new node's first line
            print(f"ObjectDialogue: Transitioned to new dialogue node: {self.current_node_id}")
        else:
            print(f"Warning: ObjectDialogue: Next node '{node_id}' not found or invalid format. Ending dialogue.")
            self.talking = False
            self.rooms_instance.current_dialogue_ref.current_dialogue = None # Clear reference

    def handle_space(self):
        #Handles spacebar input to advance dialogue or complete typing.
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
                event_data = {}
                # If the object has a 'next_room' property, pass it with the event
                if hasattr(self.obj_info, 'next_room') and self.obj_info.next_room:
                    event_data["target_room"] = self.obj_info.next_room
                
                print(f"ObjectDialogue: Triggering event: {event_name} with data: {event_data}")
                # --- CRITICAL FIX START ---
                # This dialogue object simply tells Rooms to handle the event.
                # Rooms will then decide if a new dialogue is set.
                self.rooms_instance.handle_dialogue_event(event_name, event_data)
                # After the event, check if the global dialogue reference has changed.
                # If it has changed (meaning the event started a new dialogue),
                # this old dialogue should stop talking but NOT clear the new reference.
                self.talking = False # Simply stop this dialogue
                print("ObjectDialogue: Event created a new dialogue. This ObjectDialogue is stopping without clearing the new reference.")
                return

            # If it's a regular text line (and no next/event), reset for typing the new line
            self.reset_typing()

        else: # End of current dialogue list for this node
            self.talking = False # End dialogue
            print("ObjectDialogue ended (natural end of node).")

    def draw(self, screen):
        if not self.talking: return

        dialog_x = screen.get_width() // 2 - self.dialogue_box_img.get_width() // 2
        dialog_y = screen.get_height() - self.dialogue_box_img.get_height() - 20
        screen.blit(self.dialogue_box_img, (dialog_x, dialog_y))

        # Padding inside the dialogue box
        text_x = dialog_x + 150
        text_y = dialog_y + 60
        max_text_width = self.dialogue_box_img.get_width() - 200  # 40 padding on each side

        # Get speaker and text from current_line_data (which is the current line's dictionary)
        # speaker = self.current_line_data.get("speaker", "narrator")
        text_to_display = self.current_text_display

        # speaker_color = (200, 200, 255) # Light blue for speaker
        text_color = (0, 0, 0)    # White for main dialogue text

        # speaker_x = dialog_x + 50
        # speaker_y = dialog_y + 20 

        text_x = dialog_x + self.dialogue_box_img.get_width() // 2
        text_y = dialog_y + self.dialogue_box_img.get_height() // 2 - 15

        # draw_text(screen, self.current_text_display, size=30, color=(0, 0, 0), x=text_x, y=text_y, center=False, max_width=max_text_width)
        # Draw dialogue text
        draw_text(screen, text_to_display, size=30, color=text_color, 
                    x=text_x, y=text_y, center=True, max_width=max_text_width)

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
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.screen = screen
        self.player = player
        self.npc_manager = NPCManager()
        self.current_dialogue = None
        self.visited_doors = set()
        self._pending_room = None
        self._fading = False
        self._fade_alpha = 0

        self.gameStateManager = GameStateManager('start')
        self.gameStateManager.game_instance = self
        self.intro = SimpleChapterIntro(self.screen, self.gameStateManager)
        self.start = Start(self.screen, self.gameStateManager, self.intro)
        self.level = Rooms(self.screen, self.gameStateManager, self.player, self.npc_manager, self)
        
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

            currentState = self.gameStateManager.get_state()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
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
                self.states['level'].run(moving_left, moving_right)
            else:
                self.states[currentState].run()

            # for obj in interactable_objects:
            #     obj.draw(self.screen, camera_group.offset)

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


class Rooms:    # class Level in tutorial
    def __init__(self, display, gameStateManager, player, npc_manager, game_ref):   # Added game_ref for current_dialogue_ref
        self.display = display
        self.gameStateManager = gameStateManager

        self.player = player
        self.npc_manager = npc_manager

        camera_group = CameraGroup(self.player, self.npc_manager, display)
        camera_group.add(self.player)
        self.current_dialogue_ref = game_ref

        self.space_released = True
        self.q_released = True
        self.enter_released = True  # New: for choice selection confitmation
        
        self.cutscene_active = False
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
        
        room_width, room_height = self.background.get_size()
        camera_group.set_limits(room_width, room_height)
        
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
            class ZhengNarrativeDummy:
                def __init__(self, name="Zheng", dialogue_id="Zheng"):
                    self.name = name
                    self.dialogue_id = dialogue_id
                    self.rect = pygame.Rect(0,0,1,1) # Dummy rect for consistency if 'dialog' needs it

            zheng_narrative_obj = ZhengNarrativeDummy()

            # # --- DEBUG PRINTS ---
            print(f"DEBUG (Rooms.handle_dialogue_event): Global all_dialogues keys: {list(all_dialogues.keys())}")
            zheng_narrative_tree = all_dialogues.get(zheng_narrative_obj.dialogue_id)
            print(f"DEBUG (Rooms.handle_dialogue_event): Fetched system_narrative_tree type: {type(zheng_narrative_tree)}")
            if isinstance(zheng_narrative_tree, dict):
                print(f"DEBUG (Rooms.handle_dialogue_event): Keys in zheng_narrative_tree: {list(zheng_narrative_tree.keys())}")
                if "after_puzzle_sequence" in zheng_narrative_tree:
                    seq_data = zheng_narrative_tree["after_puzzle_sequence"]
                    print(f"DEBUG (Rooms.handle_dialogue_event): 'after_puzzle_sequence' found. Type: {type(seq_data)}, Length: {len(seq_data) if isinstance(seq_data, list) else 'N/A'}")
                    print(f"DEBUG (Rooms.handle_dialogue_event): First few items: {seq_data[:2] if isinstance(seq_data, list) else 'Not a list'}")
                else:
                    print(f"ERROR (Rooms.handle_dialogue_event): 'after_puzzle_sequence' NOT found in System_Narrative data.")
            else:
                print(f"ERROR (Rooms.handle_dialogue_event): zheng_narrative_tree is not a dictionary. Value: {zheng_narrative_tree}")
            # --- END DEBUG PRINTS ---

            if zheng_narrative_tree:
                self.current_dialogue_ref.current_dialogue = dialog(
                    zheng_narrative_obj, # Pass the dummy object
                    self.player,
                    all_dialogues.get(zheng_narrative_obj.dialogue_id), # Pass the whole System_Narrative tree
                    start_node_id="after_puzzle_sequence", # Start the specific sequence
                    rooms_instance=self
                )
                self.current_dialogue_ref.current_dialogue.talking = True # Ensure it begins talking
            else:
                print(f"Error: 'Zheng_Narrative' dialogue data not found for event '{event_name}'.")

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

    def run(self, moving_left, moving_right):
        entry = {}
        keys = pygame.key.get_pressed()

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

        # --- Dialogue State Update and Input Handling (Unified) ---
        if self.current_dialogue_ref.current_dialogue:
            dialogue = self.current_dialogue_ref.current_dialogue

            dialogue.update()
            
            # Handle input specific to dialogue choices
            if isinstance(dialogue, dialog) and dialogue.choices_active:
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
                if keys[pygame.K_SPACE] and self.space_released:
                    self.space_released = False
                    if isinstance(dialogue, ObjectDialogue):
                        dialogue.handle_space()
                    elif isinstance(dialogue, dialog):
                        dialogue.handle_space(keys)

            # Check if dialogue has just finished (important for clearing reference)
            if not dialogue.talking:
                self.current_dialogue_ref.current_dialogue = None 
                print("Rooms: Current dialogue reference cleared.")

            # --- DRAW THE ACTIVE DIALOGUE ---
            # This should be the only place where the dialogue's draw method is called.
            if self.current_dialogue_ref.current_dialogue: # Check again if dialogue is still active after handling input/events
                dialogue.draw(self.display)
            else:
                print("DEBUG (Rooms.run): Dialogue just ended, will not draw this frame.")

        camera_group.custom_draw(self.player)
        
        # --- Display "Press Q to interact" text ---
        if near_obj:
            font = pygame.font.Font(None, 24)
            text_surf = font.render("Press Q to interact", True, (0, 0, 0), (255, 255, 255))
            for obj in near_obj:
                # Calculate screen position based on camera offset
                screen_pos = obj.rect.topleft - camera_group.offset # Use camera_group.offset
                self.display.blit(text_surf, (screen_pos.x - text_surf.get_width() // 2, screen_pos.y - 20))

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
                    system_narrative_tree = all_dialogues.get(narrator_dummy_obj.dialogue_id)
                    if system_narrative_tree:
                        self.current_dialogue_ref.current_dialogue = dialog(
                            narrator_dummy_obj,
                            self.player,
                            all_dialogues.get(narrator_dummy_obj.dialogue_id),
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
    
        if self.cutscene_active and entry.get("event") == "dean_exits":
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
        self.game_instance = None
    def get_state(self):
        return self.currentState
    def set_state(self, state):
        self.currentState  = state

if __name__== '__main__':
    game = Game()
    game.run()

import pygame
import sys
from pygame.locals import *
from character_movement import *
import json
from Dialogue import*


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


with open('NPC_dialog/NPC.json','r',encoding = 'utf-8') as f:
     all_dialogues = json.load(f)

try:
     print("JSON loaded successfully")
     print("Keys in JSON:", list(all_dialogues.keys()))
     if "intro" in all_dialogues:
        print("Intro chapters:", list(all_dialogues["intro"].keys()))
except Exception as e:
    print(f"Error loading JSON: {e}")
    all_dialogues = {"intro": {"chapter_1": [{"speaker": "narrator", "text": "Test intro text"}]}}

     

#global state tracking
current_chapter = "chapter_1"
player_choices = {}
showing_chapter_ending = False
ending_start_time = 0
ending_complete_callback = None
ending_image = None
space_released = True
current_dialogue = None

showing_intro = True
intro_background = None
intro_dialogue = None
intro_step = 0
intro_delay = 3000
intro_displayed_text = ""
intro_tying_delay = 45
intro_typing_last_time = 0



def start_chapter(chapter_name):
    global current_chapter,Chapter_intro
    current_chapter = chapter_name
    print(f"Starting chapter: {chapter_name}")

    #reset game state for  new chapter
    create_npcs()

    def intro_completed():
        print(f"Intro for {chapter_name} completed, creating NPCs now")
        # Only create NPCs after intro is done
        create_npcs()

    print(f"Starting intro for chapter {chapter_name}")
    Chapter_intro.active = True
    Chapter_intro.start(chapter_name, intro_completed)
          

        
def handle_chapter_ending (screen):
    global showing_chapter_ending,ending_image , ending_start_time, ending_complete_callback

    current_time = pygame.time.get_ticks()
    # Show ending for 5 seconds
    if current_time - ending_start_time > 5000:
        showing_chapter_ending = False
        print("Ending completed, calling callback")
        if ending_complete_callback:
            print("Callback exists, calling it now")
            ending_complete_callback()
        return False
    
    # Draw black background
    screen.fill((0, 0, 0))

# Draw chapter ending text
    font = pygame.font.SysFont('Comic Sans MS', 36)
    text = font.render(f"End of Chapter {current_chapter}", True, (255, 255, 255))
    screen.blit(text, (screen.get_width()//2 - text.get_width()//2, screen.get_height()//2))
    
    return True



#============Chapter Intro System ==============
class ChapterIntro:
    def __init__(self,screen):
        self.screen = screen
        self.active = False
        self.background = None
        self.dialogue = []
        self.step = 0
        self.last_time = 0
        self.delay = 3000 # 3 seconds between dialogue lines
        self.typing_index = 0
        self.displayed_text = ""
        self.typing_delay = 45
        self.typing_last_time = 0
        self.fade_alpha = 0
        self.fade_speed = 5
        self.fading_in = True
        self.fading_out = False
        self.completed_callback = None
        

    def start(self,chapter, completed_callback = None):

        self.active = True
        print(f"ChapterIntro: Starting intro for {chapter}")
        self.background = pygame.image.load( "picture/Map Art/outside.png")
        try:
           self.dialogue = all_dialogues.get("intro", {}).get(chapter, [])
           print(f"Loaded {len(self.dialogue)} dialogue entries")
        except Exception as e:
           print(f"Error loading dialogue: {e}")
           self.dialogue = [{"speaker": "narrator", "text": f"Chapter {chapter} begins..."}]

        self.step = 0
        self.last_time = pygame.time.get_ticks()
        self.typing_index = 0
        self.displayed_text = ""
        self.typing_last_time = pygame.time.get_ticks()
        self.fade_alpha = 0
        self.fading_in = True
        self.fading_out = False
        self.completed_callback = completed_callback

    def end_intro(self):
        self.active = False
        print("intro sequance ended")
        if self.completed_callback:
           self.completed_callback()
       

    def update(self,keys):
        if not self.active :
            return False

        #handle fade in
        if self.fading_in:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fading_in = False
            return True
        #handle fading out
        if self.fading_out:
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                self.active = False
                if self.completed_callback:
                    self.completed_callback()
                return False
            return True
        
        #if intro is complete,start fade out
        if self.step >= len(self.dialogue):
            self.fading_out = True
            return True
        
        #handle space key to skip
        global space_released
        if keys[pygame.K_SPACE] and space_released:
            space_released = False

            #if text still typing , display all immmediately
            if self.typing_index < len(self.dialogue[self.step].get("text","")):
                self.typing_index = len(self.dialogue[self.step].get("text",""))
                self.displayed_text = self.dialogue[self.step].get("text","")
            else:
                #move to next diakogue line
                self.step += 1
                self.typing_index = 0
                self.displayed_text = ""
                self.last_time = pygame.time.get_ticks()

        if not keys[pygame.K_SPACE]:
            space_released = True

            #get current dialogue entry
        if self.step <len(self.dialogue):
                entry = self.dialogue[self.step]
                current_text = entry.get("text","")

                #auto advance when text is complete displayed
                current_time = pygame.time.get_ticks()
                if (self.typing_index >= len(current_text)and current_time - self.last_time > self.delay):
                    self.step += 1
                    self.typing_index = 0
                    self.displayed_text = ""
                    self.last_time = current_time
                
                #typing effect
                if self.typing_index < len(current_text):
                    if current_time - self.typing_last_time > self.typing_delay:
                        self.displayed_text += current_text[self.typing_index]
                        self.typing_index += 1
                        self.typing_last_time = current_time
        return True
    
    def draw(self,screen):
        if not self.active:
            return
        
        #draw bg with fade
        screen_rect = screen.get_rect()
        bg_rect = self.background.get_rect(center = screen_rect.center)

        #fill with black first
        screen.fill((0,0,0))

        #create copy of bg with adjust alpha
        temp_bg = self.background.copy()
        temp_bg.set_alpha(self.fade_alpha)
        screen.blit(temp_bg, bg_rect)

        #text won't draw during fade transitions
        if self.fading_in or self.fading_out:
            return

        dialogue_font = pygame.font.SysFont('Comic Sans MS', 30)

        self.dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()
        dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
        dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20
        text_max_width = self.dialog_box_img.get_width() - 300 #pixel padding each side


        #let the dialog box on the center and put below
        dialog_x = screen.get_width()//2 - self.dialog_box_img.get_width() // 2
        dialog_y = screen.get_height() - self.dialog_box_img.get_height() - 20

        screen.blit(self.dialog_box_img, (dialog_x, dialog_y))

        

        #draw text with wrap
        if self.step < len(self.dialogue):
            entry = self.dialogue[self.step]
            speaker = entry.get ("speaker","")

            #draw speaker name if it is not the narrator
            if speaker != "narrator":
                speaker_text = dialogue_font.render(speaker,True,(255,255,255))

                screen.blit(speaker_text,(dialog_x,dialog_y))
            
            draw_text(screen,self.displayed_text,30,(0,0,0),dialog_x + self.dialog_box_img.get_width()//2  ,dialog_y + self.dialog_box_img.get_height()//2 - 15 ,center = True,max_width=text_max_width)

def end_chapter_and_start_next(current_chapter, next_chapter):
    global showing_chapter_ending, ending_start_time, ending_complete_callback
    
    print(f"Ending chapter {current_chapter} and preparing to start {next_chapter}")
    showing_chapter_ending = True
    ending_start_time = pygame.time.get_ticks()
    
    def transition_to_next():
        start_chapter(next_chapter)
    
    ending_complete_callback = transition_to_next


def create_npcs():

    global npc_manager 
    npc_manager.npcs = []

    if current_chapter == "chapter_1":
        nuva = NPC(600,500,"Nuva")
        dean = NPC(800,500,"Dean")
        patient1 = NPC(400,500,"zheng")

        npc_manager.add_npc(nuva)
        npc_manager.add_npc(dean)
        npc_manager.add_npc(patient1)
    
    elif current_chapter == "chapter_2":
        nuva = NPC(600,500,"Nuva")
        dean = NPC(800,500,"Dean")
        patient2 = NPC(400,500,"Emma")

        npc_manager.add_npc(nuva)
        npc_manager.add_npc(dean)
        npc_manager.add_npc(patient2)

  
Chapter_intro = ChapterIntro(screen)
#initialize the chapter intro system
def init_game():
    global current_chapter,Chapter_intro,showing_intro
    current_chapter = "chapter_1"

    start_chapter("chapter_1")

init_game()  
npc_manager = NPCManager()


run = True
while run:
          
          keys = pygame.key.get_pressed()

          if Chapter_intro.active:
              if Chapter_intro.update(keys):
                  Chapter_intro.draw(screen)
                  pygame.display.flip()
                  clock.tick(FPS)
                  continue
              
          if showing_chapter_ending:
              if handle_chapter_ending(screen):
                  pygame.display.flip()
                  clock.tick(FPS)
                  continue
              
          draw_bg(screen)
          is_moving = player.move(moving_left,moving_right)
          player.update_animation(is_moving)
          
          for npc in npc_manager.npcs:
              screen.blit(npc.image,npc.rect)

          player.draw(screen)
          
          moving_left,moving_right,run =  keyboard_input(moving_left, moving_right, run)
          nearest_npc = npc_manager.get_nearest_npc(player)

          #=====space======
          
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
              current_dialogue.update()
              current_dialogue.draw(screen)
          
          pygame.display.flip()
          clock.tick(FPS)    
          

pygame.quit()
sys.exit()       
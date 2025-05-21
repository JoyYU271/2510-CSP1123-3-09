import pygame
import sys
import json


pygame.init()

# Set up display
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Chapter Intro Test")
clock = pygame.time.Clock()
FPS = 60
# Load JSON data

with open('NPC_dialog/NPC.json', 'r', encoding='utf-8') as f:
        all_dialogues = json.load(f)

dialog_box_img = pygame.image.load("picture/Character Dialogue/dialog boxxx.png").convert_alpha()

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
           name_to_display = self.npc.name if speaker == "npc" else self.player.name
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

          
           # words come out one by one effect
           current_time = pygame.time.get_ticks()
           if self.letter_index < len(text):
                if current_time - self.last_time > self.letter_delay:
                     self.displayed_text += text[self.letter_index]
                     self.letter_index += 1
                     self.last_time = current_time
          
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
    

class SimpleChapterIntro:
    def __init__(self, display, gameStateManager):
        self.active = False
        self.background = None
        self.display = display
        self.gameStateManager = gameStateManager
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
     
class Game:
    def __init__(self):
        self.screen = screen
        self.gameStateManager = GameStateManager()
        self.start = SimpleChapterIntro(self.screen, self.gameStateManager)
        self.level = Rooms(self.screen, self.gameStateManager)
            
class Rooms:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager        
    def run(self):
        pass
    #thisdict = {
#   "world": ["Outside", "Inside", "PlayerOff", "DeanOff", "Basement", "Store"],
#   "sub_worlds": {"chapter1":["work", "class", "office", "lab?"], "chapter2":["runway ad", "dressing", "home", "bedroom", "clinic?"]}
# }

#print(thisdict)

class GameStateManager:
    def __inti__(self):
        pass




# Create intro object
showing_intro = True
chapter_intro = SimpleChapterIntro()
chapter_intro.start("chapter_1")


# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                # Restart intro
                chapter_intro.start("chapter_1")
    
    # Get keys
    keys = pygame.key.get_pressed()
    
    # Update and draw intro
    if chapter_intro.active:
        if chapter_intro.update(keys):
            chapter_intro.draw(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                   running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart intro
                        chapter_intro.start("chapter_1")
                        print("Chapter intro restarting...")
        else:
            # If intro is no longer active, restart it
            print("Chapter intro finished")
            #chapter_intro.start("chapter_1")
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
sys.exit()
import pygame
import sys
import Dialogue1
from Dialogue1 import run_dialogue
from ui_components import Button, get_font
from save_load import SaveManager


pygame.init() #initialize all import pygame modules
pygame.mixer.init()

screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height))#pygame.FULLSCREEN)
pygame.display.set_caption("main page test")

#background image
bg_img = pygame.image.load("main page/Menu Page.png").convert() #converts is for optimize image faster blitting on screen
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))

#button image
start_img = pygame.image.load('main page/start.png').convert_alpha() #alpha is use to keep transparent background
load_img = pygame.image.load('main page/load.png').convert_alpha()
collections_img = pygame.image.load('main page/collections.png').convert_alpha()
settings_img = pygame.image.load('main page/settings.png').convert_alpha()
exit_img = pygame.image.load('main page/exit.png').convert_alpha()

#button click sound
click_sound = pygame.mixer.Sound("main page/click1.wav") 

# Global variables to store settings
bgm_vol = 0.5
sfx_vol = 0.5
text_size = "Medium"
current_font_size = 30
current_language = "EN"
main_menu_bgm_played = False


def main_menu():
    global current_font_size,bgm_vol, main_menu_bgm_played

    global current_dialogue
    current_dialogue = None

    if not main_menu_bgm_played:
        pygame.mixer.music.load("bgm/main page.mp3")
        pygame.mixer.music.set_volume(bgm_vol)
        pygame.mixer.music.play(-1)
        main_menu_bgm_played = True

    start_button = Button(image=start_img, pos=(300, 120), scale=0.24)
    load_button = Button(image=load_img, pos=(300, 280), scale=0.24)
    collections_button = Button(image=collections_img, pos=(300, 440), scale=0.24)
    settings_button = Button(image=settings_img, pos=(300, 600), scale=0.24)
    #exit_button = Button(image=exit_img, pos=(300, 640), scale=0.24)

    while True: #keep window running

        screen.blit(bg_img, (0, 0)) #draw backgound from (0,0)
   
        start_button.draw(screen)
        load_button.draw(screen)
        collections_button.draw(screen)
        settings_button.draw(screen)
        #exit_button.draw(screen)

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.checkForInput(mouse_pos):
                    click_sound.play()
                    pygame.mixer.music.stop()
                    run_dialogue(current_font_size, current_language, bgm_vol, sfx_vol)

                    pygame.mixer.music.load("bgm/main page.mp3")
                    pygame.mixer.music.set_volume(bgm_vol)
                    pygame.mixer.music.play(-1)
                    
                elif load_button.checkForInput(mouse_pos):
                    click_sound.play()
                    load_screen()
                elif collections_button.checkForInput(mouse_pos):
                    click_sound.play()
                    collections_screen()
                elif settings_button.checkForInput(mouse_pos):
                    click_sound.play()
                    settings_screen()
                #elif exit_button.checkForInput(mouse_pos):
                    #pygame.quit()
                    #sys.exit()

        pygame.display.flip()


def load_screen():
    save_manager = SaveManager()
    save_files = save_manager.get_save_files()
    
    load_bg_img = pygame.image.load("main page/common background.png").convert()
    load_bg_img = pygame.transform.scale(load_bg_img, (screen_width, screen_height))

    # Create buttons for each save slot
    save_slots = []
    delete_buttons = []
    for i in range(3):  # Support for 3 save slots
        exists = f"save_{i}.sav" in save_files
        save_slots.append({
            "exists": exists,
            "button": Button(image=None, pos=(640, 200 + i*120), 
                           text_input=f"Slot {i+1} {'(Empty)' if not exists else ''}",
                           font=get_font(45), base_color="White", hovering_color="Green")
        })
        
        delete_buttons.append(
            Button(image=None, pos=(800, 200 + i*120), 
                 text_input="Delete" if exists else "",
                 font=get_font(30), base_color="Red", hovering_color="Dark Red")
        )

    back_button = Button(image=None, pos=(640, 600), text_input="BACK",
                        font=get_font(75), base_color="White", hovering_color="Green")
    
    while True:
        screen.blit(load_bg_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw title
        title_text = get_font(60).render("LOAD GAME", True, "White")
        title_rect = title_text.get_rect(center=(640, 100))
        screen.blit(title_text, title_rect)
        
        # Draw save slots
        for i, (slot, del_btn) in enumerate(zip(save_slots, delete_buttons)):
            if slot["exists"]:
                slot["button"].changeColor(mouse_pos)
            slot["button"].update(screen)
            
            save_data = save_manager.load_game(i)
            if save_data:
                # Show timestamp and chapter info
               time_text = get_font(25).render(save_data["timestamp"], True, "White")
               screen.blit(time_text, (350, 170 + i*120))  # Moved further left

               chapter_text = get_font(25).render(f"Chapter: {save_data['current_chapter']}", True, "White")
               screen.blit(chapter_text, (350, 200 + i*120))

               del_btn.changeColor(mouse_pos)
               del_btn.update(screen)
            
        back_button.changeColor(mouse_pos)
        back_button.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkForInput(mouse_pos):
                    click_sound.play()
                    return
                
                for i, slot in enumerate(save_slots):
                    if slot["button"].checkForInput(mouse_pos) and slot["exists"]:
                        click_sound.play()
                        # Load the game
                        save_data = save_manager.load_game(i)
                        if save_data:
                            # Update global settings
                            global bgm_vol, sfx_vol, text_size, current_font_size, current_language
                            settings = save_data.get("settings", {})
                            bgm_vol = settings.get("bgm_vol", 0.5)
                            sfx_vol = settings.get("sfx_vol", 0.5)
                            text_size = settings.get("text_size", "Medium")
                            current_language = settings.get("language", "EN")
                            
                            # Convert text size to font size
                            if text_size == "Small":
                                current_font_size = 25
                            elif text_size == "Medium":
                                current_font_size = 30
                            elif text_size == "Large":
                                current_font_size = 35
                            
                            # Start game with loaded state
                            pygame.mixer.music.stop()
                            run_dialogue(
                                current_font_size, 
                                current_language, 
                                bgm_vol, 
                                sfx_vol,
                                initial_state=save_data
                            )
                            return
                    
                for i, del_btn in enumerate(delete_buttons):
                    if del_btn.text_input == "Delete" and del_btn.checkForInput(mouse_pos):
                        click_sound.play()
                        if save_manager.delete_save(i):
                            # Update the slot and button states
                            save_slots[i]["exists"] = False
                            save_slots[i]["button"].base_color = "Gray"
                            save_slots[i]["button"].hovering_color = "Gray"
                            delete_buttons[i].text_input = ""
                            # Redraw immediately
                            screen.blit(load_bg_img, (0, 0))
                            screen.blit(title_text, title_rect)
                            for j, (s, d) in enumerate(zip(save_slots, delete_buttons)):
                                s["button"].update(screen)
                                d.update(screen)
                            pygame.display.flip()
                            pygame.time.delay(300)  # Short delay for visual feedback

        pygame.display.update()

def collections_screen():
    while True:
        screen.fill("white")
        mouse_pos = pygame.mouse.get_pos()

        text = get_font(45).render("This is the COLLECTIONS screen.", True, "Black")
        rect = text.get_rect(center=(640, 260))
        screen.blit(text, rect)

        back_button = Button(image=None, pos=(640, 460), text_input="BACK",
                             font=get_font(75), base_color="Black", hovering_color="Green")

        back_button.changeColor(mouse_pos)
        back_button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkForInput(mouse_pos):
                    click_sound.play()
                    return

        pygame.display.update()

def settings_screen():
    global screen,bgm_vol, sfx_vol, text_size,current_font_size,current_language #modify the global variables 

    #set backgound
    settings_bg_img = pygame.image.load("main page/common background.png").convert()
    settings_bg_img = pygame.transform.scale(settings_bg_img, (screen_width, screen_height))

    #default settings
    default_bgm_vol = 0.5
    default_sfx_vol = 0.5
    default_text_size = "Medium"
    default_language = "EN"

    while True:
        screen.blit(settings_bg_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        #bgm volume
        bgm_text = get_font(40).render(f"BGM Volume: {int(bgm_vol * 100)}%", True, "White")
        screen.blit(bgm_text, (screen_width // 2 - bgm_text.get_width() // 2, 100))

        bgm_minus = Button(None, (screen_width//2 - 100, 150), text_input="-", font=get_font(50), base_color="White", hovering_color="Green")
        bgm_plus = Button(None, (screen_width//2 + 100, 150), text_input="+", font=get_font(50), base_color="White", hovering_color="Green")

        #SFX Volume
        sfx_text = get_font(40).render(f"SFX Volume: {int(sfx_vol * 100)}%", True, "White")
        screen.blit(sfx_text, (screen_width // 2 - sfx_text.get_width() // 2, 200))

        sfx_minus = Button(None, (screen_width//2 - 100, 250), text_input="-", font=get_font(50), base_color="White", hovering_color="Green")
        sfx_plus = Button(None, (screen_width//2 + 100, 250), text_input="+", font=get_font(50), base_color="White", hovering_color="Green")

        #language setting
        lang_text = get_font(40).render(f"Language(Dialogue): {current_language}", True, "White")
        screen.blit(lang_text, (screen_width // 2 - lang_text.get_width() // 2, 300))

        lang_toggle_button = Button(None, (screen_width//2, 350), text_input="Switch", font=get_font(40), base_color="White", hovering_color="Green")

        #text size
        text_size_text = get_font(40).render(f"Text Size: {text_size}", True, "White")
        screen.blit(text_size_text, (screen_width // 2 - text_size_text.get_width() // 2, 400))

        small_button = Button(None, (screen_width//2 - 150, 450), text_input="Small", font=get_font(40), base_color="White", hovering_color="Green")
        medium_button = Button(None, (screen_width//2, 450), text_input="Medium", font=get_font(40), base_color="White", hovering_color="Green")
        large_button = Button(None, (screen_width//2 + 150, 450), text_input="Large", font=get_font(40), base_color="White", hovering_color="Green")

        #reset and back 
        default_button = Button(None, (screen_width//2, 550), text_input="Reset to Default", font=get_font(45), base_color="White", hovering_color="Green")
        back_button = Button(None, (screen_width//2, 640), text_input="BACK", font=get_font(60), base_color="White", hovering_color="Green")


        buttons = [bgm_plus, bgm_minus, sfx_plus, sfx_minus,
                   small_button, medium_button, large_button,
                   default_button, back_button,lang_toggle_button]

        for btn in buttons:
            btn.changeColor(mouse_pos)
            btn.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkForInput(mouse_pos):
                    click_sound.play()
                    return #back to menu
                
                if bgm_plus.checkForInput(mouse_pos) and bgm_vol < 1.0:
                    bgm_vol = round(min(bgm_vol + 0.1, 1.0), 1) #to not exceed 1.0
                    pygame.mixer.music.set_volume(bgm_vol)
                    if hasattr(Dialogue1, 'current_dialogue_instance') and Dialogue1.current_dialogue_instance:
                       Dialogue1.current_dialogue_instance.update_bgm_volume(bgm_vol)
                    click_sound.play()
                if bgm_minus.checkForInput(mouse_pos) and bgm_vol > 0.0:
                    bgm_vol = round(max(bgm_vol - 0.1, 0.0), 1) #to not lower than 0.0
                    pygame.mixer.music.set_volume(bgm_vol)
                    if hasattr(Dialogue1, 'current_dialogue_instance') and Dialogue1.current_dialogue_instance:
                       Dialogue1.current_dialogue_instance.update_bgm_volume(bgm_vol)
                    click_sound.play()

                if sfx_plus.checkForInput(mouse_pos) and sfx_vol < 1.0:
                    sfx_vol = round(min(sfx_vol + 0.1, 1.0), 1)
                    click_sound.set_volume(sfx_vol)
                    if hasattr(Dialogue1, 'current_dialogue_instance') and Dialogue1.current_dialogue_instance:
                       Dialogue1.current_dialogue_instance.update_sfx_volume(sfx_vol)
                    click_sound.play()
                if sfx_minus.checkForInput(mouse_pos) and sfx_vol > 0.0:
                    sfx_vol = round(max(sfx_vol - 0.1, 0.0), 1)
                    click_sound.set_volume(sfx_vol)
                    if hasattr(Dialogue1, 'current_dialogue_instance') and Dialogue1.current_dialogue_instance:
                       Dialogue1.current_dialogue_instance.update_sfx_volume(sfx_vol)
                    click_sound.play()

                if small_button.checkForInput(mouse_pos):
                    text_size = "Small"
                    current_font_size = 25
                    click_sound.play()
                if medium_button.checkForInput(mouse_pos):
                    text_size = "Medium"
                    current_font_size = 30
                    click_sound.play()
                if large_button.checkForInput(mouse_pos):
                    text_size = "Large"
                    current_font_size = 35
                    click_sound.play()
                    

                if lang_toggle_button.checkForInput(mouse_pos):
                   current_language = "CN" if current_language == "EN" else "EN"
                   click_sound.play()


                if default_button.checkForInput(mouse_pos):
                    bgm_vol = default_bgm_vol
                    sfx_vol = default_sfx_vol
                    text_size = default_text_size
                    current_font_size = 30
                    pygame.mixer.music.set_volume(bgm_vol)
                    click_sound.set_volume(sfx_vol)
                    current_language = default_language
                    click_sound.play()

        pygame.display.update()

main_menu()



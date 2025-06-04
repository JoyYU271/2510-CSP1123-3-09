import pygame
import sys
import Dialogue1
from Dialogue1 import run_dialogue
from ui_components import Button, get_font
from save_system import save_checkpoint, load_checkpoint
 

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
    #set backgound
    load_bg_img = pygame.image.load("main page/common background.png").convert()
    load_bg_img = pygame.transform.scale(load_bg_img, (screen_width, screen_height))

    while True:
        screen.blit(load_bg_img, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        title_text = get_font(45).render("LOAD SCREEN", True, "White")
        screen.blit(title_text, title_text.get_rect(center=(640, 180)))

        # 加载按钮
        continue_button = Button(
            image=None,
            pos=(640, 300),
            text_input="Continue from Last Checkpoint",
            font=get_font(40),
            base_color="White",
            hovering_color="Green"
        )

        back_button = Button(
            image=None,
            pos=(640, 450),
            text_input="BACK",
            font=get_font(50),
            base_color="White",
            hovering_color="Green"
        )

        for button in [continue_button, back_button]:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_button.checkForInput(mouse_pos):
                    click_sound.play()

                    save_data = load_checkpoint()
                    if save_data:
                        pygame.mixer.music.stop()
                        run_dialogue(
                            text_size=current_font_size,
                            language=current_language,
                            bgm_vol=bgm_vol,
                            sfx_vol=sfx_vol,
                            resume_from = (
                                save_data.get("npc_state", {}),
                                save_data.get("player_choices", {}),
                                save_data.get("flags", {}),
                                save_data.get("shown_dialogues", {})
                            )
                        )
                    else:
                        print("No save data found.")


                elif back_button.checkForInput(mouse_pos):
                    click_sound.play()
                    return

        pygame.display.update()


def collections_screen():
    collections_bg_img = pygame.image.load("main page/common background.png").convert()
    collections_bg_img = pygame.transform.scale(collections_bg_img, (screen_width, screen_height))

    save_data = load_checkpoint()
    unlocked_endings = save_data.get("flags", {}) if save_data else {}

    # 按角色组织结局
    grouped_endings = [
        ("Zheng's Endings", [
            ("The Routine Life", show_zheng_routine_life),
            ("Rediscovered Dreams", show_zheng_dreams)
        ]),
        ("Emma's Endings", [
            ("Blissful Emptiness", show_emma_bliss),
            ("Living Despite Fear", show_emma_fear)
        ]),
        ("Player's Endings", [
            ("Ship of Theseus", show_player_ship if unlocked_endings.get("ending_unlocked_Ship_of_Theseus") else None),
            ("Justice Served", show_player_justice if unlocked_endings.get("ending_unlocked_Justice_Served") else None),
            ("Rebirth of the Dual Soul", show_player_rebirth if unlocked_endings.get("ending_unlocked_Rebirth_of_the_Dual_Soul") else None)
        ])
    ]

    # 用于按钮排布的起始位置
    start_y = 70
    section_spacing = 40  # 每组之间的间距
    button_spacing = 50   # 同组按钮之间的间距

    all_buttons = []
    y = start_y

    for section_title, endings in grouped_endings:
        # 添加组标题
        title_text = get_font(36).render(section_title, True, "White")
        title_rect = title_text.get_rect(center=(640, y))
        all_buttons.append(("label", title_text, title_rect))
        y += 40  # 标题高度

        for text, action in endings:
            if action:
                button = Button(
                    image=None,
                    pos=(640, y),
                    text_input=text,
                    font=get_font(30),
                    base_color="White",
                    hovering_color="Green"
                )
            else:
                button = Button(
                    image=None,
                    pos=(640, y),
                    text_input=f"{text} (Locked)",
                    font=get_font(30),
                    base_color="Grey",
                    hovering_color="Grey"
                )
            all_buttons.append(("button", button, action))
            y += button_spacing


        y += section_spacing  # 组之间的空隙

    # 添加返回按钮
    back_button = Button(
        image=None,
        pos=(640, 650),
        text_input="BACK",
        font=get_font(40),
        base_color="White",
        hovering_color="Green"
    )

    while True:
        screen.blit(collections_bg_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        # 处理所有结局按钮和标题
        for kind, *data in all_buttons:
            if kind == "label":
                text_surface, rect = data
                screen.blit(text_surface, rect)
            elif kind == "button":
                button, _ = data
                button.changeColor(mouse_pos)
                button.update(screen)

        # BACK 按钮
        back_button.changeColor(mouse_pos)
        back_button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for kind, *data in all_buttons:
                    if kind == "button":
                        button, action = data
                        if button.checkForInput(mouse_pos):
                            if action:  # ✅ 只有解锁了才调用
                                click_sound.play()
                                action()
                                return
                            else:
                                # 未解锁提示
                                click_sound.play()
                                warning_font = get_font(30)
                                warning_text = warning_font.render("You haven't unlocked this ending yet.", True, "Red")
                                screen.blit(warning_text, warning_text.get_rect(center=(640, 680)))
                                pygame.display.update()
                                pygame.time.delay(1000)  # 停顿显示提示
                                break  # ✅ 避免同时点多个按钮

                if back_button.checkForInput(mouse_pos):
                    click_sound.play()
                    return


        pygame.display.update()


def show_cg_gallery(image_paths):
    background = pygame.image.load("main page/common background.png").convert()
    background = pygame.transform.scale(background, (screen_width, screen_height))

    thumbnail_size = (320, 180)
    spacing_x = 30
    spacing_y = 30

    thumbnails = []

    for path in image_paths:
        try:
            image = pygame.image.load(path).convert()
            thumb = pygame.transform.scale(image, thumbnail_size)
            thumbnails.append((thumb, image))
        except:
            print(f"Failed to load {path}")

    layout_positions = []
    num = len(thumbnails)

    if num == 1:
        layout_positions = [(screen_width // 2 - thumbnail_size[0] // 2, 180)]
    elif num == 4:
        start_x = (screen_width - (2 * thumbnail_size[0] + spacing_x)) // 2
        y1 = 150  # ✅ 原 100 → 150：稍微往下移
        y2 = y1 + thumbnail_size[1] + spacing_y
        layout_positions = [
            (start_x, y1), (start_x + thumbnail_size[0] + spacing_x, y1),
            (start_x, y2), (start_x + thumbnail_size[0] + spacing_x, y2)
        ]
    elif num == 5:
        start_x = (screen_width - (2 * thumbnail_size[0] + spacing_x)) // 2
        y1 = 60
        y2 = y1 + thumbnail_size[1] + spacing_y
        y3 = y2 + thumbnail_size[1] + spacing_y
        layout_positions = [
            (start_x, y1), (start_x + thumbnail_size[0] + spacing_x, y1),
            (start_x, y2), (start_x + thumbnail_size[0] + spacing_x, y2),
            (screen_width // 2 - thumbnail_size[0] // 2, y3)
        ]
    else:
        print("Unsupported number of CGs for layout.")
        return

    # ✅ BACK 按钮放左下角
    back_button = Button(
        image=None,
        pos=(150, screen_height - 100),
        text_input="BACK",
        font=get_font(40),
        base_color="White",
        hovering_color="Green"
    )

    viewing_fullscreen = False
    selected_image = None

    while True:
        screen.blit(background, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if viewing_fullscreen:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    viewing_fullscreen = False
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for idx, (thumb, full_image) in enumerate(thumbnails):
                        rect = pygame.Rect(*layout_positions[idx], *thumbnail_size)
                        if rect.collidepoint(mouse_pos):
                            selected_image = full_image
                            viewing_fullscreen = True
                            break

                    if back_button.checkForInput(mouse_pos):
                        click_sound.play()
                        return  # ✅ 返回上一级（collections_screen）

        if viewing_fullscreen and selected_image:
            fullscreen = pygame.transform.scale(selected_image, (screen_width, screen_height))
            screen.blit(fullscreen, (0, 0))
        else:
            for idx, (thumb, _) in enumerate(thumbnails):
                pos = layout_positions[idx]
                screen.blit(thumb, pos)

            back_button.changeColor(mouse_pos)
            back_button.update(screen)

        pygame.display.update()






def show_zheng_routine_life():
    show_cg_gallery([
        "picture/Ending/P1 End1.png",
    ])

def show_zheng_dreams():
    show_cg_gallery([
        "picture/Ending/P1 End2.png",
    ])

def show_emma_bliss():
    show_cg_gallery([
        "picture/Ending/P2 End1.png",
    ])

def show_emma_fear():
    show_cg_gallery([
        "picture/Ending/P2 End2.png",
    ])

def show_player_ship():
    show_cg_gallery([
        "picture/Ending/End1.1.png",
        "picture/Ending/End1.2.png",
        "picture/Ending/End1.3.png",
        "picture/Ending/End1.4.png",
    ])

def show_player_justice():
    show_cg_gallery([
        "picture/Ending/End2.1.png",
        "picture/Ending/End2.2.png",
        "picture/Ending/End2.3.png",
        "picture/Ending/End2.4.png",
    ])

def show_player_rebirth():
    show_cg_gallery([
        "picture/Ending/End3.1.png",
        "picture/Ending/End3.2.png",
        "picture/Ending/End3.3.png",
        "picture/Ending/End3.4.png",
        "picture/Ending/End3.5.png",
    ])





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
        screen.blit(bgm_text, (screen_width // 2 - bgm_text.get_width() // 2, 150))

        bgm_minus = Button(None, (screen_width//2 - 100, 200), text_input="-", font=get_font(50), base_color="White", hovering_color="Green")
        bgm_plus = Button(None, (screen_width//2 + 100, 200), text_input="+", font=get_font(50), base_color="White", hovering_color="Green")

        #SFX Volume
        sfx_text = get_font(40).render(f"SFX Volume: {int(sfx_vol * 100)}%", True, "White")
        screen.blit(sfx_text, (screen_width // 2 - sfx_text.get_width() // 2, 250))

        sfx_minus = Button(None, (screen_width//2 - 100, 300), text_input="-", font=get_font(50), base_color="White", hovering_color="Green")
        sfx_plus = Button(None, (screen_width//2 + 100, 300), text_input="+", font=get_font(50), base_color="White", hovering_color="Green")

        #language setting
        lang_text = get_font(40).render(f"Language(Dialogue): {current_language}", True, "White")
        screen.blit(lang_text, (screen_width // 2 - lang_text.get_width() // 2, 350))

        lang_toggle_button = Button(None, (screen_width//2, 400), text_input="Switch", font=get_font(40), base_color="White", hovering_color="Green")

        #text size
        text_size_text = get_font(40).render(f"Text Size: {text_size}", True, "White")
        screen.blit(text_size_text, (screen_width // 2 - text_size_text.get_width() // 2, 450))

        small_button = Button(None, (screen_width//2 - 150, 500), text_input="Small", font=get_font(40), base_color="White", hovering_color="Green")
        medium_button = Button(None, (screen_width//2, 500), text_input="Medium", font=get_font(40), base_color="White", hovering_color="Green")
        large_button = Button(None, (screen_width//2 + 150, 500), text_input="Large", font=get_font(40), base_color="White", hovering_color="Green")

        #reset and back 
        default_button = Button(None, (screen_width//2, 580), text_input="Reset to Default", font=get_font(45), base_color="White", hovering_color="Green")
        back_button = Button(None, (screen_width//2, 640), text_input="BACK", font=get_font(50), base_color="White", hovering_color="Green")


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





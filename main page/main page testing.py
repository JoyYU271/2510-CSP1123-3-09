import pygame
import sys
#import ctypes #ctypes is built-in python library that allows calling functions written in C (it allows Python to interact directly with the operating system’s native API)
#here maybe can add import sys to use sy.exit() but still figuring out how to use it

pygame.init() #initialize all import pygame modules
pygame.mixer.init()

#to get real resolution
#ctypes.windll.user32.SetProcessDPIAware() #make sure the Python program gets the actual screen resolution, not scaled one
#screen_width = ctypes.windll.user32.GetSystemMetrics(0) #ask the real screen width in pixels
#screen_height = ctypes.windll.user32.GetSystemMetrics(1) #ask the real screen height in pixels

screen_width = 1280
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height))#pygame.FULLSCREEN)
pygame.display.set_caption("main page test")

#background image
bg_img = pygame.image.load("background1.png").convert() #converts is for optimize image faster blitting on screen
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))

#button image
start_img = pygame.image.load('start.png').convert_alpha() #alpha is use to keep transparent background
load_img = pygame.image.load('load.png').convert_alpha()
collections_img = pygame.image.load('collections.png').convert_alpha()
settings_img = pygame.image.load('settings.png').convert_alpha()
exit_img = pygame.image.load('exit.png').convert_alpha()

#button click sound
click_sound = pygame.mixer.Sound("click1.wav") 

# Global variables to store settings
bgm_vol = 0.5
sfx_vol = 0.5
resolution = (1280, 720)

#get a font
def get_font(size):
    return pygame.font.Font(None, size) #None is use system default font

#button class
class Button():
    def __init__(self, image, pos, text_input="", font=None, base_color=(0, 0, 0), hovering_color=(0, 0, 0), scale=1.0):
        self.original_image = image
        if image is not None and scale != 1.0:
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            self.image = pygame.transform.scale(image, (width, height))
        else:
            self.image = image

        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font or get_font(30)
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)

        if self.image is None:
            self.image = self.text

        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos)) #detect clicks
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos)) 

    #update image and text on screen
    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    #determine is mouse on button area or not
    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColor(self, position):
        if self.checkForInput(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
    
    def draw(self, screen):
        self.update(screen)
        mouse_pos = pygame.mouse.get_pos()
        self.changeColor(mouse_pos)
        return self.checkForInput(mouse_pos)

def main_menu():
    start_button = Button(image=start_img, pos=(300, 80), scale=0.24)
    load_button = Button(image=load_img, pos=(300, 220), scale=0.24)
    collections_button = Button(image=collections_img, pos=(300, 360), scale=0.24)
    settings_button = Button(image=settings_img, pos=(300, 500), scale=0.24)
    exit_button = Button(image=exit_img, pos=(300, 640), scale=0.24)
    
    while True: #keep window running

        screen.blit(bg_img, (0, 0)) #draw backgound from (0,0)
   
        start_button.draw(screen)
        load_button.draw(screen)
        collections_button.draw(screen)
        settings_button.draw(screen)
        exit_button.draw(screen)

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.checkForInput(mouse_pos):
                    click_sound.play()
                    play()
                elif load_button.checkForInput(mouse_pos):
                    click_sound.play()
                    load_screen()
                elif collections_button.checkForInput(mouse_pos):
                    click_sound.play()
                    collections_screen()
                elif settings_button.checkForInput(mouse_pos):
                    click_sound.play()
                    settings_screen()
                elif exit_button.checkForInput(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

def play():
    while True:
        screen.fill("black")
        mouse_pos = pygame.mouse.get_pos()

        text = get_font(45).render("This is the PLAY screen.", True, "White")
        rect = text.get_rect(center=(640, 260))
        screen.blit(text, rect)

        back_button = Button(image=None, pos=(640, 460), text_input="BACK",
                             font=get_font(75), base_color="White", hovering_color="Green")

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

def load_screen():
    while True:
        screen.fill("white")
        mouse_pos = pygame.mouse.get_pos()

        text = get_font(45).render("This is the LOAD screen.", True, "Black")
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
    global bgm_vol, sfx_vol, resolution #modify the global variables bgm_vol, sfx_vol, and resolution

    while True:
        screen.fill("black")
        mouse_pos = pygame.mouse.get_pos()

        #volume control buttons
        bgm_plus = Button(None, (800, 250), text_input="+", font=get_font(45), base_color="White", hovering_color="Green")
        bgm_minus = Button(None, (480, 250), text_input="-", font=get_font(45), base_color="White", hovering_color="Green")
        
        sfx_plus = Button(None, (800, 350), text_input="+", font=get_font(45), base_color="White", hovering_color="Green")
        sfx_minus = Button(None, (480, 350), text_input="-", font=get_font(45), base_color="White", hovering_color="Green")
        
        #resolution settings
        resolution_button = Button(image=None, pos=(640, 450), text_input=f"Resolution: {resolution[0]}x{resolution[1]}",
                                    font=get_font(45), base_color="White", hovering_color="Green")
        
        back_button = Button(image=None, pos=(640, 600), text_input="BACK",
                             font=get_font(60), base_color="White", hovering_color="Green")

        #draw all buttons
        for btn in [bgm_plus, bgm_minus, sfx_plus, sfx_minus, resolution_button, back_button]:
            btn.changeColor(mouse_pos)
            btn.update(screen)

        #display BGM volume
        bgm_text = get_font(35).render(f"BGM Volume: {int(bgm_vol * 100)}%", True, "White")
        screen.blit(bgm_text, (530, 210))

        #display SFX volume
        sfx_text = get_font(35).render(f"SFX Volume: {int(sfx_vol * 100)}%", True, "White")
        screen.blit(sfx_text, (530, 310))

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
                if bgm_minus.checkForInput(mouse_pos) and bgm_vol > 0.0:
                    bgm_vol = round(max(bgm_vol - 0.1, 0.0), 1) #to not lower than 0.0
                    pygame.mixer.music.set_volume(bgm_vol)

                if sfx_plus.checkForInput(mouse_pos) and sfx_vol < 1.0:
                    sfx_vol = round(min(sfx_vol + 0.1, 1.0), 1)
                    click_sound.set_volume(sfx_vol)
                if sfx_minus.checkForInput(mouse_pos) and sfx_vol > 0.0:
                    sfx_vol = round(max(sfx_vol - 0.1, 0.0), 1)
                    click_sound.set_volume(sfx_vol)

                if resolution_button.checkForInput(mouse_pos):
                    if resolution == (1280, 720):
                        resolution = (1920, 1080)
                    else:
                        resolution = (1280, 720)
                    pygame.display.set_mode(resolution)
                    resolution_button.text = get_font(45).render(f"Resolution: {resolution[0]}x{resolution[1]}", True, "White")
                    
        pygame.display.update()

main_menu()

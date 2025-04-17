import pygame
import ctypes #ctypes is built-in python library that allows calling functions written in C (it allows Python to interact directly with the operating system’s native API)
#here maybe can add import sys to use sy.exit() but still figuring out how to use it

pygame.init() #initialize all import pygame modules

#to get real resolution
ctypes.windll.user32.SetProcessDPIAware() #make sure the Python program gets the actual screen resolution, not scaled one
screen_width = ctypes.windll.user32.GetSystemMetrics(0) #ask the real screen width in pixels
screen_height = ctypes.windll.user32.GetSystemMetrics(1) #ask the real screen height in pixels

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("main page test")

bg_img = pygame.image.load("background.png").convert() #converts is for optimize image faster blitting on screen
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))

#button image
start_img = pygame.image.load('start.png').convert_alpha() #alpha is use to keep transparent background
load_img = pygame.image.load('load.png').convert_alpha()
settings_img = pygame.image.load('settings.png').convert_alpha()
exit_img = pygame.image.load('exit.png').convert_alpha()

#button class
class Button():
    def __init__(self, x, y, image, scale):  #init is for initialize, self is button itself, xy is coordinate
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image,(int(width*scale),int(height*scale)))
        self.rect = self.image.get_rect() #rect use to store and manipulate rectangular areas
        self.rect.topleft = (x,y) #set location top left to coordinate xy
        self.clicked = False

    def draw(self):
        action = False

        position = pygame.mouse.get_pos() #get mouse position

        if self.rect.collidepoint(position): 
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: #self.clicked is to prevent mutiple click(?)
               self.clicked = True
               action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False              

        screen.blit(self.image,(self.rect.x,self.rect.y)) #draw button on screen 

        return action  

start_button = Button(100,10,start_img,0.35)
load_button = Button(100,200,load_img,0.35)
#collections_button = Button(100,360,collections_button,0.35)
settings_button = Button(100,560,settings_img,0.35)
exit_button = Button(100,750,exit_img,0.35)

#game loop
run = True
while run: #keep window running

    screen.blit(bg_img, (0, 0)) #draw backgound from (0,0)
   
    start_button.draw()
        
    load_button.draw()
    #collections_button.draw()
    settings_button.draw()
    if exit_button.draw():
        run = False

    for event in pygame.event.get(): #handle event like mouse click, keyboard press
        if event.type == pygame.QUIT: #if press x on right above will quit
            run = False

    pygame.display.flip() #to display image blit

pygame.quit()

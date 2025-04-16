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

bg_img = pygame.image.load("Mind Scape Chamber Title Screen (1).png").convert()

bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))

running = True
while running: #keep window running
    for event in pygame.event.get(): #handle event like mouse click, keyboard press
        if event.type == pygame.QUIT: #if press x on right above will quit
            running = False

    screen.blit(bg_img, (0, 0)) #draw backgound from (0,0)
    pygame.display.flip() #to display image blit

pygame.quit()

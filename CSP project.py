import pygame
from pygame.locals import *
pygame.init()

#Game loop begins
while True:
    #Code
    #More Code
    #
    #
    pygame.display.update()

#End game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
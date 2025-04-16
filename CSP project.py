import pygame, sys
from random import randint

#create class for obstacle sprite, and player sprite

pygame.init()
screen = pygame.display.set_mode((1280,720))
#To show on white bar above, we'll be in fullscreen so may not be needed
#   pygame.display.set_caption('Game_name or what have you')
clock = pygame.time.Clock() #limit game frame rate

#set up
#sprite group?

#Game loop begins
while True:
    # to End game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    #all our code goes here
    #drawn elements and updates
    pygame.display.update()
    clock.tick(60)





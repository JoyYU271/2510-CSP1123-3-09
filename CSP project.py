import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Target line connect')
clock = pygame.time.Clock()

background = pygame.image.load('minigame 2.png')

#player (line) class/code?

#CameraGroup class to move the image down. Instead of being controlled by movement, it's a bit of cutscene/automatic

#mask, to indicate correct 'target'

#outline, indicate moving aim

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(background, (0,0))

    pygame.display.update()
    clock.tick(60)
import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Target line connect')
clock = pygame.time.Clock()

background = pygame.image.load('minigame 2.png')

#player (line) class/code?
#   line_start = need to find
# pos = pygame.mouse.get_pos()  <-- need this in game loop
# pygame.draw.line(screen, color, line_start, line_end)  <-- this too

#CameraGroup class to move the image down. Instead of being controlled by movement, it's a bit of cutscene/automatic
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    # def draw(self,screen):
    #         screen.blit(background) used to draw player so we focus on them. I have no focus except screen... unless?

        #box setup (trying to go straight into it and fix holes as I go)
        self.camera_borders = {'left': 0, 'right': 400, 'top': 0, 'bottom': 800} #technically my camera borders are the screen itself... Woah wait what if replace code for borders with screen?
        #self.camera_rect = pygame.Rect()


    def draw_camera(self):
        pygame.draw.rect(self.display_surface, 'yellow', self.camera_rect, 5)
#mask, to indicate correct 'target'

#outline, indicate moving aim

camera_group = CameraGroup()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(background, (0,0))

    camera_group.draw_camera(screen)
    pygame.display.update()
    clock.tick(60)
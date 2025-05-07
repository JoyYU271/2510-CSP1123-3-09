import pygame
import random

pygame.init()

#game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Drag and Drop')

# active_box = None   #to check clicked or not...?
# boxes = []
# for i in range(5):  #repeat this whole thing 5 times (for 5 boxes)
#     x = random.randint(50,700)
#     y = random.randint(50, 350)
#     w = random.randint(35,65)
#     h = random.randint(35, 65)
#     box = pygame.Rect(x,y,w,h)
#     boxes.append(box)

#create object
binder1 = pygame.image.load("minigame 1/binder_clip(small).png").convert_alpha()
binder1_rect = binder1.get_rect()
binder1_mask = pygame.mask.from_surface(binder1)
mask_image = binder1_mask.to_surface()

run = True
while run:

    screen.fill('turquoise1')

    #draw mask image
    screen.blit(mask_image,(0,0))
    # pygame.draw.rect(screen, 'turqoise1',binder1)

    # #update and draw boxes
    # for box in boxes:
    #    pygame.draw.rect(screen, 'purple', box) 

    for event in pygame.event.get():
    #     if event.type == pygame.MOUSEBUTTONDOWN:
    #         if event.button == 1:   #1 = left most button on mouse...?
    #             for num, box in enumerate(boxes):
    #                 if box.collidepoint(event.pos):  #checking for each box if collide with mouse pointer
    #                     active_box = num             #event.pos is mouse position, but need variable to check which box mouse is over

        # if event.type == pygame.MOUSEBUTTONUP:
        #     if event.button == 1:
        #         active_box = None

        # if event.type == pygame.MOUSEMOTION:
        #     if active_box != None:   #check box is being clicked on
        #         boxes[active_box].move_ip(event.rel)    #event.rel comes from pygame.MOUSEMOTION and shows the exact position of mouse pointer

        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()
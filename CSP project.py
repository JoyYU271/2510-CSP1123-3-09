import pygame
#import random

pygame.init()

#game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Drag and Drop')

class DraggableObjects:
    def __init__(self, image_path, pos):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_surf = self.mask

        self.target_position = (100, 100)  # the fixed "hole" position
        
        #how to assign different target pos to each object, maybe list?


        #for dragging
        self.dragging = False   #basically my acitve_object but made relevant to the class
        self.mouse_offset = (0,0)

        self.mask_surf = self.mask.to_surface()
        self.mask_surf.set_colorkey((0,0,0))

        for x in range(self.mask_surf.get_width()):
            for y in range(self.mask_surf.get_height()):
                if self.mask_surf.get_at((x, y))[0] != 0:
                    self.mask_surf.set_at((x, y), pygame.Color("gray18"))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.mouse_offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

                offset_x = self.rect.x - self.target_position[0]
                offset_y = self.rect.y - self.target_position[1]
                overlap = self.mask.overlap(self.mask, (offset_x, offset_y))
                if overlap:
                    self.rect.topleft = self.target_position  # snap it to perfect alignment

        elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.rect.topleft = (event.pos[0] - self.mouse_offset[0], event.pos[1] - self.mouse_offset[1])

    def draw_target_slot(self, screen, offset=3):
        screen.blit(self.mask_surf, self.target_position)

        for dx in [-offset, 0, offset]:
            for dy in [-offset, 0, offset]:
                if dx != 0 or dy != 0:
                    screen.blit(self.mask_surf, (self.target_position[0] + dx, self.target_position[1] + dy))


    def draw(self, screen):
        screen.blit(self.image,self.rect)

# #create object
# binder1 = pygame.image.load("minigame 1/binder_clip(small).png").convert_alpha()
# binder1_rect = binder1.get_rect(topleft=(200, 100))
# # binder1_pos
# binder1_mask = pygame.mask.from_surface(binder1)

# active_object = None

# #mask -> surface
# mask_image = binder1_mask.to_surface()
# mask_image.set_colorkey((0,0,0))    #to hide black pixels

# #fill surface with color (screen.fill would fill hidden pixels as well)
# surf_w,surf_h = mask_image.get_size()
# for x in range(surf_w):
#     for y in range(surf_h):
#         if mask_image.get_at((x,y))[0] != 0:
#             mask_image.set_at((x,y), 'gray18')

binderClip = DraggableObjects("minigame 1/binder_clip(small).png", (200, 100))
BinderClip = DraggableObjects("minigame 1/binder_clip(tall).png", (300,300))


run = True
while run:
    #complex way for outline (but what if without the main image covering it?)
    # offset = 3
    # screen.blit(mask_image,(binder1_rect[0] + offset, binder1_rect[1])) #right
    # screen.blit(mask_image,(binder1_rect[0] - offset, binder1_rect[1])) #left
    # screen.blit(mask_image,(binder1_rect[0], binder1_rect[1] + offset)) #bottom
    # screen.blit(mask_image,(binder1_rect[0], binder1_rect[1] - offset)) #top
    # screen.blit(mask_image,(binder1_rect[0] + offset, binder1_rect[1] - offset)) #topright
    # screen.blit(mask_image,(binder1_rect[0] + offset, binder1_rect[1] + offset)) #bottomright
    # screen.blit(mask_image,(binder1_rect[0] - offset, binder1_rect[1] + offset)) #topleft
    # screen.blit(mask_image,(binder1_rect[0] - offset, binder1_rect[1] - offset)) #bottomleft

    # target_position = (100, 100)  # the fixed "hole" position
    # for dx in [-offset, 0, offset]:
    #     for dy in [-offset, 0, offset]:
    #         if dx != 0 or dy != 0:
    #             screen.blit(mask_image, (target_position[0] + dx, target_position[1] + dy))

    # #draw object image
    # screen.blit(binder1, binder1_rect)
    # pygame.draw.rect(screen, 'turqoise1',binder1)

    #update and draw boxes
    # for box in boxes:
    #    pygame.draw.rect(screen, 'purple', box) 

    for event in pygame.event.get():
        binderClip.handle_event(event)
        BinderClip.handle_event(event)

    #     if event.type == pygame.MOUSEBUTTONDOWN:
    #         if event.button == 1:   # 1 = left most button on mouse...?
    # #            for num, box in enumerate(boxes):  
    #             if binder1_rect.collidepoint(event.pos):     #binder1 no attribute to collidepoint XP
    #                 active_object = binder1_rect   # ?
    #                 mouse_offset = (event.pos[0] - binder1_rect.x, event.pos[1] - binder1_rect.y) #so the object doesn't move its top left of mouse pointer
    # #                 if box.collidepoint(event.pos):  #checking for each box if collide with mouse pointer
    # #                     active_box = num             #event.pos is mouse position, but need variable to check which box mouse is over

    #     if event.type == pygame.MOUSEBUTTONUP:
    #         if event.button == 1:
    #     #         active_box = None
    #             active_object = None
    #         #if binder1_rect.colliderect(pygame.Rect(target_position, binder1.get_size())):
    #                 #print("Object is over the hole!")
    #         offset_x = binder1_rect.x - target_position[0]
    #         offset_y = binder1_rect.y - target_position[1]
    #         overlap = binder1_mask.overlap(binder1_mask, (offset_x, offset_y))
    #         if overlap:
    #             binder1_rect.topleft = target_position  # snap it to perfect alignment

                    
    # maybe snap into place or check mask overlap

        # if event.type == pygame.MOUSEMOTION:
        # #     if active_box != None:   #check box is being clicked on
        # #         boxes[active_box].move_ip(event.rel)    #event.rel comes from pygame.MOUSEMOTION and shows the exact position of mouse pointer
        #     if active_object != None:
        #         binder1_rect.topleft = (event.pos[0] - mouse_offset[0], event.pos[1] - mouse_offset[1])

        if event.type == pygame.QUIT:
            run = False
    
    screen.fill('turquoise1')

    binderClip.draw_target_slot(screen)
    binderClip.draw(screen)

    BinderClip.draw_target_slot(screen)
    BinderClip.draw(screen)
    pygame.display.update()

pygame.quit()
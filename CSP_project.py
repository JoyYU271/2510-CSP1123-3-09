import pygame
#import random

pygame.init()

#game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Drag and Drop')

class DraggableObjects:
    def __init__(self, image_path, start_pos, target_pos):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.original_image = self.image.copy()  #keep original
        self.dark_image = self.create_darkened_image(self.image)
        self.rect = self.image.get_rect(topleft=start_pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.original_pos = start_pos

        self.target_position = target_pos  # the fixed "hole" position
        self.mask_surf = self.mask
        self.placed = False     #true if snappped into hole
        
        #for dragging
        self.dragging = False   #basically my acitve_object but made relevant to the class
        self.mouse_offset = (0,0)

        self.mask_surf = self.mask.to_surface()
        self.mask_surf.set_colorkey((0,0,0))

        for x in range(self.mask_surf.get_width()):
            for y in range(self.mask_surf.get_height()):
                if self.mask_surf.get_at((x, y))[0] != 0:
                    self.mask_surf.set_at((x, y), pygame.Color("gray18"))

    def handle_event(self):     #, event, active_obj_ref
        if self.placed:
            return

    def reset(self):
        self.rect.topleft = self.original_pos
        self.dragging = False
        self.placed = False

    def draw_target_slot(self, screen, offset=3):
        screen.blit(self.mask_surf, self.target_position)

        for dx in [-offset, 0, offset]:
            for dy in [-offset, 0, offset]:
                if dx != 0 or dy != 0:
                    screen.blit(self.mask_surf, (self.target_position[0] + dx, self.target_position[1] + dy))


    def draw(self, screen, is_selected=False):

        key_hint_font = pygame.font.SysFont('Comic Sans MS', 20)
        key_hint_text1 = key_hint_font.render("Press A/D to move Left and Right, W/S tp move Up and Down",True,(0,0,0))
        key_hint_text2 = key_hint_font.render("Press TAB to interchange the Clip AND Space to fill the hole with the correct Clip",True,(0,0,0))
    
        screen.blit(key_hint_text1,(20,20))
        screen.blit(key_hint_text2,(20,50))
        
        if is_selected:
            pygame.draw.rect(screen, 'gold', self.rect.inflate(4, 4), 2)
        if self.placed:
            screen.blit(self.dark_image, self.rect)
        else:
            screen.blit(self.image,self.rect)

    def create_darkened_image(self, surface):
        darkened = surface.copy()
        darkened.fill((0,0,0,100), special_flags=pygame.BLEND_RGBA_SUB)
        return darkened
    


objects = [DraggableObjects("minigame 1/binder_clip(small).png", (100, 100), (200, 100)), 
           DraggableObjects("minigame 1/binder_clip(tall).png", (300,290), (600, 250))]

selected_object_index = 0

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            #to reset the game
            if event.key == pygame.K_z:
                for obj in objects:
                    obj.reset()
                selected_object_index = 0
    
            if event.key == pygame.K_TAB:
                selected_object_index = (selected_object_index + 1) % len(objects)

            #Try to 'drop' with SPACE
            if event.key == pygame.K_SPACE:
                obj = objects[selected_object_index]
                offset_x = obj.rect.x - obj.target_position[0]
                offset_y = obj.rect.y - obj.target_position[1]
                if obj.mask.overlap(obj.mask, (offset_x, offset_y)):
                    obj.rect.topleft = obj.target_position
                    obj.placed = True

        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    obj = objects[selected_object_index]

    #Movement keys (WASD or Arrows)
    if not obj.placed:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            obj.rect.x -= 2
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            obj.rect.x += 2
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            obj.rect.y -= 2
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            obj.rect.y += 2    

    screen.fill('turquoise1')

    #draw all target holes first
    for obj in objects:
        obj.draw_target_slot(screen)

    #draw draggable objects
    for obj in objects:
        obj.draw(screen)

    for i, obj in enumerate(objects):
        obj.draw(screen, is_selected=(i == selected_object_index))

    pygame.display.update()

pygame.quit()
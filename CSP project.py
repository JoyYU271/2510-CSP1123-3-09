import pygame
import sys
import json

# Load object data
with open("objects.json", "r") as f:
    object_data = json.load(f)

# Init
pygame.init()
clock = pygame.time.Clock()
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
world_width = 2488
world_height = 720
pygame.display.set_caption("Doctor Test")

#Camera class
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        
        #camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        #box camera 
        self.camera_borders = {'left':200, 'right':200, 'top':100, 'bottom':100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l,t,w,h)

        #background
        self.ground_surf = pygame.image.load('picture/Maps/Map clinic.png').convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(topleft = (0,0))

    def center_target_camera(self,target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def box_target_camera(self,target):

        if target.rect.left < self.camera_rect.left:
           self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
           self.camera_rect.right = target.rect.right 

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

         # Clamp offset to world bounds
        self.offset.x = max(0, min(self.offset.x, world_width - self.display_surface.get_width()))
        self.offset.y = max(0, min(self.offset.y, world_height - self.display_surface.get_height()))

    def custom_draw(self,player):

        #self.center_target_camera(player)
        self.box_target_camera(player)

        #ground
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surf,ground_offset)

        #player?
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            flipped_image = pygame.transform.flip(sprite.image, sprite.flip, False)
            self.display_surface.blit(flipped_image, offset_pos)

# Doctor class
class Doctor(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.stand_img = pygame.image.load('picture/Character QQ/Doctor idle.png').convert_alpha()
        self.image = self.stand_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed
        self.flip = False
        self.direction = 1
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        for i in range(1, 5):
            walk_img = pygame.image.load(f'picture/Doctor Walking/walk {i}.png').convert_alpha()
            self.animation_list.append(walk_img)

    def move(self):
        keys = pygame.key.get_pressed()
        dx = 0
        moving = False

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
            self.flip = True
            self.direction = -1
            moving = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
            self.flip = False
            self.direction = 1
            moving = True

        self.rect.x += dx

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > world_width:
            self.rect.right = world_width

        return moving

    def update_animation(self, moving):
        if moving:
            ANIMATION_COOLDOWN = 150
            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.animation_list):
                    self.frame_index = 0
            self.image = self.animation_list[self.frame_index]
        else:
            self.image = self.stand_img

    def update(self):
        is_moving = self.move()
        self.update_animation(is_moving)

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
       super().__init__()
       self.image = pygame.image.load('table.png').convert_alpha()
       self.rect = self.image.get_rect()
       self.rect.topleft = (x, y) #set position here
       self.flip = False #so CameraGroup won't flip items with player

    def draw(self, screen):
       screen.blit(self.image,self.rect)

class InteractableObject:
    def __init__(self, name, rect, dialogue_id, start_node, active=True):
        self.name = name
        self.rect = rect
        self.dialogue_id = dialogue_id
        self.start_node = start_node
        self.active = active

#class UIElement:
    #def __init__(self, image_path, base_pos):
    #    self.original_image = pygame.image.load(image_path).convert_alpha()
    #    self.base_pos = base_pos  # Position in original 800x600
    #    self.scaled_image = self.original_image
    #    self.pos = base_pos

    #def update(self, scale_x, scale_y):
     #   w = int(self.original_image.get_width() * scale_x)
     #   h = int(self.original_image.get_height() * scale_y)
     #   self.scaled_image = pygame.transform.scale(self.original_image, (w, h))
     #   self.pos = (int(self.base_pos[0] * scale_x), int(self.base_pos[1] * scale_y))

    #def draw(self, surface):
     #   surface.blit(self.scaled_image, self.pos)



# Init camera group
camera_group = CameraGroup()

#Init objects?
object_interaction = Item(813, 397)
camera_group.add(object_interaction)

# Create player and add to camera group
player = Doctor(x=400, y=550, speed=4.5)
camera_group.add(player)

interactable_objects = []

for obj_id, obj_info in object_data.items():
    pos = obj_info["position"]
    size = obj_info["size"]
    rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
    
    obj = InteractableObject(
        name=obj_info["name"],
        rect=rect,
        dialogue_id=obj_info["dialogue_id"],
        start_node=obj_info["start_node"],
        active=obj_info.get("active", True)
    )
    
    interactable_objects.append(obj)

# Game loop
run = True
while run:
    screen.fill((100, 100, 255))  # sky blue background

    # Event check (for ESC / quit)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.w, event.h
            # Optional: tell the camera group about the new size
            camera_group.display_surface = screen
            camera_group.half_w = screen_width // 2
            camera_group.half_h = screen_height // 2 
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for obj in interactable_objects:
                if obj.rect.collidepoint(mouse_pos) and obj.active:
                    current_dialogue = dialogue_data[obj.dialogue_id][obj.start_node]
                    dialogue_index = 0
                    show_dialogue = True
                    break

    # Update player
    player.update()

    # Camera draw handles background + all sprites
    camera_group.custom_draw(player)

    # Update item/object?
    #object_interaction.draw(screen)

    # Update display
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()

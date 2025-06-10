# shared.py
import pygame

camera_group = None
screen = None

class CameraGroup(pygame.sprite.Group):
    def __init__(self, player, npc_manager, screen):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        
        self.player = player
        self.npc_manager = npc_manager
        self.screen = screen

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        # box camera
        self.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l, t, w, h)

        self.background = None


        self.world_width = 2488
        self.world_height = 720

    def set_background(self, background):
        self.background = background

    def set_limits(self, width, height):
        self.world_width = width
        self.world_height = height

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

        #camera speed
        self.keyboard_speed = 5 

         # Clamp offset to world bounds
        self.offset.x = max(0, min(self.offset.x, self.world_width - self.display_surface.get_width()))
        self.offset.y = max(0, min(self.offset.y, self.world_height - self.display_surface.get_height()))

    # def keyboard_control(self):
    #     keys = pygame.key.get_pressed()
    #     if keys[pygame.K_a]:
    #         self.offset.x -= self.keyboard_speed
    #     if keys[pygame.K_d]:
    #         self.offset.x += self.keyboard_speed  

    def custom_draw(self,player):

        #self.keyboard_control() to manually move camera, can be for animation?

        #self.center_target_camera(player)
        self.box_target_camera(player)

        # draw background (adjust this to match your game's background)
        if self.background:
            offset_bg = pygame.Vector2(0,0) - self.offset
            self.display_surface.blit(self.background, offset_bg)

        #Draw characters after
        for sprite in sorted(self.sprites(), key=lambda spr: (spr.rect.centery, spr != player)):
            offset_pos = sprite.rect.topleft - self.offset
            flipped_image = pygame.transform.flip(sprite.image, sprite.flip, False)
            self.display_surface.blit(flipped_image, offset_pos)

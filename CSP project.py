import pygame
#from pygame.locals import *


pygame.init()
screen = pygame.display.set_mode((800,400))
#To show on white bar above, we'll be in fullscreen so may not be needed
#   pygame.display.set_caption('Game_name or what have you')
clock = pygame.time.Clock() #limit game frame rate
font_handwriting = pygame.font.Font('Projects/Python game/Morning Bright.otf')

fire_surface = pygame.image.load('Projects/Python game/pfp.png').convert_alpha()
ruins_surface = pygame.image.load('Projects/Python game/Ruins.png').convert()

surface_text = font_handwriting.render('My Game', True, 'Black')
text_rect = surface_text.get_rect(center = (160, 200))

collision_surface = pygame.Surface((50,25))
collision_surface.fill('Purple')

fire_y_post = 250

fire_rectg = fire_surface.get_rect(bottomleft = (130, 342))
collision_rectg = collision_surface.get_rect(topleft = (130,110))
    

#Game loop begins
while True:
    # to End game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    
    #blit means putting a surface on top of another surface
    screen.blit(ruins_surface,(0,0)) #origin is always at top left of display screen
   # fire_y_post -= 1
    if fire_y_post < 110: fire_y_post = 250 #I didn't know 'if' statements can just be 1 line
    fire_rectg.bottom -= 1  #so weird, .bottom works, but .midbottom gets a tuple, int error??
    screen.blit(fire_surface,fire_rectg)
   # print(ruins_rectg.midbottom)
    pygame.draw.rect(screen, 'Purple', text_rect,8) #draw part of pygame literally draws the rect, not stamp it or anything
    #hmm, to settle the probelm of the empty middle, it's either print twice, or increase the width until the space get's blocked out


    screen.blit(surface_text,text_rect)
    
    #if fire_rectg.colliderect(collision_rectg): #I think because it calls it here, I don't have to worry about the code not being in the game loop
        #print('collision')

    # was thinking if I should skip trying out collision since I don't have another image for this... until I remembered I can make rectangles
    # create rectangle but don't display, see if collision will still detect
    # It works :))

    pygame.display.update()
    clock.tick(60)





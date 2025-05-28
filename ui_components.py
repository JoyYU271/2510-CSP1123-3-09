import pygame

#get a font
def get_font(size):
    return pygame.font.Font(None, size) #None is use system default font

#button class
class Button():
    def __init__(self, image, pos, text_input="", font=None, base_color=(0, 0, 0), hovering_color=(0, 0, 0), scale=1.0):
        self.original_image = image
        if image is not None and scale != 1.0:
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            self.image = pygame.transform.scale(image, (width, height))
        else:
            self.image = image

        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font or get_font(30)
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)

        if self.image is None:
            self.image = self.text

        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos)) #detect clicks
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos)) 

    #update image and text on screen
    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    #determine is mouse on button area or not
    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColor(self, position):
        if self.checkForInput(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
    
    def draw(self, screen):
        self.update(screen)
        mouse_pos = pygame.mouse.get_pos()
        self.changeColor(mouse_pos)
        return self.checkForInput(mouse_pos)
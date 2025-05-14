import pygame
import ctypes
import sys

pygame.init()

# Get real screen resolution
ctypes.windll.user32.SetProcessDPIAware()
screen_width = ctypes.windll.user32.GetSystemMetrics(0)
screen_height = ctypes.windll.user32.GetSystemMetrics(1)

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("main page test")

bg_img = pygame.image.load("Mind Scape Chamber Title Screen (1).png").convert()
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))

# Button setup
button_color = (200, 200, 200)
button_hover_color = (170, 170, 170)
button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 100, 200, 50)
font = pygame.font.SysFont(None, 36)
button_text = font.render("Start", True, (0, 0, 0))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                print("Start button clicked!")  # Replace this with your page-switching logic

    screen.blit(bg_img, (0, 0))

    # Button drawing
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, button_hover_color, button_rect)
    else:
        pygame.draw.rect(screen, button_color, button_rect)

    screen.blit(button_text, button_text.get_rect(center=button_rect.center))

    pygame.display.flip()

pygame.quit()


import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Target line connect')
clock = pygame.time.Clock()

#player (line) class/code?
#   line_start = need to find
# pos = pygame.mouse.get_pos()  <-- need this in game loop
# pygame.draw.line(screen, color, line_start, line_end)  <-- this too

background = pygame.image.load('minigame 2.png')

# --- Game States ---
camera_offset_y = 0
cutscene_active = False
cutscene_speed = 2 #pixels per frame
next_targets_ready = False

# --- Player Setup ---
player_pos = pygame.Vector2(400, 300)
player_speed = 4
PLAYER_RADIUS = 10

# -- Target Setup ---
TARGET_RADIUS = 20
target_positions = [(300, 150), (500, 250), (400, 350)] #Place targets accordingly

def trigger_cutscene():
    global cutscene_active
    cutscene_active = True

def draw_targets():
    for x, y in target_positions:
        screen_x = x
        screen_y = y - camera_offset_y
        pygame.draw.circle(screen, 'red', (screen_x, screen_y), TARGET_RADIUS)

def draw_player():
    pygame.draw.circle(screen, 'cyan', (player_pos.x, player_pos.y), PLAYER_RADIUS)

def handle_target_hit():
    global target_positions
    for (x,y) in target_positions:
        dx = player_pos.x - x
        dy = player_pos.y + camera_offset_y - y #adjust for camera
        distance = (dx ** 2 + dy **2) ** 0.5
        if distance <= TARGET_RADIUS + PLAYER_RADIUS:
            target_positions.remove((x,y))
            break

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Player presses SPACE to 'hit'
        if event.type == pygame.KEYDOWN:
            if not cutscene_active:
                if event.key == pygame.K_SPACE:
                    handle_target_hit()

    # --- Handle Movement ---
    keys = pygame.key.get_pressed()
    if not cutscene_active:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_pos.x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_pos.x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_pos.y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_pos.y += player_speed

    # Clamp to screen bounds
    player_pos.x = max(PLAYER_RADIUS, min(800 - PLAYER_RADIUS, player_pos.x))
    player_pos.y = max(PLAYER_RADIUS, min(400 - PLAYER_RADIUS, player_pos.y))


    # --- Trigger Cutscene if all targets are hit ---
    if not cutscene_active and target_positions == []:
        trigger_cutscene()

    # --- Cutscene scrolling ---
    if cutscene_active:
        if camera_offset_y < 400:
            camera_offset_y += cutscene_speed
        else:
            cutscene_active = False
            next_targets_ready = True

    # --- Background + Camera ---
    screen.blit(background, (0, -camera_offset_y))

    # --- After cutscene: spawn new targets ---
    if not cutscene_active:
        #Update + draw targets
        if next_targets_ready:
            target_positions = [(250, 500), (550, 600), (400, 700)]
            next_targets_ready = False
        draw_targets()

    draw_player()
    
    pygame.display.update()
    clock.tick(60)
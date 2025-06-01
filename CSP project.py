import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Target line connect')
clock = pygame.time.Clock()

background = pygame.image.load('minigame 2.png')

# --- Player + Game Setup ---
AIM_WIDTH = 60
AIM_HEIGHT = 5

# --- Targets ---
target_positions = [(350, 70), (430, 150), (430, 250), (250, 350)] #Place targets accordingly
current_target_index = 0
HIT_TOLERANCE = 15  

# --- Aim Bar Setup (Oscillates vertically) ---
aim_bar_x = target_positions[0][0]
aim_y_min = target_positions[0][1] - 40
aim_y_max = target_positions[0][1] + 40
aim_y = aim_y_min
aim_direction = 1
aim_speed = 2

# --- Hit Line Storage ---
hit_points = [target_positions[0]]

# --- Game States ---
camera_offset_y = 0
cutscene_active = False
cutscene_speed = 2 #pixels per frame
next_targets_ready = False
targets_initialized = False

# Fade variables
fade_alpha = 0  # Start with no fade
fade_speed = 5  # How quickly the screen fades out
fade_in_progress = False  # Whether the fade is in progress
fade_complete = False  # Whether the fade-out is complete

def trigger_cutscene():
    global cutscene_active
    cutscene_active = True

def draw_targets():
    if cutscene_active or fade_in_progress:  # Skip drawing if cutscene or fade-out is active
        return
    for i, (x, y) in enumerate(target_positions):
        screen_x = x
        screen_y = y - camera_offset_y
        if i == current_target_index:
            pygame.draw.circle(screen, 'red', (screen_x, screen_y), 10)
        elif i < current_target_index:
            pygame.draw.circle(screen, 'green', (screen_x, screen_y), 10)

def draw_aim_bar():
    if cutscene_active or fade_in_progress:  # Skip drawing if cutscene or fade-out is active
        return
    pygame.draw.rect(screen, 'yellow', (aim_bar_x - AIM_WIDTH // 2, aim_y  - camera_offset_y, AIM_WIDTH, AIM_HEIGHT))

def draw_lines():
    if fade_in_progress:  # Skip drawing lines if fade-out is active
        return
    for i in range(len(hit_points) - 1):
        p1 = (hit_points[i][0], hit_points[i][1] - camera_offset_y)
        p2 = (hit_points[i + 1][0], hit_points[i + 1][1] - camera_offset_y)
        pygame.draw.line(screen, 'white', p1, p2, 3)

def reset_minigame():
    global target_positions, current_target_index, hit_points
    global aim_bar_x, aim_y, aim_y_min, aim_y_max, aim_direction
    global camera_offset_y, cutscene_active, next_targets_ready, targets_initialized
    global fade_alpha, fade_in_progress, fade_complete

    # Reset game state
    target_positions = [(350, 70), (430, 150), (430, 250), (250, 350)]
    current_target_index = 0
    hit_points = [target_positions[0]]

    aim_bar_x = target_positions[0][0]
    ty = target_positions[0][1]
    aim_y_min = ty - 40
    aim_y_max = ty + 40
    aim_y = aim_y_min
    aim_direction = 1

    camera_offset_y = 0
    cutscene_active = False
    next_targets_ready = False
    targets_initialized = False

    # Reset fade variables
    fade_alpha = 0
    fade_in_progress = False
    fade_complete = False

    print("Minigame reset.")

# Function to trigger the fade-out effect and reset the game
def fade_out_and_reset():
    global fade_alpha, fade_in_progress, fade_complete
    fade_in_progress = True
    fade_complete = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Player presses SPACE to 'hit'
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and not fade_in_progress:
                fade_out_and_reset()
            
            if not cutscene_active:
                if event.key == pygame.K_SPACE:
                    if current_target_index < len(target_positions):
                        tx, ty = target_positions[current_target_index]
                        adjusted_aim_y = aim_y - camera_offset_y if not next_targets_ready else aim_y
                        if abs(adjusted_aim_y - ty) <= HIT_TOLERANCE:
                            hit_points.append((tx, ty))
                            current_target_index += 1

                            # Setup next target *only if it exists*
                            if current_target_index < len(target_positions):
                                # Update aim bar range for next target
                                next_tx, next_ty = target_positions[current_target_index]
                                aim_bar_x = next_tx
                                aim_y_min = max(0, next_ty - 40)
                                aim_y_max = min(800, next_ty + 40)
                                aim_y = aim_y_min
                                aim_direction = 1

                        else:
                            print("Missed!")

    # --- Trigger Cutscene if all targets are hit ---
    if not cutscene_active and current_target_index >= len(target_positions):
        trigger_cutscene()

    # --- Cutscene scrolling ---
    if cutscene_active:
        if camera_offset_y < 400:
            camera_offset_y += cutscene_speed
        else:
            cutscene_active = False
            next_targets_ready = True

    # --- After cutscene: spawn new targets ---
    if not cutscene_active and next_targets_ready and not targets_initialized:
        target_positions = [(250, 450), (500, 550), (400, 700)]
        current_target_index = 0
        aim_bar_x = target_positions[0][0]
        next_ty = target_positions[0][1]
        aim_y_min = next_ty - 40
        aim_y_max = next_ty + 40
        aim_y = aim_y_min
        aim_direction = 1
        targets_initialized = True  # ✅ so it won't run again!

    #Move the aim bar up and down
    aim_y += aim_speed * aim_direction
    if aim_y >= aim_y_max or aim_y <= aim_y_min:
        aim_direction *= -1

    # --- Handle Fade Effect ---
    if fade_in_progress:
        fade_alpha += fade_speed  # Increase opacity
        if fade_alpha >= 255:  # When the fade is complete
            fade_alpha = 255
            fade_complete = True

    # --- Reset Minigame after Fade ---
    if fade_complete:
        reset_minigame()  # Reset game state
        fade_in_progress = False  # Stop fade-out

    # --- Drawing ---
    screen.blit(background, (0, -camera_offset_y))

    # Draw the fade effect (black screen with increasing opacity)
    if fade_in_progress:
        fade_surface = pygame.Surface((800, 400))
        fade_surface.fill((0, 0, 0))  # Fill the surface with black
        fade_surface.set_alpha(fade_alpha)  # Set the opacity
        screen.blit(fade_surface, (0, 0))  # Draw it over the screen

    draw_lines()
    draw_targets()
    draw_aim_bar()

    pygame.display.update()
    clock.tick(60)
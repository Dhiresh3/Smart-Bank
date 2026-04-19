import pygame
import sys
    
pygame.init()

WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
  
font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()

player_width, player_height = 50, 50
player_x, player_y = 100, HEIGHT - player_height - 20
player_jump = False
player_gravity = 0.5
player_velocity = 0

obstacle_width, obstacle_height = 30, 30
obstacle_x, obstacle_y = WIDTH, HEIGHT - obstacle_height - 20
obstacle_speed = 5

score = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_jump = True

    if player_jump:
        player_velocity = -10
        player_jump = False
    player_velocity += player_gravity
    player_y += player_velocity

    if player_y > HEIGHT - player_height - 20:
        player_y = HEIGHT - player_height - 20
        player_velocity = 0

    obstacle_x -= obstacle_speed
    if obstacle_x < -obstacle_width:
        obstacle_x = WIDTH
        score += 1

    if (obstacle_x < player_x + player_width and
        obstacle_x + obstacle_width > player_x and
        obstacle_y < player_y + player_height and
        obstacle_y + obstacle_height > player_y):
        print("Game Over")
        pygame.quit()
        sys.exit()

    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, (player_x, player_y, player_width, player_height))
    pygame.draw.rect(screen, GREEN, (obstacle_x, obstacle_y, obstacle_width, obstacle_height))
    text = font.render("Score: " + str(score), True, BLUE)
    screen.blit(text, (10, 10))

    pygame.display.flip()

    clock.tick(60)                         
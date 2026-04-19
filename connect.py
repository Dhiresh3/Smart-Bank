import pygame
import sys
import math

pygame.init()

WIDTH = 800
HEIGHT = 600
DOT_RADIUS = 20
LINE_WIDTH = 5

DOT_COLOR = (255, 0, 0)         # Normal dot color
ACTIVE_DOT_COLOR = (0, 255, 0)  # When a dot has been activated/visited
HOVER_DOT_COLOR = (0, 0, 255)   # When the mouse hovers over a dot
LINE_COLOR = (0, 0, 255)
BG_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect the Dots")
font = pygame.font.Font(None, 36)

dots = [
    {'x': 100, 'y': 100, 'number': 1, 'visited': False},
    {'x': 200, 'y': 200, 'number': 2, 'visited': False},
    {'x': 300, 'y': 100, 'number': 3, 'visited': False},
    {'x': 400, 'y': 200, 'number': 4, 'visited': False},
    {'x': 500, 'y': 100, 'number': 5, 'visited': False},
    {'x': 600, 'y': 200, 'number': 6, 'visited': False},
]

lines = []
current_dot = None

clock = pygame.time.Clock()

game_over = False
while not game_over:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for dot in dots:
                distance = math.hypot(event.pos[0] - dot['x'], event.pos[1] - dot['y'])
                if distance <= DOT_RADIUS:
                    if current_dot is None:
                        if dot['number'] == 1:
                            current_dot = dot
                            dot['visited'] = True
                    else:
                        if dot['number'] == current_dot['number'] + 1:
                            lines.append((current_dot, dot))
                            current_dot = dot
                            dot['visited'] = True
                    break  # Stop checking other dots once a valid hit is found

    screen.fill(BG_COLOR)
    
    for line in lines:
        pygame.draw.line(screen, LINE_COLOR, (line[0]['x'], line[0]['y']),
                         (line[1]['x'], line[1]['y']), LINE_WIDTH)
    
    for dot in dots:
        distance = math.hypot(mouse_pos[0] - dot['x'], mouse_pos[1] - dot['y'])
        is_hover = (distance <= DOT_RADIUS)
        color = DOT_COLOR

        if dot['visited']:
            color = ACTIVE_DOT_COLOR
        if is_hover:
            color = HOVER_DOT_COLOR
        
        pygame.draw.circle(screen, color, (dot['x'], dot['y']), DOT_RADIUS)
        
        text = font.render(str(dot['number']), True, (0, 0, 0))
        screen.blit(text, (dot['x'] - text.get_width() // 2, dot['y'] - text.get_height() // 2))
    
    if current_dot is not None and current_dot['number'] == len(dots):
        game_over = True

    pygame.display.flip()
    clock.tick(60)

screen.fill(BG_COLOR)
message = font.render("Game Over! All dots connected!", True, (0, 0, 0))
screen.blit(message, ((WIDTH - message.get_width()) // 2, (HEIGHT - message.get_height()) // 2))
pygame.display.flip()
pygame.time.delay(3000)

pygame.quit()
sys.exit()
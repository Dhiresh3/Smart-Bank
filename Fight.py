import pygame
import sys

WIDTH, HEIGHT = 1200, 720
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GROUND_Y = HEIGHT - 100 
# --- Player Controls Definition ---
P1_CONTROLS = {
    'left': pygame.K_a, 'right': pygame.K_d, 
    'jump': pygame.K_w, 'attack': pygame.K_s 
}

P2_CONTROLS = {
    'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 
    'jump': pygame.K_UP, 'attack': pygame.K_DOWN
}

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aether Clash: Phantom Fury")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)

# --- Character Class ---
class Fighter(pygame.sprite.Sprite):
    def __init__(self, x, color, controls):
        super().__init__()
        self.color = color
        self.controls = controls
        # Simple placeholder graphic
        self.image = pygame.Surface([50, 100])
        self.image.fill(self.color)
        self.rect = self.image.get_rect(midbottom=(x, GROUND_Y))
        
        # Stats & Scoreboard
        self.hp = 100
        self.score = 0
        
        # Physics and State
        self.vel_x = 0
        self.vel_y = 0
        self.is_jumping = False
        self.is_attacking = False
        self.is_hit = False

    def handle_input(self, keys):
        self.vel_x = 0
        
        # Movement
        if keys[self.controls['left']]:
            self.vel_x = -5
        if keys[self.controls['right']]:
            self.vel_x = 5
        
        # Jump
        if keys[self.controls['jump']] and not self.is_jumping:
            self.vel_y = -16 # Jump strength
            self.is_jumping = True

        # Attack
        if keys[self.controls['attack']] and not self.is_attacking:
            self.is_attacking = True

    def update(self):
        # Apply Gravity
        if self.rect.bottom < GROUND_Y or self.vel_y < 0:
            self.vel_y += 1 # Gravity
        
        # Apply Movement
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Boundary Check (keep on screen)
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        
        # Check Ground Collision
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.is_jumping = False
            self.vel_y = 0
        
        # Flash player when hit (visual feedback for the hit state)
        if self.is_hit:
            self.image.fill(WHITE) # Flash white when hit
            self.is_hit = False
        else:
            self.image.fill(self.color) # Normal color

    def draw_hp_bar(self, surface):
        bar_x = self.rect.x if self.color == RED else self.rect.x - 50
        
        # Draw HP Bar (simple visual for health)
        bar_width = self.hp * 0.5 # Scale HP (100 HP = 50px wide bar)
        pygame.draw.rect(surface, RED, (self.rect.centerx - 25, self.rect.y - 15, 50, 10), 1) # Outline
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.centerx - 25, self.rect.y - 15, bar_width, 10))

    def attack_check(self, target):
        if self.is_attacking:
            attack_rect = pygame.Rect(self.rect.right, self.rect.centery - 10, 30, 20)
            
            # Check for collision with the target
            if attack_rect.colliderect(target.rect):
                target.hp -= 10  # Damage
                target.is_hit = True
                
                # Simple knockback
                target.vel_x = 10 if self.rect.x < target.rect.x else -10
                target.vel_y = -5
            
            # Reset attack state immediately after check
            self.is_attacking = False
            
            
# --- Scoreboard Function ---
def draw_scoreboard(surface, p1, p2):
    # Player 1 Score
    p1_score_text = font.render(f"P1 WINS: {p1.score}", True, RED)
    surface.blit(p1_score_text, (50, 20))
    
    # Player 2 Score
    p2_score_text = font.render(f"P2 WINS: {p2.score}", True, BLUE)
    surface.blit(p2_score_text, (WIDTH - p2_score_text.get_width() - 50, 20))


# --- Game Setup ---
player1 = Fighter(WIDTH // 4, RED, P1_CONTROLS)
player2 = Fighter(WIDTH * 3 // 4, BLUE, P2_CONTROLS)
all_sprites = pygame.sprite.Group(player1, player2)

# --- Main Game Loop ---
def game_loop():
    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
        # 2. Input Handling
        keys = pygame.key.get_pressed()
        player1.handle_input(keys)
        player2.handle_input(keys)

        # 3. Game Logic Update
        all_sprites.update()
        
        # Combat Check
        player1.attack_check(player2)
        player2.attack_check(player1)
        
        # Round Reset Logic
        if player1.hp <= 0:
            player2.score += 1
            # Reset positions and health for new round
            player1.hp = 100
            player2.hp = 100
            player1.rect.midbottom = (WIDTH // 4, GROUND_Y)
            player2.rect.midbottom = (WIDTH * 3 // 4, GROUND_Y)
        
        if player2.hp <= 0:
            player1.score += 1
            # Reset positions and health for new round
            player1.hp = 100
            player2.hp = 100
            player1.rect.midbottom = (WIDTH // 4, GROUND_Y)
            player2.rect.midbottom = (WIDTH * 3 // 4, GROUND_Y)

        # 4. Drawing
        screen.fill(BLACK) # Background
        
        pygame.draw.line(screen, (50, 50, 50), (0, GROUND_Y), (WIDTH, GROUND_Y), 5) 
        
        all_sprites.draw(screen)
        player1.draw_hp_bar(screen)
        player2.draw_hp_bar(screen)

        draw_scoreboard(screen, player1, player2) 
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    game_loop()
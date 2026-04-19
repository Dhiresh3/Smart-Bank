# import pygame
# import random

# # Initialize Pygame
# pygame.init()

# # Set up some constants
# WIDTH, HEIGHT = 800, 600
# WHITE = (255, 255, 255)
# RED = (255, 0, 0)
# BLACK = (0, 0, 0)

# # Set up the display
# screen = pygame.display.set_mode((WIDTH, HEIGHT))

# # Set up the font
# font = pygame.font.Font(None, 36)

# # Set up the clock
# clock = pygame.time.Clock()

# # Set up the mouse
# mouse_width, mouse_height = 50, 50
# mouse_x, mouse_y = random.randint(0, WIDTH - mouse_width), random.randint(0, HEIGHT - mouse_height)

# # Set up the score
# score = 0

# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             mouse_pos = pygame.mouse.get_pos()
#             if (mouse_x < mouse_pos[0] < mouse_x + mouse_width and
#                 mouse_y < mouse_pos[1] < mouse_y + mouse_height):
#                 score += 1
#                 mouse_x, mouse_y = random.randint(0, WIDTH - mouse_width), random.randint(0, HEIGHT - mouse_height)

#     # Move the mouse
#     mouse_x += random.randint(-5, 5)
#     mouse_y += random.randint(-5, 5)

#     # Keep the mouse on the screen
#     if mouse_x < 0:
#         mouse_x = 0
#     elif mouse_x > WIDTH - mouse_width:
#         mouse_x = WIDTH - mouse_width
#     if mouse_y < 0:
#         mouse_y = 0
#     elif mouse_y > HEIGHT - mouse_height:
#         mouse_y = HEIGHT - mouse_height

#     # Draw everything
#     screen.fill(WHITE)
#     pygame.draw.rect(screen, RED, (mouse_x, mouse_y, mouse_width, mouse_height))
#     text = font.render("Score: " + str(score), True, BLACK)
#     screen.blit(text, (10, 10))

#     # Update the display
#     pygame.display.flip()

#     # Cap the frame rate
#     clock.tick(60)


import tkinter as tk
from random import randint
import time

class WhackAMouse:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Whack-A-Mouse")
        self.window.resizable(False, False)
        
        self.score = 0
        self.game_time = 30  
        self.active = False
        
        self.game_frame = tk.Frame(self.window, width=600, height=400, bg='lightgreen')
        self.game_frame.pack(padx=10, pady=10)
        
        self.score_label = tk.Label(self.window, text=f"Score: {self.score}", font=('Arial', 16))
        self.score_label.pack()
        self.timer_label = tk.Label(self.window, text=f"Time: {self.game_time}", font=('Arial', 16))
        self.timer_label.pack()
        
        self.start_button = tk.Button(self.window, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=10)
        
        self.holes = []
        self.create_holes()
        
        self.current_mouse = None
        
    def create_holes(self):
        for row in range(3):
            for col in range(3):
                hole = tk.Label(self.game_frame, text="O", font=('Arial', 24), width=2)
                hole.grid(row=row, column=col, padx=20, pady=20)
                hole.bind('<Button-1>', self.whack)
                self.holes.append(hole)
                
    def show_mouse(self):
        if self.active:
            if self.current_mouse:
                self.current_mouse.config(text="O", fg='black')
            
            self.current_mouse = self.holes[randint(0, 8)]
            self.current_mouse.config(text="🐭", fg='brown')
            
            self.window.after(1000, self.show_mouse)
    
    def whack(self, event):
        if self.active and event.widget == self.current_mouse:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.current_mouse.config(text="O", fg='black')
    
    def update_timer(self):
        if self.active and self.game_time > 0:
            self.game_time -= 1
            self.timer_label.config(text=f"Time: {self.game_time}")
            self.window.after(1000, self.update_timer)
        elif self.game_time <= 0:
            self.end_game()
    
    def start_game(self):
        self.active = True
        self.score = 0
        self.game_time = 30
        self.score_label.config(text=f"Score: {self.score}")
        self.timer_label.config(text=f"Time: {self.game_time}")
        self.start_button.config(state='disabled')
        self.show_mouse()
        self.update_timer()
    
    def end_game(self):
        self.active = False
        self.start_button.config(state='normal')
        if self.current_mouse:
            self.current_mouse.config(text="O", fg='black')
        tk.messagebox.showinfo("Game Over", f"Final Score: {self.score}")
    
    def run(self):
        self.window.mainloop()

game = WhackAMouse()
game.run()
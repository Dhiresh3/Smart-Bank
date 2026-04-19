# import pygame
# import sys

# # Initialize Pygame
# pygame.init()

# # Set up some constants
# WIDTH = 600
# HEIGHT = 600
# LINE_WIDTH = 15
# WIN_LINE_WIDTH = 15
# BOARD_ROWS = 3
# BOARD_COLS = 3
# SQUARE_SIZE = 200
# CIRCLE_RADIUS = 60
# CIRCLE_WIDTH = 15
# CROSS_WIDTH = 25
# SPACE = 55
# # RGB
# RED = (255, 0, 0)
# BG_COLOR = (28, 170, 156)
# LINE_COLOR = (23, 145, 135)
# CIRCLE_COLOR = (239, 231, 200)
# CROSS_COLOR = (66, 66, 66)

# # Set up the display
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption('TIC TAC TOE')
# screen.fill(BG_COLOR)

# # Board
# board = [[None]*BOARD_COLS for _ in range(BOARD_ROWS)]

# # Pygame Clock
# clock = pygame.time.Clock()

# def draw_lines():
#     # 1st horizontal
#     pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
#     # 2nd horizontal
#     pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)

#     # 1st vertical
#     pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
#     # 2nd vertical
#     pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

# def draw_figures():
#     for row in range(BOARD_ROWS):
#         for col in range(BOARD_COLS):
#             if board[row][col] == 'X':
#                 pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)  
#                 pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)
#             elif board[row][col] == 'O':
#                 pygame.draw.circle(screen, CIRCLE_COLOR, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), CIRCLE_RADIUS, CIRCLE_WIDTH)

# def mark_square(row, col, player):
#     board[row][col] = player

# def available_square(row, col):
#     return board[row][col] is None

# def is_board_full():
#     for row in range(BOARD_ROWS):
#         for col in range(BOARD_COLS):
#             if board[row][col] is None:
#                 return False
#     return True

# def check_win(player):
#     # vertical win check
#     for col in range(BOARD_COLS):
#         if board[0][col] == player and board[1][col] == player and board[2][col] == player:
#             return True

#     # horizontal win check
#     for row in range(BOARD_ROWS):
#         if board[row][0] == player and board[row][1] == player and board[row][2] == player:
#             return True

#     if board[2][0] == player and board[1][1] == player and board[0][2] == player:
#         return True

#     if board[0][0] == player and board[1][1] == player and board[2][2] == player:
#         return True

#     return False

# def restart():
#     screen.fill(BG_COLOR)
#     draw_lines()
#     player = 'X'
#     for row in range(BOARD_ROWS):
#         for col in range(BOARD_COLS):
#             board[row][col] = None
#     return player

# def main():
#     player = 'X'
#     draw_lines()

    
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 sys.exit()

#             if event.type == pygame.MOUSEBUTTONDOWN and not is_board_full():
#                 mouseX = event.pos[0] 
# #                 mouseY = event.pos[1] 

# #                 clicked_row = int(mouseY // SQUARE_SIZE)
# #                 clicked_col = int(mouseX // SQUARE_SIZE)

# import pygame
# import sys

# # Initialize Pygame
# pygame.init()

# # Set up some constants
# WIDTH = 600
# HEIGHT = 600
# LINE_WIDTH = 15
# WIN_LINE_WIDTH = 15
# BOARD_ROWS = 3
# BOARD_COLS = 3
# SQUARE_SIZE = 200
# CIRCLE_RADIUS = 60
# CIRCLE_WIDTH = 15
# CROSS_WIDTH = 25
# SPACE = 55
# # RGB
# RED = (255, 0, 0)
# BG_COLOR = (28, 170, 156)
# LINE_COLOR = (23, 145, 135)
# CIRCLE_COLOR = (239, 231, 200)
# CROSS_COLOR = (66, 66, 66)

# # Set up the display
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption('TIC TAC TOE')
# screen.fill(BG_COLOR)

# # Board
# board = [[None]*BOARD_COLS for _ in range(BOARD_ROWS)]

# # Pygame Clock
# clock = pygame.time.Clock()

# def draw_lines():
#     # 1st horizontal
#     pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
#     # 2nd horizontal
#     pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)

#     # 1st vertical
#     pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
#     # 2nd vertical
#     pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

# def draw_figures():
#     for row in range(BOARD_ROWS):
#         for col in range(BOARD_COLS):
#             if board[row][col] == 'X':
#                 pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)  
#                 pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)
#             elif board[row][col] == 'O':
#                 pygame.draw.circle(screen, CIRCLE_COLOR, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), CIRCLE_RADIUS, CIRCLE_WIDTH)

# def mark_square(row, col, player):
#     board[row][col] = player

# def available_square(row, col):
#     return board[row][col] is None

# def is_board_full():
#     for row in range(BOARD_ROWS):
#         for col in range(BOARD_COLS):
#             if board[row][col] is None:
#                 return False
#     return True

# def check_win(player):
#     # vertical win check
#     for col in range(BOARD_COLS):
#         if board[0][col] == player and board[1][col] == player and board[2][col] == player:
#             return True

#     # horizontal win check
#     for row in range(BOARD_ROWS):
#         if board[row][0] == player and board[row][1] == player and board[row][2] == player:
#             return True

#     if board[2][0] == player and board[1][1] == player and board[0][2] == player:
#         return True

#     if board[0][0] == player and board[1][1] == player and board[2][2] == player:
#         return True

#     return False

# def restart():
#     screen.fill(BG_COLOR)
#     draw_lines()
#     for row in range(BOARD_ROWS):
#         for col in range(BOARD_COLS):
#             board[row][col] = None

# def main():
#     player = 'X'
#     draw_lines()
    
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 sys.exit()

#             if event.type == pygame.MOUSEBUTTONDOWN and not is_board_full():
#                 mouseX = event.pos[0] 
#                 mouseY = event.pos[1] 

#                 clicked_row = int(mouseY // SQUARE_SIZE)
#                 clicked_col = int(mouseX // SQUARE_SIZE)

#                 if available_square(clicked_row, clicked_col):
#                     mark_square(clicked_row, clicked_col, player)
#                     if check_win(player):
#                         print(f"Player {player} wins!")
#                         pygame.time.wait(2000)
#                         restart()

#                     player = 'O' if player == 'X' else 'X'

#         draw_figures()
#         pygame.display.update()

# if __name__ == "__main__":
#     main()

import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 600
HEIGHT = 600
LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 4
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = 55
RED = (255, 0, 0)
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe with AI')
screen.fill(BG_COLOR)

# Board
board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

def draw_lines():
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 'X':
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), 
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), 
                                 (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)
            elif board[row][col] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR, 
                                   (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), CIRCLE_RADIUS, CIRCLE_WIDTH)

def mark_square(row, col, player):
    board[row][col] = player

def available_square(row, col):
    return board[row][col] is None

def random_move():
    available_moves = [(row, col) for row in range(BOARD_ROWS) for col in range(BOARD_COLS) if board[row][col] is None]
    return random.choice(available_moves) if available_moves else None

def is_board_full():
    return all(board[row][col] is not None for row in range(BOARD_ROWS) for col in range(BOARD_COLS))

def check_win(player):
    for row in range(BOARD_ROWS):
        if all(board[row][col] == player for col in range(BOARD_COLS)):
            return True
    for col in range(BOARD_COLS):
        if all(board[row][col] == player for row in range(BOARD_ROWS)):
            return True
    if all(board[i][i] == player for i in range(BOARD_ROWS)) or all(board[i][BOARD_ROWS - i - 1] == player for i in range(BOARD_ROWS)):
        return True
    return False

def restart():
    global board
    board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    screen.fill(BG_COLOR)
    draw_lines()

def draw_restart_button():
    font = pygame.font.Font(None, 40)
    text = font.render("Restart", True, RED)
    button_rect = pygame.Rect(WIDTH // 2 - 70, HEIGHT - 50, 140, 40)
    pygame.draw.rect(screen, BG_COLOR, button_rect)
    screen.blit(text, (WIDTH // 2 - 60, HEIGHT - 45))
    return button_rect

def main():
    player = 'X'
    bot = 'O'
    draw_lines()
    restart_button_rect = draw_restart_button()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    restart()

                if player == 'X':
                    mouseX, mouseY = event.pos
                    clicked_row, clicked_col = mouseY // SQUARE_SIZE, mouseX // SQUARE_SIZE

                    if available_square(clicked_row, clicked_col):
                        mark_square(clicked_row, clicked_col, player)
                        if check_win(player):
                            print("Player X wins!")
                            pygame.time.wait(2000)
                            restart()
                        player = bot

        # Bot's turn
        if player == bot and not is_board_full():
            move = random_move()
            if move:
                mark_square(*move, bot)
                if check_win(bot):
                    print("Bot wins!")
                    pygame.time.wait(2000)
                    restart()
                player = 'X'

        draw_figures()
        pygame.display.update()

if __name__ == "__main__":
    main()
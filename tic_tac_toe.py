import cv2
import numpy as np
import mediapipe as mp

# Initialize board
board = [['' for _ in range(3)] for _ in range(3)]

# Draw the board
def draw_board(img, board):
    h, w, _ = img.shape
    cell_w, cell_h = w // 3, h // 3

    for i in range(1, 3):
        cv2.line(img, (0, i * cell_h), (w, i * cell_h), (255, 255, 255), 2)
        cv2.line(img, (i * cell_w, 0), (i * cell_w, h), (255, 255, 255), 2)

    for row in range(3):
        for col in range(3):
            mark = board[row][col]
            if mark:
                center_x = col * cell_w + cell_w // 2
                center_y = row * cell_h + cell_h // 2
                cv2.putText(img, mark, (center_x - 30, center_y + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

# Check for win
def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] != '':
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != '':
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != '':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != '':
        return board[0][2]
    return None

# Real gesture input using MediaPipe
def gesture_input():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    result = None

    while True:
        success, img = cap.read()
        if not success:
            continue

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        h, w, _ = img.shape
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                index_finger_tip = handLms.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                x_px = int(index_finger_tip.x * w)
                y_px = int(index_finger_tip.y * h)

                # Draw fingertip
                cv2.circle(img, (x_px, y_px), 10, (0, 0, 255), -1)

                # Map to grid cell
                cell_w, cell_h = w // 3, h // 3
                col = x_px // cell_w
                row = y_px // cell_h

                result = (row, col)
                break

        draw_board(img, board)
        cv2.imshow("Gesture Input", img)

        key = cv2.waitKey(1)
        if key == ord('s') and result is not None: 
            break
        elif key == ord('q'):
            result = None
            break

    cap.release()
    cv2.destroyAllWindows()
    return result

def play_game():
    current_player = 'X'
    while True:
        print(f"Player {current_player}'s turn. Show your finger and press 's' to select a cell...")
        result = gesture_input()
        if result is None:
            print("No gesture detected. Try again.")
            continue

        row, col = result
        if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == '':
            board[row][col] = current_player
            winner = check_winner(board)
            if winner:
                print(f"Player {winner} wins!")
                break
            elif all(cell != '' for row in board for cell in row):
                print("It's a draw!")
                break
            current_player = 'O' if current_player == 'X' else 'X'
        else:
            print("Invalid or taken cell. Try again.")

        img = np.zeros((480, 480, 3), dtype=np.uint8)
        draw_board(img, board)
        cv2.imshow("Tic Tac Toe", img)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    play_game()
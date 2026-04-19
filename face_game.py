import cv2
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils


cap = cv2.VideoCapture(0)

last_gesture = None
last_trigger_time = 0
cooldown = 0.6  

print("Starting in 3 seconds... Click into your game window!")
time.sleep(3)

def get_finger_states(landmarks):
    fingers = []

    if landmarks[4].x < landmarks[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        if landmarks[tip].y < landmarks[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def detect_gesture(fingers):
    if fingers == [0, 0, 0, 0, 0]:
        return "down"   # ✊ Fist
    elif fingers == [1, 1, 1, 1, 1]:
        return "up"     # ✋ Open palm
    elif fingers == [0, 1, 0, 0, 0]:
        return "left"   # 👉 Index only
    elif fingers == [1, 0, 0, 0, 0]:
        return "right"  # 👈 Thumb only
    else:
        return "none"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)
    h, w, _ = frame.shape

    gesture = "none"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = hand_landmarks.landmark
            fingers = get_finger_states(landmarks)
            gesture = detect_gesture(fingers)

            if gesture != last_gesture and gesture != "none" and (time.time() - last_trigger_time) > cooldown:
                if gesture == "up":
                    pyautogui.press("space")
                elif gesture == "down":
                    pyautogui.press("down")
                elif gesture == "left":
                    pyautogui.press("left")
                elif gesture == "right":
                    pyautogui.press("right")

                last_gesture = gesture
                last_trigger_time = time.time()

            cv2.putText(frame, f"Gesture: {gesture}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            break 
    cv2.imshow("Hand Gesture Control (Press 'q' to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)

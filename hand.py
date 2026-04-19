import cv2
import mediapipe as mp
import webbrowser

VIDEO_URL = "https://www.youtube.com/"

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)
video_played = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    h, w, _ = frame.shape
    center_x, center_y = w // 2, h // 2

    cv2.circle(frame, (center_x, center_y), 10, (255, 255, 0), -1)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_tip = hand_landmarks.landmark[8]
            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)

            if abs(x - center_x) < 50 and abs(y - center_y) < 50 and not video_played:
                print("Index finger reached center! Playing video...")
                webbrowser.open(VIDEO_URL)
                video_played = True

    cv2.imshow("Hand Trigger", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
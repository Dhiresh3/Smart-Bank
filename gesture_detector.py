import cv2, requests
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

def get_cell_from_position(x, y):
    if y < 200: row = 0
    elif y < 400: row = 1
    else: row = 2
    if x < 200: col = 0
    elif x < 400: col = 1
    else: col = 2
    return row * 3 + col + 1

while True:
    ret, frame = cap.read()
    h, w, _ = frame.shape
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            index_finger = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            cx, cy = int(index_finger.x * w), int(index_finger.y * h)
            cell = get_cell_from_position(cx, cy)
            requests.post('http://localhost:5000/move', json={'cell': cell})
            cv2.putText(frame, f"Cell: {cell}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("GestureTic", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
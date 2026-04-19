from flask import Flask, render_template
import threading
import cv2
import mediapipe as mp
import numpy as np

app = Flask(__name__)

# 🧩 OBJ Loader
class OBJ:
    def __init__(self, filename, swapyz=False):
        self.vertices = []
        self.faces = []
        with open(filename, "r") as file:
            for line in file:
                if line.startswith('#'): continue
                values = line.strip().split()
                if not values: continue
                if values[0] == 'v':
                    v = list(map(float, values[1:4]))
                    if swapyz: v = [v[0], v[2], v[1]]
                    self.vertices.append(v)
                elif values[0] == 'f':
                    face = []
                    for v in values[1:]:
                        w = v.split('/')
                        face.append((int(w[0]), int(w[1]) if len(w) > 1 else 0))
                    self.faces.append(face)

helmet_model = OBJ("ironman_helmet.obj", swapyz=True)

# 🧠 MediaPipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# 🎥 Suit-up logic
def run_suit_up():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 🪖 Helmet overlay
        face_results = face_mesh.process(rgb_frame)
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                forehead = face_landmarks.landmark[10]
                chin = face_landmarks.landmark[152]
                center = np.array([int(forehead.x * w), int(forehead.y * h)])
                face_height = np.linalg.norm([forehead.x - chin.x, forehead.y - chin.y])
                scale = face_height * w / 1.5

                transformed_vertices = []
                for v in helmet_model.vertices:
                    x = int(v[0] * scale + center[0])
                    y = int(v[1] * scale + center[1])
                    transformed_vertices.append((x, y))

                helmet_mask = np.zeros_like(frame)
                for face in helmet_model.faces:
                    pts = [transformed_vertices[i[0] - 1] for i in face]
                    cv2.fillPoly(helmet_mask, [np.array(pts)], color=(0, 0, 200))
                    cv2.polylines(frame, [np.array(pts)], isClosed=True, color=(255, 50, 50), thickness=2)

                helmet_glow = cv2.GaussianBlur(helmet_mask, (0, 0), sigmaX=25, sigmaY=25)
                frame = cv2.addWeighted(frame, 1.0, helmet_glow, 0.4, 0)

        # 🖐️ Hand armor
        hand_results = hands.process(rgb_frame)
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                index_base = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                pinky_base = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

                pts = np.array([
                    [int(wrist.x * w), int(wrist.y * h)],
                    [int(index_base.x * w), int(index_base.y * h)],
                    [int(pinky_base.x * w), int(pinky_base.y * h)]
                ])
                hand_mask = np.zeros_like(frame)
                cv2.fillPoly(hand_mask, [pts], color=(0, 0, 200))
                hand_glow = cv2.GaussianBlur(hand_mask, (0, 0), sigmaX=25, sigmaY=25)
                frame = cv2.addWeighted(frame, 1.0, hand_glow, 0.4, 0)

                for i in [mp_hands.HandLandmark.THUMB_TIP,
                          mp_hands.HandLandmark.INDEX_FINGER_TIP,
                          mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                          mp_hands.HandLandmark.RING_FINGER_TIP,
                          mp_hands.HandLandmark.PINKY_TIP]:
                    tip = hand_landmarks.landmark[i]
                    cv2.circle(frame, (int(tip.x * w), int(tip.y * h)), 10, (255, 215, 0), -1)

                palm = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                palm_x, palm_y = int(palm.x * w), int(palm.y * h)
                for r in range(30, 70, 10):
                    cv2.circle(frame, (palm_x, palm_y), r, (0, 0, 255), 1)

        # 🦾 Body armor + arc reactor
        pose_results = pose.process(rgb_frame)
        if pose_results.pose_landmarks:
            lm = pose_results.pose_landmarks.landmark

            def draw_plate(p1, p2, color):
                x1, y1 = int(p1.x * w), int(p1.y * h)
                x2, y2 = int(p2.x * w), int(p2.y * h)
                plate_mask = np.zeros_like(frame)
                cv2.rectangle(plate_mask, (x1 - 10, y1 - 10), (x2 + 10, y2 + 10), color, -1)
                plate_glow = cv2.GaussianBlur(plate_mask, (0, 0), sigmaX=20, sigmaY=20)
                frame[:] = cv2.addWeighted(frame, 1.0, plate_glow, 0.3, 0)
                cv2.rectangle(frame, (x1 - 10, y1 - 10), (x2 + 10, y2 + 10), (255, 255, 255), 1)

            draw_plate(lm[mp_pose.PoseLandmark.LEFT_SHOULDER], lm[mp_pose.PoseLandmark.RIGHT_SHOULDER], (180, 0, 0))
            draw_plate(lm[mp_pose.PoseLandmark.LEFT_ELBOW], lm[mp_pose.PoseLandmark.LEFT_WRIST], (180, 0, 0))
            draw_plate(lm[mp_pose.PoseLandmark.RIGHT_ELBOW], lm[mp_pose.PoseLandmark.RIGHT_WRIST], (180, 0, 0))
            draw_plate(lm[mp_pose.PoseLandmark.LEFT_KNEE], lm[mp_pose.PoseLandmark.LEFT_ANKLE], (180, 0, 0))
            draw_plate(lm[mp_pose.PoseLandmark.RIGHT_KNEE], lm[mp_pose.PoseLandmark.RIGHT_ANKLE], (180, 0, 0))

            shoulder_left = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
            shoulder_right = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            mid_x = int((shoulder_left.x + shoulder_right.x) * w / 2)
            mid_y = int((shoulder_left.y + shoulder_right.y) * h / 2)

            reactor_mask = np.zeros_like(frame)
            cv2.circle(reactor_mask, (mid_x, mid_y + 40), 30, (0, 0, 255), -1)
            reactor_glow = cv2.GaussianBlur(reactor_mask, (0, 0), sigmaX=40, sigmaY=40)
            frame = cv2.addWeighted(frame, 1.0, reactor_glow, 0.6, 0)

            cv2.circle(frame, (mid_x, mid_y + 40), 20, (255, 255, 255), 2)
            cv2.circle(frame, (mid_x, mid_y + 40), 10, (0, 0, 255), 1)

        cv2.imshow('🦾 Iron Man Suit-Up', frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def home():
    threading.Thread(target=run_suit_up).start()
    return render_template('hekmet.html')

if __name__ == '__main__':
    app.run(debug=True)
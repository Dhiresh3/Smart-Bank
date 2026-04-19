import cv2
import mediapipe as mp
import tkinter as tk
import numpy as np

def get_object_name():
    def submit():
        global object_name
        object_name = entry.get()
        root.destroy()

    root = tk.Tk()
    root.title("Enter Object Name")
    tk.Label(root, text="Object name (e.g., smartphone, leaf, ball):").pack()
    entry = tk.Entry(root)
    entry.pack()
    tk.Button(root, text="Submit", command=submit).pack()
    root.mainloop()

def draw_realistic_sphere(img, center, radius, base_color):
    overlay = img.copy()
    cx, cy = center
    for y in range(-radius, radius):
        for x in range(-radius, radius):
            dist = np.sqrt(x**2 + y**2)
            if dist <= radius:
                light_angle = (x * 0.5 + y * 0.8) / radius
                intensity = max(0.2, 1 - dist / radius + 0.3 * light_angle)
                r = int(min(base_color[2] * intensity + 40, 255))
                g = int(min(base_color[1] * intensity + 40, 255))
                b = int(min(base_color[0] * intensity + 40, 255))
                px, py = cx + x, cy + y
                if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                    overlay[py, px] = (b, g, r)
    cv2.circle(overlay, (int(cx - radius * 0.3), int(cy - radius * 0.3)), int(radius * 0.2), (255, 255, 255), -1)
    shadow = np.zeros_like(img)
    cv2.circle(shadow, (cx, cy + radius + 20), int(radius * 0.8), (50, 50, 50), -1)
    img = cv2.addWeighted(img, 1.0, shadow, 0.3, 0)
    return cv2.addWeighted(overlay, 0.8, img, 0.2, 0)

def draw_leaf(img, center, size, base_color):
    overlay = img.copy()
    cx, cy = center
    points = [(int(cx + size * np.sin(t) * np.cos(t)), int(cy + size * np.sin(t))) for t in np.linspace(0, 2 * np.pi, 100)]
    cv2.fillPoly(overlay, [np.array(points, dtype=np.int32)], base_color)
    cv2.line(overlay, (cx, cy - size), (cx, cy + size), (255, 255, 255), 2)
    shadow = np.zeros_like(img)
    cv2.ellipse(shadow, (cx, cy + size + 20), (size // 2, size // 4), 0, 0, 360, (50, 50, 50), -1)
    img = cv2.addWeighted(img, 1.0, shadow, 0.3, 0)
    return cv2.addWeighted(overlay, 0.8, img, 0.2, 0)

def draw_smartphone(img, center, size, base_color):
    overlay = img.copy()
    cx, cy = center
    w, h = size, int(size * 1.8)
    top_left = (cx - w // 2, cy - h // 2)
    bottom_right = (cx + w // 2, cy + h // 2)
    cv2.rectangle(overlay, top_left, bottom_right, base_color, -1)
    gloss_color = tuple(min(c + 60, 255) for c in base_color)
    gloss_rect = (top_left[0] + 10, top_left[1] + 10, w - 20, h // 3)
    cv2.rectangle(overlay, (gloss_rect[0], gloss_rect[1]), (gloss_rect[0] + gloss_rect[2], gloss_rect[1] + gloss_rect[3]), gloss_color, -1)
    shadow = np.zeros_like(img)
    cv2.rectangle(shadow, (top_left[0], bottom_right[1] + 10), (bottom_right[0], bottom_right[1] + 30), (50, 50, 50), -1)
    img = cv2.addWeighted(img, 1.0, shadow, 0.3, 0)
    return cv2.addWeighted(overlay, 0.85, img, 0.15, 0)

colors = {
    "ball": (30, 30, 220),
    "leaf": (20, 180, 60),
    "orb": (180, 60, 180),
    "sun": (0, 200, 255),
    "moon": (180, 180, 180),
    "fire": (60, 60, 255),
    "ice": (255, 255, 255),
    "apple": (50, 0, 200),
    "smartphone": (40, 40, 40)
}

get_object_name()
color = colors.get(object_name.lower(), (0, 0, 255))

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
print("🖐️ Show your hand. Press 'q' to quit.")

while True:
    success, img = cap.read()
    if not success:
        continue

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    h, w, _ = img.shape
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            wrist = handLms.landmark[mp_hands.HandLandmark.WRIST]
            mcp = handLms.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            cx = int((wrist.x + mcp.x) / 2 * w)
            cy = int((wrist.y + mcp.y) / 2 * h)
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            center = (cx, cy - 100)

            obj = object_name.lower()
            if obj == "leaf":
                img = draw_leaf(img, center, 40, color)
            elif obj == "smartphone":
                img = draw_smartphone(img, center, 40, color)
            else:
                img = draw_realistic_sphere(img, center, 40, color)

            cv2.putText(img, object_name, (center[0] - 30, center[1] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Floating Realistic Object", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("👋 Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
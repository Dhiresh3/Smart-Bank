import cv2
import pygame
import sys
import time
import threading
import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import tkinter as tk
from tkinter import messagebox

# ========== Setup ==========
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("🤖 Robo Assistant Face")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
CYAN = (0, 255, 255)
GRAY = (180, 180, 180)
GLOW = (0, 180, 255)
BG = (135, 206, 250)

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

engine = pyttsx3.init()
engine.setProperty('rate', 160)
recognizer = sr.Recognizer()

# States
prev_face_pos = None
blink_timer = time.time()
blink_duration = 0.2
is_blinking = False
is_speaking = False

# === Apps and Websites ===
apps = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "vscode": os.path.join(os.getenv("USERPROFILE"), "AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"),
    "spotify": "C:\\Users\\dhire\\AppData\\Roaming\\Spotify\\Spotify.exe",
    "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
    "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
    "whatsapp": "C:\\Users\\dhire\\AppData\\Local\\Packages\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\\WhatsApp.exe",
    "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
}

synonyms = {
    "google": "chrome", "google chrome": "chrome", "browser": "chrome",
    "vs code": "vscode", "visual studio": "vscode", "editor": "vscode",
    "note pad": "notepad", "calc": "calculator",
    "music": "spotify", "songs": "spotify",
    "presentation": "powerpoint", "slides": "powerpoint", "ppt": "powerpoint",
    "document": "word", "ms word": "word",
    "spreadsheet": "excel", "ms excel": "excel", "sheet": "excel",
    "whatsapp messenger": "whatsapp", "chat": "whatsapp",
    "mozilla": "firefox", "mozilla firefox": "firefox"
}

websites = {
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "google": "https://www.google.com",
    "stackoverflow": "https://stackoverflow.com",
}

# ========== Functions ==========
def speak(text):
    global is_speaking
    is_speaking = True
    engine.say(text)
    engine.runAndWait()
    is_speaking = False

def normalize_app_name(app_name):
    app_name = app_name.lower()
    for synonym, actual in synonyms.items():
        if synonym in app_name:
            return actual
    return app_name

def open_app(app_name):
    app_name = normalize_app_name(app_name)
    for site in websites:
        if site in app_name:
            speak(f"Opening {site}")
            webbrowser.open(websites[site])
            return
    for key in apps:
        if key in app_name:
            try:
                speak(f"Launching {key}")
                os.startfile(apps[key])
            except FileNotFoundError:
                speak(f"{key} is not installed.")
            return
    speak("Sorry, I couldn't find that app or website.")

def get_voice_command():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            speak("Listening")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        return recognizer.recognize_google(audio).lower()
    except:
        return ""

def get_face_position():
    ret, frame = cap.read()
    if not ret: return None
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) > 0:
        x, y, w, h = faces[0]
        return (x + w // 2, y + h // 2)
    return None

# ========== Robo Face Drawing ==========
def draw_robot_face(face_pos=None):
    global is_blinking, blink_timer, prev_face_pos, is_speaking
    screen.fill(BG)
    pygame.draw.ellipse(screen, GLOW, (115, 75, 410, 330))
    pygame.draw.ellipse(screen, BLACK, (118, 78, 404, 324))
    pygame.draw.ellipse(screen, WHITE, (120, 80, 400, 320))

    pygame.draw.ellipse(screen, BLACK, (175, 135, 290, 210))
    pygame.draw.line(screen, GRAY, (320, 60), (320, 140), 4)
    pygame.draw.circle(screen, CYAN, (320, 50), 10)

    left_eye_center = [240, 220]
    right_eye_center = [400, 220]

    if face_pos:
        fx, fy = face_pos
        if prev_face_pos:
            dx, dy = abs(fx - prev_face_pos[0]), abs(fy - prev_face_pos[1])
            if dx > 10 or dy > 10:
                fx, fy = (fx + prev_face_pos[0]) // 2, (fy + prev_face_pos[1]) // 2
        prev_face_pos = (fx, fy)
        offset_x = int((fx / 640) * 20) - 10
        offset_y = int((fy / 480) * 10) - 5
        left_eye_center[0] += offset_x; left_eye_center[1] += offset_y
        right_eye_center[0] += offset_x; right_eye_center[1] += offset_y

    # Blink
    if time.time() - blink_timer > 5:
        is_blinking, blink_timer = True, time.time()
    if is_blinking and time.time() - blink_timer < blink_duration:
        pygame.draw.rect(screen, BLACK, (220, 210, 60, 20))
        pygame.draw.rect(screen, BLACK, (380, 210, 60, 20))
    else:
        is_blinking = False
        pygame.draw.ellipse(screen, CYAN, (left_eye_center[0] - 20, left_eye_center[1] - 15, 40, 30))
        pygame.draw.ellipse(screen, CYAN, (right_eye_center[0] - 20, right_eye_center[1] - 15, 40, 30))

    # Mouth animation
    if is_speaking:
        pygame.draw.arc(screen, CYAN, (280, 300, 80, 40), 3.14, 0, 4)
    else:
        pygame.draw.arc(screen, WHITE, (280, 300, 80, 40), 3.14, 0, 3)

    pygame.display.flip()

# ========== GUI ==========
def launch_gui():
    def on_submit():
        app_name = entry.get()
        if app_name.strip():
            open_app(app_name)
            entry.delete(0, tk.END)
        else:
            messagebox.showinfo("Input Needed", "Please enter an app name.")

    def on_voice():
        app_name = get_voice_command()
        if app_name.strip():
            open_app(app_name)
        else:
            messagebox.showinfo("Try Again", "Didn't catch that.")

    root = tk.Tk()
    root.title("🎤 Robo Assistant Launcher")
    root.geometry("360x260")
    root.configure(bg="#222831")

    tk.Label(root, text="Enter app name or website:", fg="white", bg="#222831",
             font=("Segoe UI", 11, "bold")).pack(pady=10)
    entry = tk.Entry(root, width=32, font=("Segoe UI", 11))
    entry.pack(pady=5)
    entry.focus()

    style_btn = {"width": 20, "font": ("Segoe UI", 10, "bold"), "bg": "#00ADB5", "fg": "white", "activebackground": "#007B7F"}

    tk.Button(root, text="🚀 Launch App", command=on_submit, **style_btn).pack(pady=5)
    tk.Button(root, text="🎙️ Use Voice", command=on_voice, **style_btn).pack(pady=5)
    tk.Button(root, text="❌ Exit", command=root.quit, **style_btn).pack(pady=5)

    root.mainloop()

# ========== Threads ==========
threading.Thread(target=launch_gui, daemon=True).start()

# ========== Main Loop ==========
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release(); pygame.quit(); sys.exit()
    face_pos = get_face_position()
    draw_robot_face(face_pos)
    clock.tick(30)

import tkinter as tk
import pyttsx3
import threading
import time
import queue
import pygame

pygame.mixer.init()
meow_sound = pygame.mixer.Sound("meow.wav")  

class PythonPet:
    def __init__(self):
        self.hunger = 5
        self.energy = 5
        self.mood = 5
        self.cleanliness = 5

    def get_status(self):
        return {
            "Hunger": self.hunger,
            "Energy": self.energy,
            "Mood": self.mood,
            "Cleanliness": self.cleanliness
        }

    def decay(self):
        self.hunger = max(0, self.hunger - 1)
        self.energy = max(0, self.energy - 1)
        self.mood = max(0, self.mood - 1)
        self.cleanliness = max(0, self.cleanliness - 1)

def feed(pet):
    pet.hunger = min(10, pet.hunger + 3)
    return "Yum! Hunger restored."

def play(pet):
    if pet.energy > 2:
        pet.mood = min(10, pet.mood + 2)
        pet.energy -= 2
        return "That was fun!"
    return "Too tired to play."

def sleep(pet):
    pet.energy = min(10, pet.energy + 4)
    return "Resting..."

def clean(pet):
    pet.cleanliness = min(10, pet.cleanliness + 3)
    return "All clean!"

speech_queue = queue.Queue()
engine = pyttsx3.init()

def speech_worker():
    while True:
        text = speech_queue.get()
        if text:
            try:
                engine.say(text)
                engine.runAndWait()
                meow_sound.play()
            except Exception as e:
                print("Sound error:", e)
        speech_queue.task_done()

threading.Thread(target=speech_worker, daemon=True).start()

def speak(text):
    speech_queue.put(text)

def draw_cat(canvas, mood):
    canvas.delete("all")
    canvas.create_oval(50, 50, 150, 150, fill="peachpuff", outline="black", width=2)
    canvas.create_oval(75, 80, 85, 90, fill="black")
    canvas.create_oval(115, 80, 125, 90, fill="black")

    if mood > 7:
        canvas.create_arc(85, 110, 115, 130, start=0, extent=-180, style=tk.ARC, width=2)
    elif mood > 4:
        canvas.create_line(90, 120, 110, 120, width=2)
    else:
        canvas.create_arc(85, 115, 115, 135, start=0, extent=180, style=tk.ARC, width=2)

    canvas.create_line(50, 100, 80, 100)
    canvas.create_line(120, 100, 150, 100)
    canvas.create_line(50, 110, 80, 110)
    canvas.create_line(120, 110, 150, 110)

    canvas.create_polygon(60, 50, 70, 30, 80, 50, fill="peachpuff", outline="black")
    canvas.create_polygon(120, 50, 130, 30, 140, 50, fill="peachpuff", outline="black")

def start_decay(pet, update_callback):
    def decay_loop():
        while True:
            time.sleep(10)
            pet.decay()
            update_callback()
    threading.Thread(target=decay_loop, daemon=True).start()

pet = PythonPet()

def update_status():
    status = pet.get_status()
    status_text.set(
        f"Hunger: {status['Hunger']} | Energy: {status['Energy']} | Mood: {status['Mood']} | Cleanliness: {status['Cleanliness']}"
    )
    draw_cat(canvas, pet.mood)

def action_handler(action):
    if action == "feed":
        msg = feed(pet)
    elif action == "play":
        msg = play(pet)
    elif action == "sleep":
        msg = sleep(pet)
    elif action == "clean":
        msg = clean(pet)
    else:
        msg = "Unknown action."
    speak(msg)
    update_status()

root = tk.Tk()
root.title("🐱 Python Cat Pet")

status_text = tk.StringVar()
tk.Label(root, textvariable=status_text, font=("Arial", 14)).pack(pady=10)

canvas = tk.Canvas(root, width=200, height=200, bg="lightyellow", highlightthickness=0)
canvas.pack(pady=10)

for act in ["feed", "play", "sleep", "clean"]:
    tk.Button(root, text=act.capitalize(), font=("Arial", 12), width=10,
              command=lambda a=act: action_handler(a)).pack(pady=5)

update_status()
start_decay(pet, update_status)

root.mainloop()
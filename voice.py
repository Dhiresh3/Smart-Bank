import tkinter as tk
from tkinter import messagebox
import os
import webbrowser
import speech_recognition as sr
import pyttsx3

# === Voice Engine Setup ===
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# === App & Website Data ===
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
    "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    "edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "paint":"C:\Windows\System32\mspaint.exe",
    "chess": "C:\\Program Files\\Microsoft Games\\Chess\\chess.exe"
}

synonyms = {
    "google": "chrome", "google chrome": "chrome", "browser": "chrome",
    "vs code": "vscode", "visual studio": "vscode", "editor": "vscode",
    "note pad": "notepad", "calc": "calculator",
    "music": "spotify", "songs": "spotify",
    "ms paint":"paint",
    "presentation": "powerpoint", "slides": "powerpoint", "ppt": "powerpoint",
    "document": "word", "ms word": "word",
    "spreadsheet": "excel", "ms excel": "excel", "sheet": "excel",
    "whatsapp messenger": "whatsapp", "chat": "whatsapp", "whatsapp web": "whatsapp",
    "mozilla": "firefox", "mozilla firefox": "firefox",
    "microsoft edge": "edge", "edge browser": "edge",
    "play chess": "chess", "chess game": "chess", "open chess": "chess"
}

websites = {
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "google": "https://www.google.com",
    "stackoverflow": "https://stackoverflow.com",
    "firefox": "https://www.firefox.com/en-US/",
    "edge": "https://www.microsoft.com/edge",
    "chatgpt":"https://openai.com/index/chatgpt", 
    "whatsapp": "https://web.whatsapp.com"
}


def speak(text):
    print(f"🗣️ Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

def normalize_app_name(app_name):
    app_name = app_name.lower()
    for synonym, actual in synonyms.items():
        if synonym in app_name:
            print(f"🔁 Synonym matched: '{synonym}' → '{actual}'")
            return actual
    return app_name

def open_app(app_name):
    app_name = normalize_app_name(app_name)
    print(f"🔍 Normalized input: {app_name}")

    for site in websites:
        if site in app_name:
            print(f"🌐 Opening website: {websites[site]}")
            speak(f"Opening website {site}. Enjoy browsing!")
            webbrowser.open(websites[site])
            return

    for key in apps:
        if key in app_name:
            try:
                print(f"🚀 Launching app: {apps[key]}")
                speak(f"Opening {key} application. Get ready!")
                os.startfile(apps[key])
            except FileNotFoundError:
                print(f"❌ App not found: {key}")
                messagebox.showerror("Missing App", f"{key} not found on your system.")
                speak(f"{key} is not installed on your system.")
            return

    print(f"❓ Unknown input: {app_name}")
    messagebox.showerror("Error", f"App or site not found for: {app_name}")
    speak(f"Sorry, I couldn't find any app or website named {app_name}.")

def get_voice_command():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎙️ Listening...")
            speak("Listening for app name")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        command = recognizer.recognize_google(audio).lower()
        print(f"🗣️ You said: {command}")
        return command
    except Exception as e:
        print(f"⚠️ Voice input failed: {e}")
        speak("Voice input failed. Please check your microphone.")
        return ""

def launch_gui():
    def on_submit():
        app_name = entry.get()
        if app_name.strip():
            open_app(app_name)
            entry.delete(0, tk.END)
        else:
            messagebox.showinfo("Input Needed", "Please enter an app name.")
            speak("Please enter an app name.")

    def on_voice():
        app_name = get_voice_command()
        if app_name.strip():
            open_app(app_name)
        else:
            messagebox.showinfo("Try Again", "Didn't catch that.")
            speak("Didn't catch that. Try typing instead.")

    root = tk.Tk()
    root.title("🤖 Robo Assistant Launcher")
    root.geometry("360x260")
    root.configure(bg="#1e1e1e")

    tk.Label(root, text="Enter app name or website:", fg="white", bg="#1e1e1e",
             font=("Segoe UI", 11, "bold")).pack(pady=10)

    entry = tk.Entry(root, width=32, font=("Segoe UI", 11), bg="#ffffff", fg="#000000")
    entry.pack(pady=5)
    entry.focus()

    style_btn = {
        "width": 20,
        "font": ("Segoe UI", 10, "bold"),
        "bg": "#00ADB5",
        "fg": "white",
        "activebackground": "#007B7F",
        "activeforeground": "white",
        "relief": tk.FLAT
    }

    tk.Button(root, text="🚀 Launch App", command=on_submit, **style_btn).pack(pady=5)
    tk.Button(root, text="🎙️ Use Voice", command=on_voice, **style_btn).pack(pady=5)
    tk.Button(root, text="❌ Exit", command=root.quit, **style_btn).pack(pady=5)

    root.mainloop()

launch_gui()
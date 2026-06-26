import os
import webbrowser
import threading
import speech_recognition as sr
from flask import Flask, render_template, request, jsonify
import pyttsx3

app = Flask(__name__)

# === App & Website Data ===
apps = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "vscode": os.path.join(os.getenv("USERPROFILE", ""), "AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"),
    "spotify": "C:\\Users\\dhire\\AppData\\Roaming\\Spotify\\Spotify.exe",
    "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
    "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
    "whatsapp": "C:\\Users\\dhire\\AppData\\Local\\Packages\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\\WhatsApp.exe",
    "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
    "edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "paint": "C:\\Windows\\System32\\mspaint.exe",
    "chess": "C:\\Program Files\\Microsoft Games\\Chess\\chess.exe"
}

synonyms = {
    "google": "chrome", "google chrome": "chrome", "browser": "chrome",
    "vs code": "vscode", "visual studio": "vscode", "editor": "vscode",
    "note pad": "notepad", "calc": "calculator",
    "music": "spotify", "songs": "spotify",
    "ms paint": "paint",
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
    "chatgpt": "https://openai.com/index/chatgpt", 
    "whatsapp": "https://web.whatsapp.com"
}

def speak(text):
    print(f"Lily AI Speaking: {text}")
    def run_speak():
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except ImportError:
            pass # Usually not needed unless pywin32 is installed and strict COM threading is enforced
        
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

    threading.Thread(target=run_speak, daemon=True).start()

def normalize_app_name(app_name):
    app_name = app_name.lower()
    for synonym, actual in synonyms.items():
        if synonym in app_name:
            print(f"Synonym matched: '{synonym}' -> '{actual}'")
            return actual
    return app_name

def open_app(app_name):
    app_name = normalize_app_name(app_name)
    print(f"Normalized input: {app_name}")

    for site in websites:
        if site in app_name:
            print(f"Opening website: {websites[site]}")
            speak(f"Opening {site} for you.")
            webbrowser.open(websites[site])
            return f"Opening website: {site}"

    for key in apps:
        if key in app_name:
            try:
                print(f"Launching app: {apps[key]}")
                speak(f"Opening {key}. Give me a moment.")
                os.startfile(apps[key])
                return f"Launching app: {key}"
            except FileNotFoundError:
                print(f"App not found: {key}")
                speak(f"I couldn't find {key} on your system.")
                return f"Error: {key} not found on your system."

    print(f"Unknown input: {app_name}")
    speak(f"Sorry, I couldn't find any app or website named {app_name}.")
    return f"App or site not found for: {app_name}"

def get_voice_command():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening for app name on desktop microphone...")
            speak("Listening for app name")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except Exception as e:
        print(f"Voice input failed: {e}")
        speak("Voice input failed. Please check your microphone.")
        return ""

@app.route("/")
def index():
    return render_template("lily.html")

@app.route("/command", methods=["POST"])
def command():
    data = request.json
    cmd_text = data.get("command", "")
    if not cmd_text:
        return jsonify({"status": "error", "message": "No command provided."})
    
    result = open_app(cmd_text)
    return jsonify({"status": "success", "message": result, "command": cmd_text})

@app.route("/voice", methods=["POST"])
def voice_command():
    print("Voice command route triggered")
    cmd_text = get_voice_command()
    if not cmd_text.strip():
        return jsonify({"status": "error", "message": "Didn't catch that. Please try typing."})
    
    result = open_app(cmd_text)
    return jsonify({"status": "success", "message": result, "command": cmd_text})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
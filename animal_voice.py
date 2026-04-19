"""
animal_voice.py
================
An AI text-to-speech utility that announces the predicted animal.
Requires: pip install pyttsx3
"""

import pyttsx3

def announce_prediction(animal_name, confidence=None):
    """
    Speaks the predicted animal using the system's default text-to-speech engine.
    """
    try:
        engine = pyttsx3.init()
        
        # Optional: Adjust voice speed (rate)
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 20)  # Slow down slightly for clarity
        
        # Build the sentence
        if confidence:
            text = f"The predicted animal is {animal_name}, with {confidence}% confidence."
        else:
            text = f"The predicted animal is {animal_name}."
            
        print(f"🔊 Speaking: '{text}'")
        engine.say(text)
        engine.runAndWait()
        
    except Exception as e:
        print(f"⚠️ Voice error: Could not initialize text-to-speech. ({e})")

# Quick test if you run this file directly
if __name__ == "__main__":
    announce_prediction("Tiger", 91.8)

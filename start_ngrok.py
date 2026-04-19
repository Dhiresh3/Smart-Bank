from pyngrok import ngrok
import time

try:
    # Open a HTTP tunnel on port 5000
    public_url = ngrok.connect(5000).public_url
    print(f"NGROK_URL: {public_url}")
    
    # Keep the script running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down ngrok.")
except Exception as e:
    print(f"Error: {e}")

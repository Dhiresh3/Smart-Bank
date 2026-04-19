import os
import google.generativeai as genai
from dotenv import load_dotenv
from textwrap import dedent

# Mocking the setup from Application.py
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    api_key = "AIzaSyCSIMT3CR8ihgQu6HbwSQJIB3XceUk9yoAy"

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_safe_reply(user_message: str) -> str:
    if not user_message or not user_message.strip():
        return "I’m here to help with SmartBank services. How can I assist you today?"

    msg = user_message.lower()
    if any(k in msg for k in ["password", "otp", "pin", "cvv"]):
        return "For your security, please do not share passwords, PINs, CVVs, or OTPs. How else can I help?"

    system_prompt = dedent("""
        You are 'Banky', the official AI assistant for Skiller SmartBank.
        Your goal is to provide helpful, professional, and concise support to customers.
        
        Guidelines:
        - Only answer questions related to banking, loans, account management, and financial services.
        - If asked about non-banking topics, politely redirect the user to SmartBank services.
        - NEVER ask for or reveal sensitive information like passwords, PINs, OTPs, or CVVs.
        - Be empathetic and professional.
        - SmartBank offers Personal and Education loans at 8.5% interest.
        - Account types: Savings, Current, Fixed Deposit.
        - Minimum age for account opening is 18.
        
        User's question:
    """)

    try:
        response = model.generate_content(system_prompt + user_message)
        return response.text.strip()
    except Exception as e:
        return f"Gemini API error: {e}"

# Test cases
test_messages = [
    "How can I open a savings account?",
    "What is the interest rate for loans?",
    "Can you tell me a joke?",
    "My password is 1234, is it safe?"
]

print("--- Chatbot Integration Test ---")
for msg in test_messages:
    print(f"\nUser: {msg}")
    reply = generate_safe_reply(msg)
    print(f"Banky: {reply}")

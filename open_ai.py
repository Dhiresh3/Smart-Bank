import os
from flask import Flask, render_template, request, jsonify
import google.genai as genai   # ✅ use the new package
from riia import investigate_all_transactions, get_anomalies, load_investigation_data

# Configure client
api_key = os.getenv("GOOGLE_API_KEY") or "YOUR_API_KEY"
client = genai.Client(api_key=api_key)

app = Flask(__name__, template_folder=".")


def chat(prompt: str) -> str:
    """
    RIIA (RI Intelligent Investigation Assistant)
    Frontend-facing AI that helps analyze flagged UPI-style transactions,
    detect inconsistencies/anomalies, and answer banking-related questions.
    """
    system_instructions = (
        "You are RIIA, an Intelligent Investigation Assistant for a smart banking app. "
        "Keep answers concise and clear. You can:\n"
        "- Explain possible anomalies or fraud patterns in UPI / digital transactions.\n"
        "- Help interpret transaction histories and balances in simple language.\n"
        "- Give general security advice (but never ask for PINs, OTPs, CVVs, or passwords).\n"
        "The user may be a bank analyst or customer. If the question is not about banking, "
        "answer briefly and politely.\n\n"
        "User message:\n"
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=system_instructions + prompt
    )
    return response.text.strip()


@app.route("/")
def index():
    return render_template("open_ai.html")


@app.route("/chat", methods=["POST"])
def chat_api():
    user_input = request.json.get("message", "")
    if not user_input.strip():
        return jsonify({"response": "Please enter a message."})
    response = chat(user_input)
    return jsonify({"response": response})


@app.route("/api/investigations", methods=["GET"])
def api_investigations():
    """Returns enriched investigation results from riia.py / riia_*.json"""
    results = investigate_all_transactions()
    return jsonify(results)


@app.route("/api/anomalies", methods=["GET"])
def api_anomalies():
    """Returns account-level anomalies based on accounts.json / riia.py logic."""
    return jsonify(get_anomalies())


@app.route("/api/raw_data", methods=["GET"])
def api_raw_data():
    """Expose raw investigation data for debugging / admin view."""
    customers, merchants, transactions = load_investigation_data()
    return jsonify({
        "customers": customers,
        "merchants": merchants,
        "transactions": transactions,
    })


if __name__ == "__main__":
    app.run(debug=True)
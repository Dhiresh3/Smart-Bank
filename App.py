"""
app.py — Flask Web Server for Animal CNN Classifier
=====================================================
Serves a beautiful frontend where users can upload images
or provide file paths for animal predictions.
"""

import os
import json
import uuid
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory

# ── Import the CNN model class from animal.py ──
from animal import AnimalCNN, META_PATH, MODEL_PATH, IMG_SIZE

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "gif"}

# ── Load model once at startup ──
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open(META_PATH) as f:
    classes = json.load(f)

checkpoint = torch.load(MODEL_PATH, map_location=device)
model = AnimalCNN(len(classes)).to(device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()
print(f"✅ Model loaded — {len(classes)} classes, best acc: {checkpoint.get('best_acc', 0):.2f}%")

# ── Transform pipeline (same as prediction in animal.py) ──
val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Minimum confidence threshold — below this we consider the image "unknown"
CONFIDENCE_THRESHOLD = 60.0  # percent


def predict_image(image_path):
    """Run prediction on an image file and return results.
    
    Returns:
        dict with 'results' list, or raises ValueError if image is not
        recognised as a known animal (confidence below threshold).
    """
    img = Image.open(image_path).convert("RGB")
    tensor = val_transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()

    results = []
    for cls, prob in zip(classes, probs):
        results.append({"class": cls, "confidence": round(float(prob) * 100, 2)})

    results.sort(key=lambda x: x["confidence"], reverse=True)

    top_confidence = results[0]["confidence"]
    if top_confidence < CONFIDENCE_THRESHOLD:
        raise ValueError(
            f"⚠️ This image does not appear to be one of the supported animals. "
            f"The model only recognises: {', '.join(classes)}. "
            f"Please upload a clear photo of one of these animals."
        )

    return results


# ── ROUTES ──
@app.route("/")
def index():
    return render_template("index.html", classes=classes)


@app.route("/predict", methods=["POST"])
def predict():
    """Handle image upload or file path for prediction."""
    image_path = None
    image_url = None

    # Option 1: File upload
    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            image_path = os.path.join(UPLOAD_DIR, filename)
            file.save(image_path)
            image_url = f"/static/uploads/{filename}"

    # Option 2: File path provided
    if not image_path and request.form.get("filepath"):
        filepath = request.form["filepath"].strip().strip('"').strip("'")
        if os.path.isfile(filepath):
            img = Image.open(filepath).convert("RGB")
            filename = f"{uuid.uuid4().hex}.jpg"
            save_path = os.path.join(UPLOAD_DIR, filename)
            img.save(save_path)
            image_path = save_path
            image_url = f"/static/uploads/{filename}"
        else:
            return jsonify({"error": f"File not found: {filepath}"}), 400

    if not image_path:
        return jsonify({"error": "No valid image provided. Upload an image or enter a file path."}), 400

    try:
        results = predict_image(image_path)
        top = results[0]
        return jsonify({
            "success": True,
            "prediction": top["class"],
            "confidence": top["confidence"],
            "top5": results[:5],
            "all": results,
            "image_url": image_url,
        })
    except ValueError as e:
      
        return jsonify({"error": str(e), "unknown_image": True}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\n🌐  Starting Animal Classifier Web App...")
    print("   Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=False, host="127.0.0.1", port=5000)
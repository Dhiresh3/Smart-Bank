import os
from flask import Flask, request, render_template_string
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image

app = Flask(__name__)

MODEL_PATH = "C:/Users/dhire/OneDrive/Desktop/Coding1/animal_classifier.pth"

# Transforms
data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Class names (update to match your dataset)
class_names = ['cat', 'dog', 'wild']

# Load model
model = resnet18(weights=ResNet18_Weights.DEFAULT)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, len(class_names))

if os.path.exists(MODEL_PATH):
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
else:
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Train and save it first!")

def predict_image(image_path):
    img = Image.open(image_path)
    img = data_transforms(img).unsqueeze(0)
    outputs = model(img)
    _, preds = torch.max(outputs, 1)
    return class_names[preds[0]]

HTML_TEMPLATE = '''
<!doctype html>
<title>Animal Classifier</title>
<h1>Upload an image to classify</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
{% if prediction %}
  <h2>Predicted Animal: {{ prediction }}</h2>
{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    prediction = None
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join("uploads", file.filename)
            os.makedirs("uploads", exist_ok=True)
            file.save(filepath)
            prediction = predict_image(filepath)
    return render_template_string(HTML_TEMPLATE, prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
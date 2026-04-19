import cv2
import torch
import timm
import torchvision.transforms as T
from torchvision import datasets
from wildlife_tools.features import DeepFeatures
from wildlife_tools.similarity import CosineSimilarity
import mediapipe as mp
import numpy as np

# ✅ Path to your dataset
root = "C:/Users/dhire/OneDrive/Desktop/Coding1/archive/raw-img"

# ✅ Transforms
transform = T.Compose([
    T.Resize([384, 384]),
    T.ToTensor(),
    T.Normalize(mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225))
])

# ✅ Load your own wildlife dataset
dataset = datasets.ImageFolder(root=root, transform=transform)
class_names = dataset.classes
print("Classes:", class_names)

# ✅ Pretrained model (MegaDescriptor)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = timm.create_model('hf-hub:BVRA/MegaDescriptor-L-384', num_classes=0, pretrained=True)
extractor = DeepFeatures(model, device=device, batch_size=32, num_workers=0)

# ✅ Extract database features once
features_database = extractor(dataset)

# ✅ MediaPipe setup (object detection visualization)
mp_drawing = mp.solutions.drawing_utils
mp_objectron = mp.solutions.objectron

# ✅ Camera loop (real-time wildlife detection)
cap = cv2.VideoCapture(0)

with mp_objectron.Objectron(static_image_mode=False,
                            max_num_objects=5,
                            min_detection_confidence=0.5,
                            model_name='Cup') as objectron:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe detection (bounding boxes)
        results = objectron.process(rgb_frame)
        if results.detected_objects:
            for detected_object in results.detected_objects:
                mp_drawing.draw_landmarks(
                    frame, detected_object.landmarks_2d, mp_objectron.BOX_CONNECTIONS)

        # ✅ Feature extraction for live frame
        img = cv2.resize(rgb_frame, (384, 384))
        img_tensor = transform(img).unsqueeze(0).to(device)

        with torch.no_grad():
            features_query = extractor.extract_batch(img_tensor)

        # ✅ Similarity search
        similarity = CosineSimilarity()(features_query, features_database)
        pred_idx = similarity.argmax(axis=1)[0]
        pred_score = similarity[0, pred_idx]

        # ✅ Threshold for unknown animals
        threshold = 0.6
        label = class_names[pred_idx] if pred_score >= threshold else "new_individual"

        # ✅ Show prediction
        cv2.putText(frame, f"Detected: {label} ({pred_score:.2f})", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Wildlife Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
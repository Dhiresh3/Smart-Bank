import cv2
import os
import base64
import numpy as np
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["smartbank"]
users_col = db["users"]

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "face_detection.tflite")
FACE_SIZE = (200, 200)

# ── Lazy detector: created on first use, NOT at import time ──────────────────
# This prevents gunicorn from crashing at startup if the model file is missing.
_detector = None

def _get_detector():
    """Return the MediaPipe FaceDetector, creating it on first call."""
    global _detector
    if _detector is not None:
        return _detector
    try:
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        if not os.path.exists(MODEL_PATH):
            print(f"⚠️  Face detection model not found at: {MODEL_PATH}")
            return None

        base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        options = mp_vision.FaceDetectorOptions(base_options=base_options)
        _detector = mp_vision.FaceDetector.create_from_options(options)
        print("✅ MediaPipe FaceDetector loaded successfully.")
    except Exception as e:
        print(f"⚠️  Could not load FaceDetector: {e}")
        _detector = None
    return _detector


def crop_face(frame, detection):
    """Crop and resize the detected face region from the frame."""
    h, w = frame.shape[:2]
    bbox = detection.bounding_box

    x, y   = int(bbox.origin_x), int(bbox.origin_y)
    bw, bh = int(bbox.width),    int(bbox.height)

    pad_x, pad_y = int(bw * 0.2), int(bh * 0.2)
    x1 = max(0, x - pad_x);  y1 = max(0, y - pad_y)
    x2 = min(w, x + bw + pad_x); y2 = min(h, y + bh + pad_y)

    face_crop = frame[y1:y2, x1:x2]
    if face_crop.size > 0:
        face_crop = cv2.resize(face_crop, FACE_SIZE, interpolation=cv2.INTER_AREA)
    return face_crop


def decode_base64_image(b64_string):
    """Decode a Base64 image string (from browser) into an OpenCV BGR frame."""
    try:
        if "," in b64_string:
            b64_string = b64_string.split(",", 1)[1]
        img_bytes = base64.b64decode(b64_string)
        np_arr    = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None


def save_face_presence(name, face_image=None):
    """Save face enrollment status and cropped face image to MongoDB."""
    update_doc = {"face_enrolled": True}
    if face_image is not None:
        _, buffer  = cv2.imencode('.jpg', face_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        update_doc.update({
            "face_image":   img_base64,
            "image_format": "jpg",
            "image_width":  FACE_SIZE[0],
            "image_height": FACE_SIZE[1],
            "image_size":   len(img_base64),
        })
    users_col.update_one({"name": name}, {"$set": update_doc}, upsert=True)


def match_face_presence(name):
    """Check if a user has an enrolled face in MongoDB."""
    user = users_col.find_one({"name": name})
    return bool(user and user.get("face_enrolled", False))


def verify_face_image(name, face_b64, enroll=False):
    """
    Accepts a Base64 image from the browser, detects the face using MediaPipe,
    and either enrolls (enroll=True) or verifies the user.

    Returns True on success, False on any failure — never raises.
    """
    if not face_b64:
        print("No face image provided.")
        return False

    frame = decode_base64_image(face_b64)
    if frame is None:
        print("Failed to decode image.")
        return False

    detector = _get_detector()
    if detector is None:
        print("FaceDetector unavailable — skipping detection.")
        return False

    try:
        import mediapipe as mp
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        detection_result = detector.detect(mp_image)
    except Exception as e:
        print(f"Face detection error: {e}")
        return False

    if not detection_result.detections:
        print(f"No face detected for: {name}")
        return False

    print(f"Face detected for: {name}")
    face_crop = crop_face(frame, detection_result.detections[0])

    if enroll:
        save_face_presence(name, face_image=face_crop)
        print(f"Face enrolled for {name}.")
        return True

    match = match_face_presence(name)
    print(f"Face verification for {name}: {match}")
    return match
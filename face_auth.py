import cv2
import os
import base64
from pymongo import MongoClient
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["smartbank"]
users_col = db["users"]

MODEL_PATH = os.path.join("models", "face_detection.tflite")

# Load face detection model
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.FaceDetectorOptions(base_options=base_options)
detector = vision.FaceDetector.create_from_options(options)


FACE_SIZE = (200, 200)  # Standard size for stored face images


def crop_face(frame, detection):
    """Crop and resize the detected face region from the frame."""
    h, w = frame.shape[:2]
    bbox = detection.bounding_box

    # Get bounding box coordinates
    x = int(bbox.origin_x)
    y = int(bbox.origin_y)
    bw = int(bbox.width)
    bh = int(bbox.height)

    # Add 20% padding around the face
    pad_x = int(bw * 0.2)
    pad_y = int(bh * 0.2)

    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(w, x + bw + pad_x)
    y2 = min(h, y + bh + pad_y)

    face_crop = frame[y1:y2, x1:x2]

    # Resize to standard face size
    if face_crop.size > 0:
        face_crop = cv2.resize(face_crop, FACE_SIZE, interpolation=cv2.INTER_AREA)

    return face_crop


def save_face_presence(name, face_image=None):
    """Save face enrollment status and cropped face image to MongoDB."""
    update_doc = {"face_enrolled": True}

    if face_image is not None:
        # Encode cropped face image as base64 string for storage
        _, buffer = cv2.imencode('.jpg', face_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        update_doc["face_image"] = img_base64
        update_doc["image_format"] = "jpg"
        update_doc["image_width"] = FACE_SIZE[0]
        update_doc["image_height"] = FACE_SIZE[1]
        update_doc["image_size"] = len(img_base64)

    users_col.update_one(
        {"name": name},
        {"$set": update_doc},
        upsert=True
    )


def match_face_presence(name):
    """Check if a user has an enrolled face in MongoDB."""
    user = users_col.find_one({"name": name})
    if user:
        return user.get("face_enrolled", False)
    return False


def capture_and_verify(name, enroll=False):
    video = cv2.VideoCapture(0)
    success = False
    captured_frame = None

    print(f"Starting face capture for: {name} (Enroll: {enroll})")

    for _ in range(150):  # ~7 seconds
        ret, frame = video.read()
        if not ret:
            continue

        cv2.imshow("Face Capture - Press Q to cancel", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Capture cancelled by user.")
            break

        # Convert frame to Mediapipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        detection_result = detector.detect(mp_image)

        if detection_result.detections:
            print("Face detected!")
            success = True
            # Crop only the face region and resize it
            captured_frame = crop_face(frame, detection_result.detections[0])
            break

    video.release()
    cv2.destroyAllWindows()

    if not success:
        print("Face capture failed.")
        return False

    if enroll:
        save_face_presence(name, face_image=captured_frame)
        print("Face enrolled successfully (image saved to MongoDB).")
        return True

    match = match_face_presence(name)
    print("Face match result:", match)
    return match
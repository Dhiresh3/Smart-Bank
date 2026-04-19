import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import os

MODEL_PATH = os.path.join("models", "face_detection.tflite")

print("Loading model...")
base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.FaceDetectorOptions(base_options=base_options)
detector = vision.FaceDetector.create_from_options(options)

print("Opening camera...")
cap = cv2.VideoCapture(0)
print("Camera opened:", cap.isOpened())
print("\n>>> CAMERA WINDOW SHOULD APPEAR. Look at your camera. Press Q to quit. <<<\n")

for _ in range(200):
    ret, frame = cap.read()
    if not ret:
        continue

    cv2.imshow("FACE CAPTURE TEST - Press Q to quit", frame)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                        data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    result = detector.detect(mp_image)

    if result.detections:
        print(f"FACE DETECTED! ({len(result.detections)} face(s))")
        cv2.waitKey(1000)
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Quit by user.")
        break
else:
    print("No face detected in time.")

cap.release()
cv2.destroyAllWindows()
print("Done.")

import requests
import cv2
import matplotlib.pyplot as plt
import os

image_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb"
image_path = "aurora_test.jpg"

if not os.path.exists(image_path):
    print("📥 Downloading image...")
    response = requests.get(image_url)
    with open(image_path, "wb") as f:
        f.write(response.content)
    print("✅ Image downloaded and saved as aurora_test.jpg")
else:
    print("📁 Image already exists. Skipping download.")

img = cv2.imread(image_path)
if img is None:
    print("❌ Failed to load image. Check the file format or path.")
else:
    print("✅ Image loaded successfully.")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    plt.imshow(img_rgb)
    plt.title("Aurora Borealis 🌌")
    plt.axis("off")
    plt.show()
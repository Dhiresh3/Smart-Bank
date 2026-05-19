import base64
import os
from pymongo import MongoClient

# Use the same connection as the app
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["smartbank"]
users_col = db["users"]

# Find the most recently updated or just any user with a face_image
user = users_col.find_one({"face_enrolled": True, "face_image": {"$exists": True}})

if user:
    img_base64 = user["face_image"]
    name = user.get("name", "Unknown")
    
    # Base64 string may or may not have a header
    if "," in img_base64:
        img_base64 = img_base64.split(",", 1)[1]
        
    img_data = base64.b64decode(img_base64)
    
    # Save to workspace so the assistant can display it
    output_path = "latest_face_from_mongo.jpg"
    with open(output_path, "wb") as f:
        f.write(img_data)
        
    print(f"SUCCESS: Saved face for user '{name}' to {output_path}")
else:
    print("NO_FACES_FOUND")

import base64
import os
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['smartbank']
users_col = db['users']
img_path = 'static/uploads/2178077c95c74afc96f9f4b94d5d2052.jpg'

if os.path.exists(img_path):
    with open(img_path, 'rb') as f:
        img_data = f.read()
    img_b64 = base64.b64encode(img_data).decode('utf-8')
    users_col.update_one({'name': 'TestUserRender'}, {'$set': {'face_enrolled': True, 'face_image': img_b64}}, upsert=True)
    print('Face injected successfully into local MongoDB.')
else:
    print('Image not found.')

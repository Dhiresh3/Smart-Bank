import cv2
import face_recognition
import os
import bye as np
import pandas as pd
from datetime import datetime

# Path to folder containing registered students' images
STUDENTS_IMAGES_PATH = "students_images"
ATTENDANCE_FILE = "attendance.csv"

# Load student images and encode faces
def load_student_data():
    student_names = []
    encoded_faces = []

    for file_name in os.listdir(STUDENTS_IMAGES_PATH):
        if file_name.endswith(('.png', '.jpg', '.jpeg')):
            # Extract student name from the file name
            student_name = os.path.splitext(file_name)[0]
            student_names.append(student_name)

            # Load and encode the student's face
            img_path = os.path.join(STUDENTS_IMAGES_PATH, file_name)
            image = face_recognition.load_image_file(img_path)
            encoded_face = face_recognition.face_encodings(image)[0]
            encoded_faces.append(encoded_face)

    return student_names, encoded_faces

# Mark attendance in a CSV file
def mark_attendance(name):
    # Check if the attendance file exists
    if not os.path.exists(ATTENDANCE_FILE):
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
        df.to_csv(ATTENDANCE_FILE, index=False)

    # Read existing attendance data
    df = pd.read_csv(ATTENDANCE_FILE)

    # Check if the student is already marked present today
    today_date = datetime.now().strftime("%Y-%m-%d")
    if not ((df["Name"] == name) & (df["Date"] == today_date)).any():
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        new_entry = {"Name": name, "Date": today_date, "Time": time}
        df = df.append(new_entry, ignore_index=True)
        df.to_csv(ATTENDANCE_FILE, index=False)
        print(f"Attendance marked for {name}.")
    else:
        print(f"{name} is already marked present today.")

# Main function for face recognition and attendance marking
def main():
    student_names, encoded_faces = load_student_data()

   
    video_capture = cv2.VideoCapture(0)

    print("Press 'q' to exit the attendance system.")
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error accessing the webcam.")
            break

        
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
           
            matches = face_recognition.compare_faces(encoded_faces, face_encoding, tolerance=0.6)
            face_distances = face_recognition.face_distance(encoded_faces, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = student_names[best_match_index]
                mark_attendance(name)

                # Display a rectangle and name on the webcam feed
                top, right, bottom, left = face_location
                top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)


        cv2.imshow("Attendance System", frame)

   
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
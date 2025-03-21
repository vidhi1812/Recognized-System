import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime, timedelta
from deepface import DeepFace
from retinaface import RetinaFace  # RetinaFace for face detection
from scipy.spatial.distance import cosine
from mark_attendance import markAttendance  # Ensure this function is defined
import threading

# Initialize attendance DataFrame with proper columns
columns = [
    'Employee Name', 'Entry Date', 'Entry Time', 'Exit Date', 'Exit Time', 'Total Duration'
]
attendance_path = 'Attendance.csv'

# Create a fresh DataFrame
try:
    if os.path.exists(attendance_path):
        df = pd.read_csv(attendance_path)
        if list(df.columns) != columns:
            df = pd.DataFrame(columns=columns)
            df.to_csv(attendance_path, index=False)
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(attendance_path, index=False)
except:
    df = pd.DataFrame(columns=columns)
    df.to_csv(attendance_path, index=False)

# Load Cameras
entry_cam = cv2.VideoCapture(0)  # Entry camera
exit_cam = cv2.VideoCapture(1)   # Exit camera

# Load and encode known faces from "Training_images" folder
training_images_path = "Training_images"

# Dictionary to store face embeddings for each person
face_representations = {}
classNames = []

# Loop through each person's folder
for person in os.listdir(training_images_path):
    person_folder = os.path.join(training_images_path, person)

    # Ensure it's a directory (not a file)
    if os.path.isdir(person_folder):
        print(f"Processing folder: {person}")
        classNames.append(person)

        # Loop through each image in the person's folder
        for image_file in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_file)

            # Ensure it's an image file
            if image_path.lower().endswith(('.jpg', '.png', '.jpeg')):
                print(f"Processing image: {image_path}")

                # Extract face representation (embedding) using ArcFace
                try:
                    embedding = DeepFace.represent(image_path, model_name='Facenet512', enforce_detection=False)[0]['embedding']
                    
                    # Store the first embedding found for that person
                    if person not in face_representations:
                        face_representations[person] = embedding

                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

print("Face representations successfully extracted!")

# Store entry and exit times
tracked_persons = {}  # Shared dictionary for tracking

# Function to calculate duration
def calculate_duration(entry_time, exit_time):
    duration = int((exit_time - entry_time).total_seconds())
    hr, remain = divmod(duration, 3600)
    min, sec = divmod(remain, 60)
    return f"{hr:02d}:{min:02d}:{sec:02d}"

# Function to process frames from the entry camera
def process_entry_camera():
    while True:
        ret, frame = entry_cam.read()
        if not ret:
            print("Failed to capture frame from entry camera")
            continue

        # Detect faces using RetinaFace
        faces = RetinaFace.detect_faces(frame)

        if not faces:
            print("No faces detected in entry camera")
            continue

        for face_id, face_data in faces.items():
            facial_area = face_data['facial_area']
            x, y, w, h = facial_area
            x, y = max(0, x), max(0, y)
            w, h = min(w, frame.shape[1] - x), min(h, frame.shape[0] - y)
            face_crop = frame[y:y+h, x:x+w]

            try:
                # Extract face embedding using ArcFace
                face_embedding = DeepFace.represent(face_crop, model_name='ArcFace', enforce_detection=False, detector_backend='retinaface')
                if not face_embedding or 'embedding' not in face_embedding[0]:
                    print("No valid embedding found in entry camera, skipping face.")
                    continue

                embedding = face_embedding[0]['embedding']
                distances = {name: cosine(face_representations[name], embedding) for name in classNames}
                recognized_name = min(distances, key=distances.get)

                if distances[recognized_name] < 0.55:  # Threshold for recognition
                    if recognized_name not in tracked_persons:
                        tracked_persons[recognized_name] = {'entry': datetime.now(), 'exit': None}
                        print(f"Marked Entry: {recognized_name}")

                    # Draw bounding box and name
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, recognized_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            except Exception as e:
                print(f"DeepFace Error in entry camera: {e}")
                continue

        cv2.imshow("Entry Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Function to process frames from the exit camera
def process_exit_camera():
    while True:
        ret, frame = exit_cam.read()
        if not ret:
            print("Failed to capture frame from exit camera")
            continue

        # Detect faces using RetinaFace
        faces = RetinaFace.detect_faces(frame)

        if not faces:
            print("No faces detected in exit camera")
            continue

        for face_id, face_data in faces.items():
            facial_area = face_data['facial_area']
            x, y, w, h = facial_area
            x, y = max(0, x), max(0, y)
            w, h = min(w, frame.shape[1] - x), min(h, frame.shape[0] - y)
            face_crop = frame[y:y+h, x:x+w]

            try:
                # Extract face embedding using ArcFace
                face_embedding = DeepFace.represent(face_crop, model_name='ArcFace', enforce_detection=False, detector_backend='retinaface')
                if not face_embedding or 'embedding' not in face_embedding[0]:
                    print("No valid embedding found in exit camera, skipping face.")
                    continue

                embedding = face_embedding[0]['embedding']
                distances = {name: cosine(face_representations[name], embedding) for name in classNames}
                recognized_name = min(distances, key=distances.get)

                if distances[recognized_name] < 0.55:  # Threshold for recognition
                    if recognized_name in tracked_persons and tracked_persons[recognized_name]['exit'] is None:
                        tracked_persons[recognized_name]['exit'] = datetime.now()
                        duration = calculate_duration(tracked_persons[recognized_name]['entry'], tracked_persons[recognized_name]['exit'])
                        markAttendance(recognized_name, tracked_persons[recognized_name]['entry'], tracked_persons[recognized_name]['exit'], duration, df, attendance_path)
                        print(f"Marked Exit: {recognized_name} - Duration: {duration}")

                    # Draw bounding box and name
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, recognized_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            except Exception as e:
                print(f"DeepFace Error in exit camera: {e}")
                continue

        cv2.imshow("Exit Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Start threads for entry and exit cameras
entry_thread = threading.Thread(target=process_entry_camera)
exit_thread = threading.Thread(target=process_exit_camera)

entry_thread.start()
exit_thread.start()

entry_thread.join()
exit_thread.join()

# Release cameras and close windows
entry_cam.release()
exit_cam.release()
cv2.destroyAllWindows()
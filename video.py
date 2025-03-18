import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime, timedelta
from deepface import DeepFace
from mtcnn import MTCNN
from scipy.spatial.distance import cosine 
from mark_attendance import markAttendance

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

# Load Camera
webcam = cv2.VideoCapture(0)  # Single camera setup

# Load and encode known faces from "Training_images" folde

# Define the path where your person folders are stored
training_images_path = "Training_images"

# Dictionary to store face embeddings for each person
face_representations = {}
classNames=[]

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

                # Extract face representation (embedding)
                try:
                    embedding = DeepFace.represent(image_path, model_name='Facenet', enforce_detection=False)[0]['embedding']
                    
                    # Store the first embedding found for that person
                    if person not in face_representations:
                        face_representations[person] = embedding

                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

# Print results
print("Face representations successfully extracted!")


# Store entry and exit times
tracked_persons = {}

# Function to calculate duration
def calculate_duration(entry_time, exit_time):
    duration = int((exit_time - entry_time).total_seconds())
    hr,remain=divmod(duration, 3600)
    min,sec=divmod(remain, 60)
    return f"{hr:02d}:{min:02d}:{sec:02d}"


######################  Use to be optimized the function as it fails in many scenerios ###################################
# Function to mark attnedance
# def markAttendance(name, entry_datetime, exit_datetime, duration):
#     global df
#     entry_date = entry_datetime.strftime('%Y-%m-%d')
#     entry_time = entry_datetime.strftime('%H:%M:%S')
#     exit_date = exit_datetime.strftime('%Y-%m-%d')
#     exit_time = exit_datetime.strftime('%H:%M:%S')

#     incomplete_entry = df[(df['Employee Name'] == name) & (df['Entry Date'] == entry_date) & pd.isna(df['Exit Date'])]
    
#     if not incomplete_entry.empty:
#         idx = incomplete_entry.index[0]
#         df.loc[idx, 'Exit Date'] = exit_date
#         df.loc[idx, 'Exit Time'] = exit_time
#         df.loc[idx, 'Total Duration'] = duration
#     else:
#         new_record = {
#             'Employee Name': name, 'Entry Date': entry_date, 'Entry Time': entry_time,
#             'Exit Date': exit_date, 'Exit Time': exit_time, 'Total Duration': duration
#         }
#         df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
#     df.to_csv(attendance_path, index=False)
#     print(f"Attendance marked for {name}")

detector=MTCNN()


while True:
    ret, frame = webcam.read()
    if not ret:
        print("Failed to capture frame from webcam")
        # continue  # Skip the current frame
    faces = detector.detect_faces(frame)
    if not faces:
        print("No faces detected")
        continue
    for face in faces:
        height, width, _ = frame.shape
        x, y, w, h = face['box']
        x, y = max(0, x), max(0, y)
        w, h = min(w, width - x), min(h, height - y)
        face_crop = frame[y:y+h, x:x+w]
        try:
            face_embedding = DeepFace.represent(face_crop, model_name='Facenet', enforce_detection=False, detector_backend='mtcnn')
            if not face_embedding or 'embedding' not in face_embedding[0]:
                print("No valid embedding found, skipping face.")
                continue
            embedding = face_embedding[0]['embedding']
            distances = {name: cosine(face_representations[name], embedding) for name in classNames}
            recognized_name = min(distances, key=distances.get)
            if distances[recognized_name] < 0.55:
                if recognized_name not in tracked_persons:
                    tracked_persons[recognized_name] = {'entry': datetime.now(), 'exit': None}
                    print(f"Marked Entry: {recognized_name}")
                elif tracked_persons[recognized_name]['exit'] is not None:
                    tracked_persons[recognized_name] = {'entry': datetime.now(), 'exit': None}
                    print(f"Marked Re-entry: {recognized_name}")
                elif tracked_persons[recognized_name]['exit'] is None:
                    tracked_persons[recognized_name]['exit'] = datetime.now()
                    duration = calculate_duration(tracked_persons[recognized_name]['entry'], tracked_persons[recognized_name]['exit'])
                    markAttendance(recognized_name, tracked_persons[recognized_name]['entry'], tracked_persons[recognized_name]['exit'], duration, df, attendance_path)
                    print(f"Marked Exit: {recognized_name} - Duration: {duration}")
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, recognized_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        except Exception as e:
            print(f"DeepFace Error: {e}")
            continue  
    cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
webcam.release()
cv2.destroyAllWindows()

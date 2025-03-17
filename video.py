import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime, timedelta
from deepface import DeepFace
from scipy.spatial.distance import cosine 

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

# Load and encode known faces from "Training_images" folder
path = 'Training_images'
classNames = []
myList = os.listdir(path)
face_representations = {}

for cl in myList:
    classNames.append(os.path.splitext(cl)[0])
    face_representations[os.path.splitext(cl)[0]] = DeepFace.represent(f'{path}/{cl}', model_name='Facenet', enforce_detection=False)[0]['embedding']

# Store entry and exit times
tracked_persons = {}

# Function to calculate duration
def calculate_duration(entry_time, exit_time):
    duration = int((exit_time - entry_time).total_seconds())
    hr,remain=divmod(duration, 3600)
    min,sec=divmod(remain, 60)
    return f"{hr:02d}:{min:02d}:{sec:02d}"


######################  Use to be optimized the function as it fails in many scenerios ###################################
# Function to mark attendance
def markAttendance(name, entry_datetime, exit_datetime, duration):
    global df
    entry_date = entry_datetime.strftime('%Y-%m-%d')
    entry_time = entry_datetime.strftime('%H:%M:%S')
    exit_date = exit_datetime.strftime('%Y-%m-%d')
    exit_time = exit_datetime.strftime('%H:%M:%S')

    incomplete_entry = df[(df['Employee Name'] == name) & (df['Entry Date'] == entry_date) & pd.isna(df['Exit Date'])]
    
    if not incomplete_entry.empty:
        idx = incomplete_entry.index[0]
        df.loc[idx, 'Exit Date'] = exit_date
        df.loc[idx, 'Exit Time'] = exit_time
        df.loc[idx, 'Total Duration'] = duration
    else:
        new_record = {
            'Employee Name': name, 'Entry Date': entry_date, 'Entry Time': entry_time,
            'Exit Date': exit_date, 'Exit Time': exit_time, 'Total Duration': duration
        }
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
    df.to_csv(attendance_path, index=False)
    print(f"Attendance marked for {name}")

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    ret, frame = webcam.read()
    if not ret:
        print("Failed to capture frame from webcam")
        continue
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) == 0:
        print("No faces detected")
    else:
        for (x, y, w, h) in faces:
            face_crop = frame[y:y+h, x:x+w]
            try:
                face_embedding = DeepFace.represent(face_crop, model_name='Facenet', enforce_detection=False)
                if face_embedding:
                    embedding = face_embedding[0]['embedding']
                    distances ={name:cosine(face_representations[name],embedding) for name in classNames} 
                    recognized_name = min(distances, key=distances.get)
                    print(f"Recognition confidence: {distances[recognized_name]}")
                    if distances[recognized_name] < 0.7:
                        if recognized_name not in tracked_persons:
                            tracked_persons[recognized_name] = {'entry': datetime.now(), 'exit': None}
                            print(f"Marked Entry: {recognized_name}")
                        elif tracked_persons[recognized_name]['exit'] is None:
                            tracked_persons[recognized_name]['exit'] = datetime.now()
                            duration = calculate_duration(tracked_persons[recognized_name]['entry'], tracked_persons[recognized_name]['exit'])
                            markAttendance(recognized_name, tracked_persons[recognized_name]['entry'], tracked_persons[recognized_name]['exit'], duration)
                            print(f"Marked Exit: {recognized_name} - Duration: {duration}")
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, recognized_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            except Exception as e:
                print(f"DeepFace Error: {e}")
    
    cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

webcam.release()
cv2.destroyAllWindows()

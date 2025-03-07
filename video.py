import cv2
import face_recognition
import numpy as np
import os
import pandas as pd
from datetime import datetime, timedelta

# Initialize attendance DataFrame with proper columns
columns = [
    'Employee Name',
    'Entry Date',
    'Entry Time',
    'Exit Date',
    'Exit Time',
    'Total Duration'
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
entry_cam = cv2.VideoCapture(1)  # Entry camera
exit_cam = cv2.VideoCapture(0)   # Exit camera

# Load and encode known faces from "Training_images" folder
path = 'Training_images'
images = []
classNames = []
myList = os.listdir(path)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    if curImg is not None:
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encodeList.append(encodings[0])
    return encodeList

encodeListKnown = findEncodings(images)
print('Encoding Complete')

# Store entry and exit times, and last detection times
tracked_persons = {}
last_detection_times = {}  # To prevent multiple detections
DETECTION_COOLDOWN = 5  # Seconds between allowed detections

def calculate_duration(entry_time, exit_time):
    duration = (exit_time - entry_time).total_seconds()
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def check_existing_entry(name, entry_date):
    """Check if person already has an incomplete entry for today"""
    today_entries = df[
        (df['Employee Name'] == name) & 
        (df['Entry Date'] == entry_date) & 
        (pd.isna(df['Exit Date']))
    ]
    return not today_entries.empty

def check_duplicate_exit(name, exit_date, exit_time):
    """Check if person already has an exit record for this time"""
    today_exits = df[
        (df['Employee Name'] == name) & 
        (df['Exit Date'] == exit_date) & 
        (df['Exit Time'] == exit_time)
    ]
    return not today_exits.empty

def can_detect_person(name, current_time):
    """Check if enough time has passed since last detection"""
    if name in last_detection_times:
        time_since_last = (current_time - last_detection_times[name]).total_seconds()
        return time_since_last >= DETECTION_COOLDOWN
    return True

def process_entries(faces_data, current_time):
    """Process multiple entries simultaneously"""
    detected_names = []
    for face_encoding in faces_data:
        matches = face_recognition.compare_faces(encodeListKnown, face_encoding)
        if True in matches:
            matchIndex = matches.index(True)
            name = classNames[matchIndex].upper()
            entry_date = current_time.strftime('%Y-%m-%d')
            
            # Check if we can detect this person now
            if can_detect_person(name, current_time):
                if not check_existing_entry(name, entry_date):
                    tracked_persons[name] = {'entry': current_time, 'exit': None}
                    last_detection_times[name] = current_time
                    print(f"{name} Entered at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    detected_names.append(name)
    return detected_names

def process_exits(faces_data, current_time):
    """Process multiple exits simultaneously"""
    for face_encoding in faces_data:
        matches = face_recognition.compare_faces(encodeListKnown, face_encoding)
        if True in matches:
            matchIndex = matches.index(True)
            name = classNames[matchIndex].upper()
            
            # Check if we can detect this person now
            if can_detect_person(name, current_time):
                if name in tracked_persons and tracked_persons[name]['exit'] is None:
                    tracked_persons[name]['exit'] = current_time
                    last_detection_times[name] = current_time
                    duration = calculate_duration(
                        tracked_persons[name]['entry'],
                        tracked_persons[name]['exit']
                    )
                    print(f"{name} Exited at {current_time.strftime('%Y-%m-%d %H:%M:%S')} - Duration: {duration}")
                    markAttendance(
                        name,
                        tracked_persons[name]['entry'],
                        tracked_persons[name]['exit'],
                        duration
                    )

def markAttendance(name, entry_datetime, exit_datetime, duration):
    global df
    
    entry_date = entry_datetime.strftime('%Y-%m-%d')
    entry_time = entry_datetime.strftime('%H:%M:%S')
    exit_date = exit_datetime.strftime('%Y-%m-%d')
    exit_time = exit_datetime.strftime('%H:%M:%S')

    # Check for duplicate exit
    if check_duplicate_exit(name, exit_date, exit_time):
        print(f"Exit already recorded for {name} at {exit_time}")
        return

    # Find incomplete entry for today
    incomplete_entry = df[
        (df['Employee Name'] == name) & 
        (df['Entry Date'] == entry_date) & 
        (pd.isna(df['Exit Date']))
    ]

    if not incomplete_entry.empty:
        # Update existing entry with exit information
        idx = incomplete_entry.index[0]
        df.loc[idx, 'Exit Date'] = exit_date
        df.loc[idx, 'Exit Time'] = exit_time
        df.loc[idx, 'Total Duration'] = duration
    else:
        # Create new record
        new_record = {
            'Employee Name': name,
            'Entry Date': entry_date,
            'Entry Time': entry_time,
            'Exit Date': exit_date,
            'Exit Time': exit_time,
            'Total Duration': duration
        }
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
    # Save the updated DataFrame to CSV
    df.to_csv(attendance_path, index=False)
    print(f"Attendance marked for {name}")

while True:
    # Read frames from both cameras
    ret_entry, entry_frame = entry_cam.read()
    ret_exit, exit_frame = exit_cam.read()

    if not ret_entry or not ret_exit:
        break

    current_time = datetime.now()

    # Process entry camera
    entry_rgb = cv2.cvtColor(entry_frame, cv2.COLOR_BGR2RGB)
    entry_faces = face_recognition.face_locations(entry_rgb)
    entry_encodings = face_recognition.face_encodings(entry_rgb, entry_faces)

    # Process exit camera
    exit_rgb = cv2.cvtColor(exit_frame, cv2.COLOR_BGR2RGB)
    exit_faces = face_recognition.face_locations(exit_rgb)
    exit_encodings = face_recognition.face_encodings(exit_rgb, exit_faces)

    # Process all entries simultaneously
    if entry_encodings:
        process_entries(entry_encodings, current_time)

    # Process all exits simultaneously
    if exit_encodings:
        process_exits(exit_encodings, current_time)

    # Draw rectangles around detected faces
    for (top, right, bottom, left) in entry_faces:
        cv2.rectangle(entry_frame, (left, top), (right, bottom), (0, 255, 0), 2)

    for (top, right, bottom, left) in exit_faces:
        cv2.rectangle(exit_frame, (left, top), (right, bottom), (0, 0, 255), 2)

    # Show minimal preview windows with face detection
    cv2.imshow("Entry Camera", cv2.resize(entry_frame, (320, 240)))
    cv2.imshow("Exit Camera", cv2.resize(exit_frame, (320, 240)))

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Save final DataFrame before closing
df.to_csv(attendance_path, index=False)

entry_cam.release()
exit_cam.release()
cv2.destroyAllWindows()

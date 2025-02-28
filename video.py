import cv2
import numpy as np
import face_recognition
import reactangle , mark_attendance
import os
import pandas as pd
from datetime import datetime 
from pathlib import Path

# Ensure the video directory exists
# video_dir = "Recorded_Videos"
# if not os.path.exists(video_dir):
#     os.makedirs(video_dir)
video_dir="Recorded_Videos"
Path(video_dir).mkdir(exist_ok=True)
# Initialize video capture  
cap = cv2.VideoCapture(0)

# Get video properties
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define codec and create VideoWriter object
video_filename = os.path.join(video_dir, "video_" + datetime.now().strftime("%Y_%B_%d_%I_%M_%S %p") + ".mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' if 'mp4v' doesn't work
out = cv2.VideoWriter(video_filename, fourcc, 30.0, (frame_width, frame_height))

# Face recognition setup
path = 'Training_images'
images = []
classNames = []
myList = os.listdir(path)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    if curImg is not None:  # Ensure valid image
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:  # Check if encoding exists
            encodeList.append(encodings[0])
    return encodeList



encodeListKnown = findEncodings(images)
print('Encoding Complete')

tracked_persons = {}
### Turn time into readable format 
def readable_time(seconds):
            hours=seconds//3600
            min=(seconds%3600)/60
            sec=seconds%60
            return f"{int(hours)}h {int(min)}m {int(sec)}s"
while True:
    success, img = cap.read()
    if not success:
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    detected_names = set()
    
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis) if faceDis.size > 0 else None

        if matchIndex is not None and matches[matchIndex]:
            name = classNames[matchIndex].upper()
            detected_names.add(name)

            # Draw rectangle and name
            reactangle.rectangle(img,faceLoc,name)
            
            # Track entry and exit
            if name not in tracked_persons:    
                tracked_persons[name] = {'entry': datetime.now(), 'exit': None}
                mark_attendance.markAttendance(name, "Entry")

    # Check for exits
    for name in list(tracked_persons.keys()):
        if name not in detected_names and tracked_persons[name]['exit'] is None:
            tracked_persons[name]['exit'] = datetime.now()
            duration = (tracked_persons[name]['exit'] - tracked_persons[name]['entry']).total_seconds()
            total_time=readable_time(duration)
            mark_attendance.markAttendance(name, "Exit")


    # Write frame to video file
    out.write(img)

    # Display the recording in real time
    cv2.imshow('Recording...', img)

    # Press 'q' to stop recording
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

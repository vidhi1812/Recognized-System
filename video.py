import cv2
import numpy as np
import face_recognition
import os
import pandas as pd
from datetime import datetime

# Ensure the video directory exists
video_dir = "Recorded_Videos"
if not os.path.exists(video_dir):
    os.makedirs(video_dir)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Get video properties
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define codec and create VideoWriter object
video_filename = os.path.join(video_dir, "video_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' if 'mp4v' doesn't work
out = cv2.VideoWriter(video_filename, fourcc, 20.0, (frame_width, frame_height))

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

def markAttendance(name, status):
    attendance_path = 'Attendance.csv'

    if not os.path.isfile(attendance_path):
        with open(attendance_path, 'w') as f:
            f.write('Name,Status,Time\n')

    with open(attendance_path, 'a') as f:
        now = datetime.now()
        dtString = now.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{name},{status},{dtString}\n')

encodeListKnown = findEncodings(images)
print('Encoding Complete')

person_present = False
entry_time = None

while True:
    success, img = cap.read()
    if not success:
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    person_detected = False
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis) if faceDis.size > 0 else None

        if matchIndex is not None and matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            # Person detected, mark attendance
            if not person_present:
                markAttendance(name, "Entry")
                entry_time = datetime.now()
                person_present = True
            person_detected = True

    # If person leaves, mark exit
    if person_present and not person_detected:
        exit_time = datetime.now()
        duration = (exit_time - entry_time).total_seconds()
        markAttendance(name, f"Exit - Duration: {duration} sec")
        person_present = False

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

# Print saved video location


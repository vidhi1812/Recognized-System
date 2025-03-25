import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime
from deepface import DeepFace
from retinaface import RetinaFace
from scipy.spatial.distance import cosine
import threading
import logging
import requests

# API URLs
url1 = "http://localhost:8000/api/attendance/entryExit?type=entry"
url2 = "http://localhost:8000/api/attendance/entryExit?type=exit"
headers = {"Content-Type": "application/json"}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FaceRecognitionSystem:
    def __init__(self, training_images_path="Training_images", attendance_path="Attendance.csv"):
        self.training_images_path = training_images_path
        self.attendance_path = attendance_path
        self.face_representations = {}
        self.classNames = []
        self.tracked_persons = {}
        self.tracked_persons_lock = threading.Lock()
        self.df = self.initialize_attendance()
        self.train_model()

    def initialize_attendance(self):
        columns = ['Employee Name', 'Entry DateTime', 'Exit DateTime', 'Total Duration']
        if not os.path.exists(self.attendance_path):
            logging.info("Creating new attendance file.")
            return pd.DataFrame(columns=columns).to_csv(self.attendance_path, index=False)
        df = pd.read_csv(self.attendance_path)
        if list(df.columns) != columns:
            logging.warning("Attendance file has incorrect columns. Recreating it.")
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.attendance_path, index=False)
        return df

    def train_model(self):
        self.face_representations.clear()
        self.classNames.clear()
        for person in os.listdir(self.training_images_path):
            person_folder = os.path.join(self.training_images_path, person)
            if os.path.isdir(person_folder):
                logging.info(f"Processing folder: {person}")
                self.classNames.append(person)
                for image_file in os.listdir(person_folder):
                    image_path = os.path.join(person_folder, image_file)
                    if image_path.lower().endswith(('.jpg', '.png', '.jpeg')):
                        try:
                            embedding = DeepFace.represent(image_path, model_name='ArcFace', enforce_detection=False)[0]['embedding']
                            if person not in self.face_representations:
                                self.face_representations[person] = embedding
                        except Exception as e:
                            logging.error(f"Error processing {image_path}: {e}")
        logging.info("Model training completed!")

    def calculate_duration(self, entry_time, exit_time):
        duration = int((exit_time - entry_time).total_seconds())
        hr, min_remain = divmod(duration, 3600)
        min, sec = divmod(min_remain, 60)
        return f"{hr:02d}:{min:02d}:{sec:02d}"

    def mark_attendance(self, name, entry_time=None, exit_time=None):
        if entry_time:
            entry_str = entry_time.strftime('%Y-%m-%d %H:%M:%S')
            new_record = {'Employee Name': name, 'Entry DateTime': entry_str, 'Exit DateTime': '', 'Total Duration': ''}
            self.df = pd.concat([self.df, pd.DataFrame([new_record])], ignore_index=True)
            self.df.to_csv(self.attendance_path, index=False)
            logging.info(f"Entry marked: {name} at {entry_str}")
            requests.post(ENTRY_URL, json={"name": name, "entry": entry_str}, headers=HEADERS)

        if exit_time:
            exit_str = exit_time.strftime('%Y-%m-%d %H:%M:%S')
            last_entry_index = self.df[(self.df['Employee Name'] == name) & (self.df['Exit DateTime'] == '')].index.max()
            if pd.notna(last_entry_index):
                self.df.at[last_entry_index, 'Exit DateTime'] = exit_str
                entry_time = datetime.strptime(self.df.at[last_entry_index, 'Entry DateTime'], '%Y-%m-%d %H:%M:%S')
                duration = self.calculate_duration(entry_time, exit_time)
                self.df.at[last_entry_index, 'Total Duration'] = duration
                self.df.to_csv(self.attendance_path, index=False)
                logging.info(f"Exit marked: {name} at {exit_str} - Duration: {duration}")
                requests.post(EXIT_URL, json={"name": name, "exit": exit_str}, headers=HEADERS)

    def process_camera(self, cam, cam_type):
        while True:
            ret, frame = cam.read()
            if not ret:
                logging.error(f"Failed to capture frame from {cam_type} camera")
                continue

            faces = RetinaFace.detect_faces(frame)
            if not faces:
                logging.info(f"No faces detected in {cam_type} camera")
                continue

            for face_id, face_data in faces.items():
                x, y, w, h = face_data['facial_area']
                face_crop = frame[max(0, y):y+h, max(0, x):x+w]

                try:
                    face_embedding = DeepFace.represent(face_crop, model_name='ArcFace', enforce_detection=False, detector_backend='retinaface')
                    if not face_embedding or 'embedding' not in face_embedding[0]:
                        logging.warning(f"No valid embedding found in {cam_type} camera, skipping face.")
                        continue

                    embedding = face_embedding[0]['embedding']
                    distances = {name: cosine(self.face_representations[name], embedding) for name in self.classNames}
                    recognized_name = min(distances, key=distances.get)

                    if distances[recognized_name] < 0.55:
                        with self.tracked_persons_lock:
                            if cam_type == 'entry' and recognized_name not in self.tracked_persons:
                                entry_time = datetime.now()
                                self.tracked_persons[recognized_name] = {'entry': entry_time, 'exit': None}
                                self.mark_attendance(recognized_name, entry_time=entry_time)
                                payload={
                                    "name":recognized_name,
                                    "entry":entry_time.strftime('%Y-%m-%d %H:%M:%S')
                                }
                                print(payload)
                                res=requests.post(url1, json=payload,headers=headers)
                            elif cam_type == 'exit' and recognized_name in self.tracked_persons and self.tracked_persons[recognized_name]['exit'] is None:
                                exit_time = datetime.now()
                                self.tracked_persons[recognized_name]['exit'] = exit_time
                                self.mark_attendance(recognized_name, exit_time=exit_time)
                                payload={
                                    "name":recognized_name,
                                    "exit":exit_time.strftime('%Y-%m-%d  %H:%M:%S')
                                }
                                print(payload)
                                res=requests.post(url1, json=payload,headers=headers)
                                print(res.text)
                                print(res.json())
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0) if cam_type == 'entry' else (0, 0, 255), 2)
                        cv2.putText(frame, recognized_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0) if cam_type == 'entry' else (0, 0, 255), 2)
                except Exception as e:
                    logging.error(f"DeepFace Error in {cam_type} camera: {e}")
                    continue

            cv2.imshow(f"{cam_type.capitalize()} Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

if __name__ == "__main__":
    face_system = FaceRecognitionSystem()
    entry_thread = threading.Thread(target=face_system.process_camera, args=(cv2.VideoCapture(0), 'entry'))
    exit_thread = threading.Thread(target=face_system.process_camera, args=(cv2.VideoCapture(1), 'exit'))
    entry_thread.start()
    exit_thread.start()
    entry_thread.join()
    exit_thread.join()
    cv2.destroyAllWindows()

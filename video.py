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

url="http://localhost:8000/api/attendance/entryExit?type=entry"
url1="http://localhost:8000/api/attendance/entryExit?type=exit"
headers={"Content-Type": "application/json"}



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
        try:
            columns = [
                'Employee Name', 'Entry Date', 'Entry Time', 'Exit Date', 'Exit Time', 'Total Duration'
            ]
            
            # Check if file exists
            if not os.path.exists(self.attendance_path):
                logging.info(f"Creating new attendance file: {self.attendance_path}")
                df = pd.DataFrame(columns=columns)
                df.to_csv(self.attendance_path, index=False)
                return df
            
            # If file exists, read it
            df = pd.read_csv(self.attendance_path)
            
            # Check if columns match
            if list(df.columns) != columns:
                logging.info("Updating attendance file with correct columns")
                df = pd.DataFrame(columns=columns)
                df.to_csv(self.attendance_path, index=False)
            
            return df
            
        except Exception as e:
            logging.error(f"Error initializing attendance file: {e}")
            # Create new file if there's an error
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.attendance_path, index=False)
            return df

    def train_model(self):
        """Train the model using images from the training directory."""
        self.face_representations = {}
        self.classNames = []
        for person in os.listdir(self.training_images_path):
            person_folder = os.path.join(self.training_images_path, person)
            if os.path.isdir(person_folder):
                logging.info(f"Processing folder: {person}")
                self.classNames.append(person)
                for image_file in os.listdir(person_folder):
                    image_path = os.path.join(person_folder, image_file)
                    if image_path.lower().endswith(('.jpg', '.png', '.jpeg')):
                        logging.info(f"Processing image: {image_path}")
                        try:
                            embedding = DeepFace.represent(image_path, model_name='ArcFace', enforce_detection=False)[0]['embedding']
                            if person not in self.face_representations:
                                self.face_representations[person] = embedding
                        except Exception as e:
                            logging.error(f"Error processing {image_path}: {e}")
        logging.info("Face representations successfully extracted!")

    def calculate_duration(self, entry_time, exit_time):
        duration = int((exit_time - entry_time).total_seconds())
        hr, remain = divmod(duration, 3600)
        min, sec = divmod(remain, 60)
        return f"{hr:02d}:{min:02d}:{sec:02d}"

    def mark_attendance(self, name, entry_time=None, exit_time=None):
        if entry_time:
             entry_datetime = entry_time.strftime('%Y-%m-%d %H:%M:%S')
             new_record = {
                'Employee Name': name,
                'Entry DateTime': entry_datetime,
                'Exit DateTime':'',
                'Total Duration': ''
            }
             self.df = pd.concat([self.df, pd.DataFrame([new_record])], ignore_index=True)
             self.df.to_csv(self.attendance_path, index=False)
             logging.info(f"Entry marked for {name} at {entry_datetime}")

        if exit_time:
            exit_datetime = exit_time.strftime('%Y-%m-%d %H:%M:%S')
            last_entry_index = self.df[(self.df['Employee Name'] == name) & (self.df['Exit DateTime'] == '')].index.max()
            if pd.notna(last_entry_index):
                self.df.at[last_entry_index, 'Exit DateTime'] = exit_datetime
                
                entry_time = datetime.strptime(self.df.at[last_entry_index, 'Entry DateTime'] , '%Y-%m-%d %H:%M:%S')
                duration = self.calculate_duration(entry_time, exit_time)
                self.df.at[last_entry_index, 'Total Duration'] = duration
                self.df.to_csv(self.attendance_path, index=False)
                logging.info(f"Exit marked for {name} at {exit_datetime} - Duration: {duration}")

    def process_entry_camera(self, entry_cam):
        while True:
            ret, frame = entry_cam.read()
            if not ret:
                logging.error("Failed to capture frame from entry camera")
                continue

            faces = RetinaFace.detect_faces(frame)
            if not faces:
                logging.info("No faces detected in entry camera")
                continue

            for face_id, face_data in faces.items():
                facial_area = face_data['facial_area']
                x, y, w, h = facial_area
                x, y = max(0, x), max(0, y)
                w, h = min(w, frame.shape[1] - x), min(h, frame.shape[0] - y)
                face_crop = frame[y:y+h, x:x+w]

                try:
                    face_embedding = DeepFace.represent(face_crop, model_name='ArcFace', enforce_detection=False, detector_backend='retinaface')
                    if not face_embedding or 'embedding' not in face_embedding[0]:
                        logging.warning("No valid embedding found in entry camera, skipping face.")
                        continue

                    embedding = face_embedding[0]['embedding']
                    distances = {name: cosine(self.face_representations[name], embedding) for name in self.classNames}
                    recognized_name = min(distances, key=distances.get)

                    if distances[recognized_name] < 0.4:
                        with self.tracked_persons_lock:
                            if recognized_name not in self.tracked_persons:
                                entry_time = datetime.now()
                                self.tracked_persons[recognized_name] = {'entry': entry_time, 'exit': None}
                                self.mark_attendance(recognized_name, entry_time=entry_time)
                               
                                payload={
                                    "name":recognized_name,
                                    "entry":entry_time.strftime('%Y-%m-%d %H:%M:%S')
                                }
                                print(payload)
                                res=requests.post(url, json=payload,headers=headers)
                                print(res.text)
                                print(res.json())
                                logging.info(f"Marked Entry: {recognized_name}")

                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, recognized_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                except Exception as e:
                    logging.error(f"DeepFace Error in entry camera: {e}")
                    continue

            cv2.imshow("Entry Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def process_exit_camera(self, exit_cam):
        while True:
            ret, frame = exit_cam.read()
            if not ret:
                logging.error("Failed to capture frame from exit camera")
                continue

            faces = RetinaFace.detect_faces(frame)
            if not faces:
                logging.info("No faces detected in exit camera")
                continue

            for face_id, face_data in faces.items():
                facial_area = face_data['facial_area']
                x, y, w, h = facial_area
                x, y = max(0, x), max(0, y)
                w, h = min(w, frame.shape[1] - x), min(h, frame.shape[0] - y)
                face_crop = frame[y:y+h, x:x+w]

                try:
                    face_embedding = DeepFace.represent(face_crop, model_name='ArcFace', enforce_detection=False, detector_backend='retinaface')
                    if not face_embedding or 'embedding' not in face_embedding[0]:
                        logging.warning("No valid embedding found in exit camera, skipping face.")
                        continue

                    embedding = face_embedding[0]['embedding']
                    distances = {name: cosine(self.face_representations[name], embedding) for name in self.classNames}
                    recognized_name = min(distances, key=distances.get)

                    if distances[recognized_name] < 0.4:
                        with self.tracked_persons_lock:
                            if recognized_name in self.tracked_persons and self.tracked_persons[recognized_name]['exit'] is None:
                                self.tracked_persons[recognized_name]['exit'] = datetime.now()
                                self.mark_attendance(recognized_name, exit_time=datetime.now())
                                current_datetime1=datetime.now()
                                payload={
                                    "name":recognized_name,
                                    "exit":current_datetime1
                                }
                                res=requests.post(url1, json=payload,headers=headers)
                                print(res.text)
                                print(res.json())
                                logging.info(f"Marked Exit: {recognized_name}")

                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(frame, recognized_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                except Exception as e:
                    logging.error(f"DeepFace Error in exit camera: {e}")
                    continue

            cv2.imshow("Exit Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Main Execution
if __name__ == "__main__":
    face_system = FaceRecognitionSystem()

    entry_cam = cv2.VideoCapture(0)  # Entry camera
    exit_cam = cv2.VideoCapture(1)   # Exit camera

    entry_thread = threading.Thread(target=face_system.process_entry_camera, args=(entry_cam,))
    exit_thread = threading.Thread(target=face_system.process_exit_camera, args=(exit_cam,))

    entry_thread.start()
    exit_thread.start()

    entry_thread.join()
    exit_thread.join()

    entry_cam.release()
    exit_cam.release()
    cv2.destroyAllWindows()
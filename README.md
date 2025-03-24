# AI Automated Attendance System

A robust face recognition-based attendance system that supports multiple face recognition models and can be integrated with web applications.

## Features

- Multiple face recognition models:
  - DeepFace
  - ArcFace
  - RetinaFace
  - FaceNet
- Dual camera support (entry and exit)
- Real-time face detection and recognition
- Automatic attendance marking
- Configurable recognition thresholds
- Detailed logging system
- CSV-based attendance records
- Thread-safe processing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-attendance-system
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Directory Structure

```
ai-attendance-system/
├── face_database/           # Store face images for each person
│   ├── person1/
│   │   ├── image1.jpg
│   │   └── image2.jpg
│   └── person2/
│       ├── image1.jpg
│       └── image2.jpg
├── ai_attendance_system.py  # Main system code
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
└── Attendance.csv         # Attendance records
```

## Configuration

The system uses a `config.json` file for configuration. You can modify the following settings:

```json
{
    "models": {
        "deepface": {"enabled": true, "threshold": 0.4},
        "arcface": {"enabled": true, "threshold": 0.6},
        "retinaface": {"enabled": true, "threshold": 0.5},
        "facenet": {"enabled": true, "threshold": 0.7}
    },
    "camera": {
        "entry": 0,
        "exit": 1,
        "width": 640,
        "height": 480
    },
    "database": {
        "path": "face_database",
        "attendance_file": "Attendance.csv"
    },
    "recognition": {
        "min_confidence": 0.7,
        "max_faces": 10,
        "processing_interval": 0.5
    }
}
```

## Usage

1. Prepare face database:
   - Create a folder for each person in the `face_database` directory
   - Add multiple clear face images of each person
   - Images should be in JPG, PNG, or JPEG format

2. Run the system:
```bash
python ai_attendance_system.py
```

3. The system will:
   - Initialize all enabled face recognition models
   - Load face embeddings from the database
   - Start processing both entry and exit cameras
   - Display real-time recognition results
   - Save attendance records to CSV

4. Press 'q' to quit the application

## Web Integration

To integrate with a web application:

1. Import the `AIAttendanceSystem` class:
```python
from ai_attendance_system import AIAttendanceSystem
```

2. Initialize the system:
```python
system = AIAttendanceSystem()
```

3. Start the system:
```python
system.start()
```

4. Access attendance data:
```python
# Read attendance CSV
df = pd.read_csv('Attendance.csv')
```

## Logging

The system logs all activities to `attendance_system.log`. You can monitor:
- Model initialization
- Face detection and recognition
- Attendance marking
- Errors and exceptions

## Performance Optimization

- The system processes every 3rd frame to reduce CPU usage
- Multiple face recognition models run in parallel
- Thread-safe processing for dual cameras
- Configurable processing intervals

## Troubleshooting

1. If face recognition is not working:
   - Check if face images are clear and well-lit
   - Adjust recognition thresholds in config.json
   - Ensure proper camera setup

2. If system is slow:
   - Reduce processing frequency in config.json
   - Disable some face recognition models
   - Lower camera resolution

3. If cameras are not detected:
   - Check camera indices in config.json
   - Ensure cameras are properly connected
   - Verify camera permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 

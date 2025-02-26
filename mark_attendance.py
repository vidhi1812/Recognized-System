import os
from datetime import datetime

def markAttendance(name, status,file_path):
    
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write('Name,Status,Time\n')

    with open(file_path, 'a') as f:
        now = datetime.now()
        dtString = now.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'{name},{status},{dtString}\n')

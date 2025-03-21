import pandas as pd
from datetime import datetime,timedelta
from timezone import maketime_zone
import pytz

def markAttendance(name, entry_datetime, exit_datetime, duration, df, attendance_path):
    # Convert entry and exit times to local timezone strings
    entry_date = entry_datetime.strftime('%Y-%m-%d')
    entry_time = entry_datetime.strftime('%H:%M:%S')
    exit_date = exit_datetime.strftime('%Y-%m-%d')
    exit_time = exit_datetime.strftime('%H:%M:%S')

    # Find incomplete entries for the same person on the same day
    recent_entries = df[
        (df['Employee Name'] == name) & 
        (df['Entry Date'] == entry_date) & 
        pd.isna(df['Exit Date'])
    ]
    
    if not recent_entries.empty:
        # Update the existing entry
        idx = recent_entries.index[0]
        df.loc[idx, 'Exit Date'] = exit_date
        df.loc[idx, 'Exit Time'] = exit_time
        df.loc[idx, 'Total Duration'] = duration
    else:
        # Create new entry
        new_record = {
            'Employee Name': name,
            'Entry Date': entry_date,
            'Entry Time': entry_time,
            'Exit Date': exit_date,
            'Exit Time': exit_time,
            'Total Duration': duration
        }
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    
    # Save to CSV
    df.to_csv(attendance_path, index=False)
    print(f"Attendance marked for {name}")



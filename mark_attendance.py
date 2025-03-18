import pandas as pd
from datetime import datetime,timedelta
from timezone import maketime_zone
import pytz

def markAttendance(name, entry_datetime, exit_datetime, duration,df,attendance_path):

    #  Avoid clock drift
    entry_datetime=maketime_zone(entry_datetime)
    exit_datetime=maketime_zone(exit_datetime)
    
    # Formatting dates and times
    entry_date, entry_time = entry_datetime.strftime('%Y-%m-%d'), entry_datetime.strftime('%H:%M:%S')
    exit_date, exit_time = exit_datetime.strftime('%Y-%m-%d'), exit_datetime.strftime('%H:%M:%S')

 # Exit before entry
    if exit_datetime < entry_datetime:
     print(f"Error: Exit time {exit_time} is before entry time {entry_time} for {name}. Skipping entry.")
     return df
 
 # Duplicate entry
    recent_entries = df[(df['Employee Name'] == name) & (df['Entry Date'] == entry_date)]
    if not recent_entries.empty:
     last_entry_time = pd.to_datetime(recent_entries['Entry Time'].max()).astimezone(pytz.UTC)
     if (entry_datetime - last_entry_time).total_seconds() < 60:
        print(f"Duplicate entry detected for {name}. Skipping.")
        return df
# Handle missing logouts
    incomplete_entry = df[(df['Employee Name'] == name) & (df['Entry Date'] == entry_date) & df['Exit Date'].isna()]
    if not incomplete_entry.empty:
     idx = incomplete_entry.index[0]
     df.loc[idx, 'Exit Date'] = exit_date
     df.loc[idx, 'Exit Time'] = exit_time
     df.loc[idx, 'Total Duration'] = duration
    else:
     prev_day_entry = df[(df['Employee Name'] == name) & df['Exit Date'].isna()]
     if not prev_day_entry.empty:
        prev_idx = prev_day_entry.index[0]
        df.loc[prev_idx, 'Exit Date'] = entry_date  # Assuming they left on the next entry's day
        df.loc[prev_idx, 'Exit Time'] = "18:00:00"
        df.loc[prev_idx, 'Total Duration'] = str(timedelta(hours=9))  # Example: Default work hours
    
    
    df.loc[len(df)] = [name, entry_date, entry_time, exit_date, exit_time, duration]
    
    try:
     df.to_csv(attendance_path, index=False)
    except Exception as e:
     print(f"Error saving attendance file: {e}")
     
    
    print(f"Attendance marked for {name}")
    return df



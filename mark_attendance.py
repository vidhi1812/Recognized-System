import pandas as pd
from datetime import datetime
import os
from pathlib import Path

attendance_file = Path("Attendance.csv")

# Ensure the file exists with correct headers
def initialize_attendance_file():
    if not attendance_file.exists() or attendance_file.stat().st_size == 0:
        df_init = pd.DataFrame(columns=["Name", "Entry Time", "Exit Time", "Total Hours", "Status"])
        df_init.to_csv(attendance_file, index=False)
        

def markAttendance(name, status):
    now = datetime.now()
    
    try:
        df = pd.read_csv(attendance_file)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["Name", "Entry Time", "Exit Time", "Total Hours", "Status"])

    # Ensure columns exist
    required_columns = ["Name", "Entry Time", "Exit Time", "Total Hours", "Status"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    today_str = now.strftime("%Y-%m-%d")
    
    # Check if the person is already marked today
    user_data = df[(df["Name"] == name) & (df["Entry Time"].astype(str).str.startswith(today_str, na=False))]

    if status == "Entry":
        if user_data.empty:
            df.loc[len(df)] = [name, now.strftime("%Y-%m-%d %H:%M:%S"), "", "", "Present"]
        else:
            return  # Already marked, no need to do anything
    else:  # Exit
        if not user_data.empty:
            index = user_data.index[0]
            entry_time = datetime.strptime(user_data.iloc[0]["Entry Time"], "%Y-%m-%d %H:%M:%S")
            total_seconds = (now - entry_time).total_seconds()
            total_working_time = f"{int(total_seconds // 3600)}h {int((total_seconds % 3600) // 60)}m"
            df.at[index, "Exit Time"] = now.strftime("%Y-%m-%d %H:%M:%S")
            df.at[index, "Total Hours"] = total_working_time

    df.to_csv(attendance_file, index=False)

import pytz
import datetime
def maketime_zone(dt,local_tz='Asia/Kolkata'):
     if dt.tzinfo is None:  # Check if it's naive
        local_timezone = pytz.timezone(local_tz)  # Get the local timezone
        dt = local_timezone.localize(dt)  # Localize the naive datetime
     return dt.astimezone(pytz.UTC) 
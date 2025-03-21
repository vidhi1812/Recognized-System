import pytz
from datetime import datetime

def maketime_zone(dt, local_tz='Asia/Kolkata'):
    """
    Convert a datetime object to UTC, handling both naive and timezone-aware datetimes.
    
    Args:
        dt (datetime): The datetime object to convert
        local_tz (str): The local timezone name (default: 'Asia/Kolkata')
    
    Returns:
        datetime: UTC timezone-aware datetime object
    
    Raises:
        ValueError: If the timezone name is invalid
        TypeError: If dt is not a datetime object
    """
    try:
        # Validate input
        if not isinstance(dt, datetime):
            raise TypeError("Input must be a datetime object")
            
        # Get the local timezone
        try:
            local_timezone = pytz.timezone(local_tz)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Invalid timezone: {local_tz}")
            
        # Handle naive datetime (no timezone info)
        if dt.tzinfo is None:
            dt = local_timezone.localize(dt)
        
        # Convert to UTC
        utc_dt = dt.astimezone(pytz.UTC)
        
        return utc_dt
        
    except Exception as e:
        print(f"Error in timezone conversion: {str(e)}")
        # Return original datetime if conversion fails
        return dt 
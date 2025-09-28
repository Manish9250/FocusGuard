import sqlite3
import os
from datetime import datetime, timedelta, timezone # Import timezone

def get_history_for_range(start_time, end_time):
    """
    Fetches Brave browser history within a specific time range,
    correctly handling timezones.

    Args:
        start_time (datetime): A timezone-aware datetime object (in UTC).
        end_time (datetime): A timezone-aware datetime object (in UTC).

    Returns:
        list: A list of tuples, where each tuple contains
              (url, title, duration_in_seconds, local_visit_datetime).
    """
    history_db = os.path.expanduser('~') + '/.config/BraveSoftware/Brave-Browser/Default/History'
    temp_db = '/tmp/brave_history_copy.db'
    
    os.system(f'cp {history_db} {temp_db}')

    try:
        con = sqlite3.connect(temp_db)
        cursor = con.cursor()

        # --- MODIFICATION 1: Make the epoch start timezone-aware (UTC) ---
        epoch_start = datetime(1601, 1, 1, tzinfo=timezone.utc)
        
        # Convert our aware start/end times to microseconds
        start_us = (start_time - epoch_start).total_seconds() * 1_000_000
        end_us = (end_time - epoch_start).total_seconds() * 1_000_000

        query = """
        SELECT u.url, u.title, v.visit_duration, v.visit_time 
        FROM urls u JOIN visits v ON u.id = v.url
        WHERE v.visit_time >= ? AND v.visit_time < ?
        """
        
        cursor.execute(query, (start_us, end_us))
        
        history_data = []
        for url, title, duration_us, visit_time_us in cursor.fetchall():
            # --- MODIFICATION 2: Filter out noise (visits less than 1 second) ---
            if duration_us > 1000000: # Only count visits longer than 1 second
                
                # Convert browser's microsecond timestamp to a UTC datetime object
                visit_datetime_utc = epoch_start + timedelta(microseconds=visit_time_us)
                
                # --- MODIFICATION 3: Convert from UTC to the system's local timezone ---
                local_visit_datetime = visit_datetime_utc.astimezone()

                history_data.append(
                    (url, title, round(duration_us / 1_000_000), local_visit_datetime)
                )
        
        return history_data

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if 'con' in locals() and con:
            con.close()
        os.remove(temp_db)

### Updated Usage Example

#You must now use timezone-aware `datetime` objects when calling the function.

if __name__ == "__main__":
    # --- IMPORTANT: Get current time and last check time in UTC ---
    # This ensures we query the database correctly.
    # 1. Get the current time in your LOCAL timezone (IST)
    now_local = datetime.now().astimezone()

    # 2. Determine the start of today (midnight) in your LOCAL timezone
    start_of_today_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 3. NOW, convert that correct local start time to UTC for the database
    start_time_utc = start_of_today_local.astimezone(timezone.utc)

    # 4. The end time is simply the current moment in UTC
    end_time_utc = datetime.now(timezone.utc)
    
    print(f"✅ Correctly fetching history for today ({now_local.strftime('%Y-%m-%d')}).")
    print(f"Querying data from {start_time_utc.isoformat()} to {end_time_utc.isoformat()}...")

    # The rest of your script follows...
    new_history = get_history_for_range(start_time_utc, end_time_utc)
    if not new_history:
        print("No significant new browsing activity found.")
    else:
        for url, title, duration, visit_time in new_history:
            # visit_time is now in your local timezone!
            time_str = visit_time.strftime('%H:%M:%S') 
            print(f"- At {time_str}, visited {url} for {duration} seconds.")
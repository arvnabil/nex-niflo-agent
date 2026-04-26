from datetime import datetime, timedelta, timezone as py_timezone
import logging

def test_time():
    wib = py_timezone(timedelta(hours=7))
    now = datetime.now(wib)
    today_str = now.strftime("%Y-%m-%d")
    
    start_time = f"{today_str}T00:00:00+07:00"
    end_time = f"{today_str}T23:59:59+07:00"
    
    print(f"Now: {now}")
    print(f"Today Str: {today_str}")
    print(f"Default Start: {start_time}")
    print(f"Default End: {end_time}")

if __name__ == "__main__":
    test_time()

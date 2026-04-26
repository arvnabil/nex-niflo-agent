from datetime import datetime, timedelta, timezone as py_timezone

def calendar_logic_test(start_time, end_time, today_str):
    if not start_time:
        start_time = f"{today_str}T00:00:00+07:00"
    
    if not end_time:
        base_date = start_time.split("T")[0] if "T" in start_time else today_str
        end_time = f"{base_date}T23:59:59+07:00"
    
    return start_time, end_time

def run_tests():
    # Case 1: Today is 24th, Agent wants 24th (matches)
    print("--- Case 1 (Match) ---")
    s, e = calendar_logic_test("2026-04-24T00:00:00+07:00", None, "2026-04-24")
    print(f"Start: {s}, End: {e}")
    assert s < e, "Invalid range in Case 1"

    # Case 2: Today is 23rd (server clock lag), Agent wants 24th (TODAY'S BUG)
    print("\n--- Case 2 (Server Lag/UTC issue) ---")
    s, e = calendar_logic_test("2026-04-24T00:00:00+07:00", None, "2026-04-23")
    print(f"Start: {s}, End: {e}")
    assert s < e, f"Invalid range in Case 2: {s} >= {e}"

    # Case 3: Tomorrow's agenda
    print("\n--- Case 3 (Tomorrow) ---")
    s, e = calendar_logic_test("2026-04-25T00:00:00+07:00", None, "2026-04-24")
    print(f"Start: {s}, End: {e}")
    assert s < e, "Invalid range in Case 3"

    print("\n✅ All logic tests passed!")

if __name__ == "__main__":
    run_tests()

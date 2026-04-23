# skills/productivity/task_reminder.py

async def task_reminder(input_data: dict):
    """
    Schedules a task or creates a reminder.
    Params: task (string), time (string)
    """
    task = input_data.get("task")
    time = input_data.get("time")

    if not task:
        return {"status": "error", "message": "No task description provided"}

    # Placeholder for database/reminder service
    return {
        "status": "success",
        "data": {"task": task, "time": time},
        "message": f"Reminder scheduled for: {task} at {time or 'unspecified time'}"
    }

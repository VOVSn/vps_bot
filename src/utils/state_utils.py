import json
import os

from constants import JSON_FILE


def load_task_state():
    """Load the current task state from a JSON file."""
    try:
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_task_state(state):
    """Save the task state to a JSON file."""
    with open(JSON_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def archive_completed_task():
    """Archive a completed task by renaming the task state file."""
    if os.path.exists(JSON_FILE):
        i = 1
        while os.path.exists(f'{JSON_FILE}.{i:03d}'):
            i += 1
        os.rename(JSON_FILE, f'{JSON_FILE}.{i:03d}')
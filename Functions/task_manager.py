import json
import os
import datetime
from typing import Dict, List, Any

DATA_DIR = "data"
TODO_FILE = os.path.join(DATA_DIR, "todo.json")
REMINDER_FILE = os.path.join(DATA_DIR, "reminders.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Todo list functions
def get_todos() -> List[Dict[str, Any]]:
    """Get all todo items"""
    if not os.path.exists(TODO_FILE):
        return []
    
    try:
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_todos(todos: List[Dict[str, Any]]) -> None:
    """Save todo items to file"""
    with open(TODO_FILE, 'w') as f:
        json.dump(todos, f, indent=2)

def add_todo(task: str, priority: str = "medium") -> str:
    """Add a new todo item"""
    todos = get_todos()
    new_todo = {
        "id": len(todos) + 1,
        "task": task,
        "priority": priority,
        "created": datetime.datetime.now().isoformat(),
        "completed": False
    }
    todos.append(new_todo)
    save_todos(todos)
    return f"Added task: {task}"

def complete_todo(task_id: int) -> str:
    """Mark a todo item as completed"""
    todos = get_todos()
    for todo in todos:
        if todo.get("id") == task_id:
            todo["completed"] = True
            todo["completed_date"] = datetime.datetime.now().isoformat()
            save_todos(todos)
            return f"Marked task {task_id} as completed"
    return f"Task {task_id} not found"

def list_todos(show_completed: bool = False) -> str:
    """List all todo items"""
    todos = get_todos()
    if not todos:
        return "No tasks found"
    
    active_todos = [t for t in todos if not t.get("completed") or show_completed]
    if not active_todos:
        return "No active tasks found"
    
    result = []
    for todo in active_todos:
        status = "✓" if todo.get("completed") else "□"
        result.append(f"{todo.get('id')}. [{status}] {todo.get('task')} (Priority: {todo.get('priority', 'medium')})")
    
    return "\n".join(result)

# Reminder functions
def get_reminders() -> List[Dict[str, Any]]:
    """Get all reminders"""
    if not os.path.exists(REMINDER_FILE):
        return []
    
    try:
        with open(REMINDER_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_reminders(reminders: List[Dict[str, Any]]) -> None:
    """Save reminders to file"""
    with open(REMINDER_FILE, 'w') as f:
        json.dump(reminders, f, indent=2)

def add_reminder(text: str, remind_time: str) -> str:
    """Add a new reminder with a specified time"""
    try:
        remind_datetime = datetime.datetime.fromisoformat(remind_time)
    except ValueError:
        try:
            # Try to parse as simpler format
            remind_datetime = datetime.datetime.strptime(remind_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD HH:MM format."
    
    reminders = get_reminders()
    new_reminder = {
        "id": len(reminders) + 1,
        "text": text,
        "time": remind_datetime.isoformat(),
        "created": datetime.datetime.now().isoformat(),
        "notified": False
    }
    reminders.append(new_reminder)
    save_reminders(reminders)
    return f"Reminder set for {remind_datetime.strftime('%Y-%m-%d %H:%M')}: {text}"

def check_due_reminders() -> List[Dict[str, Any]]:
    """Check for due reminders that haven't been notified"""
    reminders = get_reminders()
    now = datetime.datetime.now()
    due_reminders = []
    
    for reminder in reminders:
        if not reminder.get("notified"):
            remind_time = datetime.datetime.fromisoformat(reminder.get("time"))
            if remind_time <= now:
                reminder["notified"] = True
                due_reminders.append(reminder)
    
    if due_reminders:
        save_reminders(reminders)
    
    return due_reminders

# Note functions
def get_notes() -> List[Dict[str, Any]]:
    """Get all notes"""
    if not os.path.exists(NOTES_FILE):
        return []
    
    try:
        with open(NOTES_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_notes(notes: List[Dict[str, Any]]) -> None:
    """Save notes to file"""
    with open(NOTES_FILE, 'w') as f:
        json.dump(notes, f, indent=2)

def add_note(title: str, content: str) -> str:
    """Add a new note"""
    notes = get_notes()
    new_note = {
        "id": len(notes) + 1,
        "title": title,
        "content": content,
        "created": datetime.datetime.now().isoformat(),
        "updated": datetime.datetime.now().isoformat()
    }
    notes.append(new_note)
    save_notes(notes)
    return f"Added note: {title}"

def find_note(query: str) -> List[Dict[str, Any]]:
    """Find notes containing the query in title or content"""
    notes = get_notes()
    query = query.lower()
    
    return [note for note in notes if 
            query in note.get("title", "").lower() or 
            query in note.get("content", "").lower()] 
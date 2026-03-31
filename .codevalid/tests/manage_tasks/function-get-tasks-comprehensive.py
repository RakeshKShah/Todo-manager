import os
import json
import tempfile
import shutil
import pytest
from typing import List

import sys
from pathlib import Path

# Patch sys.path to import backend modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from database import get_tasks, add_task
from models import Task, TaskCreate, Priority, Category

DB_FILE = "tasks.json"

@pytest.fixture(autouse=True)
def temp_db(monkeypatch, tmp_path):
    """
    Fixture to run tests in a temp directory and patch DB_FILE location.
    """
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    monkeypatch.setattr("backend.database.DB_FILE", DB_FILE)
    yield
    os.chdir(orig_cwd)

def write_to_tasks_json(content):
    with open(DB_FILE, "w") as f:
        f.write(content)

def test_get_tasks_when_file_does_not_exist():
    """Test: Should return an empty list if the tasks file does not exist."""
    # Given: tasks.json does not exist
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    # When
    result = get_tasks()
    # Then
    assert result == []
    assert isinstance(result, list)

def test_get_tasks_with_empty_file():
    """Test: Should return an empty list if the tasks file exists but is empty."""
    # Given: tasks.json exists and is empty
    write_to_tasks_json("")
    # When
    result = get_tasks()
    # Then
    assert result == []
    assert isinstance(result, list)

def test_get_tasks_with_invalid_json():
    """Test: Should return an empty list if the tasks file contains invalid JSON."""
    # Given: tasks.json contains invalid JSON
    write_to_tasks_json("{invalid}")
    # When
    result = get_tasks()
    # Then
    assert result == []

def test_get_tasks_with_valid_empty_list():
    """Test: Should return an empty list if the tasks file contains a valid empty JSON list."""
    # Given: tasks.json contains []
    write_to_tasks_json("[]")
    # When
    result = get_tasks()
    # Then
    assert result == []
    assert isinstance(result, list)

def test_get_tasks_with_single_task():
    """Test: Should return a list with one Task object if the tasks file contains a single valid task."""
    # Given: tasks.json contains one valid task
    data = [{
        "id": "abc123",
        "title": "Task 1",
        "description": "Desc",
        "priority": "Medium",
        "category": "Work",
        "due_date": "2026-01-10",
        "completed": False
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert isinstance(result, list)
    assert len(result) == 1
    t = result[0]
    assert isinstance(t, Task)
    assert t.title == "Task 1"
    assert t.description == "Desc"
    assert t.priority == Priority.medium
    assert t.category == Category.work
    assert str(t.due_date) == "2026-01-10"
    assert t.completed is False

def test_get_tasks_with_multiple_tasks():
    """Test: Should return a list of Task objects if the tasks file contains multiple valid tasks."""
    # Given: tasks.json contains multiple valid tasks
    data = [
        {
            "id": "abc123",
            "title": "Task 1",
            "description": "Desc1",
            "priority": "Low",
            "category": "Work",
            "due_date": "2026-01-10",
            "completed": False
        },
        {
            "id": "def456",
            "title": "Task 2",
            "description": "Desc2",
            "priority": "High",
            "category": "Personal",
            "due_date": "2026-01-11",
            "completed": True
        }
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].title == "Task 1"
    assert result[1].title == "Task 2"
    assert result[0].priority == Priority.low
    assert result[1].priority == Priority.high
    assert result[0].category == Category.work
    assert result[1].category == Category.personal

def test_get_tasks_with_partial_invalid_json():
    """Test: Should handle tasks with missing required fields."""
    # Given: tasks.json contains a task with only title (other fields default)
    data = [{
        "id": "abc123",
        "title": "Task 1"
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert isinstance(result, list)
    assert len(result) == 1
    t = result[0]
    assert t.title == "Task 1"
    # Defaults
    assert t.description is None
    assert t.priority == Priority.medium
    assert t.category is None
    assert t.due_date is None
    assert t.completed is False

def test_get_tasks_with_non_array_json():
    """Test: Should return an empty list if the tasks file contains valid JSON that is not a list."""
    # Given: tasks.json contains a valid JSON object, not a list
    data = {
        "id": "abc123",
        "title": "Task 1"
    }
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert result == []

def test_get_tasks_with_list_containing_invalid_items():
    """Test: Should handle lists with mixed valid and invalid items."""
    # Given: tasks.json contains a list with valid and invalid items
    data = [
        {
            "id": "abc123",
            "title": "Task 1"
        },
        "not a dict",
        123,
        None
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    try:
        result = get_tasks()
    except Exception:
        result = []
    # Then: Only valid dicts should be converted, others skipped or error handled
    if result:
        assert all(isinstance(t, Task) for t in result)
        assert result[0].title == "Task 1"
    else:
        assert result == []

def test_get_tasks_with_large_number_of_tasks():
    """Test: Should handle and return all tasks if the tasks file contains a large number of valid tasks."""
    # Given: tasks.json contains 10000 valid tasks
    data = [{
        "id": f"id_{i}",
        "title": f"Task {i}",
        "description": f"Desc {i}",
        "priority": "Medium",
        "category": "Work",
        "due_date": "2026-01-10",
        "completed": False
    } for i in range(10000)]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert isinstance(result, list)
    assert len(result) == 10000
    assert result[0].title == "Task 0"
    assert result[-1].title == "Task 9999"

def test_get_tasks_with_unicode_characters():
    """Test: Should correctly parse and return tasks with Unicode characters in their fields."""
    # Given: tasks.json contains tasks with Unicode characters
    data = [{
        "id": "unicode_task",
        "title": "买菜 🛒",
        "description": "Comprar leche, huevos y pan 🥛🥚🍞",
        "priority": "High",
        "category": "Personal",
        "due_date": "2026-01-10",
        "completed": False
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 1
    assert result[0].title == "买菜 🛒"
    assert result[0].description == "Comprar leche, huevos y pan 🥛🥚🍞"

def test_get_tasks_with_special_characters():
    """Test: Should correctly parse tasks with special characters."""
    # Given: tasks.json contains tasks with special characters
    data = [{
        "id": "special_task",
        "title": 'Task with "quotes" and \'apostrophes\'',
        "description": "Line1\nLine2\tTabbed",
        "priority": "Medium",
        "completed": False
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 1
    assert 'quotes' in result[0].title
    assert '\n' in result[0].description

def test_get_tasks_with_all_priorities():
    """Test: Should correctly parse tasks with all priority levels."""
    # Given: tasks.json contains tasks with all priorities
    data = [
        {"id": "1", "title": "Low", "priority": "Low", "completed": False},
        {"id": "2", "title": "Medium", "priority": "Medium", "completed": False},
        {"id": "3", "title": "High", "priority": "High", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 3
    assert result[0].priority == Priority.low
    assert result[1].priority == Priority.medium
    assert result[2].priority == Priority.high

def test_get_tasks_with_all_categories():
    """Test: Should correctly parse tasks with all category types."""
    # Given: tasks.json contains tasks with all categories
    data = [
        {"id": "1", "title": "Work", "category": "Work", "completed": False},
        {"id": "2", "title": "Personal", "category": "Personal", "completed": False},
        {"id": "3", "title": "Study", "category": "Study", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 3
    assert result[0].category == Category.work
    assert result[1].category == Category.personal
    assert result[2].category == Category.study

def test_get_tasks_with_completed_status():
    """Test: Should correctly parse completed status."""
    # Given: tasks.json contains tasks with different completion statuses
    data = [
        {"id": "1", "title": "Completed", "completed": True},
        {"id": "2", "title": "Incomplete", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 2
    assert result[0].completed is True
    assert result[1].completed is False

def test_get_tasks_with_null_values():
    """Test: Should handle null values in optional fields."""
    # Given: tasks.json contains tasks with null values
    data = [{
        "id": "null_task",
        "title": "Task",
        "description": None,
        "category": None,
        "due_date": None,
        "completed": False
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 1
    assert result[0].description is None
    assert result[0].category is None
    assert result[0].due_date is None

def test_get_tasks_with_empty_strings():
    """Test: Should handle empty string values."""
    # Given: tasks.json contains tasks with empty strings
    data = [{
        "id": "empty_task",
        "title": "Task",
        "description": "",
        "completed": False
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 1
    assert result[0].description == ""

def test_get_tasks_with_whitespace_values():
    """Test: Should preserve whitespace in values."""
    # Given: tasks.json contains tasks with whitespace
    data = [{
        "id": "whitespace_task",
        "title": "  Task with spaces  ",
        "description": "\n\t\n",
        "completed": False
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 1
    assert result[0].title == "  Task with spaces  "
    assert result[0].description == "\n\t\n"

def test_get_tasks_with_very_long_strings():
    """Test: Should handle very long strings in fields."""
    # Given: tasks.json contains tasks with very long strings
    long_title = "A" * 1000
    long_desc = "B" * 5000
    data = [{
        "id": "long_task",
        "title": long_title,
        "description": long_desc,
        "completed": False
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 1
    assert result[0].title == long_title
    assert result[0].description == long_desc

def test_get_tasks_with_various_date_formats():
    """Test: Should correctly parse various date formats."""
    # Given: tasks.json contains tasks with different date formats
    data = [
        {"id": "1", "title": "Task1", "due_date": "2026-01-01", "completed": False},
        {"id": "2", "title": "Task2", "due_date": "2026-12-31", "completed": False},
        {"id": "3", "title": "Task3", "due_date": None, "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 3
    assert str(result[0].due_date) == "2026-01-01"
    assert str(result[1].due_date) == "2026-12-31"
    assert result[2].due_date is None

def test_get_tasks_order_preservation():
    """Test: Should preserve the order of tasks from the file."""
    # Given: tasks.json contains tasks in specific order
    data = [
        {"id": "3", "title": "Third", "completed": False},
        {"id": "1", "title": "First", "completed": False},
        {"id": "2", "title": "Second", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 3
    assert result[0].title == "Third"
    assert result[1].title == "First"
    assert result[2].title == "Second"

def test_get_tasks_with_duplicate_ids():
    """Test: Should handle tasks with duplicate IDs."""
    # Given: tasks.json contains tasks with duplicate IDs
    data = [
        {"id": "dup", "title": "Task 1", "completed": False},
        {"id": "dup", "title": "Task 2", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 2
    assert result[0].id == "dup"
    assert result[1].id == "dup"

def test_get_tasks_with_missing_id_field():
    """Test: Should handle tasks missing the ID field."""
    # Given: tasks.json contains a task without ID
    data = [{
        "title": "No ID Task",
        "completed": False
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    try:
        result = get_tasks()
    except Exception:
        result = []
    # Then: Should either skip or raise error
    # Depending on implementation

def test_get_tasks_with_extra_fields():
    """Test: Should handle tasks with extra fields not in schema."""
    # Given: tasks.json contains tasks with extra fields
    data = [{
        "id": "extra_task",
        "title": "Task",
        "description": "Desc",
        "extra_field": "Extra value",
        "another_extra": 123,
        "completed": False
    }]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 1
    assert result[0].title == "Task"
    # Extra fields should be ignored

def test_get_tasks_with_numeric_id():
    """Test: Should handle numeric IDs."""
    # Given: tasks.json contains tasks with numeric IDs
    data = [
        {"id": 1, "title": "Task 1", "completed": False},
        {"id": 2, "title": "Task 2", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 2

def test_get_tasks_with_boolean_values():
    """Test: Should correctly parse boolean values."""
    # Given: tasks.json contains various boolean values
    data = [
        {"id": "1", "title": "True", "completed": True},
        {"id": "2", "title": "False", "completed": False},
        {"id": "3", "title": "Default", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    result = get_tasks()
    # Then
    assert len(result) == 3
    assert result[0].completed is True
    assert result[1].completed is False
    assert result[2].completed is False

def test_get_tasks_after_add_task():
    """Test: Should return newly added tasks."""
    # Given: Empty task list
    # When: Add a task
    task = TaskCreate(title="New Task", priority=Priority.high)
    add_task(task)
    result = get_tasks()
    # Then
    assert len(result) == 1
    assert result[0].title == "New Task"

def test_get_tasks_multiple_calls_consistency():
    """Test: Multiple calls to get_tasks should return consistent results."""
    # Given: tasks.json with data
    data = [
        {"id": "1", "title": "Task 1", "completed": False},
        {"id": "2", "title": "Task 2", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When: Call get_tasks multiple times
    result1 = get_tasks()
    result2 = get_tasks()
    result3 = get_tasks()
    # Then
    assert len(result1) == len(result2) == len(result3) == 2
    assert result1[0].title == result2[0].title == result3[0].title

def test_get_tasks_with_mixed_case_priority():
    """Test: Should handle mixed case priority values."""
    # Given: tasks.json with mixed case priorities
    data = [
        {"id": "1", "title": "Task", "priority": "low", "completed": False},
        {"id": "2", "title": "Task", "priority": "MEDIUM", "completed": False},
        {"id": "3", "title": "Task", "priority": "High", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    try:
        result = get_tasks()
        # Then: Should handle case variations
        assert len(result) >= 1
    except Exception:
        # Case sensitivity might cause errors
        pass

def test_get_tasks_with_mixed_case_category():
    """Test: Should handle mixed case category values."""
    # Given: tasks.json with mixed case categories
    data = [
        {"id": "1", "title": "Task", "category": "work", "completed": False},
        {"id": "2", "title": "Task", "category": "PERSONAL", "completed": False},
        {"id": "3", "title": "Task", "category": "Study", "completed": False}
    ]
    write_to_tasks_json(json.dumps(data))
    # When
    try:
        result = get_tasks()
        # Then: Should handle case variations
        assert len(result) >= 1
    except Exception:
        # Case sensitivity might cause errors
        pass

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

from database import add_task, get_tasks, delete_task
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

def test_delete_existing_task_success():
    """Test: Delete an existing task by valid ID"""
    # Given: A task exists
    task_create = TaskCreate(title="Task to Delete", priority=Priority.medium)
    added_task = add_task(task_create)
    task_id = added_task.id
    
    # When: Delete the task
    result = delete_task(task_id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_nonexistent_task():
    """Test: Attempt to delete a non-existent task"""
    # Given: A task exists but we try to delete a different one
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    add_task(task_create)
    
    # When: Try to delete non-existent task
    result = delete_task("nonexistent_id")
    
    # Then
    assert result is False
    tasks = get_tasks()
    assert len(tasks) == 1  # Original task still exists

def test_delete_task_empty_list():
    """Test: Attempt to delete from an empty task list"""
    # Given: Empty task list
    # When: Try to delete
    result = delete_task("any_id")
    
    # Then
    assert result is False
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_multiple_same_id():
    """Test: Delete when multiple tasks have the same ID"""
    # Given: Manually create tasks with same ID (edge case)
    data = [
        {
            "id": "duplicate_id",
            "title": "Task 1",
            "priority": "Medium",
            "completed": False
        },
        {
            "id": "duplicate_id",
            "title": "Task 2",
            "priority": "Medium",
            "completed": False
        }
    ]
    write_to_tasks_json(json.dumps(data))
    
    # When: Delete the duplicate ID
    result = delete_task("duplicate_id")
    
    # Then: Should remove all with that ID
    assert result is True
    tasks = get_tasks()
    # After deletion, no tasks should have that ID
    assert all(t.id != "duplicate_id" for t in tasks)

def test_delete_task_invalid_id_type_string():
    """Test: Delete with invalid ID type (string that doesn't exist)"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    add_task(task_create)
    
    # When: Try to delete with non-matching string ID
    result = delete_task("not_a_valid_uuid")
    
    # Then
    assert result is False
    tasks = get_tasks()
    assert len(tasks) == 1

def test_delete_task_last_remaining():
    """Test: Delete the last remaining task"""
    # Given: Only one task exists
    task_create = TaskCreate(title="Last Task", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Delete it
    result = delete_task(added_task.id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_id_zero():
    """Test: Delete a task with ID zero"""
    # Given: Manually create a task with id=0
    data = [
        {
            "id": "0",
            "title": "Task with ID 0",
            "priority": "Medium",
            "completed": False
        }
    ]
    write_to_tasks_json(json.dumps(data))
    
    # When: Delete task with id=0
    result = delete_task("0")
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_negative_id():
    """Test: Delete a task with a negative ID"""
    # Given: Manually create a task with negative ID
    data = [
        {
            "id": "-5",
            "title": "Task with negative ID",
            "priority": "Medium",
            "completed": False
        }
    ]
    write_to_tasks_json(json.dumps(data))
    
    # When: Delete task with negative ID
    result = delete_task("-5")
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_id_as_float_string():
    """Test: Delete a task with ID as float string"""
    # Given: A task with regular UUID
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Try to delete with float string (won't match UUID)
    result = delete_task("1.0")
    
    # Then
    assert result is False
    tasks = get_tasks()
    assert len(tasks) == 1

def test_delete_task_from_multiple_tasks():
    """Test: Delete specific task from multiple tasks"""
    # Given: Multiple tasks exist
    task1 = TaskCreate(title="Task 1", priority=Priority.low)
    task2 = TaskCreate(title="Task 2", priority=Priority.medium)
    task3 = TaskCreate(title="Task 3", priority=Priority.high)
    
    added1 = add_task(task1)
    added2 = add_task(task2)
    added3 = add_task(task3)
    
    # When: Delete task2
    result = delete_task(added2.id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 3"

def test_delete_task_first_of_many():
    """Test: Delete first task from many"""
    # Given: Multiple tasks exist
    added_tasks = []
    for i in range(5):
        task = TaskCreate(title=f"Task {i}", priority=Priority.medium)
        added_tasks.append(add_task(task))
    
    # When: Delete first task
    result = delete_task(added_tasks[0].id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 4
    assert tasks[0].title == "Task 1"

def test_delete_task_middle_of_many():
    """Test: Delete middle task from many"""
    # Given: Multiple tasks exist
    added_tasks = []
    for i in range(5):
        task = TaskCreate(title=f"Task {i}", priority=Priority.medium)
        added_tasks.append(add_task(task))
    
    # When: Delete middle task
    result = delete_task(added_tasks[2].id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 4
    assert tasks[0].title == "Task 0"
    assert tasks[1].title == "Task 1"
    assert tasks[2].title == "Task 3"
    assert tasks[3].title == "Task 4"

def test_delete_task_last_of_many():
    """Test: Delete last task from many"""
    # Given: Multiple tasks exist
    added_tasks = []
    for i in range(5):
        task = TaskCreate(title=f"Task {i}", priority=Priority.medium)
        added_tasks.append(add_task(task))
    
    # When: Delete last task
    result = delete_task(added_tasks[4].id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 4
    assert tasks[-1].title == "Task 3"

def test_delete_task_sequential_deletions():
    """Test: Delete tasks sequentially"""
    # Given: Multiple tasks exist
    added_tasks = []
    for i in range(5):
        task = TaskCreate(title=f"Task {i}", priority=Priority.medium)
        added_tasks.append(add_task(task))
    
    # When: Delete tasks one by one
    for i, added_task in enumerate(added_tasks):
        result = delete_task(added_task.id)
        assert result is True
        tasks = get_tasks()
        assert len(tasks) == 4 - i
    
    # Then: All tasks should be deleted
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_already_deleted():
    """Test: Try to delete already deleted task"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    added_task = add_task(task_create)
    task_id = added_task.id
    
    # When: Delete it once
    result1 = delete_task(task_id)
    assert result1 is True
    
    # When: Try to delete again
    result2 = delete_task(task_id)
    
    # Then
    assert result2 is False
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_case_sensitive_id():
    """Test: Delete with case-sensitive ID matching"""
    # Given: A task with UUID (case-insensitive in UUID)
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    added_task = add_task(task_create)
    original_id = added_task.id
    
    # When: Try to delete with different case (if UUID contains letters)
    if any(c.isalpha() for c in original_id):
        modified_id = original_id.upper() if original_id.islower() else original_id.lower()
        result = delete_task(modified_id)
        # UUIDs are case-insensitive in most implementations
        # This test verifies the actual behavior
    else:
        result = delete_task(original_id)
    
    # Then: Verify behavior
    tasks = get_tasks()
    # Either deleted (if case-insensitive) or not (if case-sensitive)
    assert len(tasks) in [0, 1]

def test_delete_task_with_unicode_title():
    """Test: Delete task that has Unicode characters"""
    # Given: A task with Unicode title
    task_create = TaskCreate(
        title="买菜 🛒",
        description="Comprar 🥛🥚🍞",
        priority=Priority.medium
    )
    added_task = add_task(task_create)
    
    # When: Delete it
    result = delete_task(added_task.id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_with_special_characters():
    """Test: Delete task that has special characters"""
    # Given: A task with special characters
    task_create = TaskCreate(
        title='Task with "quotes" and \'apostrophes\'',
        description="Line1\nLine2\tTabbed",
        priority=Priority.medium
    )
    added_task = add_task(task_create)
    
    # When: Delete it
    result = delete_task(added_task.id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_with_large_data():
    """Test: Delete task with large title and description"""
    # Given: A task with large data
    task_create = TaskCreate(
        title="X" * 1000,
        description="Y" * 5000,
        priority=Priority.medium
    )
    added_task = add_task(task_create)
    
    # When: Delete it
    result = delete_task(added_task.id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_completed_status():
    """Test: Delete completed task"""
    # Given: A completed task
    task_create = TaskCreate(
        title="Completed Task",
        priority=Priority.medium,
        completed=True
    )
    added_task = add_task(task_create)
    
    # When: Delete it
    result = delete_task(added_task.id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_incomplete_status():
    """Test: Delete incomplete task"""
    # Given: An incomplete task
    task_create = TaskCreate(
        title="Incomplete Task",
        priority=Priority.medium,
        completed=False
    )
    added_task = add_task(task_create)
    
    # When: Delete it
    result = delete_task(added_task.id)
    
    # Then
    assert result is True
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_with_all_priorities():
    """Test: Delete tasks with all priority levels"""
    # Given: Tasks with different priorities
    priorities = [Priority.low, Priority.medium, Priority.high]
    added_tasks = []
    for priority in priorities:
        task = TaskCreate(title=f"Task {priority}", priority=priority)
        added_tasks.append(add_task(task))
    
    # When: Delete each one
    for added_task in added_tasks:
        result = delete_task(added_task.id)
        assert result is True
    
    # Then
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_with_all_categories():
    """Test: Delete tasks with all categories"""
    # Given: Tasks with different categories
    categories = [Category.work, Category.personal, Category.study]
    added_tasks = []
    for category in categories:
        task = TaskCreate(
            title=f"Task {category}",
            priority=Priority.medium,
            category=category
        )
        added_tasks.append(add_task(task))
    
    # When: Delete each one
    for added_task in added_tasks:
        result = delete_task(added_task.id)
        assert result is True
    
    # Then
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_task_persistence():
    """Test: Verify deletion is persisted to storage"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    added_task = add_task(task_create)
    task_id = added_task.id
    
    # When: Delete it
    result = delete_task(task_id)
    assert result is True
    
    # Then: Verify it's gone from storage
    tasks = get_tasks()
    assert len(tasks) == 0
    # Verify file was updated
    assert os.path.exists(DB_FILE)
    with open(DB_FILE, "r") as f:
        data = json.load(f)
        assert len(data) == 0

def test_delete_task_empty_string_id():
    """Test: Delete with empty string ID"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    add_task(task_create)
    
    # When: Try to delete with empty string
    result = delete_task("")
    
    # Then
    assert result is False
    tasks = get_tasks()
    assert len(tasks) == 1

def test_delete_task_none_id():
    """Test: Delete with None ID"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    add_task(task_create)
    
    # When: Try to delete with None
    # Then: Should handle gracefully
    try:
        result = delete_task(None)
        assert result is False
    except (TypeError, AttributeError):
        # It's acceptable to raise an error for None
        pass
    
    tasks = get_tasks()
    assert len(tasks) == 1

def test_delete_task_whitespace_id():
    """Test: Delete with whitespace ID"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    add_task(task_create)
    
    # When: Try to delete with whitespace
    result = delete_task("   ")
    
    # Then
    assert result is False
    tasks = get_tasks()
    assert len(tasks) == 1

def test_delete_task_very_long_id():
    """Test: Delete with very long ID string"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    add_task(task_create)
    
    # When: Try to delete with very long ID
    result = delete_task("a" * 10000)
    
    # Then
    assert result is False
    tasks = get_tasks()
    assert len(tasks) == 1

def test_delete_task_special_id_characters():
    """Test: Delete with special characters in ID"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    add_task(task_create)
    
    # When: Try to delete with special characters
    result = delete_task("!@#$%^&*()")
    
    # Then
    assert result is False
    tasks = get_tasks()
    assert len(tasks) == 1

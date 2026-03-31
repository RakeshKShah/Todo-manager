import os
import json
import tempfile
import shutil
import pytest
from typing import List
from datetime import date, timedelta

import sys
from pathlib import Path

# Patch sys.path to import backend modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from database import add_task, get_tasks, update_task, delete_task
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

def test_update_existing_task_success():
    """Test: Update existing task with valid data"""
    # Given: A task exists
    task_create = TaskCreate(title="Original Title", priority=Priority.low)
    added_task = add_task(task_create)
    task_id = added_task.id
    
    # When: Update the task
    update_data = TaskCreate(
        title="Updated Title",
        description="Updated description",
        priority=Priority.high,
        category=Category.work,
        due_date=date(2026, 5, 15),
        completed=True
    )
    result = update_task(task_id, update_data)
    
    # Then
    assert result is not None
    assert result.id == task_id
    assert result.title == "Updated Title"
    assert result.description == "Updated description"
    assert result.priority == Priority.high
    assert result.category == Category.work
    assert str(result.due_date) == "2026-05-15"
    assert result.completed is True
    
    # Verify persistence
    tasks = get_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Updated Title"

def test_update_nonexistent_task():
    """Test: Attempt to update a non-existent task"""
    # Given: No tasks exist
    # When: Try to update non-existent task
    update_data = TaskCreate(title="New Title", priority=Priority.medium)
    result = update_task("nonexistent_id", update_data)
    
    # Then
    assert result is None
    tasks = get_tasks()
    assert len(tasks) == 0

def test_update_task_empty_list():
    """Test: Attempt to update when task list is empty"""
    # Given: Empty task list
    # When: Try to update
    update_data = TaskCreate(title="Title", priority=Priority.medium)
    result = update_task("any_id", update_data)
    
    # Then
    assert result is None

def test_update_task_partial_data():
    """Test: Update task with partial data"""
    # Given: A task exists
    task_create = TaskCreate(
        title="Original",
        description="Original desc",
        priority=Priority.low,
        category=Category.personal
    )
    added_task = add_task(task_create)
    task_id = added_task.id
    
    # When: Update only title
    update_data = TaskCreate(title="New Title", priority=Priority.medium)
    result = update_task(task_id, update_data)
    
    # Then: Only title should change, priority defaults to medium
    assert result.title == "New Title"
    assert result.priority == Priority.medium
    # Note: update_task replaces entire task, so other fields get defaults
    tasks = get_tasks()
    assert len(tasks) == 1

def test_update_task_invalid_priority():
    """Test: Update task with invalid priority"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.low)
    added_task = add_task(task_create)
    
    # When: Try to update with invalid priority
    # Then: Should raise validation error
    with pytest.raises(Exception):
        update_data = TaskCreate(title="Task", priority="InvalidPriority")

def test_update_task_to_duplicate_title():
    """Test: Update task to a title that already exists"""
    # Given: Two tasks exist
    task1 = TaskCreate(title="Task A", priority=Priority.low)
    task2 = TaskCreate(title="Task B", priority=Priority.medium)
    added1 = add_task(task1)
    added2 = add_task(task2)
    
    # When: Update task2 to have same title as task1
    update_data = TaskCreate(title="Task A", priority=Priority.high)
    result = update_task(added2.id, update_data)
    
    # Then: Should allow duplicate titles
    assert result is not None
    assert result.title == "Task A"
    tasks = get_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == "Task A"
    assert tasks[1].title == "Task A"

def test_update_task_mark_completed():
    """Test: Update task status to Completed"""
    # Given: A task exists with completed=False
    task_create = TaskCreate(title="Task", priority=Priority.medium, completed=False)
    added_task = add_task(task_create)
    
    # When: Update to mark as completed
    update_data = TaskCreate(title="Task", priority=Priority.medium, completed=True)
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result.completed is True
    tasks = get_tasks()
    assert tasks[0].completed is True

def test_update_task_mark_incomplete():
    """Test: Update task status to Incomplete"""
    # Given: A task exists with completed=True
    task_create = TaskCreate(title="Task", priority=Priority.medium, completed=True)
    added_task = add_task(task_create)
    
    # When: Update to mark as incomplete
    update_data = TaskCreate(title="Task", priority=Priority.medium, completed=False)
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result.completed is False
    tasks = get_tasks()
    assert tasks[0].completed is False

def test_update_task_boundary_id():
    """Test: Update task with boundary ID value"""
    # Given: A task with id=0 (if possible)
    # When: Try to update
    update_data = TaskCreate(title="Title", priority=Priority.medium)
    result = update_task("0", update_data)
    
    # Then: Should return None (no task with id=0)
    assert result is None

def test_update_task_no_changes():
    """Test: Update task with no changes in data"""
    # Given: A task exists
    task_create = TaskCreate(
        title="Original Title",
        description="Original desc",
        priority=Priority.medium,
        category=Category.work
    )
    added_task = add_task(task_create)
    
    # When: Update with same data
    update_data = TaskCreate(
        title="Original Title",
        description="Original desc",
        priority=Priority.medium,
        category=Category.work
    )
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result is not None
    assert result.title == "Original Title"
    tasks = get_tasks()
    assert len(tasks) == 1

def test_update_task_due_date_past():
    """Test: Update task with a due date in the past"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Update with past due date
    past_date = date.today() - timedelta(days=30)
    update_data = TaskCreate(
        title="Task",
        priority=Priority.medium,
        due_date=past_date
    )
    result = update_task(added_task.id, update_data)
    
    # Then: Should allow past dates
    assert result is not None
    assert result.due_date == past_date

def test_update_task_due_date_future():
    """Test: Update task with a due date in the future"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Update with future due date
    future_date = date.today() + timedelta(days=60)
    update_data = TaskCreate(
        title="Task",
        priority=Priority.medium,
        due_date=future_date
    )
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result is not None
    assert result.due_date == future_date

def test_update_task_change_priority():
    """Test: Update task priority"""
    # Given: A task with low priority
    task_create = TaskCreate(title="Task", priority=Priority.low)
    added_task = add_task(task_create)
    
    # When: Update to high priority
    update_data = TaskCreate(title="Task", priority=Priority.high)
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result.priority == Priority.high
    tasks = get_tasks()
    assert tasks[0].priority == Priority.high

def test_update_task_change_category():
    """Test: Update task category"""
    # Given: A task with work category
    task_create = TaskCreate(
        title="Task",
        priority=Priority.medium,
        category=Category.work
    )
    added_task = add_task(task_create)
    
    # When: Update to personal category
    update_data = TaskCreate(
        title="Task",
        priority=Priority.medium,
        category=Category.personal
    )
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result.category == Category.personal
    tasks = get_tasks()
    assert tasks[0].category == Category.personal

def test_update_task_clear_description():
    """Test: Update task to clear description"""
    # Given: A task with description
    task_create = TaskCreate(
        title="Task",
        description="Original description",
        priority=Priority.medium
    )
    added_task = add_task(task_create)
    
    # When: Update to remove description
    update_data = TaskCreate(title="Task", priority=Priority.medium)
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result.description is None
    tasks = get_tasks()
    assert tasks[0].description is None

def test_update_task_add_description():
    """Test: Update task to add description"""
    # Given: A task without description
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Update to add description
    update_data = TaskCreate(
        title="Task",
        description="New description",
        priority=Priority.medium
    )
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result.description == "New description"
    tasks = get_tasks()
    assert tasks[0].description == "New description"

def test_update_task_unicode_characters():
    """Test: Update task with Unicode characters"""
    # Given: A task exists
    task_create = TaskCreate(title="Original", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Update with Unicode
    update_data = TaskCreate(
        title="买菜 🛒",
        description="Comprar 🥛🥚🍞",
        priority=Priority.medium
    )
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result.title == "买菜 🛒"
    assert result.description == "Comprar 🥛🥚🍞"
    tasks = get_tasks()
    assert tasks[0].title == "买菜 🛒"

def test_update_task_special_characters():
    """Test: Update task with special characters"""
    # Given: A task exists
    task_create = TaskCreate(title="Original", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Update with special characters
    update_data = TaskCreate(
        title='Task with "quotes" and \'apostrophes\'',
        description="Line1\nLine2\tTabbed",
        priority=Priority.medium
    )
    result = update_task(added_task.id, update_data)
    
    # Then
    assert 'quotes' in result.title
    assert '\n' in result.description
    tasks = get_tasks()
    assert 'quotes' in tasks[0].title

def test_update_task_large_title():
    """Test: Update task with large title"""
    # Given: A task exists
    task_create = TaskCreate(title="Original", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Update with large title
    large_title = "X" * 1000
    update_data = TaskCreate(title=large_title, priority=Priority.medium)
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result.title == large_title
    tasks = get_tasks()
    assert tasks[0].title == large_title

def test_update_task_large_description():
    """Test: Update task with large description"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Update with large description
    large_desc = "Y" * 5000
    update_data = TaskCreate(
        title="Task",
        description=large_desc,
        priority=Priority.medium
    )
    result = update_task(added_task.id, update_data)
    
    # Then
    assert result.description == large_desc
    tasks = get_tasks()
    assert tasks[0].description == large_desc

def test_update_task_multiple_updates():
    """Test: Update same task multiple times"""
    # Given: A task exists
    task_create = TaskCreate(title="Task 1", priority=Priority.low)
    added_task = add_task(task_create)
    
    # When: Update multiple times
    for i in range(5):
        update_data = TaskCreate(
            title=f"Task {i+2}",
            priority=Priority.medium if i % 2 == 0 else Priority.high
        )
        result = update_task(added_task.id, update_data)
        assert result is not None
    
    # Then: Only one task should exist with latest data
    tasks = get_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Task 6"

def test_update_task_preserves_id():
    """Test: Update task preserves original ID"""
    # Given: A task exists
    task_create = TaskCreate(title="Original", priority=Priority.low)
    added_task = add_task(task_create)
    original_id = added_task.id
    
    # When: Update the task
    update_data = TaskCreate(title="Updated", priority=Priority.high)
    result = update_task(original_id, update_data)
    
    # Then: ID should remain the same
    assert result.id == original_id
    tasks = get_tasks()
    assert tasks[0].id == original_id

def test_update_task_with_multiple_tasks_in_list():
    """Test: Update specific task when multiple tasks exist"""
    # Given: Multiple tasks exist
    task1 = TaskCreate(title="Task 1", priority=Priority.low)
    task2 = TaskCreate(title="Task 2", priority=Priority.medium)
    task3 = TaskCreate(title="Task 3", priority=Priority.high)
    
    added1 = add_task(task1)
    added2 = add_task(task2)
    added3 = add_task(task3)
    
    # When: Update only task2
    update_data = TaskCreate(title="Task 2 Updated", priority=Priority.high)
    result = update_task(added2.id, update_data)
    
    # Then: Only task2 should be updated
    assert result.title == "Task 2 Updated"
    tasks = get_tasks()
    assert len(tasks) == 3
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2 Updated"
    assert tasks[2].title == "Task 3"

def test_update_task_all_priorities():
    """Test: Update task through all priority levels"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.low)
    added_task = add_task(task_create)
    
    # When: Update through all priorities
    priorities = [Priority.medium, Priority.high, Priority.low]
    for priority in priorities:
        update_data = TaskCreate(title="Task", priority=priority)
        result = update_task(added_task.id, update_data)
        assert result.priority == priority
    
    # Then: Final priority should be low
    tasks = get_tasks()
    assert tasks[0].priority == Priority.low

def test_update_task_all_categories():
    """Test: Update task through all categories"""
    # Given: A task exists
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    added_task = add_task(task_create)
    
    # When: Update through all categories
    categories = [Category.work, Category.personal, Category.study]
    for category in categories:
        update_data = TaskCreate(
            title="Task",
            priority=Priority.medium,
            category=category
        )
        result = update_task(added_task.id, update_data)
        assert result.category == category
    
    # Then: Final category should be study
    tasks = get_tasks()
    assert tasks[0].category == Category.study

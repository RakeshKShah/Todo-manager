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

def test_add_task_valid_input():
    """Test: Add Task with Valid Input"""
    # Given: A valid TaskCreate object with all fields
    task_create = TaskCreate(
        title="Buy Groceries",
        description="Buy milk, eggs, and bread",
        priority=Priority.high,
        category=Category.personal,
        due_date=date(2026, 4, 15),
        completed=False
    )
    # When
    result = add_task(task_create)
    # Then
    assert isinstance(result, Task)
    assert result.title == "Buy Groceries"
    assert result.description == "Buy milk, eggs, and bread"
    assert result.priority == Priority.high
    assert result.category == Category.personal
    assert str(result.due_date) == "2026-04-15"
    assert result.completed is False
    assert result.id is not None
    # Verify it's saved
    tasks = get_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == result.id

def test_add_task_multiple_tasks_unique_ids():
    """Test: Add Multiple Tasks and Ensure Unique IDs"""
    # Given: Empty task list
    task1 = TaskCreate(title="Task 1", priority=Priority.low)
    task2 = TaskCreate(title="Task 2", priority=Priority.medium)
    task3 = TaskCreate(title="Task 3", priority=Priority.high)
    # When
    result1 = add_task(task1)
    result2 = add_task(task2)
    result3 = add_task(task3)
    # Then
    assert result1.id != result2.id
    assert result2.id != result3.id
    assert result1.id != result3.id
    tasks = get_tasks()
    assert len(tasks) == 3
    ids = [t.id for t in tasks]
    assert len(set(ids)) == 3  # All unique

def test_add_task_missing_title():
    """Test: Add Task with Missing Title"""
    # Given: A TaskCreate object missing the title field
    # When/Then: Should raise validation error
    with pytest.raises(Exception):  # Pydantic validation error
        task_create = TaskCreate(
            description="No title provided",
            priority=Priority.medium
        )

def test_add_task_empty_description():
    """Test: Add Task with Empty Description"""
    # Given: A TaskCreate object with empty description
    task_create = TaskCreate(
        title="Task with no description",
        description="",
        priority=Priority.medium
    )
    # When
    result = add_task(task_create)
    # Then
    assert result.title == "Task with no description"
    assert result.description == ""
    tasks = get_tasks()
    assert len(tasks) == 1

def test_add_task_none_description():
    """Test: Add Task with None Description"""
    # Given: A TaskCreate object with None description
    task_create = TaskCreate(
        title="Task with none description",
        priority=Priority.medium
    )
    # When
    result = add_task(task_create)
    # Then
    assert result.title == "Task with none description"
    assert result.description is None
    tasks = get_tasks()
    assert len(tasks) == 1

def test_add_task_invalid_priority():
    """Test: Add Task with Invalid Priority"""
    # Given: A TaskCreate object with invalid priority
    # When/Then: Should raise validation error
    with pytest.raises(Exception):
        task_create = TaskCreate(
            title="Task",
            priority="UltraHigh"  # Invalid priority
        )

def test_add_task_past_due_date():
    """Test: Add Task with Past Due Date"""
    # Given: A TaskCreate object with past due date
    past_date = date.today() - timedelta(days=10)
    task_create = TaskCreate(
        title="Past task",
        priority=Priority.medium,
        due_date=past_date
    )
    # When
    result = add_task(task_create)
    # Then: Should allow past dates
    assert result.due_date == past_date
    tasks = get_tasks()
    assert len(tasks) == 1

def test_add_task_future_due_date():
    """Test: Add Task with Future Due Date"""
    # Given: A TaskCreate object with future due date
    future_date = date.today() + timedelta(days=30)
    task_create = TaskCreate(
        title="Future task",
        priority=Priority.medium,
        due_date=future_date
    )
    # When
    result = add_task(task_create)
    # Then
    assert result.due_date == future_date
    tasks = get_tasks()
    assert len(tasks) == 1

def test_add_task_duplicate_title():
    """Test: Add Task with Duplicate Title"""
    # Given: A task list with a task
    task1 = TaskCreate(title="Duplicate Title", priority=Priority.medium)
    add_task(task1)
    # When: Add another task with same title
    task2 = TaskCreate(title="Duplicate Title", priority=Priority.high)
    result = add_task(task2)
    # Then: Should allow duplicate titles
    assert result.title == "Duplicate Title"
    tasks = get_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == tasks[1].title

def test_add_task_large_title():
    """Test: Add Task with Large Title"""
    # Given: A TaskCreate object with very long title
    large_title = "A" * 1000
    task_create = TaskCreate(
        title=large_title,
        priority=Priority.medium
    )
    # When
    result = add_task(task_create)
    # Then
    assert result.title == large_title
    tasks = get_tasks()
    assert len(tasks) == 1

def test_add_task_large_description():
    """Test: Add Task with Large Description"""
    # Given: A TaskCreate object with very long description
    large_desc = "B" * 5000
    task_create = TaskCreate(
        title="Task",
        description=large_desc,
        priority=Priority.medium
    )
    # When
    result = add_task(task_create)
    # Then
    assert result.description == large_desc
    tasks = get_tasks()
    assert len(tasks) == 1

def test_add_task_minimum_fields():
    """Test: Add Task with Only Required Fields"""
    # Given: A TaskCreate object with only title (required field)
    task_create = TaskCreate(title="Minimal Task")
    # When
    result = add_task(task_create)
    # Then
    assert result.title == "Minimal Task"
    assert result.description is None
    assert result.priority == Priority.medium  # Default
    assert result.category is None
    assert result.due_date is None
    assert result.completed is False  # Default
    tasks = get_tasks()
    assert len(tasks) == 1

def test_add_task_with_all_priorities():
    """Test: Add Tasks with All Priority Levels"""
    # Given: TaskCreate objects with different priorities
    priorities = [Priority.low, Priority.medium, Priority.high]
    # When
    results = []
    for priority in priorities:
        task = TaskCreate(title=f"Task {priority}", priority=priority)
        results.append(add_task(task))
    # Then
    assert len(results) == 3
    assert results[0].priority == Priority.low
    assert results[1].priority == Priority.medium
    assert results[2].priority == Priority.high
    tasks = get_tasks()
    assert len(tasks) == 3

def test_add_task_with_all_categories():
    """Test: Add Tasks with All Category Types"""
    # Given: TaskCreate objects with different categories
    categories = [Category.work, Category.personal, Category.study]
    # When
    results = []
    for category in categories:
        task = TaskCreate(title=f"Task {category}", category=category, priority=Priority.medium)
        results.append(add_task(task))
    # Then
    assert len(results) == 3
    assert results[0].category == Category.work
    assert results[1].category == Category.personal
    assert results[2].category == Category.study
    tasks = get_tasks()
    assert len(tasks) == 3

def test_add_task_completed_flag():
    """Test: Add Task with Completed Flag"""
    # Given: A TaskCreate object with completed=True
    task_create = TaskCreate(
        title="Completed Task",
        priority=Priority.medium,
        completed=True
    )
    # When
    result = add_task(task_create)
    # Then
    assert result.completed is True
    tasks = get_tasks()
    assert len(tasks) == 1
    assert tasks[0].completed is True

def test_add_task_unicode_characters():
    """Test: Add Task with Unicode Characters"""
    # Given: A TaskCreate object with Unicode characters
    task_create = TaskCreate(
        title="买菜 🛒 Acheter",
        description="Comprar leche, huevos y pan 🥛🥚🍞",
        priority=Priority.medium
    )
    # When
    result = add_task(task_create)
    # Then
    assert result.title == "买菜 🛒 Acheter"
    assert result.description == "Comprar leche, huevos y pan 🥛🥚🍞"
    tasks = get_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "买菜 🛒 Acheter"

def test_add_task_special_characters():
    """Test: Add Task with Special Characters"""
    # Given: A TaskCreate object with special characters
    task_create = TaskCreate(
        title='Task with "quotes" and \'apostrophes\'',
        description="Line1\nLine2\tTabbed",
        priority=Priority.medium
    )
    # When
    result = add_task(task_create)
    # Then
    assert 'quotes' in result.title
    assert 'apostrophes' in result.title
    assert '\n' in result.description
    tasks = get_tasks()
    assert len(tasks) == 1

def test_add_task_sequential_additions():
    """Test: Add Tasks Sequentially and Verify Persistence"""
    # Given: Empty task list
    # When: Add multiple tasks sequentially
    for i in range(5):
        task = TaskCreate(title=f"Task {i}", priority=Priority.medium)
        add_task(task)
    # Then: All tasks should be persisted
    tasks = get_tasks()
    assert len(tasks) == 5
    for i, task in enumerate(tasks):
        assert task.title == f"Task {i}"

def test_add_task_with_existing_tasks():
    """Test: Add Task to Non-Empty List"""
    # Given: A task list with existing tasks
    task1 = TaskCreate(title="Existing Task", priority=Priority.low)
    add_task(task1)
    # When: Add a new task
    task2 = TaskCreate(title="New Task", priority=Priority.high)
    result = add_task(task2)
    # Then
    assert result.title == "New Task"
    tasks = get_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == "Existing Task"
    assert tasks[1].title == "New Task"

def test_add_task_id_format():
    """Test: Verify Added Task Has Valid ID Format"""
    # Given: A TaskCreate object
    task_create = TaskCreate(title="Task", priority=Priority.medium)
    # When
    result = add_task(task_create)
    # Then: ID should be a non-empty string (UUID format)
    assert isinstance(result.id, str)
    assert len(result.id) > 0
    # UUID format check (36 chars with hyphens)
    assert len(result.id) == 36
    assert result.id.count('-') == 4

def test_add_task_date_format():
    """Test: Verify Added Task Date Format"""
    # Given: A TaskCreate object with specific date
    test_date = date(2026, 12, 25)
    task_create = TaskCreate(
        title="Christmas Task",
        priority=Priority.medium,
        due_date=test_date
    )
    # When
    result = add_task(task_create)
    # Then
    assert result.due_date == test_date
    assert str(result.due_date) == "2026-12-25"
    tasks = get_tasks()
    assert tasks[0].due_date == test_date

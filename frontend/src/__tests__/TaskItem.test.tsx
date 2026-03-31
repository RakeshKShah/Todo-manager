import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskItem } from '../components/TaskItem';
import type { Task } from '../api';

describe('TaskItem Component', () => {
  const mockTask: Task = {
    id: '1',
    title: 'Test Task',
    description: 'Test description',
    priority: 'High',
    category: 'Work',
    due_date: '2026-04-15',
    completed: false,
  };

  const mockOnToggleComplete = vi.fn();
  const mockOnDelete = vi.fn();
  const mockOnEdit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Task Display', () => {
    it('should render task title', () => {
      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Test Task')).toBeInTheDocument();
    });

    it('should render task description', () => {
      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Test description')).toBeInTheDocument();
    });

    it('should render priority badge', () => {
      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('High')).toBeInTheDocument();
    });

    it('should render category badge', () => {
      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Work')).toBeInTheDocument();
    });

    it('should render due date', () => {
      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText(/Due:/)).toBeInTheDocument();
    });

    it('should not render category if not provided', () => {
      const taskWithoutCategory = { ...mockTask, category: undefined };

      render(
        <TaskItem
          task={taskWithoutCategory}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      // Should not have a badge for category
      const badges = screen.getAllByText(/High|Work|Personal|Study/);
      expect(badges.length).toBe(1); // Only priority badge
    });

    it('should not render description if not provided', () => {
      const taskWithoutDesc = { ...mockTask, description: undefined };

      render(
        <TaskItem
          task={taskWithoutDesc}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.queryByText('Test description')).not.toBeInTheDocument();
    });

    it('should not render due date if not provided', () => {
      const taskWithoutDueDate = { ...mockTask, due_date: undefined };

      render(
        <TaskItem
          task={taskWithoutDueDate}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.queryByText(/Due:/)).not.toBeInTheDocument();
    });
  });

  describe('Task Status Display', () => {
    it('should show "Done" button for incomplete task', () => {
      const incompleteTask = { ...mockTask, completed: false };

      render(
        <TaskItem
          task={incompleteTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Done')).toBeInTheDocument();
    });

    it('should show "Undo" button for completed task', () => {
      const completedTask = { ...mockTask, completed: true };

      render(
        <TaskItem
          task={completedTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Undo')).toBeInTheDocument();
    });

    it('should apply strikethrough to completed task title', () => {
      const completedTask = { ...mockTask, completed: true };

      render(
        <TaskItem
          task={completedTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const titleElement = screen.getByText('Test Task');
      expect(titleElement).toHaveStyle('text-decoration: line-through');
    });

    it('should not apply strikethrough to incomplete task title', () => {
      const incompleteTask = { ...mockTask, completed: false };

      render(
        <TaskItem
          task={incompleteTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const titleElement = screen.getByText('Test Task');
      expect(titleElement).toHaveStyle('text-decoration: none');
    });

    it('should reduce opacity for completed task', () => {
      const completedTask = { ...mockTask, completed: true };

      render(
        <TaskItem
          task={completedTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const cardElement = screen.getByText('Test Task').closest('div');
      expect(cardElement).toHaveStyle('opacity: 0.7');
    });
  });

  describe('Priority Badge Styling', () => {
    it('should render high priority badge', () => {
      const highPriorityTask = { ...mockTask, priority: 'High' };

      render(
        <TaskItem
          task={highPriorityTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const badge = screen.getByText('High');
      expect(badge).toHaveClass('badge-high');
    });

    it('should render medium priority badge', () => {
      const mediumPriorityTask = { ...mockTask, priority: 'Medium' };

      render(
        <TaskItem
          task={mediumPriorityTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const badge = screen.getByText('Medium');
      expect(badge).toHaveClass('badge-medium');
    });

    it('should render low priority badge', () => {
      const lowPriorityTask = { ...mockTask, priority: 'Low' };

      render(
        <TaskItem
          task={lowPriorityTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const badge = screen.getByText('Low');
      expect(badge).toHaveClass('badge-low');
    });
  });

  describe('Button Actions', () => {
    it('should call onToggleComplete when Done button is clicked', async () => {
      const user = userEvent.setup();

      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const doneButton = screen.getByText('Done');
      await user.click(doneButton);

      expect(mockOnToggleComplete).toHaveBeenCalledWith(mockTask);
    });

    it('should call onToggleComplete when Undo button is clicked', async () => {
      const user = userEvent.setup();
      const completedTask = { ...mockTask, completed: true };

      render(
        <TaskItem
          task={completedTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const undoButton = screen.getByText('Undo');
      await user.click(undoButton);

      expect(mockOnToggleComplete).toHaveBeenCalledWith(completedTask);
    });

    it('should call onEdit when Edit button is clicked', async () => {
      const user = userEvent.setup();

      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const editButton = screen.getByText('Edit');
      await user.click(editButton);

      expect(mockOnEdit).toHaveBeenCalledWith(mockTask);
    });

    it('should show confirmation dialog when Delete button is clicked', async () => {
      const user = userEvent.setup();
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this task?');
      confirmSpy.mockRestore();
    });

    it('should call onDelete when Delete is confirmed', async () => {
      const user = userEvent.setup();
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      expect(mockOnDelete).toHaveBeenCalledWith(mockTask.id);
      confirmSpy.mockRestore();
    });

    it('should not call onDelete when Delete is cancelled', async () => {
      const user = userEvent.setup();
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);

      render(
        <TaskItem
          task={mockTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const deleteButton = screen.getByText('Delete');
      await user.click(deleteButton);

      expect(mockOnDelete).not.toHaveBeenCalled();
      confirmSpy.mockRestore();
    });
  });

  describe('Unicode and Special Characters', () => {
    it('should handle unicode characters in title', () => {
      const unicodeTask = { ...mockTask, title: '买菜 🛒' };

      render(
        <TaskItem
          task={unicodeTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('买菜 🛒')).toBeInTheDocument();
    });

    it('should handle unicode characters in description', () => {
      const unicodeTask = { ...mockTask, description: 'Comprar 🥛🥚🍞' };

      render(
        <TaskItem
          task={unicodeTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Comprar 🥛🥚🍞')).toBeInTheDocument();
    });

    it('should handle special characters in title', () => {
      const specialTask = { ...mockTask, title: 'Task with "quotes" and \'apostrophes\'' };

      render(
        <TaskItem
          task={specialTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Task with "quotes" and \'apostrophes\'')).toBeInTheDocument();
    });

    it('should handle very long title', () => {
      const longTitle = 'A'.repeat(200);
      const longTask = { ...mockTask, title: longTitle };

      render(
        <TaskItem
          task={longTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText(longTitle)).toBeInTheDocument();
    });

    it('should handle very long description', () => {
      const longDesc = 'B'.repeat(500);
      const longTask = { ...mockTask, description: longDesc };

      render(
        <TaskItem
          task={longTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText(longDesc)).toBeInTheDocument();
    });
  });

  describe('Category Display', () => {
    it('should display Work category', () => {
      const workTask = { ...mockTask, category: 'Work' };

      render(
        <TaskItem
          task={workTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Work')).toBeInTheDocument();
    });

    it('should display Personal category', () => {
      const personalTask = { ...mockTask, category: 'Personal' };

      render(
        <TaskItem
          task={personalTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Personal')).toBeInTheDocument();
    });

    it('should display Study category', () => {
      const studyTask = { ...mockTask, category: 'Study' };

      render(
        <TaskItem
          task={studyTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText('Study')).toBeInTheDocument();
    });
  });

  describe('Date Formatting', () => {
    it('should format due date correctly', () => {
      const task = { ...mockTask, due_date: '2026-04-15' };

      render(
        <TaskItem
          task={task}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      // Date should be formatted by toLocaleDateString
      expect(screen.getByText(/Due:/)).toBeInTheDocument();
    });

    it('should handle different date formats', () => {
      const task = { ...mockTask, due_date: '2026-12-25' };

      render(
        <TaskItem
          task={task}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      expect(screen.getByText(/Due:/)).toBeInTheDocument();
    });
  });

  describe('Button Accessibility', () => {
    it('should have proper button titles', () => {
      const incompleteTask = { ...mockTask, completed: false };

      render(
        <TaskItem
          task={incompleteTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const doneButton = screen.getByTitle('Mark as completed');
      expect(doneButton).toBeInTheDocument();
    });

    it('should have proper button title for completed task', () => {
      const completedTask = { ...mockTask, completed: true };

      render(
        <TaskItem
          task={completedTask}
          onToggleComplete={mockOnToggleComplete}
          onDelete={mockOnDelete}
          onEdit={mockOnEdit}
        />
      );

      const undoButton = screen.getByTitle('Mark as pending');
      expect(undoButton).toBeInTheDocument();
    });
  });
});

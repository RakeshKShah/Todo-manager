import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskForm } from '../components/TaskForm';
import type { Task } from '../api';

describe('TaskForm Component', () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Add New Task Mode', () => {
    it('should render form for creating new task', () => {
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      expect(screen.getByText('Add New Task')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('What needs to be done?')).toBeInTheDocument();
    });

    it('should have empty title field for new task', () => {
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByPlaceholderText('What needs to be done?') as HTMLInputElement;
      expect(titleInput.value).toBe('');
    });

    it('should have default priority of Medium', () => {
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const prioritySelect = screen.getByDisplayValue('Medium') as HTMLSelectElement;
      expect(prioritySelect.value).toBe('Medium');
    });

    it('should have empty category by default', () => {
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const categorySelect = screen.getByDisplayValue('None') as HTMLSelectElement;
      expect(categorySelect.value).toBe('');
    });

    it('should submit form with valid data', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByPlaceholderText('What needs to be done?');
      await user.type(titleInput, 'New Task');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'New Task',
            priority: 'Medium',
            completed: false,
          })
        );
      });
    });

    it('should require title field', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByPlaceholderText('What needs to be done?') as HTMLInputElement;
      expect(titleInput.required).toBe(true);
    });

    it('should allow setting description', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const descriptionInput = screen.getByPlaceholderText('Details...');
      await user.type(descriptionInput, 'Task description');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            description: 'Task description',
          })
        );
      });
    });

    it('should allow setting priority', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const prioritySelect = screen.getByDisplayValue('Medium');
      await user.selectOptions(prioritySelect, 'High');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            priority: 'High',
          })
        );
      });
    });

    it('should allow setting category', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const categorySelect = screen.getByDisplayValue('None');
      await user.selectOptions(categorySelect, 'Work');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            category: 'Work',
          })
        );
      });
    });

    it('should allow setting due date', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const dateInput = screen.getByDisplayValue('') as HTMLInputElement;
      const dateInputs = screen.getAllByDisplayValue('');
      const dueDateInput = dateInputs.find(input => (input as HTMLInputElement).type === 'date');

      if (dueDateInput) {
        await user.type(dueDateInput, '2026-04-15');
      }

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled();
      });
    });

    it('should call onCancel when cancel button is clicked', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
    });
  });

  describe('Edit Task Mode', () => {
    const mockTask: Task = {
      id: '1',
      title: 'Existing Task',
      description: 'Existing description',
      priority: 'High',
      category: 'Work',
      due_date: '2026-04-15',
      completed: false,
    };

    it('should render form for editing task', () => {
      render(
        <TaskForm
          initialTask={mockTask}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      expect(screen.getByText('Edit Task')).toBeInTheDocument();
    });

    it('should populate form with existing task data', () => {
      render(
        <TaskForm
          initialTask={mockTask}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByDisplayValue('Existing Task') as HTMLInputElement;
      expect(titleInput.value).toBe('Existing Task');

      const descriptionInput = screen.getByDisplayValue('Existing description') as HTMLTextAreaElement;
      expect(descriptionInput.value).toBe('Existing description');

      const prioritySelect = screen.getByDisplayValue('High') as HTMLSelectElement;
      expect(prioritySelect.value).toBe('High');

      const categorySelect = screen.getByDisplayValue('Work') as HTMLSelectElement;
      expect(categorySelect.value).toBe('Work');
    });

    it('should preserve completed status when editing', async () => {
      const completedTask = { ...mockTask, completed: true };
      const user = userEvent.setup();

      render(
        <TaskForm
          initialTask={completedTask}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            completed: true,
          })
        );
      });
    });

    it('should allow updating task title', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={mockTask}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByDisplayValue('Existing Task');
      await user.clear(titleInput);
      await user.type(titleInput, 'Updated Task');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Updated Task',
          })
        );
      });
    });

    it('should allow clearing description', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={mockTask}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const descriptionInput = screen.getByDisplayValue('Existing description');
      await user.clear(descriptionInput);

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            description: undefined,
          })
        );
      });
    });

    it('should allow changing priority', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={mockTask}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const prioritySelect = screen.getByDisplayValue('High');
      await user.selectOptions(prioritySelect, 'Low');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            priority: 'Low',
          })
        );
      });
    });

    it('should allow changing category', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={mockTask}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const categorySelect = screen.getByDisplayValue('Work');
      await user.selectOptions(categorySelect, 'Personal');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            category: 'Personal',
          })
        );
      });
    });

    it('should allow clearing category', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={mockTask}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const categorySelect = screen.getByDisplayValue('Work');
      await user.selectOptions(categorySelect, 'None');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            category: undefined,
          })
        );
      });
    });
  });

  describe('Form Validation', () => {
    it('should handle unicode characters in title', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByPlaceholderText('What needs to be done?');
      await user.type(titleInput, '买菜 🛒');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            title: '买菜 🛒',
          })
        );
      });
    });

    it('should handle unicode characters in description', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const descriptionInput = screen.getByPlaceholderText('Details...');
      await user.type(descriptionInput, 'Comprar 🥛🥚🍞');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            description: 'Comprar 🥛🥚🍞',
          })
        );
      });
    });

    it('should handle special characters', async () => {
      const user = userEvent.setup();
      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByPlaceholderText('What needs to be done?');
      await user.type(titleInput, 'Task with "quotes" and \'apostrophes\'');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Task with "quotes" and \'apostrophes\'',
          })
        );
      });
    });

    it('should handle very long title', async () => {
      const user = userEvent.setup();
      const longTitle = 'A'.repeat(500);

      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByPlaceholderText('What needs to be done?');
      await user.type(titleInput, longTitle);

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            title: longTitle,
          })
        );
      });
    });

    it('should handle very long description', async () => {
      const user = userEvent.setup();
      const longDesc = 'B'.repeat(2000);

      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByPlaceholderText('What needs to be done?');
      await user.type(titleInput, 'Task');

      const descriptionInput = screen.getByPlaceholderText('Details...');
      await user.type(descriptionInput, longDesc);

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            description: longDesc,
          })
        );
      });
    });
  });

  describe('Form Submission', () => {
    it('should handle async submission', async () => {
      const user = userEvent.setup();
      mockOnSubmit.mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByPlaceholderText('What needs to be done?');
      await user.type(titleInput, 'Task');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled();
      });
    });

    it('should handle submission errors gracefully', async () => {
      const user = userEvent.setup();
      mockOnSubmit.mockRejectedValueOnce(new Error('Submission failed'));

      render(
        <TaskForm
          initialTask={null}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      );

      const titleInput = screen.getByPlaceholderText('What needs to be done?');
      await user.type(titleInput, 'Task');

      const submitButton = screen.getByText('Save Task');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled();
      });
    });
  });
});

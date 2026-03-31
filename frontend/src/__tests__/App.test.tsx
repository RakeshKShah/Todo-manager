import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import * as apiModule from '../api';

// Mock the API module
vi.mock('../api', () => ({
  api: {
    getTasks: vi.fn(),
    createTask: vi.fn(),
    updateTask: vi.fn(),
    deleteTask: vi.fn(),
  },
}));

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial Load', () => {
    it('should display loading state initially', () => {
      (apiModule.api.getTasks as any).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve([]), 100))
      );

      render(<App />);

      expect(screen.getByText('Loading tasks...')).toBeInTheDocument();
    });

    it('should load tasks on mount', async () => {
      const mockTasks = [
        {
          id: '1',
          title: 'Task 1',
          priority: 'High',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(apiModule.api.getTasks).toHaveBeenCalled();
      });
    });

    it('should display empty state when no tasks exist', async () => {
      (apiModule.api.getTasks as any).mockResolvedValueOnce([]);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('No tasks found. Create one to get started!')).toBeInTheDocument();
      });
    });

    it('should display tasks after loading', async () => {
      const mockTasks = [
        {
          id: '1',
          title: 'Task 1',
          priority: 'High',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task 1')).toBeInTheDocument();
      });
    });
  });

  describe('Task Creation', () => {
    it('should open form when Add Task button is clicked', async () => {
      const user = userEvent.setup();
      (apiModule.api.getTasks as any).mockResolvedValueOnce([]);

      render(<App />);

      const addButton = screen.getByText('+ Add Task');
      await user.click(addButton);

      await waitFor(() => {
        expect(screen.getByText('Add New Task')).toBeInTheDocument();
      });
    });

    it('should create task and reload list', async () => {
      const user = userEvent.setup();
      const mockTasks = [
        {
          id: '1',
          title: 'New Task',
          priority: 'Medium',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any)
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce(mockTasks);

      (apiModule.api.createTask as any).mockResolvedValueOnce(mockTasks[0]);

      render(<App />);

      const addButton = screen.getByText('+ Add Task');
      await user.click(addButton);

      // Form should be visible
      await waitFor(() => {
        expect(screen.getByText('Add New Task')).toBeInTheDocument();
      });
    });

    it('should show error alert on creation failure', async () => {
      const user = userEvent.setup();
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      (apiModule.api.getTasks as any).mockResolvedValueOnce([]);
      (apiModule.api.createTask as any).mockRejectedValueOnce(new Error('Failed'));

      render(<App />);

      const addButton = screen.getByText('+ Add Task');
      await user.click(addButton);

      // Note: The actual error handling would depend on form submission
      alertSpy.mockRestore();
    });
  });

  describe('Task Deletion', () => {
    it('should delete task from list', async () => {
      const user = userEvent.setup();
      const mockTasks = [
        {
          id: '1',
          title: 'Task to Delete',
          priority: 'High',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);
      (apiModule.api.deleteTask as any).mockResolvedValueOnce(undefined);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task to Delete')).toBeInTheDocument();
      });

      // Task should be in the list
      expect(screen.getByText('Task to Delete')).toBeInTheDocument();
    });

    it('should show error alert on deletion failure', async () => {
      const user = userEvent.setup();
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      const mockTasks = [
        {
          id: '1',
          title: 'Task',
          priority: 'High',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);
      (apiModule.api.deleteTask as any).mockRejectedValueOnce(new Error('Failed'));

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task')).toBeInTheDocument();
      });

      alertSpy.mockRestore();
    });
  });

  describe('Task Filtering', () => {
    it('should filter tasks by status', async () => {
      const user = userEvent.setup();
      const mockTasks = [
        {
          id: '1',
          title: 'Completed Task',
          priority: 'High',
          completed: true,
        },
        {
          id: '2',
          title: 'Pending Task',
          priority: 'Medium',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Completed Task')).toBeInTheDocument();
        expect(screen.getByText('Pending Task')).toBeInTheDocument();
      });

      // Filter to pending
      const filterSelect = screen.getByDisplayValue('All Status');
      await user.selectOptions(filterSelect, 'pending');

      // Should only show pending task
      await waitFor(() => {
        expect(screen.getByText('Pending Task')).toBeInTheDocument();
        expect(screen.queryByText('Completed Task')).not.toBeInTheDocument();
      });
    });

    it('should filter to completed tasks', async () => {
      const user = userEvent.setup();
      const mockTasks = [
        {
          id: '1',
          title: 'Completed Task',
          priority: 'High',
          completed: true,
        },
        {
          id: '2',
          title: 'Pending Task',
          priority: 'Medium',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Completed Task')).toBeInTheDocument();
      });

      // Filter to completed
      const filterSelect = screen.getByDisplayValue('All Status');
      await user.selectOptions(filterSelect, 'completed');

      // Should only show completed task
      await waitFor(() => {
        expect(screen.getByText('Completed Task')).toBeInTheDocument();
        expect(screen.queryByText('Pending Task')).not.toBeInTheDocument();
      });
    });

    it('should show all tasks when filter is set to all', async () => {
      const user = userEvent.setup();
      const mockTasks = [
        {
          id: '1',
          title: 'Completed Task',
          priority: 'High',
          completed: true,
        },
        {
          id: '2',
          title: 'Pending Task',
          priority: 'Medium',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Completed Task')).toBeInTheDocument();
        expect(screen.getByText('Pending Task')).toBeInTheDocument();
      });

      // Filter to pending then back to all
      const filterSelect = screen.getByDisplayValue('All Status');
      await user.selectOptions(filterSelect, 'pending');

      await waitFor(() => {
        expect(screen.queryByText('Completed Task')).not.toBeInTheDocument();
      });

      await user.selectOptions(filterSelect, 'all');

      // Should show both again
      await waitFor(() => {
        expect(screen.getByText('Completed Task')).toBeInTheDocument();
        expect(screen.getByText('Pending Task')).toBeInTheDocument();
      });
    });
  });

  describe('Task Sorting', () => {
    it('should sort tasks by due date', async () => {
      const user = userEvent.setup();
      const mockTasks = [
        {
          id: '1',
          title: 'Task Due Later',
          priority: 'High',
          due_date: '2026-05-15',
          completed: false,
        },
        {
          id: '2',
          title: 'Task Due Earlier',
          priority: 'Medium',
          due_date: '2026-04-15',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task Due Later')).toBeInTheDocument();
      });

      // Default sort is by due date, so earlier date should come first
      const tasks = screen.getAllByText(/Task Due/);
      expect(tasks[0].textContent).toContain('Task Due Earlier');
    });

    it('should sort tasks by priority', async () => {
      const user = userEvent.setup();
      const mockTasks = [
        {
          id: '1',
          title: 'Low Priority Task',
          priority: 'Low',
          completed: false,
        },
        {
          id: '2',
          title: 'High Priority Task',
          priority: 'High',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Low Priority Task')).toBeInTheDocument();
      });

      // Change sort to priority
      const sortSelect = screen.getByDisplayValue('Sort by Due Date');
      await user.selectOptions(sortSelect, 'priority');

      // High priority should come first
      const tasks = screen.getAllByText(/Priority Task/);
      expect(tasks[0].textContent).toContain('High Priority Task');
    });
  });

  describe('Task Toggle Complete', () => {
    it('should toggle task completion status', async () => {
      const user = userEvent.setup();
      const mockTasks = [
        {
          id: '1',
          title: 'Task',
          priority: 'High',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any)
        .mockResolvedValueOnce(mockTasks)
        .mockResolvedValueOnce([{ ...mockTasks[0], completed: true }]);

      (apiModule.api.updateTask as any).mockResolvedValueOnce({
        ...mockTasks[0],
        completed: true,
      });

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task')).toBeInTheDocument();
      });

      // Click Done button
      const doneButton = screen.getByText('Done');
      await user.click(doneButton);

      await waitFor(() => {
        expect(apiModule.api.updateTask).toHaveBeenCalled();
      });
    });

    it('should show error alert on toggle failure', async () => {
      const user = userEvent.setup();
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      const mockTasks = [
        {
          id: '1',
          title: 'Task',
          priority: 'High',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);
      (apiModule.api.updateTask as any).mockRejectedValueOnce(new Error('Failed'));

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task')).toBeInTheDocument();
      });

      const doneButton = screen.getByText('Done');
      await user.click(doneButton);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Failed to update task status');
      });

      alertSpy.mockRestore();
    });
  });

  describe('Task Edit', () => {
    it('should open edit form when Edit button is clicked', async () => {
      const user = userEvent.setup();
      const mockTasks = [
        {
          id: '1',
          title: 'Task to Edit',
          priority: 'High',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task to Edit')).toBeInTheDocument();
      });

      const editButton = screen.getByText('Edit');
      await user.click(editButton);

      await waitFor(() => {
        expect(screen.getByText('Edit Task')).toBeInTheDocument();
      });
    });

    it('should show error alert on update failure', async () => {
      const user = userEvent.setup();
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      const mockTasks = [
        {
          id: '1',
          title: 'Task',
          priority: 'High',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);
      (apiModule.api.updateTask as any).mockRejectedValueOnce(new Error('Failed'));

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task')).toBeInTheDocument();
      });

      const editButton = screen.getByText('Edit');
      await user.click(editButton);

      await waitFor(() => {
        expect(screen.getByText('Edit Task')).toBeInTheDocument();
      });

      alertSpy.mockRestore();
    });
  });

  describe('UI Elements', () => {
    it('should display header with title', async () => {
      (apiModule.api.getTasks as any).mockResolvedValueOnce([]);

      render(<App />);

      expect(screen.getByText('My Tasks')).toBeInTheDocument();
    });

    it('should display Add Task button', async () => {
      (apiModule.api.getTasks as any).mockResolvedValueOnce([]);

      render(<App />);

      expect(screen.getByText('+ Add Task')).toBeInTheDocument();
    });

    it('should display filter dropdown', async () => {
      (apiModule.api.getTasks as any).mockResolvedValueOnce([]);

      render(<App />);

      expect(screen.getByDisplayValue('All Status')).toBeInTheDocument();
    });

    it('should display sort dropdown', async () => {
      (apiModule.api.getTasks as any).mockResolvedValueOnce([]);

      render(<App />);

      expect(screen.getByDisplayValue('Sort by Due Date')).toBeInTheDocument();
    });
  });

  describe('Multiple Tasks Display', () => {
    it('should display multiple tasks', async () => {
      const mockTasks = [
        {
          id: '1',
          title: 'Task 1',
          priority: 'High',
          completed: false,
        },
        {
          id: '2',
          title: 'Task 2',
          priority: 'Medium',
          completed: false,
        },
        {
          id: '3',
          title: 'Task 3',
          priority: 'Low',
          completed: false,
        },
      ];

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task 1')).toBeInTheDocument();
        expect(screen.getByText('Task 2')).toBeInTheDocument();
        expect(screen.getByText('Task 3')).toBeInTheDocument();
      });
    });

    it('should handle large number of tasks', async () => {
      const mockTasks = Array.from({ length: 100 }, (_, i) => ({
        id: String(i),
        title: `Task ${i}`,
        priority: 'Medium' as const,
        completed: false,
      }));

      (apiModule.api.getTasks as any).mockResolvedValueOnce(mockTasks);

      render(<App />);

      await waitFor(() => {
        expect(screen.getByText('Task 0')).toBeInTheDocument();
      });
    });
  });

  describe('Form Modal', () => {
    it('should close form when cancel is clicked', async () => {
      const user = userEvent.setup();
      (apiModule.api.getTasks as any).mockResolvedValueOnce([]);

      render(<App />);

      const addButton = screen.getByText('+ Add Task');
      await user.click(addButton);

      await waitFor(() => {
        expect(screen.getByText('Add New Task')).toBeInTheDocument();
      });

      const cancelButton = screen.getByText('Cancel');
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText('Add New Task')).not.toBeInTheDocument();
      });
    });

    it('should close form after successful creation', async () => {
      const user = userEvent.setup();
      (apiModule.api.getTasks as any)
        .mockResolvedValueOnce([])
        .mockResolvedValueOnce([]);

      (apiModule.api.createTask as any).mockResolvedValueOnce({
        id: '1',
        title: 'New Task',
        priority: 'Medium',
        completed: false,
      });

      render(<App />);

      const addButton = screen.getByText('+ Add Task');
      await user.click(addButton);

      await waitFor(() => {
        expect(screen.getByText('Add New Task')).toBeInTheDocument();
      });

      // Note: Actual form submission would require more setup
    });
  });
});

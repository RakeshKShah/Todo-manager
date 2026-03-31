import { describe, it, expect, beforeEach, vi } from 'vitest';
import { api } from '../api';

// Mock fetch globally
global.fetch = vi.fn();

describe('API - getTasks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch tasks successfully', async () => {
    const mockTasks = [
      {
        id: '1',
        title: 'Task 1',
        description: 'Desc 1',
        priority: 'High',
        category: 'Work',
        due_date: '2026-04-15',
        completed: false,
      },
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockTasks,
    });

    const result = await api.getTasks();
    expect(result).toEqual(mockTasks);
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/tasks');
  });

  it('should return empty array when no tasks exist', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    const result = await api.getTasks();
    expect(result).toEqual([]);
  });

  it('should throw error when fetch fails', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
    });

    await expect(api.getTasks()).rejects.toThrow('Failed to fetch tasks');
  });

  it('should throw error on network failure', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    await expect(api.getTasks()).rejects.toThrow('Network error');
  });

  it('should handle multiple tasks with different priorities', async () => {
    const mockTasks = [
      { id: '1', title: 'High Priority', priority: 'High', completed: false },
      { id: '2', title: 'Medium Priority', priority: 'Medium', completed: false },
      { id: '3', title: 'Low Priority', priority: 'Low', completed: false },
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockTasks,
    });

    const result = await api.getTasks();
    expect(result).toHaveLength(3);
    expect(result[0].priority).toBe('High');
    expect(result[1].priority).toBe('Medium');
    expect(result[2].priority).toBe('Low');
  });

  it('should handle tasks with unicode characters', async () => {
    const mockTasks = [
      {
        id: '1',
        title: '买菜 🛒',
        description: 'Comprar 🥛🥚🍞',
        priority: 'Medium',
        completed: false,
      },
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockTasks,
    });

    const result = await api.getTasks();
    expect(result[0].title).toBe('买菜 🛒');
    expect(result[0].description).toBe('Comprar 🥛🥚🍞');
  });

  it('should handle tasks with null optional fields', async () => {
    const mockTasks = [
      {
        id: '1',
        title: 'Task',
        description: null,
        priority: 'Medium',
        category: null,
        due_date: null,
        completed: false,
      },
    ];

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockTasks,
    });

    const result = await api.getTasks();
    expect(result[0].description).toBeNull();
    expect(result[0].category).toBeNull();
    expect(result[0].due_date).toBeNull();
  });
});

describe('API - createTask', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should create a task successfully', async () => {
    const taskData = {
      title: 'New Task',
      description: 'Task description',
      priority: 'High' as const,
      category: 'Work' as const,
      due_date: '2026-04-15',
      completed: false,
    };

    const mockResponse = { id: '123', ...taskData };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await api.createTask(taskData);
    expect(result).toEqual(mockResponse);
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskData),
    });
  });

  it('should create task with minimal fields', async () => {
    const taskData = {
      title: 'Minimal Task',
      priority: 'Medium' as const,
      completed: false,
    };

    const mockResponse = { id: '456', ...taskData };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await api.createTask(taskData);
    expect(result.title).toBe('Minimal Task');
    expect(result.id).toBe('456');
  });

  it('should throw error when create fails', async () => {
    const taskData = {
      title: 'Task',
      priority: 'Medium' as const,
      completed: false,
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
    });

    await expect(api.createTask(taskData)).rejects.toThrow('Failed to create task');
  });

  it('should handle unicode in task creation', async () => {
    const taskData = {
      title: '买菜 🛒',
      description: 'Comprar 🥛',
      priority: 'High' as const,
      completed: false,
    };

    const mockResponse = { id: '789', ...taskData };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await api.createTask(taskData);
    expect(result.title).toBe('买菜 🛒');
  });

  it('should handle all priority levels', async () => {
    const priorities: Array<'Low' | 'Medium' | 'High'> = ['Low', 'Medium', 'High'];

    for (const priority of priorities) {
      const taskData = {
        title: `Task ${priority}`,
        priority,
        completed: false,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: '1', ...taskData }),
      });

      const result = await api.createTask(taskData);
      expect(result.priority).toBe(priority);
    }
  });

  it('should handle all categories', async () => {
    const categories: Array<'Work' | 'Personal' | 'Study'> = ['Work', 'Personal', 'Study'];

    for (const category of categories) {
      const taskData = {
        title: `Task ${category}`,
        priority: 'Medium' as const,
        category,
        completed: false,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: '1', ...taskData }),
      });

      const result = await api.createTask(taskData);
      expect(result.category).toBe(category);
    }
  });
});

describe('API - updateTask', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should update a task successfully', async () => {
    const taskData = {
      title: 'Updated Task',
      priority: 'High' as const,
      completed: true,
    };

    const mockResponse = { id: '123', ...taskData };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await api.updateTask('123', taskData);
    expect(result).toEqual(mockResponse);
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/tasks/123', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskData),
    });
  });

  it('should throw error when update fails', async () => {
    const taskData = {
      title: 'Task',
      priority: 'Medium' as const,
      completed: false,
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
    });

    await expect(api.updateTask('999', taskData)).rejects.toThrow('Failed to update task');
  });

  it('should update task status', async () => {
    const taskData = {
      title: 'Task',
      priority: 'Medium' as const,
      completed: true,
    };

    const mockResponse = { id: '123', ...taskData };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await api.updateTask('123', taskData);
    expect(result.completed).toBe(true);
  });

  it('should handle partial updates', async () => {
    const taskData = {
      title: 'New Title',
      priority: 'Low' as const,
      completed: false,
    };

    const mockResponse = { id: '123', ...taskData };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await api.updateTask('123', taskData);
    expect(result.title).toBe('New Title');
    expect(result.priority).toBe('Low');
  });

  it('should handle unicode in updates', async () => {
    const taskData = {
      title: '更新任务 ✅',
      priority: 'High' as const,
      completed: false,
    };

    const mockResponse = { id: '123', ...taskData };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await api.updateTask('123', taskData);
    expect(result.title).toBe('更新任务 ✅');
  });
});

describe('API - deleteTask', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should delete a task successfully', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
    });

    await api.deleteTask('123');
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/tasks/123', {
      method: 'DELETE',
    });
  });

  it('should throw error when delete fails', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
    });

    await expect(api.deleteTask('999')).rejects.toThrow('Failed to delete task');
  });

  it('should handle network error on delete', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    await expect(api.deleteTask('123')).rejects.toThrow('Network error');
  });

  it('should delete task with special ID format', async () => {
    const specialId = 'abc-123-def-456';

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
    });

    await api.deleteTask(specialId);
    expect(global.fetch).toHaveBeenCalledWith(`http://localhost:8000/tasks/${specialId}`, {
      method: 'DELETE',
    });
  });
});

describe('API - Error Handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle 404 errors', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    await expect(api.getTasks()).rejects.toThrow('Failed to fetch tasks');
  });

  it('should handle 500 errors', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    await expect(api.getTasks()).rejects.toThrow('Failed to fetch tasks');
  });

  it('should handle timeout errors', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Timeout'));

    await expect(api.getTasks()).rejects.toThrow('Timeout');
  });

  it('should handle malformed JSON response', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => {
        throw new Error('Invalid JSON');
      },
    });

    await expect(api.getTasks()).rejects.toThrow('Invalid JSON');
  });
});

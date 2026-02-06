import { Task, TaskCreate, TaskUpdate, ApiError } from "./types";

/**
 * Centralized API client for backend communication
 *
 * Features:
 * - Automatic JWT token attachment to requests
 * - Consistent error handling
 * - Type-safe request/response handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Generic fetch wrapper with JWT token handling
 */
async function fetchWithAuth<T>(
  endpoint: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.message || error.error || "API request failed");
  }

  return response.json();
}

/**
 * API Client class with all backend endpoints
 */
export class ApiClient {
  constructor(private token: string) {}

  /**
   * Get all tasks for authenticated user
   */
  async getTasks(): Promise<Task[]> {
    return fetchWithAuth<Task[]>("/api/tasks", this.token);
  }

  /**
   * Get a specific task by ID
   */
  async getTask(taskId: number): Promise<Task> {
    return fetchWithAuth<Task>(`/api/tasks/${taskId}`, this.token);
  }

  /**
   * Create a new task
   */
  async createTask(task: TaskCreate): Promise<Task> {
    return fetchWithAuth<Task>("/api/tasks", this.token, {
      method: "POST",
      body: JSON.stringify(task),
    });
  }

  /**
   * Update an existing task
   */
  async updateTask(taskId: number, updates: TaskUpdate): Promise<Task> {
    return fetchWithAuth<Task>(`/api/tasks/${taskId}`, this.token, {
      method: "PUT",
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a task
   */
  async deleteTask(taskId: number): Promise<void> {
    return fetchWithAuth<void>(`/api/tasks/${taskId}`, this.token, {
      method: "DELETE",
    });
  }

  /**
   * Toggle task completion status
   */
  async toggleTask(taskId: number, completed: boolean): Promise<Task> {
    return this.updateTask(taskId, { completed });
  }
}

/**
 * Factory function to create API client with token
 */
export function createApiClient(token: string): ApiClient {
  return new ApiClient(token);
}

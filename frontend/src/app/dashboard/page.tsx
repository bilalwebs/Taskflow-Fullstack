"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { createApiClient } from "@/lib/api-client";
import { Task, TaskCreate } from "@/lib/types";
import Navbar from "@/components/Navbar";
import AuthModal from "@/components/AuthModal";

/**
 * Dashboard Layout Component
 *
 * Dark theme professional SaaS dashboard with:
 * - Navbar for navigation and theme toggle
 * - AuthModal for unauthenticated users
 * - Left sidebar navigation
 * - Stats cards
 * - Task management
 * - Right-side add task panel
 */

export default function DashboardPage() {
  const router = useRouter();
  const { user, token, isLoading: authLoading, signOut } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDescription, setNewTaskDescription] = useState("");
  const [newTaskPriority, setNewTaskPriority] = useState("medium");
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editTaskTitle, setEditTaskTitle] = useState("");
  const [editTaskDescription, setEditTaskDescription] = useState("");

  // Show auth modal if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      setShowAuthModal(true);
    }
  }, [authLoading, user, router]);

  // Fetch tasks on mount
  useEffect(() => {
    if (user && token) {
      fetchTasks();
    }
  }, [user, token]);

  // Listen for task updates from chatbot
  useEffect(() => {
    const handleTasksUpdated = () => {
      console.log("Tasks updated event received - refreshing dashboard");
      fetchTasks();
    };

    window.addEventListener("tasks_updated", handleTasksUpdated);

    return () => {
      window.removeEventListener("tasks_updated", handleTasksUpdated);
    };
  }, [user, token]);

  const fetchTasks = async () => {
    if (!token) return;

    setIsLoadingTasks(true);
    setError(null);

    try {
      const apiClient = createApiClient(token);
      const fetchedTasks = await apiClient.getTasks();
      setTasks(fetchedTasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoadingTasks(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !newTaskTitle.trim()) return;

    try {
      const apiClient = createApiClient(token);
      const newTask = await apiClient.createTask({
        title: newTaskTitle.trim(),
        description: newTaskDescription.trim() || undefined,
      });
      setTasks((prev) => [newTask, ...prev]);
      setNewTaskTitle("");
      setNewTaskDescription("");
      setNewTaskPriority("medium");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task");
    }
  };

  const handleToggleComplete = async (taskId: number, completed: boolean) => {
    if (!token) return;

    try {
      const apiClient = createApiClient(token);
      const task = tasks.find((t) => t.id === taskId);
      if (!task) return;

      const updatedTask = await apiClient.updateTask(taskId, {
        title: task.title,
        description: task.description ?? undefined,
        completed,
      });

      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? updatedTask : t))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update task");
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!token) return;

    try {
      const apiClient = createApiClient(token);
      await apiClient.deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete task");
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTaskId(task.id);
    setEditTaskTitle(task.title);
    setEditTaskDescription(task.description || "");
  };

  const handleUpdateTask = async (taskId: number) => {
    if (!token || !editTaskTitle.trim()) return;

    try {
      const apiClient = createApiClient(token);
      const task = tasks.find((t) => t.id === taskId);
      if (!task) return;

      const updatedTask = await apiClient.updateTask(taskId, {
        title: editTaskTitle.trim(),
        description: editTaskDescription.trim() || undefined,
        completed: task.completed,
      });

      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? updatedTask : t))
      );
      setEditingTaskId(null);
      setEditTaskTitle("");
      setEditTaskDescription("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update task");
    }
  };

  const handleCancelEdit = () => {
    setEditingTaskId(null);
    setEditTaskTitle("");
    setEditTaskDescription("");
  };

  const handleSignOut = () => {
    signOut();
    router.push("/signin");
  };

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
    // User is now authenticated, dashboard will load automatically
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#0B1120] flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  // Show auth modal if not authenticated
  if (!user) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-[#0B1120] via-[#1a1f3a] to-[#0B1120] pt-16">
          <AuthModal
            isOpen={showAuthModal}
            onClose={() => router.push("/")}
            onSuccess={handleAuthSuccess}
          />
        </div>
      </>
    );
  }

  const totalTasks = tasks.length;
  const pendingTasks = tasks.filter((t) => !t.completed).length;
  const completedTasks = tasks.filter((t) => t.completed).length;

  return (
    <>
      <Navbar />
      <div className="min-h-screen flex pt-16 transition-colors duration-300">
        {/* Left Sidebar */}
        <aside className="w-64 bg-[#111827]/60 backdrop-blur-xl border-r border-white/10 flex flex-col transition-colors">
          {/* Logo */}
          <div className="p-6 border-b border-white/10 transition-colors">
            <h1 className="text-2xl font-bold text-white transition-colors">TaskFlow</h1>
          </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <button className="w-full flex items-center gap-3 px-4 py-3 text-white bg-indigo-500 rounded-lg hover:bg-indigo-600 transition-all">
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
              />
            </svg>
            Dashboard
          </button>
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-[#1F2937]">
          <button
            onClick={handleSignOut}
            className="w-full flex items-center gap-3 px-4 py-3 text-gray-400 hover:text-white hover:bg-[#1F2937] rounded-lg transition-all"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-8">
          {/* Header */}
          <div className="mb-8">
            <h2 className="text-4xl font-bold text-white mb-2">Dashboard</h2>
            <p className="text-gray-400">Manage your tasks and stay organized</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Total Tasks */}
            <div className="bg-gradient-to-br from-[#111827] to-[#1F2937] border border-[#1F2937] rounded-xl p-6 hover:scale-[1.02] hover:shadow-lg transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-400 text-sm font-medium">Total Tasks</h3>
                <svg
                  className="h-8 w-8 text-indigo-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
              <p className="text-4xl font-bold text-white">{totalTasks}</p>
            </div>

            {/* Pending Tasks */}
            <div className="bg-gradient-to-br from-[#111827] to-[#1F2937] border border-[#1F2937] rounded-xl p-6 hover:scale-[1.02] hover:shadow-lg transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-400 text-sm font-medium">Pending</h3>
                <svg
                  className="h-8 w-8 text-yellow-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <p className="text-4xl font-bold text-white">{pendingTasks}</p>
            </div>

            {/* Completed Tasks */}
            <div className="bg-gradient-to-br from-[#111827] to-[#1F2937] border border-[#1F2937] rounded-xl p-6 hover:scale-[1.02] hover:shadow-lg transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-400 text-sm font-medium">Completed</h3>
                <svg
                  className="h-8 w-8 text-emerald-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <p className="text-4xl font-bold text-white">{completedTasks}</p>
            </div>
          </div>

          {/* Tasks and Add Task Panel */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Tasks List */}
            <div className="lg:col-span-2">
              <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6">
                <h3 className="text-xl font-bold text-white mb-6">Your Tasks</h3>

                {isLoadingTasks ? (
                  <div className="text-center py-12">
                    <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-500 border-r-transparent"></div>
                    <p className="text-gray-400 mt-4">Loading tasks...</p>
                  </div>
                ) : tasks.length === 0 ? (
                  <div className="text-center py-16">
                    <svg
                      className="h-16 w-16 text-gray-600 mx-auto mb-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                      />
                    </svg>
                    <h4 className="text-xl font-semibold text-white mb-2">No tasks found</h4>
                    <p className="text-gray-400">
                      Your productivity journey starts here. Add your first task to stay organized.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {tasks.map((task) => (
                      <div
                        key={task.id}
                        className={`border rounded-lg p-4 transition-all ${
                          task.completed
                            ? "bg-emerald-900/20 border-emerald-700/30"
                            : "bg-[#0B1120] border-[#1F2937] hover:border-indigo-500"
                        }`}
                      >
                        {editingTaskId === task.id ? (
                          // Edit Mode
                          <div className="space-y-3">
                            <input
                              type="text"
                              value={editTaskTitle}
                              onChange={(e) => setEditTaskTitle(e.target.value)}
                              className="w-full px-3 py-2 bg-[#111827] border border-[#1F2937] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                              placeholder="Task title"
                              autoFocus
                            />
                            <textarea
                              value={editTaskDescription}
                              onChange={(e) => setEditTaskDescription(e.target.value)}
                              rows={2}
                              className="w-full px-3 py-2 bg-[#111827] border border-[#1F2937] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                              placeholder="Task description (optional)"
                            />
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleUpdateTask(task.id)}
                                disabled={!editTaskTitle.trim()}
                                className="px-4 py-2 bg-indigo-500 text-white text-sm font-medium rounded-lg hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                Save
                              </button>
                              <button
                                onClick={handleCancelEdit}
                                className="px-4 py-2 bg-gray-600 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors"
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          // View Mode
                          <div className="flex items-start gap-3">
                            {/* Custom Circular Checkbox */}
                            <button
                              onClick={() => handleToggleComplete(task.id, !task.completed)}
                              className={`mt-1 h-6 w-6 rounded-full border-2 flex items-center justify-center transition-all flex-shrink-0 ${
                                task.completed
                                  ? "bg-emerald-500 border-emerald-500"
                                  : "border-gray-600 hover:border-indigo-500"
                              }`}
                            >
                              {task.completed && (
                                <svg
                                  className="h-4 w-4 text-white"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={3}
                                    d="M5 13l4 4L19 7"
                                  />
                                </svg>
                              )}
                            </button>
                            <div className="flex-1 min-w-0">
                              <h4
                                className={`font-medium break-words ${
                                  task.completed ? "line-through text-gray-500" : "text-white"
                                }`}
                              >
                                {task.title}
                              </h4>
                              {task.description && (
                                <p className={`text-sm mt-1 break-words ${
                                  task.completed ? "text-gray-500" : "text-gray-400"
                                }`}>
                                  {task.description}
                                </p>
                              )}
                            </div>
                            <div className="flex gap-2 flex-shrink-0">
                              <button
                                onClick={() => handleEditTask(task)}
                                className="text-gray-400 hover:text-indigo-400 transition-colors"
                                title="Edit task"
                              >
                                <svg
                                  className="h-5 w-5"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                                  />
                                </svg>
                              </button>
                              <button
                                onClick={() => handleDeleteTask(task.id)}
                                className="text-gray-400 hover:text-red-400 transition-colors"
                                title="Delete task"
                              >
                                <svg
                                  className="h-5 w-5"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                  />
                                </svg>
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Add Task Panel */}
            <div className="lg:col-span-1">
              <div className="bg-[#111827] border border-[#1F2937] rounded-xl p-6 sticky top-8">
                <h3 className="text-xl font-bold text-white mb-6">Add New Task</h3>

                <form onSubmit={handleCreateTask} className="space-y-4">
                  {/* Title Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Title
                    </label>
                    <input
                      type="text"
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      placeholder="Enter task title"
                      className="w-full px-4 py-2 bg-[#0B1120] border border-[#1F2937] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                      required
                    />
                  </div>

                  {/* Priority Dropdown */}
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Priority
                    </label>
                    <select
                      value={newTaskPriority}
                      onChange={(e) => setNewTaskPriority(e.target.value)}
                      className="w-full px-4 py-2 bg-[#0B1120] border border-[#1F2937] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>

                  {/* Description Textarea */}
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Description
                    </label>
                    <textarea
                      value={newTaskDescription}
                      onChange={(e) => setNewTaskDescription(e.target.value)}
                      placeholder="Enter task description (optional)"
                      rows={4}
                      className="w-full px-4 py-2 bg-[#0B1120] border border-[#1F2937] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all resize-none"
                    />
                  </div>

                  {/* Add Task Button */}
                  <button
                    type="submit"
                    className="w-full px-6 py-3 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white font-semibold rounded-lg hover:from-indigo-600 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    Add Task
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
    </>
  );
}

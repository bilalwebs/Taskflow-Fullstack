"use client";

import { Task } from "@/lib/types";
import TaskItem from "./TaskItem";

/**
 * TaskList Component
 *
 * Modern task list display with:
 * - Elegant empty state
 * - Smooth loading animation
 * - Professional error state
 * - Card-based layout
 */

interface TaskListProps {
  tasks: Task[];
  isLoading?: boolean;
  error?: string | null;
  onEdit: (task: Task) => void;
  onDelete: (taskId: number) => void;
  onToggleComplete: (taskId: number, completed: boolean) => void;
}

export default function TaskList({
  tasks,
  isLoading = false,
  error = null,
  onEdit,
  onDelete,
  onToggleComplete,
}: TaskListProps) {
  // Loading State
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="relative">
          <div className="h-16 w-16 rounded-full border-4 border-slate-200"></div>
          <div className="absolute top-0 left-0 h-16 w-16 rounded-full border-4 border-indigo-600 border-t-transparent animate-spin"></div>
        </div>
        <p className="mt-4 text-slate-600 font-medium">Loading your tasks...</p>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
          <svg
            className="h-8 w-8 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to load tasks</h3>
        <p className="text-sm text-red-700">{error}</p>
      </div>
    );
  }

  // Empty State
  if (tasks.length === 0) {
    return (
      <div className="bg-gradient-to-br from-slate-50 to-slate-100 border-2 border-dashed border-slate-300 rounded-2xl p-16 text-center">
        <div className="inline-flex items-center justify-center h-20 w-20 rounded-full bg-white shadow-sm mb-6">
          <svg
            className="h-10 w-10 text-slate-400"
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
        <h3 className="text-xl font-semibold text-slate-900 mb-2">No tasks yet</h3>
        <p className="text-slate-600 max-w-sm mx-auto">
          Get started by creating your first task or use the chat assistant to add tasks naturally.
        </p>
      </div>
    );
  }

  // Task List
  return (
    <div className="space-y-4">
      {/* Stats Header */}
      <div className="flex items-center justify-between px-1 mb-2">
        <h2 className="text-lg font-semibold text-slate-900">
          All Tasks
          <span className="ml-2 text-sm font-normal text-slate-500">
            ({tasks.length})
          </span>
        </h2>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-sky-500"></span>
            <span className="text-slate-600">
              {tasks.filter((t) => !t.completed).length} Active
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
            <span className="text-slate-600">
              {tasks.filter((t) => t.completed).length} Completed
            </span>
          </div>
        </div>
      </div>

      {/* Task Cards */}
      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onEdit={onEdit}
            onDelete={onDelete}
            onToggleComplete={onToggleComplete}
          />
        ))}
      </div>
    </div>
  );
}

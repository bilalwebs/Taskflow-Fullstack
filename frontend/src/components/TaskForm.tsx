"use client";

import { Task, TaskCreate } from "@/lib/types";
import { useState, FormEvent } from "react";

/**
 * TaskForm Component
 *
 * Form for creating or editing tasks with:
 * - Title input (required, max 200 chars)
 * - Description textarea (optional, max 2000 chars)
 * - Character counters
 * - Validation
 * - Loading states
 */

interface TaskFormProps {
  onSubmit: (data: TaskCreate) => Promise<void>;
  initialTask?: Task;
  onCancel: () => void;
}

export default function TaskForm({
  onSubmit,
  initialTask,
  onCancel,
}: TaskFormProps) {
  const [title, setTitle] = useState(initialTask?.title || "");
  const [description, setDescription] = useState(initialTask?.description || "");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const titleMaxLength = 200;
  const descriptionMaxLength = 2000;

  const titleCharsRemaining = titleMaxLength - title.length;
  const descriptionCharsRemaining = descriptionMaxLength - description.length;

  const isValid = title.trim().length > 0 && title.length <= titleMaxLength;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!isValid) {
      setError("Title is required and must be 200 characters or less");
      return;
    }

    if (description.length > descriptionMaxLength) {
      setError(`Description must be ${descriptionMaxLength} characters or less`);
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
      });
      // Reset form on successful create (not edit)
      if (!initialTask) {
        setTitle("");
        setDescription("");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save task");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-slate-900 mb-5">
        {initialTask ? "Edit Task" : "Create New Task"}
      </h2>

      {/* Error Message */}
      {error && (
        <div
          className="mb-5 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-start gap-3"
          role="alert"
        >
          <svg
            className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5"
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
          <span>{error}</span>
        </div>
      )}

      {/* Title Input */}
      <div className="mb-5">
        <label htmlFor="task-title" className="block text-sm font-semibold text-slate-700 mb-2">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          id="task-title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={titleMaxLength}
          className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-slate-900 placeholder:text-slate-400"
          placeholder="Enter task title"
          disabled={isSubmitting}
          required
          aria-required="true"
          aria-invalid={title.length > titleMaxLength}
        />
        <div className="flex justify-between items-center mt-2">
          <p className="text-xs text-slate-500">Required field</p>
          <p
            className={`text-xs font-medium ${
              titleCharsRemaining < 20 ? "text-red-500" : "text-slate-500"
            }`}
          >
            {titleCharsRemaining} characters remaining
          </p>
        </div>
      </div>

      {/* Description Textarea */}
      <div className="mb-6">
        <label htmlFor="task-description" className="block text-sm font-semibold text-slate-700 mb-2">
          Description <span className="text-slate-400 font-normal">(optional)</span>
        </label>
        <textarea
          id="task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={descriptionMaxLength}
          rows={4}
          className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-vertical transition-all text-slate-900 placeholder:text-slate-400"
          placeholder="Add more details about this task"
          disabled={isSubmitting}
          aria-invalid={description.length > descriptionMaxLength}
        />
        <div className="flex justify-end mt-2">
          <p
            className={`text-xs font-medium ${
              descriptionCharsRemaining < 100 ? "text-orange-500" : "text-slate-500"
            }`}
          >
            {descriptionCharsRemaining} characters remaining
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 justify-end">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-5 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 to-indigo-500 rounded-lg hover:from-indigo-700 hover:to-indigo-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
        >
          {isSubmitting ? (
            <span className="flex items-center gap-2">
              <svg
                className="animate-spin h-4 w-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Saving...
            </span>
          ) : (
            <span>{initialTask ? "Update Task" : "Create Task"}</span>
          )}
        </button>
      </div>
    </form>
  );
}

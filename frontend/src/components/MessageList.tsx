"use client";

import { Message } from "@/lib/types";

/**
 * MessageList Component
 *
 * Modern chat message display with:
 * - Elegant chat bubbles
 * - Role-based styling (user vs assistant)
 * - Avatar indicators
 * - Tool usage badges with emojis
 * - Enhanced formatting for task operations
 */

interface MessageListProps {
  messages: Message[];
}

/**
 * Get formatted success message based on tool call
 */
function getToolSuccessMessage(toolName: string): { emoji: string; message: string } | null {
  const toolMessages: Record<string, { emoji: string; message: string }> = {
    create_task: {
      emoji: "✅",
      message: "Task has been added successfully!"
    },
    delete_task: {
      emoji: "🗑️",
      message: "Task has been deleted successfully!"
    },
    update_task: {
      emoji: "✏️",
      message: "Task has been updated successfully!"
    },
    complete_task: {
      emoji: "✓",
      message: "Task has been marked as complete!"
    },
    list_tasks: {
      emoji: "📋",
      message: "Here are your tasks:"
    },
    get_task: {
      emoji: "👁️",
      message: "Task details:"
    }
  };

  return toolMessages[toolName] || null;
}

export function MessageList({ messages }: MessageListProps) {
  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col space-y-3">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${
            message.role === "user" ? "justify-end" : "justify-start"
          }`}
        >
          {/* Assistant Avatar */}
          {message.role === "assistant" && (
            <div className="flex-shrink-0 mr-2">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-600 to-sky-500 flex items-center justify-center">
                <svg
                  className="h-5 w-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
            </div>
          )}

          <div
            className={`max-w-[85%] rounded-2xl px-4 py-3 ${
              message.role === "user"
                ? "bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-sm"
                : "bg-white text-slate-900 shadow-sm border border-slate-200"
            }`}
          >
            {/* Tool Success Banner (for assistant messages with tool calls) */}
            {message.role === "assistant" && message.tool_calls && message.tool_calls.length > 0 && (
              <div className="mb-3 pb-3 border-b border-slate-200">
                {message.tool_calls.map((toolCall, index) => {
                  const successMsg = getToolSuccessMessage(toolCall.tool);
                  if (successMsg) {
                    return (
                      <div
                        key={index}
                        className="flex items-center gap-2 px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-lg mb-2 last:mb-0"
                      >
                        <span className="text-2xl">{successMsg.emoji}</span>
                        <span className="text-sm font-semibold text-emerald-700">
                          {successMsg.message}
                        </span>
                      </div>
                    );
                  }
                  return null;
                })}
              </div>
            )}

            {/* Message content */}
            <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
              {message.content}
            </div>

            {/* Timestamp */}
            <div
              className={`text-xs mt-2 ${
                message.role === "user" ? "text-indigo-100" : "text-slate-500"
              }`}
            >
              {new Date(message.created_at).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
                hour12: true,
              })}
            </div>
          </div>

          {/* User Avatar */}
          {message.role === "user" && (
            <div className="flex-shrink-0 ml-2">
              <div className="h-8 w-8 rounded-full bg-slate-300 flex items-center justify-center">
                <svg
                  className="h-5 w-5 text-slate-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

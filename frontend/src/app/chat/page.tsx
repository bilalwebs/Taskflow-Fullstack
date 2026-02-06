"use client";

import { useState } from "react";
import { ChatInterface } from "@/components/ChatInterface";
import { ConversationList } from "@/components/ConversationList";
import Link from "next/link";

/**
 * Chat Page
 *
 * Main page for conversational task management.
 * Users can interact with the AI agent to manage tasks through natural language.
 * Includes conversation history sidebar for resuming previous conversations.
 */

export default function ChatPage() {
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [key, setKey] = useState(0); // Key to force ChatInterface remount

  /**
   * Handle conversation selection from sidebar
   */
  const handleConversationSelect = (id: number) => {
    setConversationId(id);
    setKey((prev) => prev + 1); // Force remount to load new conversation
  };

  /**
   * Handle new conversation creation
   */
  const handleNewConversation = () => {
    setConversationId(null);
    setKey((prev) => prev + 1); // Force remount for new conversation
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-8">
              <h1 className="text-xl font-bold text-gray-900">KIro Todo</h1>
              <div className="flex gap-4">
                <Link
                  href="/dashboard"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  href="/chat"
                  className="text-blue-600 font-medium border-b-2 border-blue-600"
                >
                  Chat Assistant
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="h-[calc(100vh-4rem)] flex">
        {/* Conversation List Sidebar */}
        <ConversationList
          currentConversationId={conversationId || undefined}
          onConversationSelect={handleConversationSelect}
          onNewConversation={handleNewConversation}
        />

        {/* Chat Interface */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 p-6">
            <ChatInterface
              key={key}
              conversationId={conversationId || undefined}
              onConversationCreated={setConversationId}
            />
          </div>

          {/* Help Section */}
          <div className="px-6 pb-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">
                💡 How to use the assistant
              </h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>
                  <strong>Create tasks:</strong> "remind me to buy groceries",
                  "add task: call dentist"
                </li>
                <li>
                  <strong>View tasks:</strong> "show my tasks", "what do I need
                  to do today?"
                </li>
                <li>
                  <strong>Complete tasks:</strong> "I finished buying
                  groceries", "mark the first task as done"
                </li>
                <li>
                  <strong>Update tasks:</strong> "change 'buy milk' to 'buy
                  milk and eggs'"
                </li>
                <li>
                  <strong>Delete tasks:</strong> "delete the groceries task",
                  "remove my first task"
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

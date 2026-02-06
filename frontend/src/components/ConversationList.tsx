"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { createChatClient } from "@/lib/chat-client";

/**
 * ConversationList Component
 *
 * Displays a sidebar list of user's conversations.
 * Allows switching between conversations and starting new ones.
 */

interface Conversation {
  id: number;
  title: string | null;
  created_at: string;
  updated_at: string;
}

interface ConversationListProps {
  currentConversationId?: number;
  onConversationSelect: (conversationId: number) => void;
  onNewConversation: () => void;
}

export function ConversationList({
  currentConversationId,
  onConversationSelect,
  onNewConversation,
}: ConversationListProps) {
  const { user, token } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load conversations on mount
   */
  useEffect(() => {
    const loadConversations = async () => {
      if (!token || !user) return;

      try {
        setLoading(true);
        const chatClient = createChatClient(token, user.id);
        const response = await chatClient.getConversations();
        setConversations(response.conversations);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load conversations"
        );
      } finally {
        setLoading(false);
      }
    };

    loadConversations();
  }, [token, user]);

  /**
   * Format conversation title
   */
  const getConversationTitle = (conv: Conversation): string => {
    if (conv.title) return conv.title;
    return `Conversation ${conv.id}`;
  };

  /**
   * Format relative time
   */
  const getRelativeTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (!user || !token) {
    return null;
  }

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onNewConversation}
          className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          New Chat
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {loading && (
          <div className="p-4 text-center text-gray-500">
            Loading conversations...
          </div>
        )}

        {error && (
          <div className="p-4 text-center text-red-500 text-sm">{error}</div>
        )}

        {!loading && !error && conversations.length === 0 && (
          <div className="p-4 text-center text-gray-500 text-sm">
            No conversations yet. Start a new chat!
          </div>
        )}

        {!loading && !error && conversations.length > 0 && (
          <div className="py-2">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => onConversationSelect(conv.id)}
                className={`w-full text-left px-4 py-3 hover:bg-gray-100 transition-colors border-l-4 ${
                  currentConversationId === conv.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-transparent"
                }`}
              >
                <div className="font-medium text-gray-900 text-sm truncate">
                  {getConversationTitle(conv)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {getRelativeTime(conv.updated_at)}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
        {conversations.length} conversation{conversations.length !== 1 ? "s" : ""}
      </div>
    </div>
  );
}

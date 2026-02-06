"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { createChatClient } from "@/lib/chat-client";
import { useStreamingChat } from "@/hooks/useStreamingChat";
import { Message } from "@/lib/types";
import { MessageList } from "./MessageList";

/**
 * ChatInterface Component
 *
 * Main chat interface for conversational task management.
 * Handles message sending, conversation persistence, and real-time updates.
 * Supports both standard and streaming responses.
 */

interface ChatInterfaceProps {
  conversationId?: number;
  onConversationCreated?: (conversationId: number) => void;
  useStreaming?: boolean; // Toggle between streaming and standard mode
}

export function ChatInterface({
  conversationId: initialConversationId,
  onConversationCreated,
  useStreaming = false, // Default to standard mode for stability
}: ChatInterfaceProps) {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | undefined>(
    initialConversationId
  );
  const [streamingContent, setStreamingContent] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { sendStreamingMessage, isStreaming } = useStreamingChat();

  /**
   * Load conversation history on mount if conversationId is provided
   */
  useEffect(() => {
    const loadConversationHistory = async () => {
      if (!conversationId || !token || !user) return;

      try {
        setLoading(true);
        const chatClient = createChatClient(token, user.id);
        const response = await chatClient.getConversationHistory(conversationId);

        // Convert API messages to Message type
        const loadedMessages: Message[] = response.messages.map((msg) => ({
          id: msg.id,
          conversation_id: response.conversation_id,
          role: msg.role as "user" | "assistant",
          content: msg.content,
          tool_calls: msg.tool_calls || undefined,
          created_at: msg.created_at,
        }));

        setMessages(loadedMessages);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load conversation history"
        );
      } finally {
        setLoading(false);
      }
    };

    loadConversationHistory();
  }, [conversationId, token, user]);

  /**
   * Auto-scroll to bottom when new messages arrive
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  /**
   * Send message with streaming support
   */
  const sendMessageStreaming = async () => {
    if (!input.trim() || !token || !user) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);
    setStreamingContent("");

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: Date.now(),
      conversation_id: conversationId || 0,
      role: "user",
      content: userMessage,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMessage]);

    try {
      await sendStreamingMessage(userMessage, conversationId, {
        onChunk: (chunk) => {
          setStreamingContent((prev) => prev + chunk);
        },
        onComplete: (data) => {
          // Update conversation ID if new
          if (!conversationId && data.conversation_id) {
            setConversationId(data.conversation_id);
            onConversationCreated?.(data.conversation_id);
          }

          // Add complete assistant message
          const assistantMessage: Message = {
            id: data.message_id,
            conversation_id: data.conversation_id,
            role: "assistant",
            content: streamingContent,
            tool_calls: data.tool_calls || undefined,
            created_at: data.timestamp,
          };

          setMessages((prev) => [...prev, assistantMessage]);
          setStreamingContent("");

          // Dispatch event to refresh dashboard
          window.dispatchEvent(new CustomEvent("tasks_updated"));
        },
        onError: (errorMsg) => {
          setError(errorMsg);
          setMessages((prev) => prev.slice(0, -1)); // Remove temp user message
          setStreamingContent("");
        },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      setMessages((prev) => prev.slice(0, -1));
    }
  };

  /**
   * Send message (standard mode)
   */
  const sendMessage = async () => {
    if (!input.trim() || !token || !user) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);
    setLoading(true);

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      id: Date.now(),
      conversation_id: conversationId || 0,
      role: "user",
      content: userMessage,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMessage]);

    try {
      const chatClient = createChatClient(token, user.id);
      const response = await chatClient.sendMessage(userMessage, conversationId);

      // Update conversation ID if this is a new conversation
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
        onConversationCreated?.(response.conversation_id);
      }

      // Add assistant response to messages
      const assistantMessage: Message = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        role: "assistant",
        content: response.assistant_message,
        tool_calls: response.tool_calls || undefined,
        created_at: response.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Dispatch event to refresh dashboard
      window.dispatchEvent(new CustomEvent("tasks_updated"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle Enter key press to send message
   */
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (useStreaming) {
        sendMessageStreaming();
      } else {
        sendMessage();
      }
    }
  };

  const isProcessing = useStreaming ? isStreaming : loading;

  if (!user || !token) {
    return (
      <div className="flex items-center justify-center h-full p-6 bg-[#0B1120]">
        <p className="text-gray-400 text-sm">Please sign in to use the chat</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-[#0B1120]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 bg-[#0B1120]">
        {messages.length === 0 && !streamingContent && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="h-16 w-16 rounded-full bg-purple-500/20 flex items-center justify-center mb-4">
              <svg
                className="h-8 w-8 text-purple-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <h3 className="text-sm font-semibold text-white mb-2">
              Start a conversation
            </h3>
            <p className="text-xs text-gray-400 mb-4">
              Ask me to create, view, or manage your tasks
            </p>
            <div className="text-xs text-gray-500 space-y-1">
              <p>💡 Try: "add task: call dentist"</p>
              <p>💡 Try: "show my tasks"</p>
            </div>
          </div>
        )}

        <MessageList messages={messages} />

        {/* Show streaming content */}
        {streamingContent && (
          <div className="flex justify-start mb-3">
            <div className="max-w-[85%] rounded-2xl px-4 py-3 bg-[#111827] border border-purple-500/30">
              <div className="whitespace-pre-wrap break-words text-sm text-white">
                {streamingContent}
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-400 mt-2">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-purple-400 animate-bounce"></span>
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-purple-400 animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-purple-400 animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                <span className="ml-1">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-4 py-2 bg-red-500/10 border-t border-red-500/30">
          <p className="text-xs text-red-400 flex items-center gap-2">
            <svg
              className="h-4 w-4 flex-shrink-0"
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
            {error}
          </p>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-[#1F2937] px-4 py-3 bg-[#111827]">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              isProcessing
                ? "Thinking..."
                : "Type a message..."
            }
            disabled={isProcessing}
            className="flex-1 border border-[#1F2937] bg-[#0B1120] rounded-lg px-3 py-2 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          />
          <button
            onClick={useStreaming ? sendMessageStreaming : sendMessage}
            disabled={isProcessing || !input.trim()}
            className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-2 rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-purple-500/50 flex items-center justify-center"
            aria-label="Send message"
          >
            {isProcessing ? (
              <svg
                className="animate-spin h-5 w-5"
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
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            ) : (
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
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

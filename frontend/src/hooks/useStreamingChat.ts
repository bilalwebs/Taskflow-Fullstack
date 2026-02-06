"use client";

import { useState, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";

/**
 * useStreamingChat Hook
 *
 * Custom hook for streaming chat responses with Server-Sent Events (SSE).
 * Provides progressive message rendering for better user experience.
 */

interface StreamingChatOptions {
  onChunk?: (chunk: string) => void;
  onComplete?: (data: {
    conversation_id: number;
    message_id: number;
    tool_calls: any[] | null;
    timestamp: string;
  }) => void;
  onError?: (error: string) => void;
}

export function useStreamingChat() {
  const { user, token } = useAuth();
  const [isStreaming, setIsStreaming] = useState(false);

  const sendStreamingMessage = useCallback(
    async (
      message: string,
      conversationId: number | undefined,
      options: StreamingChatOptions = {}
    ) => {
      if (!token || !user) {
        options.onError?.("Authentication required");
        return;
      }

      setIsStreaming(true);

      try {
        const API_BASE_URL =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

        const response = await fetch(
          `${API_BASE_URL}/api/${user.id}/chat/stream`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              message,
              ...(conversationId && { conversation_id: conversationId }),
            }),
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
          throw new Error("Response body is not readable");
        }

        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.error) {
                  options.onError?.(data.error);
                  break;
                }

                if (data.done) {
                  if (data.conversation_id) {
                    options.onComplete?.({
                      conversation_id: data.conversation_id,
                      message_id: data.message_id,
                      tool_calls: data.tool_calls,
                      timestamp: data.timestamp,
                    });
                  }
                  break;
                }

                if (data.content) {
                  options.onChunk?.(data.content);
                }
              } catch (e) {
                console.error("Error parsing SSE data:", e);
              }
            }
          }
        }
      } catch (error) {
        options.onError?.(
          error instanceof Error ? error.message : "Failed to send message"
        );
      } finally {
        setIsStreaming(false);
      }
    },
    [token, user]
  );

  return {
    sendStreamingMessage,
    isStreaming,
  };
}

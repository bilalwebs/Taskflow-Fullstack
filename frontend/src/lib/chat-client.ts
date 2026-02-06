import { ChatRequest, ChatResponse, ApiError } from "./types";

/**
 * Chat API Client for conversational task management
 *
 * Features:
 * - Send messages to AI agent
 * - Automatic JWT token attachment
 * - Conversation persistence
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
 * Conversation list response
 */
interface ConversationListResponse {
  conversations: Array<{
    id: number;
    title: string | null;
    created_at: string;
    updated_at: string;
  }>;
  total: number;
}

/**
 * Conversation messages response
 */
interface ConversationMessagesResponse {
  conversation_id: number;
  messages: Array<{
    id: number;
    role: string;
    content: string;
    tool_calls: any;
    created_at: string;
  }>;
  total: number;
}

/**
 * Chat API Client class
 */
export class ChatClient {
  constructor(private token: string, private userId: number) {}

  /**
   * Send a message to the AI agent
   *
   * @param message - User's natural language message
   * @param conversationId - Optional conversation ID to continue existing conversation
   * @returns Agent response with conversation metadata
   */
  async sendMessage(
    message: string,
    conversationId?: number
  ): Promise<ChatResponse> {
    const payload: ChatRequest = {
      message,
      ...(conversationId && { conversation_id: conversationId }),
    };

    return fetchWithAuth<ChatResponse>(
      `/api/${this.userId}/chat`,
      this.token,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  }

  /**
   * Get list of all conversations for the user
   *
   * @returns List of conversations ordered by most recent
   */
  async getConversations(): Promise<ConversationListResponse> {
    return fetchWithAuth<ConversationListResponse>(
      `/api/${this.userId}/conversations`,
      this.token,
      {
        method: "GET",
      }
    );
  }

  /**
   * Get all messages in a specific conversation
   *
   * @param conversationId - ID of the conversation to retrieve
   * @returns List of messages in chronological order
   */
  async getConversationHistory(
    conversationId: number
  ): Promise<ConversationMessagesResponse> {
    return fetchWithAuth<ConversationMessagesResponse>(
      `/api/${this.userId}/conversations/${conversationId}/messages`,
      this.token,
      {
        method: "GET",
      }
    );
  }
}

/**
 * Factory function to create chat client with token and user ID
 */
export function createChatClient(token: string, userId: number): ChatClient {
  return new ChatClient(token, userId);
}

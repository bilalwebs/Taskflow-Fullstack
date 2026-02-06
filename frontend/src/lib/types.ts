// User type
export interface User {
  id: number;
  email: string;
  created_at: string;
}

// Task type
export interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

// API Error type
export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, any>;
}

// Task creation payload
export interface TaskCreate {
  title: string;
  description?: string;
}

// Task update payload
export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

// Conversation types for AI chat
export interface Conversation {
  id: number;
  user_id: number;
  title: string | null;
  created_at: string;
  updated_at: string;
}

// Message role enum
export type MessageRole = 'user' | 'assistant';

// Message type
export interface Message {
  id: number;
  conversation_id: number;
  role: MessageRole;
  content: string;
  tool_calls?: ToolCall[] | null;
  created_at: string;
}

// Tool call metadata
export interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
  duration_ms: number;
}

// Chat request payload
export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

// Chat response
export interface ChatResponse {
  conversation_id: number;
  message_id: number;
  assistant_message: string;
  tool_calls: ToolCall[] | null;
  timestamp: string;
}

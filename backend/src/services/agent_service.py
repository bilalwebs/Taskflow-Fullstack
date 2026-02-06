"""
Agent Service Module

This module provides the AgentService class that orchestrates AI agent interactions.
The service wraps MCP tools with user_id pre-bound for security and data isolation.
"""

from typing import List, Dict, Any, Optional
import json
import time
from openai import OpenAI
from ..config import settings
from ..tools.mcp_server import mcp_server, MCPContext
from ..tools import (
    get_list_tasks_definition,
    get_create_task_definition,
    get_mark_complete_definition,
    get_update_task_definition,
    get_delete_task_definition,
    get_get_task_definition
)
from ..database import engine


class AgentService:
    """
    Agent Service for processing conversational task management requests.

    This service:
    1. Initializes OpenAI client with configured API key
    2. Wraps MCP tools with user_id pre-bound for security
    3. Processes user messages with conversation history
    4. Returns agent responses with tool call metadata
    """

    def __init__(self, user_id: int):
        """
        Initialize AgentService for a specific user.

        Args:
            user_id: Authenticated user ID for data scoping
        """
        self.user_id = user_id

        # Configure client for OpenRouter if base URL is provided
        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if hasattr(settings, 'OPENAI_BASE_URL') and settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL

        self.client = OpenAI(**client_kwargs)
        self.model = settings.OPENAI_MODEL
        self.mcp_context = mcp_server.create_context(user_id=user_id)

    def create_user_scoped_tools(self) -> List[Dict[str, Any]]:
        """
        Create user-scoped tool definitions for OpenAI function calling.

        This method wraps internal MCP tools with user_id pre-bound,
        ensuring the agent can only access the authenticated user's data.

        Returns:
            List of tool definitions in OpenAI function calling format
        """
        tools = [
            get_list_tasks_definition(),
            get_create_task_definition(),
            get_mark_complete_definition(),
            get_update_task_definition(),
            get_delete_task_definition(),
            get_get_task_definition()
        ]

        return tools

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool with the given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments (user_id is pre-bound from context)

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        # Get tool function from MCP server
        tool_func = mcp_server.get_tool(tool_name)

        if not tool_func:
            raise ValueError(f"Tool '{tool_name}' not found")

        # Execute tool with user-scoped context
        try:
            result = await tool_func(self.mcp_context, **arguments)
            return result
        except Exception as e:
            print(f"Error executing tool '{tool_name}': {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process user message with conversation history and return agent response.

        This method implements the full OpenAI function calling workflow:
        1. Send message with tool definitions to OpenAI
        2. If model calls tools, execute them
        3. Send tool results back to model
        4. Return final natural language response

        Args:
            message: User's natural language input
            conversation_history: List of previous messages in conversation

        Returns:
            Dict containing:
                - content: Agent's natural language response
                - tool_calls: List of tool invocations with results (if any)
                - model: Model used for generation

        Raises:
            Exception: If OpenAI API call fails
        """
        # Build messages array for OpenAI API
        messages = []

        # Add system message for agent behavior
        system_prompt = (
            "You are a helpful task management assistant. "
            "You help users manage their tasks through natural conversation.\n\n"

            "**Task Creation Intent Recognition:**\n"
            "When users express intent to create a task, use the create_task tool. Examples:\n"
            "- 'remind me to X' → create_task(title='X')\n"
            "- 'add task X' → create_task(title='X')\n"
            "- 'I need to X' → create_task(title='X')\n"
            "- 'create a task for X' → create_task(title='X')\n"
            "- 'don't let me forget to X' → create_task(title='X')\n\n"

            "**Task Listing Intent Recognition:**\n"
            "When users want to see their tasks, use the list_tasks tool. Examples:\n"
            "- 'show my tasks' → list_tasks()\n"
            "- 'what do I need to do' → list_tasks()\n"
            "- 'list my todos' → list_tasks()\n"
            "- 'what are my tasks' → list_tasks()\n"
            "- 'show me my task list' → list_tasks()\n\n"

            "**Task Completion Intent Recognition:**\n"
            "When users indicate they finished a task, use mark_complete tool. Examples:\n"
            "- 'I finished X' → list_tasks() to find task, then mark_complete(task_id)\n"
            "- 'mark X as done' → list_tasks() to find task, then mark_complete(task_id)\n"
            "- 'I completed the groceries task' → list_tasks() to find task, then mark_complete(task_id)\n"
            "- 'done with X' → list_tasks() to find task, then mark_complete(task_id)\n\n"

            "**Task Update Intent Recognition:**\n"
            "When users want to modify a task, use update_task tool. Examples:\n"
            "- 'change X to Y' → list_tasks() to find task, then update_task(task_id, title='Y')\n"
            "- 'update task X' → list_tasks() to find task, then update_task(task_id, ...)\n"
            "- 'rename X to Y' → list_tasks() to find task, then update_task(task_id, title='Y')\n"
            "- 'add details to X' → list_tasks() to find task, then update_task(task_id, description='...')\n\n"

            "**Task Deletion Intent Recognition:**\n"
            "When users want to remove a task, use delete_task tool. Examples:\n"
            "- 'delete X' → list_tasks() to find task, then delete_task(task_id)\n"
            "- 'remove the task' → list_tasks() to find task, then delete_task(task_id)\n"
            "- 'cancel X' → list_tasks() to find task, then delete_task(task_id)\n"
            "- 'get rid of X' → list_tasks() to find task, then delete_task(task_id)\n\n"

            "**Multi-Step Operations:**\n"
            "For operations that reference tasks by title or description (not ID):\n"
            "1. First call list_tasks() to get all tasks\n"
            "2. Identify the matching task from the list\n"
            "3. Use the task's ID for the operation (mark_complete, update_task, delete_task)\n"
            "4. If multiple tasks match, ask the user to clarify which one\n"
            "5. If no tasks match, inform the user the task wasn't found\n\n"

            "**Context Awareness:**\n"
            "- Remember previous messages in the conversation\n"
            "- When users say 'the first task', 'the second one', 'that task', refer to recently listed tasks\n"
            "- Maintain context across multiple turns\n"
            "- If context is unclear, ask clarifying questions\n\n"

            "**Response Guidelines:**\n"
            "- Always confirm actions taken (e.g., 'I've added X to your tasks')\n"
            "- Format task lists in a readable way (use bullet points or numbered lists)\n"
            "- Show completed vs incomplete tasks clearly\n"
            "- Be concise, friendly, and conversational\n"
            "- If no tasks exist, provide an encouraging message\n"
            "- If a request is ambiguous, ask clarifying questions\n"
            "- When multiple tasks match a reference, list them and ask which one\n"
            "- Provide helpful error messages when operations fail"
        )

        messages.append({
            "role": "system",
            "content": system_prompt
        })

        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": message
        })

        # Get user-scoped tools
        tools = self.create_user_scoped_tools()

        # Track tool calls for response metadata
        executed_tool_calls = []

        # Call OpenAI API with retry logic
        max_retries = 3
        retry_delay = 1  # seconds

        try:
            if tools:
                # First API call with tools (with retry)
                for attempt in range(max_retries):
                    try:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            tools=tools,
                            temperature=0.3,
                            max_tokens=500
                        )
                        break  # Success, exit retry loop
                    except Exception as api_error:
                        if attempt < max_retries - 1:
                            # Retry on transient errors
                            error_str = str(api_error).lower()
                            if any(keyword in error_str for keyword in ['timeout', 'connection', 'rate_limit', '429', '503', '502']):
                                print(f"OpenAI API error (attempt {attempt + 1}/{max_retries}): {api_error}. Retrying in {retry_delay}s...")
                                time.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                                continue
                        # Non-retryable error or max retries reached
                        raise

                assistant_message = response.choices[0].message

                # Check if model wants to call tools
                if assistant_message.tool_calls:
                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name

                        # Handle None or empty arguments from OpenRouter
                        tool_args_str = tool_call.function.arguments
                        if tool_args_str is None or tool_args_str == "":
                            tool_args = {}
                        else:
                            tool_args = json.loads(tool_args_str)

                        # Execute tool and track timing
                        start_time = time.time()
                        tool_result = await self.execute_tool(tool_name, tool_args)
                        duration_ms = int((time.time() - start_time) * 1000)

                        # Store tool call metadata
                        executed_tool_calls.append({
                            "tool": tool_name,
                            "parameters": tool_args,
                            "result": tool_result,
                            "duration_ms": duration_ms
                        })

                        # Add tool call and result to messages for next API call
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [{
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_call.function.arguments
                                }
                            }]
                        })

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result)
                        })

                    # Second API call to get natural language response
                    final_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=500
                    )

                    final_content = final_response.choices[0].message.content or ""

                    return {
                        "content": final_content,
                        "tool_calls": executed_tool_calls if executed_tool_calls else None,
                        "model": self.model,
                        "finish_reason": final_response.choices[0].finish_reason
                    }

                else:
                    # No tool calls, return direct response
                    content = assistant_message.content or ""

                    return {
                        "content": content,
                        "tool_calls": None,
                        "model": self.model,
                        "finish_reason": response.choices[0].finish_reason
                    }

            else:
                # No tools available, call without tools
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=500
                )

                content = response.choices[0].message.content or ""

                return {
                    "content": content,
                    "tool_calls": None,
                    "model": self.model,
                    "finish_reason": response.choices[0].finish_reason
                }

        except Exception as e:
            # Log error and re-raise
            print(f"Error processing message with OpenAI: {str(e)}")
            raise

    def format_conversation_history(
        self,
        messages: List[Any]
    ) -> List[Dict[str, str]]:
        """
        Format database messages into OpenAI conversation history format.

        Args:
            messages: List of Message model instances from database

        Returns:
            List of message dicts in OpenAI format
        """
        history = []
        for msg in messages:
            history.append({
                "role": msg.role.value if hasattr(msg.role, 'value') else msg.role,
                "content": msg.content
            })
        return history

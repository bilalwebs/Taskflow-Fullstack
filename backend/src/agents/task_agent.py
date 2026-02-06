"""
TaskAgent class for handling AI-powered task management conversations.

This module implements the core agent that processes user messages and
executes task operations through MCP tools.
"""
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from ..config import settings
from .agent_config import TASK_AGENT_SYSTEM_PROMPT, AGENT_CONFIG


class TaskAgent:
    """
    AI agent for task management conversations.

    This agent uses OpenAI's API (or OpenRouter) with function calling to process natural
    language requests and execute task operations through MCP tools.
    """

    def __init__(self):
        """
        Initialize the TaskAgent with OpenAI client.

        The agent is configured with:
        - OpenAI API key from settings (can be OpenRouter key)
        - System prompt defining agent behavior
        - Model configuration (temperature, max_tokens, etc.)
        - Empty tools list (tools registered later via register_tools)
        """
        # Configure client for OpenRouter if base URL is provided
        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if hasattr(settings, 'OPENAI_BASE_URL') and settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL

        self.client = AsyncOpenAI(**client_kwargs)
        self.model = settings.OPENAI_MODEL
        self.system_prompt = TASK_AGENT_SYSTEM_PROMPT
        self.temperature = AGENT_CONFIG["temperature"]
        self.max_tokens = AGENT_CONFIG["max_tokens"]
        self.tools: List[Dict[str, Any]] = []

    def register_tools(self, tools: List[Dict[str, Any]]) -> None:
        """
        Register MCP tools with the agent.

        Tools should be in OpenAI function calling format:
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "Tool description",
                "parameters": {...}
            }
        }

        Args:
            tools: List of tool definitions in OpenAI format
        """
        self.tools = tools

    async def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        tool_executor: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        This method:
        1. Constructs the full message history with system prompt
        2. Calls OpenAI API with tool definitions
        3. Handles tool calls if the agent decides to use them
        4. Returns the final response with any tool call metadata

        Args:
            message: The user's message to process
            conversation_history: Previous messages in the conversation
                Format: [{"role": "user"|"assistant", "content": "..."}]
            tool_executor: Optional callable to execute tool calls
                Should accept (tool_name, arguments) and return result

        Returns:
            Dict containing:
                - content: The assistant's response text
                - tool_calls: List of tool calls made (if any)
                - finish_reason: Why the model stopped generating

        Raises:
            Exception: If OpenAI API call fails
        """
        # Build messages array with system prompt
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": message})

        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools if self.tools else None,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        # Extract response
        assistant_message = response.choices[0].message

        # Handle tool calls if present
        tool_calls_data = []
        if assistant_message.tool_calls and tool_executor:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments

                # Execute tool
                try:
                    import json
                    args_dict = json.loads(tool_args)
                    result = await tool_executor(tool_name, args_dict)

                    tool_calls_data.append({
                        "id": tool_call.id,
                        "name": tool_name,
                        "arguments": args_dict,
                        "result": result
                    })
                except Exception as e:
                    tool_calls_data.append({
                        "id": tool_call.id,
                        "name": tool_name,
                        "arguments": tool_args,
                        "error": str(e)
                    })

            # If tools were called, make another API call with tool results
            # to get the final response
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"])
                        }
                    }
                    for tc in tool_calls_data
                ]
            })

            # Add tool results
            for tc in tool_calls_data:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(tc.get("result", {"error": tc.get("error")}))
                })

            # Get final response
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            final_message = final_response.choices[0].message

            return {
                "content": final_message.content,
                "tool_calls": tool_calls_data,
                "finish_reason": final_response.choices[0].finish_reason
            }

        # No tool calls - return direct response
        return {
            "content": assistant_message.content,
            "tool_calls": [],
            "finish_reason": response.choices[0].finish_reason
        }

    async def health_check(self) -> bool:
        """
        Verify the agent can communicate with OpenAI API.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            await self.client.models.retrieve(self.model)
            return True
        except Exception:
            return False

"""
Cohere Agent Service Module

This module provides the CohereAgentService class that uses Cohere API for chat.
"""

from typing import List, Dict, Any
import json
import time
import cohere
from ..config import settings
from ..tools.mcp_server import mcp_server
from ..tools import (
    get_list_tasks_definition,
    get_create_task_definition,
    get_mark_complete_definition,
    get_update_task_definition,
    get_delete_task_definition,
    get_get_task_definition
)
from ..database import engine


class CohereAgentService:
    """
    Cohere Agent Service for processing conversational task management requests.
    """

    def __init__(self, user_id: int):
        """
        Initialize CohereAgentService for a specific user.

        Args:
            user_id: Authenticated user ID for data scoping
        """
        self.user_id = user_id
        self.client = cohere.Client(api_key=settings.COHERE_API_KEY)
        self.model = settings.COHERE_MODEL
        self.mcp_context = mcp_server.create_context(user_id=user_id)

    def create_user_scoped_tools(self) -> List[Dict[str, Any]]:
        """
        Create user-scoped tool definitions for Cohere function calling.

        Converts OpenAI-style tool definitions to Cohere format.
        """
        openai_tools = [
            get_list_tasks_definition(),
            get_create_task_definition(),
            get_mark_complete_definition(),
            get_update_task_definition(),
            get_delete_task_definition(),
            get_get_task_definition()
        ]

        # Convert OpenAI format to Cohere format
        cohere_tools = []
        for tool in openai_tools:
            func = tool["function"]
            cohere_tool = {
                "name": func["name"],
                "description": func["description"],
                "parameter_definitions": {}
            }

            # Convert parameters
            if "parameters" in func and "properties" in func["parameters"]:
                for param_name, param_info in func["parameters"]["properties"].items():
                    cohere_tool["parameter_definitions"][param_name] = {
                        "description": param_info.get("description", ""),
                        "type": param_info.get("type", "string"),
                        "required": param_name in func["parameters"].get("required", [])
                    }

            cohere_tools.append(cohere_tool)

        return cohere_tools

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given arguments.
        """
        try:
            # Get the tool handler from MCP server
            tool_handler = mcp_server.get_tool(tool_name)

            if not tool_handler:
                return {"error": f"Tool '{tool_name}' not found"}

            # Execute with user context
            result = await tool_handler(self.mcp_context, **arguments)

            return result

        except Exception as e:
            return {"error": str(e)}

    async def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process a user message using Cohere API.
        """
        try:
            # Get tools
            tools = self.create_user_scoped_tools()

            # Convert conversation history to Cohere format
            chat_history = []
            for msg in conversation_history:
                if msg["role"] == "user":
                    chat_history.append({
                        "role": "USER",
                        "message": msg["content"]
                    })
                elif msg["role"] == "assistant":
                    chat_history.append({
                        "role": "CHATBOT",
                        "message": msg["content"]
                    })

            # System message (preamble in Cohere)
            preamble = """You are a helpful task management assistant for KIro Todo application.

Your role is to help users manage their tasks through natural language conversation. You have access to tools for:
- Listing tasks
- Creating new tasks
- Updating tasks
- Deleting tasks
- Marking tasks as complete/incomplete

Be friendly, concise, and helpful. Always confirm actions clearly."""

            # Call Cohere API with tools
            response = self.client.chat(
                model=self.model,
                message=message,
                chat_history=chat_history,
                tools=tools,
                preamble=preamble,
                temperature=0.7
            )

            executed_tool_calls = []

            # Check if model wants to use tools
            if response.tool_calls:
                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call.name
                    tool_args = tool_call.parameters

                    # Execute tool
                    start_time = time.time()
                    tool_result = await self.execute_tool(tool_name, tool_args)
                    duration_ms = int((time.time() - start_time) * 1000)

                    executed_tool_calls.append({
                        "tool": tool_name,
                        "parameters": tool_args,
                        "result": tool_result,
                        "duration_ms": duration_ms
                    })

                # Make second call with tool results
                tool_results = [
                    {
                        "call": {
                            "name": tc["tool"],
                            "parameters": tc["parameters"]
                        },
                        "outputs": [tc["result"]]
                    }
                    for tc in executed_tool_calls
                ]

                final_response = self.client.chat(
                    model=self.model,
                    message=message,
                    chat_history=chat_history,
                    tools=tools,
                    tool_results=tool_results,
                    preamble=preamble,
                    temperature=0.7
                )

                return {
                    "content": final_response.text,
                    "tool_calls": executed_tool_calls if executed_tool_calls else None,
                    "model": self.model,
                    "finish_reason": "complete"
                }
            else:
                # No tool calls
                return {
                    "content": response.text,
                    "tool_calls": None,
                    "model": self.model,
                    "finish_reason": "complete"
                }

        except Exception as e:
            print(f"Error processing message with Cohere: {str(e)}")
            raise

    def format_conversation_history(
        self,
        messages: List[Any]
    ) -> List[Dict[str, str]]:
        """
        Format database messages for Cohere API.
        """
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.role.value,
                "content": msg.content
            })
        return formatted

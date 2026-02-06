"""
Agents package for AI-powered task management.

This package contains the TaskAgent class and configuration for
handling natural language task management conversations.
"""
from .task_agent import TaskAgent
from .agent_config import TASK_AGENT_SYSTEM_PROMPT, AGENT_CONFIG, TOOL_CONFIG

__all__ = ["TaskAgent", "TASK_AGENT_SYSTEM_PROMPT", "AGENT_CONFIG", "TOOL_CONFIG"]

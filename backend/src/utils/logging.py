"""
Structured Logging Utility

Provides structured logging for agent operations, tool invocations, and errors.
Enables better debugging and monitoring in production.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import sys


class StructuredLogger:
    """
    Structured logger for application events.

    Logs events in JSON format for easy parsing and analysis.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize structured logger.

        Args:
            name: Logger name (typically module name)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create console handler with JSON formatter
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)
            self.logger.addHandler(handler)

    def _log(
        self,
        level: int,
        event: str,
        **kwargs: Any
    ):
        """
        Log structured event.

        Args:
            level: Logging level
            event: Event name/description
            **kwargs: Additional context fields
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **kwargs
        }

        self.logger.log(level, json.dumps(log_entry))

    def info(self, event: str, **kwargs: Any):
        """Log info level event."""
        self._log(logging.INFO, event, **kwargs)

    def warning(self, event: str, **kwargs: Any):
        """Log warning level event."""
        self._log(logging.WARNING, event, **kwargs)

    def error(self, event: str, error: Optional[Exception] = None, **kwargs: Any):
        """Log error level event."""
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
        self._log(logging.ERROR, event, **kwargs)

    def debug(self, event: str, **kwargs: Any):
        """Log debug level event."""
        self._log(logging.DEBUG, event, **kwargs)

    def agent_operation(
        self,
        user_id: int,
        conversation_id: int,
        message: str,
        response: str,
        tool_calls: Optional[list] = None,
        duration_ms: Optional[int] = None
    ):
        """
        Log agent operation with full context.

        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            message: User message
            response: Agent response
            tool_calls: List of tool invocations
            duration_ms: Operation duration in milliseconds
        """
        self.info(
            "agent_operation",
            user_id=user_id,
            conversation_id=conversation_id,
            message_length=len(message),
            response_length=len(response),
            tool_calls_count=len(tool_calls) if tool_calls else 0,
            tools_used=[tc.get("tool") for tc in tool_calls] if tool_calls else [],
            duration_ms=duration_ms
        )

    def tool_invocation(
        self,
        user_id: int,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        duration_ms: int
    ):
        """
        Log MCP tool invocation.

        Args:
            user_id: User identifier
            tool_name: Name of the tool
            parameters: Tool parameters
            result: Tool result
            duration_ms: Execution duration in milliseconds
        """
        self.info(
            "tool_invocation",
            user_id=user_id,
            tool=tool_name,
            parameters=parameters,
            status=result.get("status", "unknown"),
            duration_ms=duration_ms
        )

    def api_request(
        self,
        method: str,
        path: str,
        user_id: Optional[int] = None,
        status_code: Optional[int] = None,
        duration_ms: Optional[int] = None
    ):
        """
        Log API request.

        Args:
            method: HTTP method
            path: Request path
            user_id: User identifier (if authenticated)
            status_code: Response status code
            duration_ms: Request duration in milliseconds
        """
        self.info(
            "api_request",
            method=method,
            path=path,
            user_id=user_id,
            status_code=status_code,
            duration_ms=duration_ms
        )

    def rate_limit_exceeded(
        self,
        user_id: int,
        endpoint: str,
        limit: int,
        reset_time: int
    ):
        """
        Log rate limit exceeded event.

        Args:
            user_id: User identifier
            endpoint: API endpoint
            limit: Rate limit threshold
            reset_time: When limit resets (unix timestamp)
        """
        self.warning(
            "rate_limit_exceeded",
            user_id=user_id,
            endpoint=endpoint,
            limit=limit,
            reset_time=reset_time
        )


# Global logger instances
agent_logger = StructuredLogger("agent", level=logging.INFO)
api_logger = StructuredLogger("api", level=logging.INFO)
tool_logger = StructuredLogger("tools", level=logging.INFO)

"""
Rate Limiting Middleware

Implements token bucket algorithm for rate limiting API requests.
Limits: 60 requests per minute per user.
"""

from fastapi import Request, HTTPException, status
from typing import Dict
import time
from collections import defaultdict
import threading


class TokenBucket:
    """
    Token bucket implementation for rate limiting.

    Each user gets a bucket with tokens that refill over time.
    Each request consumes one token.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.

        Args:
            capacity: Maximum number of tokens (burst size)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        with self.lock:
            # Refill tokens based on time elapsed
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + (elapsed * self.refill_rate)
            )
            self.last_refill = now

            # Try to consume tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_remaining(self) -> int:
        """Get number of tokens remaining."""
        with self.lock:
            return int(self.tokens)

    def get_reset_time(self) -> int:
        """Get timestamp when bucket will be full."""
        with self.lock:
            if self.tokens >= self.capacity:
                return int(time.time())

            tokens_needed = self.capacity - self.tokens
            seconds_to_full = tokens_needed / self.refill_rate
            return int(time.time() + seconds_to_full)


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.

    Tracks rate limits per user_id.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: int = 10
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute per user
            burst_size: Maximum burst size (extra tokens beyond rate)
        """
        self.requests_per_minute = requests_per_minute
        self.capacity = requests_per_minute + burst_size
        self.refill_rate = requests_per_minute / 60.0  # Tokens per second
        self.buckets: Dict[int, TokenBucket] = defaultdict(
            lambda: TokenBucket(self.capacity, self.refill_rate)
        )
        self.lock = threading.Lock()

    def check_rate_limit(self, user_id: int) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit.

        Args:
            user_id: User identifier

        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        with self.lock:
            bucket = self.buckets[user_id]

        allowed = bucket.consume(1)
        remaining = bucket.get_remaining()
        reset_time = bucket.get_reset_time()

        return allowed, remaining, reset_time


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60, burst_size=10)


async def rate_limit_middleware(request: Request, user_id: int):
    """
    Rate limiting middleware for API endpoints.

    Args:
        request: FastAPI request object
        user_id: Authenticated user ID

    Raises:
        HTTPException 429: Rate limit exceeded
    """
    allowed, remaining, reset_time = rate_limiter.check_rate_limit(user_id)

    # Add rate limit headers to response
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(rate_limiter.requests_per_minute),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_time)
    }

    if not allowed:
        retry_after = reset_time - int(time.time())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(rate_limiter.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(max(1, retry_after))
            }
        )

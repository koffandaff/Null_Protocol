import time
from fastapi import HTTPException, status, Request
from collections import defaultdict
from typing import Dict, Tuple

class SimpleRateLimiter:
    """
    A simple in-memory rate limiter to prevent brute force and spam.
    Tracks requests by IP and endpoint.
    """
    def __init__(self):
        # Dictionary to store (ip, endpoint) -> [timestamps]
        self.requests: Dict[Tuple[str, str], list] = defaultdict(list)

    def is_rate_limited(self, ip: str, endpoint: str, limit: int, window: int) -> bool:
        """
        Check if the request should be limited.
        
        Args:
            ip: Client IP address
            endpoint: The API endpoint being accessed
            limit: Max requests allowed in the window
            window: Time window in seconds
        """
        now = time.time()
        key = (ip, endpoint)
        
        # Clean up old timestamps
        self.requests[key] = [t for t in self.requests[key] if now - t < window]
        
        if len(self.requests[key]) >= limit:
            return True
        
        self.requests[key].append(now)
        return False

    def limit(self, limit: int, window: int):
        """Decorator style check (manual call in router)"""
        async def dependency(request: Request):
            ip = request.client.host
            endpoint = request.url.path
            
            if self.is_rate_limited(ip, endpoint, limit, window):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Too many requests. Please try again after {window} seconds."
                    }
                )
        return dependency

# Global instance
limiter = SimpleRateLimiter()

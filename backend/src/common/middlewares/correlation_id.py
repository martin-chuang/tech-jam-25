"""Correlation ID middleware"""

import uuid
from typing import Optional
from flask import Flask, request, g


CORRELATION_ID_HEADER = 'X-Correlation-ID'


class CorrelationIdMiddleware:
    """Middleware to handle correlation ID for request tracing."""
    
    def __init__(self, app: Optional[Flask] = None):
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize the correlation ID middleware with Flask app."""
        app.before_request(self._before_request)
    
    def _before_request(self):
        """Generate or extract correlation ID before each request."""
        # Try to get correlation ID from request header
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)
        
        # If not provided, generate a new one
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Store in request context for easy access
        request.correlation_id = correlation_id
        
        # Also store in g for template access if needed
        g.correlation_id = correlation_id
    
    @staticmethod
    def get_correlation_id() -> Optional[str]:
        """Get the current request's correlation ID."""
        return getattr(request, 'correlation_id', None)


def get_correlation_id() -> Optional[str]:
    """Utility function to get correlation ID from anywhere in the application."""
    return CorrelationIdMiddleware.get_correlation_id()

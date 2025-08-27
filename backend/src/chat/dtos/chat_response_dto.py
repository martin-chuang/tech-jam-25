"""Chat response DTOs for API responses."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatResponseDto:
    """DTO for chat response containing only the deanonymised response."""
    
    response: str
    """The deanonymised AI response."""


@dataclass
class ErrorResponseDto:
    """DTO for error responses."""
    
    statusCode: int
    timestamp: str
    correlationId: str
    error: str
    message: str

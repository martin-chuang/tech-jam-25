"""Chat response DTOs."""

from dataclasses import dataclass


@dataclass
class ChatResponseDto:
    """Simple chat response containing only the deanonymised response."""
    
    response: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'response': self.response
        }
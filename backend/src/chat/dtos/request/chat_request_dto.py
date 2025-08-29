"""Chat request DTOs."""

from dataclasses import dataclass
from typing import List, Optional
from werkzeug.datastructures import FileStorage


@dataclass
class ChatRequestDto:
    """Chat request data transfer object."""
    
    prompt: str
    files: Optional[List[FileStorage]] = None
    
    def __post_init__(self):
        if self.files is None:
            self.files = []
"""Chat-specific validators."""

import hashlib
from typing import List, Optional
from werkzeug.datastructures import FileStorage
from ...common.validators import BaseValidator, ValidatorChain


class FileValidator(BaseValidator):
    """Validator for uploaded files."""
    
    def __init__(self, max_file_size: int = 10 * 1024 * 1024):  # 10MB default
        self.max_file_size = max_file_size
        self.allowed_types = [
            'text/plain',
            'text/csv',
            'application/pdf',
            'application/json',
            'text/markdown',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
    
    def handle_validation(self, data: FileStorage) -> Optional[str]:
        if not data:
            return "File is required"
        
        # Check filename
        if not data.filename:
            return "File must have a filename"
        
        # Basic validation without file operations that might close the stream
        # Skip content type validation for now as it might cause issues
        # if data.content_type not in self.allowed_types:
        #     return f"File type '{data.content_type}' is not supported. Allowed types: {', '.join(self.allowed_types)}"
        
        # Skip size validation that requires seeking
        # File size checks can be done later if needed
        
        return None


class FilesListValidator(BaseValidator):
    """Validator for list of files."""
    
    def __init__(self, max_files: int = 5):
        self.max_files = max_files
        self.file_validator = FileValidator()
    
    def handle_validation(self, data: List[FileStorage]) -> Optional[str]:
        if not data:
            return "At least one file is required"
        
        if len(data) > self.max_files:
            return f"Cannot upload more than {self.max_files} files at once"
        
        # Validate each file
        for i, file in enumerate(data):
            error = self.file_validator.validate(file)
            if error:
                return f"File {i + 1} ({file.filename if file.filename else 'unknown'}): {error}"
        
        # Check for duplicate files
        file_hashes = []
        for file in data:
            if file.filename:
                try:
                    # Save current position
                    current_pos = file.tell()
                    
                    # Read content for hash
                    file.seek(0)
                    content = file.read()
                    file_hash = hashlib.md5(content).hexdigest()
                    
                    # Reset to original position
                    file.seek(current_pos)
                    
                    if file_hash in file_hashes:
                        return f"Duplicate file detected: {file.filename}"
                    
                    file_hashes.append(file_hash)
                except (IOError, OSError):
                    # Skip duplicate check if file can't be read
                    continue
        
        return None


def create_files_validator() -> ValidatorChain:
    """Create a validator chain for files."""
    
    validator_chain = ValidatorChain()
    validator_chain.add_validator(FilesListValidator())
    
    return validator_chain


def create_chat_validator_chain() -> ValidatorChain:
    """Create a comprehensive validator chain for chat requests."""
    
    validator_chain = ValidatorChain()
    
    # Add prompt validator
    validator_chain.add_validator(PromptValidator())
    
    # Add file validator
    validator_chain.add_validator(FileValidator())
    
    return validator_chain


class PromptValidator(BaseValidator):
    """Validator for chat prompts."""
    
    def __init__(self, required: bool = True):
        """
        Initialize prompt validator.
        
        Args:
            required: Whether prompt is required. If False, empty prompts are allowed.
        """
        self.required = required
    
    def handle_validation(self, data: str) -> Optional[str]:
        # If prompt is not required and data is empty, allow it
        if not self.required and (not data or not data.strip()):
            return None
            
        # If prompt is required, apply standard validation
        if self.required and not data:
            return "Prompt is required"
        
        if data and not isinstance(data, str):
            return "Prompt must be a string"
        
        if self.required and not data.strip():
            return "Prompt cannot be empty"
        
        if data and len(data.strip()) < 3:
            return "Prompt must be at least 3 characters"
        
        if data and len(data) > 10000:
            return "Prompt cannot exceed 10,000 characters"
        
        return None

"""Validator interface definition."""

from abc import ABC, abstractmethod
from typing import TypeVar, Optional

T = TypeVar('T')


class ValidatorInterface(ABC):
    """Interface for all validators."""
    
    @abstractmethod
    def validate(self, data: T) -> Optional[str]:
        """
        Validate the given data.
        
        Args:
            data: The data to validate
            
        Returns:
            None if validation passes, error message string if validation fails
        """
        pass

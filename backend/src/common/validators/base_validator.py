"""Base validator implementation."""

from abc import abstractmethod
from typing import Optional, TypeVar

from .validator_interface import ValidatorInterface

T = TypeVar("T")


class BaseValidator(ValidatorInterface):
    """Base validator class that implements the validator interface."""

    @abstractmethod
    def handle_validation(self, data: T) -> Optional[str]:
        """
        Handle the actual validation logic.
        To be implemented by concrete validators.

        Args:
            data: The data to validate

        Returns:
            None if validation passes, error message string if validation fails
        """
        pass

    def validate(self, data: T) -> Optional[str]:
        """
        Validate the given data.

        Args:
            data: The data to validate

        Returns:
            None if validation passes, error message string if validation fails
        """
        return self.handle_validation(data)

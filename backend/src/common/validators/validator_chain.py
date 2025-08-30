"""Validator chain implementation for combining multiple validators."""

from typing import List, Optional, TypeVar
from .validator_interface import ValidatorInterface

T = TypeVar("T")


class ValidatorChain(ValidatorInterface):
    """Chain multiple validators together."""

    def __init__(self, validators: List[ValidatorInterface] = None):
        """
        Initialize the validator chain.

        Args:
            validators: List of validators to chain together
        """
        self._validators: List[ValidatorInterface] = validators or []

    def add_validator(self, validator: ValidatorInterface) -> "ValidatorChain":
        """
        Add a validator to the chain.

        Args:
            validator: The validator to add

        Returns:
            Self for method chaining
        """
        self._validators.append(validator)
        return self

    def validate(self, data: T) -> Optional[str]:
        """
        Validate using all validators in the chain.
        Returns the first error encountered, or None if all validations pass.

        Args:
            data: The data to validate

        Returns:
            None if all validations pass, first error message if any validation fails
        """
        for validator in self._validators:
            error = validator.validate(data)
            if error:
                return error
        return None

    def validate_all(self, data: T) -> List[str]:
        """
        Validate using all validators and return all errors.

        Args:
            data: The data to validate

        Returns:
            List of all error messages (empty if all validations pass)
        """
        errors = []
        for validator in self._validators:
            error = validator.validate(data)
            if error:
                errors.append(error)
        return errors

    def clear(self) -> None:
        """Clear all validators from the chain."""
        self._validators.clear()

    def count(self) -> int:
        """Get the number of validators in the chain."""
        return len(self._validators)

"""State machine interface and error definitions."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import TypeVar, Generic, Callable, Optional, Any


class StateMachineErrorCode(Enum):
    """State machine error codes."""

    TRANSITION_NOT_ALLOWED = "TRANSITION_NOT_ALLOWED"
    TRANSITION_NOT_FOUND = "TRANSITION_NOT_FOUND"
    HANDLER_ERROR = "HANDLER_ERROR"
    STATE_NOT_FOUND = "STATE_NOT_FOUND"
    EVENT_NOT_RECOGNIZED = "EVENT_NOT_RECOGNIZED"
    TECHNICAL_ERROR = "TECHNICAL_ERROR"


class StateMachineError(Exception):
    """Custom exception for state machine errors."""

    def __init__(self, message: str, code: StateMachineErrorCode):
        super().__init__(message)
        self.code = code
        self.name = "StateMachineError"


# Type variables for generic state machine
S = TypeVar("S", bound=str)  # State type
E = TypeVar("E", bound=str)  # Event type
C = TypeVar("C")  # Context type

# Type alias for event handler
StateMachineEventHandler = Callable[[S, S, E, Optional[C]], None]


class Transition(Generic[S, E, C]):
    """Represents a state transition."""

    def __init__(
        self,
        from_state: S,
        to_state: S,
        state_machine_event: E,
        handler: Optional[StateMachineEventHandler] = None,
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.state_machine_event = state_machine_event
        self.handler = handler


class IStateMachine(ABC, Generic[S, E, C]):
    """Interface for state machine implementation."""

    @abstractmethod
    def add_transition(self, transition: Transition[S, E, C]) -> None:
        """Add a transition to the state machine."""
        pass

    @abstractmethod
    def trigger(self, from_state: S, event: E, context: Optional[C] = None) -> S:
        """Trigger a state transition."""
        pass

    @abstractmethod
    def can_trigger(self, from_state: S, event: E) -> bool:
        """Check if a transition is possible."""
        pass

    @abstractmethod
    def get_valid_events(self, from_state: S) -> list[E]:
        """Get valid events for a given state."""
        pass

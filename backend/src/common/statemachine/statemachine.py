"""State machine implementation."""

from typing import Dict, List, Optional
from .istatemachine import (
    IStateMachine,
    StateMachineError,
    StateMachineErrorCode,
    Transition,
    S,
    E,
    C,
)


class StateMachine(IStateMachine[S, E, C]):
    """Generic state machine implementation."""

    def __init__(self):
        self._transitions: Dict[str, Transition[S, E, C]] = {}

    def _create_transition_key(self, from_state: S, event: E) -> str:
        """Create a unique key for a transition."""
        return f"{from_state}:{event}"

    def _get_transition(self, from_state: S, event: E) -> Transition[S, E, C]:
        """Get a transition for the given state and event."""
        if from_state is None:
            raise StateMachineError(
                "Invalid fromState: state cannot be None",
                StateMachineErrorCode.TECHNICAL_ERROR,
            )

        if event is None:
            raise StateMachineError(
                "Invalid event: event cannot be None",
                StateMachineErrorCode.TECHNICAL_ERROR,
            )

        try:
            key = self._create_transition_key(from_state, event)
            transition = self._transitions.get(key)

            if not transition:
                raise StateMachineError(
                    f"No transition found for state '{from_state}' and event '{event}'",
                    StateMachineErrorCode.TRANSITION_NOT_ALLOWED,
                )

            return transition

        except StateMachineError:
            raise
        except Exception as error:
            raise StateMachineError(
                f"Failed to get transition: {str(error)}",
                StateMachineErrorCode.TECHNICAL_ERROR,
            )

    def add_transition(self, transition: Transition[S, E, C]) -> None:
        """Add a transition to the state machine."""
        if not transition:
            raise StateMachineError(
                "Transition cannot be None", StateMachineErrorCode.TECHNICAL_ERROR
            )

        if not transition.from_state:
            raise StateMachineError(
                "Transition fromState cannot be None or empty",
                StateMachineErrorCode.TECHNICAL_ERROR,
            )

        if not transition.to_state:
            raise StateMachineError(
                "Transition toState cannot be None or empty",
                StateMachineErrorCode.TECHNICAL_ERROR,
            )

        if not transition.state_machine_event:
            raise StateMachineError(
                "Transition event cannot be None or empty",
                StateMachineErrorCode.TECHNICAL_ERROR,
            )

        key = self._create_transition_key(
            transition.from_state, transition.state_machine_event
        )

        # Check if transition already exists
        if key in self._transitions:
            raise StateMachineError(
                f"Transition already exists for state '{transition.from_state}' "
                f"and event '{transition.state_machine_event}'",
                StateMachineErrorCode.TECHNICAL_ERROR,
            )

        self._transitions[key] = transition

    def trigger(self, from_state: S, event: E, context: Optional[C] = None) -> S:
        """Trigger a state transition."""
        try:
            transition = self._get_transition(from_state, event)

            # Execute handler if present
            if transition.handler:
                try:
                    transition.handler(
                        transition.from_state,
                        transition.to_state,
                        transition.state_machine_event,
                        context,
                    )
                except Exception as error:
                    raise StateMachineError(
                        f"Handler execution failed: {str(error)}",
                        StateMachineErrorCode.HANDLER_ERROR,
                    )

            return transition.to_state

        except StateMachineError:
            raise
        except Exception as error:
            raise StateMachineError(
                f"Failed to trigger transition: {str(error)}",
                StateMachineErrorCode.TECHNICAL_ERROR,
            )

    def can_trigger(self, from_state: S, event: E) -> bool:
        """Check if a transition is possible."""
        try:
            self._get_transition(from_state, event)
            return True
        except StateMachineError as error:
            if error.code == StateMachineErrorCode.TRANSITION_NOT_ALLOWED:
                return False
            raise

    def get_valid_events(self, from_state: S) -> List[E]:
        """Get valid events for a given state."""
        if not from_state:
            raise StateMachineError(
                "State cannot be None or empty", StateMachineErrorCode.TECHNICAL_ERROR
            )

        valid_events = []

        for key, transition in self._transitions.items():
            if transition.from_state == from_state:
                valid_events.append(transition.state_machine_event)

        return valid_events

    def get_transitions_count(self) -> int:
        """Get the total number of transitions."""
        return len(self._transitions)

    def clear_transitions(self) -> None:
        """Clear all transitions."""
        self._transitions.clear()

    def get_all_transitions(self) -> List[Transition[S, E, C]]:
        """Get all transitions."""
        return list(self._transitions.values())

    def remove_transition(self, from_state: S, event: E) -> bool:
        """Remove a specific transition."""
        key = self._create_transition_key(from_state, event)
        if key in self._transitions:
            del self._transitions[key]
            return True
        return False

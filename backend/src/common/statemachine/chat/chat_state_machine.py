"""Chat state machine configuration and transitions."""

from typing import List, Dict, Any
from ..istatemachine import Transition
from .chat_state_machine_events import ChatStatusEvent
from .chat_state_machine_handlers import ChatStateHandlers


# Chat status enum values as strings
class ChatStatus:
    """Chat processing status constants."""
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    ANONYMISED = "ANONYMISED"
    PROCESSED = "PROCESSED"
    DEANONYMISED = "DEANONYMISED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


def get_chat_transitions() -> List[Transition[str, str, Dict[str, Any]]]:
    """Get all chat state machine transitions."""
    
    return [
        # From PENDING
        Transition(
            from_state=ChatStatus.PENDING,
            to_state=ChatStatus.VALIDATED,
            state_machine_event=ChatStatusEvent.VALIDATE_SUCCESS.value,
            handler=ChatStateHandlers.validation_success_handler
        ),
        Transition(
            from_state=ChatStatus.PENDING,
            to_state=ChatStatus.FAILURE,
            state_machine_event=ChatStatusEvent.VALIDATE_FAILURE.value,
            handler=ChatStateHandlers.validation_failure_handler
        ),
        
        # From VALIDATED
        Transition(
            from_state=ChatStatus.VALIDATED,
            to_state=ChatStatus.ANONYMISED,
            state_machine_event=ChatStatusEvent.ANONYMISE_SUCCESS.value,
            handler=ChatStateHandlers.anonymisation_success_handler
        ),
        Transition(
            from_state=ChatStatus.VALIDATED,
            to_state=ChatStatus.FAILURE,
            state_machine_event=ChatStatusEvent.ANONYMISE_FAILURE.value,
            handler=ChatStateHandlers.anonymisation_failure_handler
        ),
        
        # From ANONYMISED
        Transition(
            from_state=ChatStatus.ANONYMISED,
            to_state=ChatStatus.PROCESSED,
            state_machine_event=ChatStatusEvent.PROCESS_SUCCESS.value,
            handler=ChatStateHandlers.processing_success_handler
        ),
        Transition(
            from_state=ChatStatus.ANONYMISED,
            to_state=ChatStatus.FAILURE,
            state_machine_event=ChatStatusEvent.PROCESS_FAILURE.value,
            handler=ChatStateHandlers.processing_failure_handler
        ),
        
        # From PROCESSED
        Transition(
            from_state=ChatStatus.PROCESSED,
            to_state=ChatStatus.DEANONYMISED,
            state_machine_event=ChatStatusEvent.DEANONYMISE_SUCCESS.value,
            handler=ChatStateHandlers.deanonymisation_success_handler
        ),
        Transition(
            from_state=ChatStatus.PROCESSED,
            to_state=ChatStatus.FAILURE,
            state_machine_event=ChatStatusEvent.DEANONYMISE_FAILURE.value,
            handler=ChatStateHandlers.deanonymisation_failure_handler
        ),
        
        # From DEANONYMISED
        Transition(
            from_state=ChatStatus.DEANONYMISED,
            to_state=ChatStatus.SUCCESS,
            state_machine_event=ChatStatusEvent.COMPLETE_SUCCESS.value,
            handler=ChatStateHandlers.completion_success_handler
        ),
    ]

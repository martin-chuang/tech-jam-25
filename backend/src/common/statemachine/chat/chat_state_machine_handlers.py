"""Chat state machine handlers."""

import logging
from typing import Any, Dict, Optional

from ..istatemachine import StateMachineEventHandler
from .chat_state_machine_events import ChatStatusEvent

# Type alias for chat state handler
ChatStateHandler = StateMachineEventHandler[str, str, Dict[str, Any]]


class ChatStateHandlers:
    """Handlers for chat state machine transitions."""

    @staticmethod
    def log_transition_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log state transitions."""
        logger = logging.getLogger(__name__)
        session_id = context.get("session_id", "unknown") if context else "unknown"
        message_id = context.get("message_id", "unknown") if context else "unknown"

        logger.info(
            f"Chat state transition [{session_id}:{message_id}]: "
            f"{from_state} -> {to_state} via event {event}"
        )

    @staticmethod
    def validation_success_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle successful validation."""
        ChatStateHandlers.log_transition_handler(from_state, to_state, event, context)

        if context:
            context["validation_completed_at"] = context.get("timestamp")
            logger = logging.getLogger(__name__)
            session_id = context.get("session_id", "unknown")
            logger.debug(f"Files validated successfully for session {session_id}")

    @staticmethod
    def validation_failure_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle validation failure."""
        ChatStateHandlers.log_transition_handler(from_state, to_state, event, context)

        if context:
            context["validation_failed_at"] = context.get("timestamp")
            logger = logging.getLogger(__name__)
            session_id = context.get("session_id", "unknown")
            error = context.get("error_message", "Unknown error")
            logger.warning(f"File validation failed for session {session_id}: {error}")

    @staticmethod
    def anonymisation_success_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle successful anonymisation."""
        ChatStateHandlers.log_transition_handler(from_state, to_state, event, context)

        if context:
            context["anonymisation_completed_at"] = context.get("timestamp")
            logger = logging.getLogger(__name__)
            session_id = context.get("session_id", "unknown")
            logger.debug(f"Prompt anonymised successfully for session {session_id}")

    @staticmethod
    def anonymisation_failure_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle anonymisation failure."""
        ChatStateHandlers.log_transition_handler(from_state, to_state, event, context)

        if context:
            context["anonymisation_failed_at"] = context.get("timestamp")
            logger = logging.getLogger(__name__)
            session_id = context.get("session_id", "unknown")
            logger.error(f"Prompt anonymisation failed for session {session_id}")

    @staticmethod
    def processing_success_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle successful LLM processing."""
        ChatStateHandlers.log_transition_handler(from_state, to_state, event, context)

        if context:
            context["processing_completed_at"] = context.get("timestamp")
            logger = logging.getLogger(__name__)
            session_id = context.get("session_id", "unknown")
            logger.debug(
                f"LLM processing completed successfully for session {session_id}"
            )

    @staticmethod
    def processing_failure_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle LLM processing failure."""
        ChatStateHandlers.log_transition_handler(from_state, to_state, event, context)

        if context:
            context["processing_failed_at"] = context.get("timestamp")
            logger = logging.getLogger(__name__)
            session_id = context.get("session_id", "unknown")
            logger.error(f"LLM processing failed for session {session_id}")

    @staticmethod
    def deanonymisation_success_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle successful deanonymisation."""
        ChatStateHandlers.log_transition_handler(from_state, to_state, event, context)

        if context:
            context["deanonymisation_completed_at"] = context.get("timestamp")
            logger = logging.getLogger(__name__)
            session_id = context.get("session_id", "unknown")
            logger.debug(f"Response deanonymised successfully for session {session_id}")

    @staticmethod
    def deanonymisation_failure_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle deanonymisation failure."""
        ChatStateHandlers.log_transition_handler(from_state, to_state, event, context)

        if context:
            context["deanonymisation_failed_at"] = context.get("timestamp")
            logger = logging.getLogger(__name__)
            session_id = context.get("session_id", "unknown")
            logger.error(f"Response deanonymisation failed for session {session_id}")

    @staticmethod
    def completion_success_handler(
        from_state: str,
        to_state: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Handle successful completion."""
        ChatStateHandlers.log_transition_handler(from_state, to_state, event, context)

        if context:
            context["completed_at"] = context.get("timestamp")
            logger = logging.getLogger(__name__)
            session_id = context.get("session_id", "unknown")
            logger.info(
                f"Chat processing completed successfully for session {session_id}"
            )

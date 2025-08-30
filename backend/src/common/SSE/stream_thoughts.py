from flask import Blueprint, Response, stream_with_context
import time
import json
from typing import Generator
from datetime import datetime

chat_bp = Blueprint("chat", __name__)


def process_chat_with_thoughts(chat_service, request_dto) -> Generator[str, None, None]:
    """
    Process chat request with streaming thoughts for each state transition.

    Args:
        chat_service: The ChatService instance
        request_dto: The chat request DTO

    Yields:
        SSE formatted strings with state transition thoughts and final response
    """
    try:
        # Step 1: Validate request
        yield _create_thought_event("Validating request...")
        current_state = chat_service._transition_to_validated(request_dto)
        yield _create_thought_event("Request validated successfully")

        # Step 2: Convert files to markdown
        yield _create_thought_event("Converting files to markdown...")
        current_state, markdown_content = chat_service._transition_to_file_processed(
            request_dto
        )

        if markdown_content:
            yield _create_thought_event(
                f"Converted {len(request_dto.files) if request_dto.files else 0} files to markdown ({len(markdown_content)} characters)"
            )
        else:
            yield _create_thought_event("No files to process")

        # Step 3: Anonymise request
        yield _create_thought_event("Anonymising content...")
        current_state, anonymised_prompt, anonymised_content = chat_service._transition_to_anonymised(request_dto.prompt or "", request_dto.context or "", markdown_content)
        
        # Show anonymised content if different from original
        original_content = f"{request_dto.prompt or ''}\n\n{markdown_content}".strip()
        anonymised_combined = f"{anonymised_prompt}\n\n{anonymised_content}".strip()

        if anonymised_combined != original_content:
            yield _create_thought_event(
                "Content anonymised - sensitive data detected and protected"
            )
        else:
            yield _create_thought_event(
                "No sensitive data detected - content unchanged"
            )

        # Step 4: Process with privacy service
        yield _create_thought_event("Privacy service is processing...")
        current_state, llm_response = chat_service._transition_to_processed(
            anonymised_prompt, anonymised_content
        )
        yield _create_thought_event("Privacy service processing completed")

        # Step 5: Deanonymise response
        yield _create_thought_event("Deanonymising response...")
        current_state, final_response = chat_service._transition_to_deanonymised(
            llm_response
        )

        # Step 6: Success
        current_state = chat_service._transition_to_success()
        yield _create_thought_event("Processing completed successfully")
        
        # Final response - stream the response content
        yield _create_content_event(final_response)
        
        # Send done signal
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        chat_service._transition_to_failure()
        yield _create_error_event(f"Error: {str(e)}")
        yield "data: [DONE]\n\n"

def _create_thought_event(message: str) -> str:
    """Create SSE event for thought/state update."""
    event_data = {
        "type": "thought",
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    return f"data: {json.dumps(event_data)}\n\n"


def _create_final_response_event(response: str) -> str:
    """Create SSE event for final response."""
    event_data = {
        "type": "final_response",
        "response": response,
        "timestamp": datetime.now().isoformat(),
    }
    return f"data: {json.dumps(event_data)}\n\n"

def _create_content_event(content: str) -> str:
    """Create SSE event for content (expected by frontend)."""
    event_data = {
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    return f"data: {json.dumps(event_data)}\n\n"

def _create_error_event(error_message: str) -> str:
    """Create SSE event for errors."""
    event_data = {
        "type": "error",
        "message": error_message,
        "timestamp": datetime.now().isoformat(),
    }
    return f"data: {json.dumps(event_data)}\n\n"

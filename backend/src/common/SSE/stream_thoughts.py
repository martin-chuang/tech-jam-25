from flask import Blueprint, Response, stream_with_context
import time
import json
from typing import Generator
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

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
        # Step 2: Anonymise request  
        yield _create_thought_event("Anonymising prompt...")
        current_state, anonymised_request = chat_service._transition_to_anonymised(request_dto)
        
        # Show anonymised prompt if different from original
        if anonymised_request.prompt != request_dto.prompt:
            yield _create_thought_event(f"Anonymised prompt is now: {anonymised_request.prompt}")
        else:
            yield _create_thought_event("No sensitive data detected - prompt unchanged")
        
        # Step 3: Process with LLM
        yield _create_thought_event("LLM is thinking...")
        current_state, llm_response = chat_service._transition_to_processed(anonymised_request)
        yield _create_thought_event(f"Original LLM response: {llm_response}")
        
        # Step 4: Deanonymise response
        yield _create_thought_event("Deanonymising...")
        current_state, final_response = chat_service._transition_to_deanonymised(llm_response)
        
        # Step 5: Success
        current_state = chat_service._transition_to_success()
        
        # Final response - this is what the frontend will use as the actual answer
        yield _create_final_response_event(final_response)
        
    except Exception as e:
        chat_service._transition_to_failure()
        yield _create_error_event(f"Error: {str(e)}")

def _create_thought_event(message: str) -> str:
    """Create SSE event for thought/state update."""
    event_data = {
        "type": "thought",
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    return f"data: {json.dumps(event_data)}\n\n"

def _create_final_response_event(response: str) -> str:
    """Create SSE event for final response."""
    event_data = {
        "type": "final_response", 
        "response": response,
        "timestamp": datetime.now().isoformat()
    }
    return f"data: {json.dumps(event_data)}\n\n"

def _create_error_event(error_message: str) -> str:
    """Create SSE event for errors."""
    event_data = {
        "type": "error",
        "message": error_message,
        "timestamp": datetime.now().isoformat()
    }
    return f"data: {json.dumps(event_data)}\n\n"

@chat_bp.route('/stream-thoughts')
def stream_thoughts():
    """Legacy route - kept for compatibility but not integrated with actual chat service."""
    def simple_steps():
        steps = [
            "Validating files….",
            "Files validated!",
            "Anonymising prompt…",
            "LLM is thinking…",
            "Deanonymising…",
            "Success!"
        ]
        for step in steps:
            yield f"data: {step}\n\n"
            time.sleep(1)
    
    return Response(stream_with_context(simple_steps()), mimetype='text/event-stream')
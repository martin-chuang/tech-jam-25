"""Chat controller implementing proper MVC pattern."""

from flask import request, jsonify, g, Response, stream_with_context
from datetime import datetime
import logging

from .chat_service import ChatService
from .dtos.request.chat_request_dto import ChatRequestDto
from .dtos.chat_response_dto import ChatResponseDto


class ChatController:
    """Controller handling HTTP requests for chat endpoints."""

    def __init__(self, chat_service: ChatService):
        """Initialize controller with chat service dependency."""
        self.chat_service = chat_service
        self.logger = logging.getLogger(__name__)

    def process_chat(self):
        """
        Handle POST /api/v1/chat endpoint.
        Handles both JSON and FormData requests.
        Always returns SSE stream (as expected by frontend).
        
        Returns:
            SSE stream response
        """
        correlation_id = getattr(g, "correlation_id", "unknown")

        try:
            self.logger.info(f"[{correlation_id}] Received chat request")
            
            # Handle FormData (multipart) or JSON requests
            if request.content_type and 'multipart/form-data' in request.content_type:
                # FormData request from frontend
                prompt = request.form.get('message', '').strip()
                context = request.form.get('context', '').strip()
                sessionId = request.form.get('sessionId', '')
                files = []
                
                # Extract files from FormData
                for key in request.files:
                    if key.startswith('file-'):
                        files.append(request.files[key])
                
                self.logger.info(f"[{correlation_id}] FormData request - prompt: {prompt[:50]}..., files: {len(files)}")
                
            else:
                # JSON request (fallback)
                data = request.get_json() or {}
                prompt = data.get('prompt', '').strip()
                context = data.get('context', '').strip()
                sessionId = data.get('sessionId', '')
                files = data.get('files', [])
                
                self.logger.info(f"[{correlation_id}] JSON request - prompt: {prompt[:50]}...")
            
            request_dto = ChatRequestDto(prompt=prompt, context=context, files=files)
            
            # Always return streaming response (as frontend expects SSE)
            self.logger.info(f"[{correlation_id}] Processing as streaming request")
            stream_generator = self.chat_service.process_chat_streaming(request_dto)
            
            return Response(
                stream_with_context(stream_generator),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            )
            
        except Exception as e:
            self.logger.error(f"[{correlation_id}] Error processing chat: {str(e)}")
            return self._create_error_response(
                500, "INTERNAL_ERROR", "An unexpected error occurred", correlation_id
            )

    def _create_error_response(
        self, status_code: int, error_type: str, message: str, correlation_id: str
    ):
        """Create standardized error response."""
        return (
            jsonify(
                {
                    "statusCode": status_code,
                    "timestamp": datetime.now().isoformat() + "Z",
                    "path": request.path,
                    "correlationId": correlation_id,
                    "error": error_type,
                    "message": message,
                }
            ),
            status_code,
        )

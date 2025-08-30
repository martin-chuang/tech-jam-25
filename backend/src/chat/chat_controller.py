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
        Detects if client wants streaming via Accept header.

        Returns:
            JSON response for regular requests or SSE stream for streaming requests
        """
        correlation_id = getattr(g, "correlation_id", "unknown")

        try:
            self.logger.info(f"[{correlation_id}] Received chat request")
            data = request.get_json() or {}
            prompt = data.get("prompt", "").strip()

            files_data = data.get("files", [])

            request_dto = ChatRequestDto(prompt=prompt, files=files_data)

            accept_header = request.headers.get("Accept", "")
            if "text/event-stream" in accept_header:
                # Return streaming response
                self.logger.info(f"[{correlation_id}] Processing as streaming request")
                stream_generator = self.chat_service.process_chat_streaming(request_dto)

                return Response(
                    stream_with_context(stream_generator),
                    mimetype="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no",
                    },
                )
            else:
                self.logger.info(f"[{correlation_id}] Processing as regular request")
                deanonymised_response = self.chat_service.process_chat(request_dto)

                response_dto = ChatResponseDto(response=deanonymised_response)

                return jsonify({"response": response_dto.response}), 200

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

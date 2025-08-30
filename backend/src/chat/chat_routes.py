"""Chat routes blueprint using dependency injection."""

from flask import Blueprint
from ..common.container import container
from .chat_controller import ChatController

chat_blueprint = Blueprint("chat", __name__)


@chat_blueprint.route("/chat", methods=["POST"])
def process_chat():
    """Route for processing chat requests."""
    try:
        controller = container.get(ChatController)
        return controller.process_chat()
    except ValueError:
        from flask import jsonify, g
        from datetime import datetime

        correlation_id = getattr(g, "correlation_id", "unknown")

        return (
            jsonify(
                {
                    "statusCode": 503,
                    "timestamp": datetime.now().isoformat() + "Z",
                    "correlationId": correlation_id,
                    "error": "SERVICE_UNAVAILABLE",
                    "message": "Chat service not available",
                }
            ),
            503,
        )

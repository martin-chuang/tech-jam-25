"""Flask application factory with middleware and dependency injection."""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from datetime import datetime
import uuid
import logging

from .container import container
from .config.config_loader import ConfigLoader
from .middlewares.correlation_id import CorrelationIdMiddleware
from .filters.global_exception_filter import GlobalExceptionFilter


def setup_dependencies():
    """Setup dependency injection container."""
    try:
        from ..privacy.privacy_service import PrivacyService
        from ..chat.chat_service import ChatService
        from ..chat.chat_controller import ChatController
        from ..redis.redis_service import RedisService

        # Register services
        redis_service = RedisService()
        container.register_singleton(RedisService, redis_service)

        privacy_service = PrivacyService()
        container.register_singleton(PrivacyService, privacy_service)

        chat_service = ChatService(privacy_service)
        container.register_singleton(ChatService, chat_service)

        chat_controller = ChatController(chat_service)
        container.register_singleton(ChatController, chat_controller)

        logging.getLogger(__name__).info("Dependency injection setup complete")
        return True
    except Exception as e:
        logging.getLogger(__name__).warning(f"Could not setup dependencies: {e}")
        return False


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Load configuration from common config loader
    try:
        config = ConfigLoader.load_config()
        app.config["SECRET_KEY"] = config.secret_key
        app.config["DEBUG"] = config.debug
        app.logger.info("Configuration loaded successfully")
    except Exception as e:
        app.logger.warning(f"Could not load config: {e}, using defaults")
        app.config["DEBUG"] = True
        app.config["SECRET_KEY"] = "dev-secret-key"

    # Configure CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Correlation-ID"],
                "expose_headers": ["X-Correlation-ID"],
            }
        },
    )

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Setup dependencies
    di_success = setup_dependencies()
    if di_success:
        app.logger.info("Dependencies registered successfully")
    else:
        app.logger.warning("Running without full DI - using fallback endpoints")

    # Initialize common middleware and filters
    correlation_middleware = CorrelationIdMiddleware()
    correlation_middleware.init_app(app)

    exception_filter = GlobalExceptionFilter()
    exception_filter.init_app(app)

    # Register blueprints or fallback
    if di_success:
        try:
            from ..chat.chat_routes import chat_blueprint

            app.register_blueprint(chat_blueprint, url_prefix="/api/v1")
            app.logger.info("Successfully registered chat blueprint with DI")
        except ImportError as e:
            app.logger.warning(f"Could not import chat blueprint: {e}")
            di_success = False

    if not di_success:
        # Fallback simple endpoint
        @app.route("/api/v1/chat", methods=["POST"])
        def fallback_chat():
            correlation_id = getattr(g, "correlation_id", "unknown")

            # Basic request parsing
            try:
                data = request.get_json() or {}
                prompt = data.get("prompt", "").strip()
                files = request.files.getlist("files") if request.files else []

                if not prompt:
                    return (
                        jsonify(
                            {
                                "statusCode": 400,
                                "timestamp": datetime.utcnow().isoformat() + "Z",
                                "path": request.path,
                                "correlationId": correlation_id,
                                "error": "VALIDATION_ERROR",
                                "message": "Prompt is required",
                            }
                        ),
                        400,
                    )

                # Mock response
                return (
                    jsonify(
                        {
                            "statusCode": 200,
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "correlationId": correlation_id,
                            "data": {
                                "response": f"Fallback response for: {prompt[:100]}... (Files: {len(files)} - optional)"
                            },
                        }
                    ),
                    200,
                )

            except Exception as e:
                app.logger.error(f"[{correlation_id}] Fallback chat error: {str(e)}")
                return (
                    jsonify(
                        {
                            "statusCode": 500,
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "path": request.path,
                            "correlationId": correlation_id,
                            "error": "INTERNAL_ERROR",
                            "message": "Error processing request",
                        }
                    ),
                    500,
                )

    # Health endpoint
    @app.route("/health")
    def health_check():
        correlation_id = getattr(g, "correlation_id", "unknown")

        return (
            jsonify(
                {
                    "statusCode": 200,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "correlationId": correlation_id,
                    "data": {
                        "status": "healthy",
                        "service": "tiktok-techjam-backend",
                        "version": "1.0.0",
                        "di_enabled": di_success,
                    },
                }
            ),
            200,
        )

    return app

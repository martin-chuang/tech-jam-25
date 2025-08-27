"""Logger interceptor middleware."""

import time
import logging
from typing import Optional
from flask import Flask, request, g
from werkzeug.wrappers import Response


class LoggerInterceptor:
    """Logger interceptor middleware for request/response logging."""
    
    def __init__(self, app: Optional[Flask] = None):
        self.logger = logging.getLogger(__name__)
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize the logger interceptor with Flask app."""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown)
    
    def _get_correlation_id(self) -> Optional[str]:
        """Get correlation ID from request context."""
        return getattr(request, 'correlation_id', None)
    
    def _before_request(self):
        """Log incoming request."""
        g.start_time = time.time()
        
        correlation_id = self._get_correlation_id()
        method = request.method
        url = request.url
        
        # Log request details
        self.logger.info(
            f"[{correlation_id}] ==> {method} {url}"
        )
        
        # Log request headers (excluding sensitive information)
        if self.logger.isEnabledFor(logging.DEBUG):
            safe_headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ['authorization', 'cookie', 'x-api-key']
            }
            self.logger.debug(
                f"[{correlation_id}] Request headers: {safe_headers}"
            )
        
        # Log request body for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH'] and self.logger.isEnabledFor(logging.DEBUG):
            if request.is_json:
                try:
                    # Only log if content is not too large
                    if request.content_length and request.content_length < 10240:  # 10KB limit
                        self.logger.debug(
                            f"[{correlation_id}] Request body: {request.get_json()}"
                        )
                except Exception as e:
                    self.logger.debug(
                        f"[{correlation_id}] Could not log request body: {str(e)}"
                    )
    
    def _after_request(self, response: Response) -> Response:
        """Log outgoing response."""
        correlation_id = self._get_correlation_id()
        method = request.method
        url = request.url
        status_code = response.status_code
        
        # Calculate request duration
        duration = 0
        if hasattr(g, 'start_time'):
            duration = round((time.time() - g.start_time) * 1000, 2)  # Convert to milliseconds
        
        # Set correlation ID in response header
        if correlation_id:
            response.headers['X-Correlation-ID'] = correlation_id
        
        # Log response
        self.logger.info(
            f"[{correlation_id}] <== {method} {url} {status_code} - {duration}ms"
        )
        
        # Log response headers in debug mode
        if self.logger.isEnabledFor(logging.DEBUG):
            safe_headers = {
                k: v for k, v in response.headers.items()
                if k.lower() not in ['set-cookie']
            }
            self.logger.debug(
                f"[{correlation_id}] Response headers: {safe_headers}"
            )
        
        # Log response body in debug mode (be careful with large responses)
        if self.logger.isEnabledFor(logging.DEBUG) and response.content_length:
            if response.content_length < 5120:  # 5KB limit
                try:
                    if response.is_json:
                        self.logger.debug(
                            f"[{correlation_id}] Response body: {response.get_json()}"
                        )
                except Exception as e:
                    self.logger.debug(
                        f"[{correlation_id}] Could not log response body: {str(e)}"
                    )
        
        return response
    
    def _teardown(self, exception):
        """Clean up after request."""
        if exception:
            correlation_id = self._get_correlation_id()
            self.logger.error(
                f"[{correlation_id}] Request failed with exception: {str(exception)}",
                exc_info=True
            )


def setup_logging(app: Flask, log_level: str = 'INFO') -> None:
    """Setup application logging configuration."""
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up Flask's logger
    app.logger.setLevel(getattr(logging, log_level.upper()))
    
    # Reduce noise from some third-party libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Create file handler for errors
    if not app.debug:
        import os
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/tiktok_techjam.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        
        app.logger.info('TikTok TechJam application startup')

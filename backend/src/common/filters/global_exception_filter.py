"""Global exception filter for Flask application."""

import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, jsonify, Flask
from werkzeug.exceptions import HTTPException
import logging


class GlobalExceptionFilter:
    """Global exception filter for handling all application exceptions."""
    
    def __init__(self, app: Optional[Flask] = None):
        self.logger = logging.getLogger(__name__)
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize the exception filter with Flask app."""
        app.register_error_handler(Exception, self._handle_exception)
        app.register_error_handler(HTTPException, self._handle_http_exception)
    
    def _get_correlation_id(self) -> Optional[str]:
        """Get correlation ID from request context."""
        return getattr(request, 'correlation_id', None)
    
    def _create_error_response(
        self,
        status_code: int,
        message: str,
        error_type: str = "Error"
    ) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "statusCode": status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": request.path if request else "unknown",
            "correlationId": self._get_correlation_id(),
            "message": message,
            "error": error_type
        }
    
    def _handle_http_exception(self, error: HTTPException):
        """Handle HTTP exceptions."""
        self.logger.warning(
            f"HTTP Exception [{self._get_correlation_id()}]: "
            f"{error.code} - {error.description} - Path: {request.path}"
        )
        
        response_data = self._create_error_response(
            status_code=error.code,
            message=error.description,
            error_type=error.name
        )
        
        response = jsonify(response_data)
        response.status_code = error.code
        response.headers['X-Correlation-ID'] = self._get_correlation_id() or ''
        return response
    
    def _handle_exception(self, error: Exception):
        """Handle general exceptions."""
        correlation_id = self._get_correlation_id()
        
        # Log the full exception with stack trace
        self.logger.error(
            f"Unhandled Exception [{correlation_id}]: "
            f"{str(error)} - Path: {request.path if request else 'unknown'}",
            exc_info=True
        )
        
        message = "Internal server error"
        
        response_data = self._create_error_response(
            status_code=500,
            message=message,
            error_type="InternalServerError"
        )
        
        response = jsonify(response_data)
        response.status_code = 500
        response.headers['X-Correlation-ID'] = correlation_id or ''
        return response


# Custom exception classes
class ValidationError(Exception):
    """Custom validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class BusinessLogicError(Exception):
    """Custom business logic error."""
    
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(message)


class ResourceNotFoundError(Exception):
    """Custom resource not found error."""
    
    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        self.message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(self.message)


def register_custom_exception_handlers(app: Flask) -> None:
    """Register custom exception handlers."""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        filter_instance = GlobalExceptionFilter()
        response_data = filter_instance._create_error_response(
            status_code=400,
            message=error.message,
            error_type="ValidationError"
        )
        if error.field:
            response_data["field"] = error.field
        
        response = jsonify(response_data)
        response.status_code = 400
        return response
    
    @app.errorhandler(BusinessLogicError)
    def handle_business_logic_error(error):
        filter_instance = GlobalExceptionFilter()
        response_data = filter_instance._create_error_response(
            status_code=422,
            message=error.message,
            error_type="BusinessLogicError"
        )
        if error.code:
            response_data["code"] = error.code
        
        response = jsonify(response_data)
        response.status_code = 422
        return response
    
    @app.errorhandler(ResourceNotFoundError)
    def handle_resource_not_found_error(error):
        filter_instance = GlobalExceptionFilter()
        response_data = filter_instance._create_error_response(
            status_code=404,
            message=error.message,
            error_type="ResourceNotFoundError"
        )
        response_data["resource"] = error.resource
        response_data["identifier"] = error.identifier
        
        response = jsonify(response_data)
        response.status_code = 404
        return response

"""
Advanced error handling and logging system for Hospital AI Consulting OS.

This module provides comprehensive error handling, structured logging, and monitoring
integration for production-grade applications.
"""

import sys
import traceback
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Callable
from contextlib import contextmanager
from functools import wraps
from enum import Enum

import structlog
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error category types."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    INTEGRATION = "integration"
    DATABASE = "database"
    NETWORK = "network"
    CONFIGURATION = "configuration"
    PERFORMANCE = "performance"


class ErrorContext(BaseModel):
    """Error context information."""
    
    user_id: Optional[str] = None
    hospital_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    additional_data: Dict[str, Any] = Field(default_factory=dict)


class ApplicationError(Exception):
    """
    Base application error class with comprehensive error information.
    
    Provides structured error information including:
    - Error codes and messages
    - Severity and category classification
    - Context information
    - User-friendly messages
    - Monitoring and alerting integration
    """
    
    def __init__(
        self,
        message: str,
        error_code: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        context: Optional[ErrorContext] = None,
        user_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        should_alert: bool = False
    ):
        """
        Initialize application error.
        
        Args:
            message: Technical error message for developers
            error_code: Unique error code for tracking
            severity: Error severity level
            category: Error category
            context: Request/user context information
            user_message: User-friendly error message
            details: Additional error details
            cause: Original exception that caused this error
            should_alert: Whether this error should trigger alerts
        """
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context or ErrorContext()
        self.user_message = user_message or "An unexpected error occurred"
        self.details = details or {}
        self.cause = cause
        self.should_alert = should_alert
        self.timestamp = datetime.utcnow()
        self.trace_id = self._generate_trace_id()
    
    def _generate_trace_id(self) -> str:
        """Generate unique trace ID for error tracking."""
        import uuid
        return str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging and API responses."""
        error_dict = {
            'error_code': self.error_code,
            'message': self.message,
            'user_message': self.user_message,
            'severity': self.severity.value,
            'category': self.category.value,
            'timestamp': self.timestamp.isoformat(),
            'trace_id': self.trace_id,
            'details': self.details,
            'should_alert': self.should_alert
        }
        
        if self.context:
            error_dict['context'] = self.context.model_dump(exclude_none=True)
        
        if self.cause:
            error_dict['cause'] = {
                'type': type(self.cause).__name__,
                'message': str(self.cause)
            }
        
        return error_dict
    
    def to_json(self) -> str:
        """Convert error to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class ValidationError(ApplicationError):
    """Data validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            user_message="Invalid input provided",
            details={'field': field, 'value': str(value) if value is not None else None},
            **kwargs
        )


class AuthenticationError(ApplicationError):
    """Authentication errors."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            user_message="Authentication required",
            should_alert=True,
            **kwargs
        )


class AuthorizationError(ApplicationError):
    """Authorization errors."""
    
    def __init__(self, message: str = "Access denied", resource: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR", 
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHORIZATION,
            user_message="Insufficient permissions",
            details={'resource': resource},
            should_alert=True,
            **kwargs
        )


class BusinessLogicError(ApplicationError):
    """Business logic and rule violations."""
    
    def __init__(self, message: str, rule: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="Operation not allowed",
            details={'rule': rule},
            **kwargs
        )


class DatabaseError(ApplicationError):
    """Database operation errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE,
            user_message="Data operation failed",
            details={'operation': operation},
            should_alert=True,
            **kwargs
        )


class IntegrationError(ApplicationError):
    """External service integration errors."""
    
    def __init__(
        self, 
        message: str, 
        service: Optional[str] = None, 
        status_code: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="INTEGRATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.INTEGRATION,
            user_message="External service unavailable",
            details={'service': service, 'status_code': status_code},
            should_alert=True,
            **kwargs
        )


class PerformanceError(ApplicationError):
    """Performance-related errors."""
    
    def __init__(self, message: str, threshold: Optional[float] = None, actual: Optional[float] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="PERFORMANCE_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PERFORMANCE,
            user_message="Operation took longer than expected",
            details={'threshold': threshold, 'actual': actual},
            should_alert=True,
            **kwargs
        )


class ErrorHandler:
    """
    Comprehensive error handling system with logging and monitoring integration.
    """
    
    def __init__(
        self,
        logger: Optional[structlog.BoundLogger] = None,
        alert_handler: Optional[Callable[[ApplicationError], None]] = None
    ):
        """
        Initialize error handler.
        
        Args:
            logger: Structured logger instance
            alert_handler: Function to handle error alerts
        """
        self.logger = logger or structlog.get_logger(__name__)
        self.alert_handler = alert_handler
        self.error_stats: Dict[str, int] = {}
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        additional_details: Optional[Dict[str, Any]] = None
    ) -> ApplicationError:
        """
        Handle and process any exception into a structured error.
        
        Args:
            error: Original exception
            context: Request context
            additional_details: Additional error details
            
        Returns:
            Structured application error
        """
        # Convert to ApplicationError if needed
        if isinstance(error, ApplicationError):
            app_error = error
        else:
            app_error = self._convert_exception(error, context, additional_details)
        
        # Update context if provided
        if context:
            app_error.context = context
        
        # Log error
        self._log_error(app_error)
        
        # Update statistics
        self._update_stats(app_error)
        
        # Send alert if needed
        if app_error.should_alert and self.alert_handler:
            self.alert_handler(app_error)
        
        return app_error
    
    def _convert_exception(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        additional_details: Optional[Dict[str, Any]] = None
    ) -> ApplicationError:
        """Convert generic exception to ApplicationError."""
        error_type = type(error).__name__
        
        # Map common exception types
        if isinstance(error, ValueError):
            return ValidationError(
                message=str(error),
                context=context,
                details=additional_details or {},
                cause=error
            )
        elif isinstance(error, PermissionError):
            return AuthorizationError(
                message=str(error),
                context=context,
                details=additional_details or {},
                cause=error
            )
        elif isinstance(error, ConnectionError):
            return IntegrationError(
                message=str(error),
                context=context,
                details=additional_details or {},
                cause=error
            )
        else:
            # Generic system error
            return ApplicationError(
                message=str(error),
                error_code=f"SYSTEM_ERROR_{error_type.upper()}",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.SYSTEM,
                context=context,
                user_message="An unexpected error occurred",
                details={
                    'exception_type': error_type,
                    'traceback': traceback.format_exc(),
                    **(additional_details or {})
                },
                cause=error,
                should_alert=True
            )
    
    def _log_error(self, error: ApplicationError) -> None:
        """Log structured error information."""
        log_data = error.to_dict()
        
        # Determine log level based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical("Critical error occurred", **log_data)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error("High severity error occurred", **log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning("Medium severity error occurred", **log_data)
        else:
            self.logger.info("Low severity error occurred", **log_data)
    
    def _update_stats(self, error: ApplicationError) -> None:
        """Update error statistics."""
        self.error_stats[error.error_code] = self.error_stats.get(error.error_code, 0) + 1
    
    def get_error_stats(self) -> Dict[str, int]:
        """Get current error statistics."""
        return self.error_stats.copy()
    
    def reset_stats(self) -> None:
        """Reset error statistics."""
        self.error_stats.clear()


class ErrorMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for handling errors and exceptions.
    """
    
    def __init__(self, app, error_handler: Optional[ErrorHandler] = None):
        super().__init__(app)
        self.error_handler = error_handler or ErrorHandler()
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle any errors."""
        try:
            # Create error context from request
            context = ErrorContext(
                request_id=getattr(request.state, 'request_id', None),
                endpoint=str(request.url.path),
                method=request.method,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get('user-agent'),
                additional_data={
                    'query_params': dict(request.query_params),
                    'path_params': dict(request.path_params) if hasattr(request, 'path_params') else {}
                }
            )
            
            # Add context to request state for use in handlers
            request.state.error_context = context
            
            response = await call_next(request)
            return response
            
        except Exception as exc:
            # Handle unexpected errors
            error = self.error_handler.handle_error(exc, context)
            
            # Return appropriate HTTP response
            return self._create_error_response(error)
    
    def _create_error_response(self, error: ApplicationError) -> JSONResponse:
        """Create HTTP error response from ApplicationError."""
        # Map error severity to HTTP status codes
        status_map = {
            ErrorCategory.VALIDATION: status.HTTP_400_BAD_REQUEST,
            ErrorCategory.AUTHENTICATION: status.HTTP_401_UNAUTHORIZED,
            ErrorCategory.AUTHORIZATION: status.HTTP_403_FORBIDDEN,
            ErrorCategory.BUSINESS_LOGIC: status.HTTP_422_UNPROCESSABLE_ENTITY,
            ErrorCategory.DATABASE: status.HTTP_503_SERVICE_UNAVAILABLE,
            ErrorCategory.INTEGRATION: status.HTTP_502_BAD_GATEWAY,
            ErrorCategory.PERFORMANCE: status.HTTP_504_GATEWAY_TIMEOUT
        }
        
        status_code = status_map.get(error.category, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create response body
        response_body = {
            'error': {
                'code': error.error_code,
                'message': error.user_message,
                'trace_id': error.trace_id,
                'timestamp': error.timestamp.isoformat()
            }
        }
        
        # Add details in development mode
        from backend.config.advanced_config_manager import is_debug_mode
        if is_debug_mode():
            response_body['error']['technical_message'] = error.message
            response_body['error']['details'] = error.details
        
        return JSONResponse(
            status_code=status_code,
            content=response_body
        )


def error_handler(
    error_type: type = Exception,
    error_code: Optional[str] = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.SYSTEM,
    user_message: Optional[str] = None,
    should_alert: bool = False
):
    """
    Decorator for automatic error handling in functions.
    
    Args:
        error_type: Type of exception to catch
        error_code: Custom error code
        severity: Error severity
        category: Error category
        user_message: User-friendly message
        should_alert: Whether to send alerts
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except error_type as e:
                handler = ErrorHandler()
                app_error = ApplicationError(
                    message=str(e),
                    error_code=error_code or f"{func.__name__.upper()}_ERROR",
                    severity=severity,
                    category=category,
                    user_message=user_message or "Operation failed",
                    details={'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)},
                    cause=e,
                    should_alert=should_alert
                )
                handler.handle_error(app_error)
                raise app_error
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                handler = ErrorHandler()
                app_error = ApplicationError(
                    message=str(e),
                    error_code=error_code or f"{func.__name__.upper()}_ERROR",
                    severity=severity,
                    category=category,
                    user_message=user_message or "Operation failed",
                    details={'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)},
                    cause=e,
                    should_alert=should_alert
                )
                handler.handle_error(app_error)
                raise app_error
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@contextmanager
def error_context(context_data: Dict[str, Any]):
    """Context manager for providing error context."""
    # Store context data in thread-local storage or similar
    # This is a simplified implementation
    try:
        yield
    except Exception as e:
        handler = ErrorHandler()
        context = ErrorContext(additional_data=context_data)
        error = handler.handle_error(e, context)
        raise error


def setup_logging(
    log_level: str = "INFO",
    structured: bool = True,
    include_trace: bool = False
) -> structlog.BoundLogger:
    """
    Set up structured logging configuration.
    
    Args:
        log_level: Logging level
        structured: Use structured logging
        include_trace: Include trace information
        
    Returns:
        Configured logger
    """
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if include_trace:
        processors.append(structlog.processors.format_exc_info)
    
    if structured:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    return structlog.get_logger()


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get or create global error handler."""
    global _global_error_handler
    
    if _global_error_handler is None:
        logger = setup_logging()
        _global_error_handler = ErrorHandler(logger=logger)
    
    return _global_error_handler


# Convenience functions for common error types
def raise_validation_error(message: str, field: Optional[str] = None, value: Optional[Any] = None):
    """Raise a validation error."""
    raise ValidationError(message=message, field=field, value=value)


def raise_authentication_error(message: str = "Authentication required"):
    """Raise an authentication error."""
    raise AuthenticationError(message=message)


def raise_authorization_error(message: str = "Access denied", resource: Optional[str] = None):
    """Raise an authorization error."""
    raise AuthorizationError(message=message, resource=resource)


def raise_business_error(message: str, rule: Optional[str] = None):
    """Raise a business logic error."""
    raise BusinessLogicError(message=message, rule=rule)


def raise_database_error(message: str, operation: Optional[str] = None):
    """Raise a database error."""
    raise DatabaseError(message=message, operation=operation)


def raise_integration_error(message: str, service: Optional[str] = None, status_code: Optional[int] = None):
    """Raise an integration error."""
    raise IntegrationError(message=message, service=service, status_code=status_code)
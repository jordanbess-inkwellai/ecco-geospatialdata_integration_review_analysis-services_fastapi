import logging
import time
from functools import wraps
from typing import Callable, Dict, Any, Optional, Type, List, Union
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Define error types
class RcloneError(Exception):
    """Base class for Rclone errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class RcloneConnectionError(RcloneError):
    """Error connecting to remote storage"""
    pass


class RcloneAuthenticationError(RcloneError):
    """Authentication error with remote storage"""
    pass


class RclonePermissionError(RcloneError):
    """Permission error with remote storage"""
    pass


class RcloneFileNotFoundError(RcloneError):
    """File not found in remote storage"""
    pass


class RcloneConfigError(RcloneError):
    """Error in Rclone configuration"""
    pass


class RcloneExecutionError(RcloneError):
    """Error executing Rclone command"""
    pass


# Error mapping from Rclone output to specific error types
ERROR_PATTERNS = [
    (r"connection.*failed|network error|timeout", RcloneConnectionError),
    (r"permission denied|access denied|not authorized", RclonePermissionError),
    (r"file not found|no such file|does not exist|not found", RcloneFileNotFoundError),
    (r"auth.*failed|unauthorized|invalid.*token|expired.*token", RcloneAuthenticationError),
    (r"config.*error|invalid.*config|unknown.*remote", RcloneConfigError),
]


def parse_rclone_error(error_message: str) -> RcloneError:
    """
    Parse Rclone error message and return appropriate error type
    
    Args:
        error_message: Error message from Rclone
        
    Returns:
        Specific RcloneError subclass
    """
    import re
    
    for pattern, error_class in ERROR_PATTERNS:
        if re.search(pattern, error_message, re.IGNORECASE):
            return error_class(error_message)
    
    return RcloneExecutionError(error_message)


def handle_rclone_error(error: Union[str, Exception]) -> Dict[str, Any]:
    """
    Handle Rclone error and return standardized error response
    
    Args:
        error: Error message or exception
        
    Returns:
        Standardized error response dictionary
    """
    if isinstance(error, str):
        rclone_error = parse_rclone_error(error)
    elif isinstance(error, RcloneError):
        rclone_error = error
    else:
        rclone_error = RcloneExecutionError(str(error))
    
    logger.error(f"Rclone error: {rclone_error.message}", exc_info=True)
    
    return {
        "success": False,
        "error": rclone_error.message,
        "error_type": rclone_error.__class__.__name__,
        "details": rclone_error.details
    }


def with_retry(max_retries: int = 3, retry_delay: float = 1.0, 
               retry_exceptions: List[Type[Exception]] = None):
    """
    Decorator to retry a function on specified exceptions
    
    Args:
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
        retry_exceptions: List of exception types to retry on
        
    Returns:
        Decorated function
    """
    if retry_exceptions is None:
        retry_exceptions = [RcloneConnectionError, RcloneAuthenticationError]
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None
            
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except tuple(retry_exceptions) as e:
                    last_exception = e
                    retries += 1
                    
                    if retries < max_retries:
                        wait_time = retry_delay * (2 ** (retries - 1))  # Exponential backoff
                        logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} after {wait_time}s due to: {str(e)}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Max retries ({max_retries}) reached for {func.__name__}")
            
            # If we get here, all retries failed
            if isinstance(last_exception, RcloneError):
                return handle_rclone_error(last_exception)
            else:
                return {
                    "success": False,
                    "error": f"Operation failed after {max_retries} retries: {str(last_exception)}",
                    "error_type": "MaxRetriesExceeded"
                }
        
        return wrapper
    
    return decorator


def http_error_handler(error_response: Dict[str, Any]) -> None:
    """
    Convert error response to HTTPException
    
    Args:
        error_response: Error response dictionary
        
    Raises:
        HTTPException: FastAPI HTTP exception
    """
    # Map error types to status codes
    status_codes = {
        "RcloneConnectionError": 503,  # Service Unavailable
        "RcloneAuthenticationError": 401,  # Unauthorized
        "RclonePermissionError": 403,  # Forbidden
        "RcloneFileNotFoundError": 404,  # Not Found
        "RcloneConfigError": 400,  # Bad Request
        "RcloneExecutionError": 500,  # Internal Server Error
    }
    
    error_type = error_response.get("error_type", "RcloneExecutionError")
    status_code = status_codes.get(error_type, 500)
    
    raise HTTPException(
        status_code=status_code,
        detail={
            "error": error_response.get("error", "Unknown error"),
            "error_type": error_type,
            "details": error_response.get("details", {})
        }
    )

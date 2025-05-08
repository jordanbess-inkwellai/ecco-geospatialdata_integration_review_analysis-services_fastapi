from fastapi import HTTPException, status

class ProcessNotFoundException(HTTPException):
    """Exception raised when a process is not found."""
    
    def __init__(self, process_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process {process_id} not found"
        )

class ProcessExecutionException(HTTPException):
    """Exception raised when a process execution fails."""
    
    def __init__(self, process_id: str, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing process {process_id}: {message}"
        )

class ValidationException(HTTPException):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {message}"
        )

class DatabaseException(HTTPException):
    """Exception raised when a database operation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {message}"
        )

class TimeoutException(HTTPException):
    """Exception raised when a process times out."""
    
    def __init__(self, process_id: str):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Process {process_id} timed out"
        )

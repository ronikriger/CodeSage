from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Union
import logging

logger = logging.getLogger(__name__)

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Error processing request: {str(exc)}")
    
    error_mapping = {
        "ValidationError": (status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid input data"),
        "AuthenticationError": (status.HTTP_401_UNAUTHORIZED, "Authentication failed"),
        "PermissionError": (status.HTTP_403_FORBIDDEN, "Permission denied"),
        "NotFoundError": (status.HTTP_404_NOT_FOUND, "Resource not found"),
    }
    
    error_type = type(exc).__name__
    status_code, message = error_mapping.get(
        error_type,
        (status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
    )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "detail": str(exc),
            "path": request.url.path
        }
    ) 
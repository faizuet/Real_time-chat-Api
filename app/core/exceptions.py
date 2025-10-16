from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles manually raised HTTP exceptions."""
    logger.warning(f"HTTPException on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handles SQLAlchemy-specific database errors."""
    logger.error(f"Database error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred. Please try again later."},
    )

async def jwt_exception_handler(request: Request, exc: JWTError):
    """Handles JWT-related authentication errors."""
    logger.error(f"JWT error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid or expired authentication token."},
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handles all unexpected errors."""
    logger.exception(f"Unexpected error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


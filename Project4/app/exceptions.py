# In-built packages (Standard Library modules)
import traceback

# External packages
from fastapi import Request
from starlette import status
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Our Own Imports
from app.logger import get_logger


# Create module-specific logger (uses this file's name internally)
logger = get_logger(__file__)


# ---------------------------------------------------------------------------
# Helper function to create a consistent JSON error response structure
# ---------------------------------------------------------------------------
def error_response(error_type: str, message: str, status_code: int, path: str):
    """
    Builds and returns a JSON error response with a consistent format.
    
    This ensures all errors in the project follow the same structure:
    
    {
        "error": {
            "type": "...",
            "message": "...",
            "path": "..."   # URL where the error occurred
        }
    }
    """
    
    return JSONResponse(status_code = status_code, 
                        content = {
                            "error" : {
                                "type" : error_type, 
                                "message" : message, 
                                "path" : path
                                }
                            })


# ---------------------------------------------------------------------------
# Handles SQLAlchemy IntegrityError (e.g. duplicate username, duplicate email)
# ---------------------------------------------------------------------------
async def integrity_error_handler(request : Request, exc : IntegrityError):
    """
    Handles database constraint violations.
    
    Example triggers:
    - Unique constraint failed (username/email already exists)
    - Foreign key constraint violations
    - NOT NULL violations
    """
    
    # Extract raw database error message (varies for SQLite / PostgreSQL)
    raw_message = str(exc.orig) if exc.orig else str(exc)
    
    # Default generic message shown to user
    user_message = "Database constraint failed (duplicate or invalid data)."
    
    # Attempt to detect and extract column name from the DB error string
    # Example raw message: "UNIQUE constraint failed: users.username"
    if "UNIQUE constraint failed" in raw_message:
        try:
            # Split on ":" → ["UNIQUE constraint failed", " users.username"]
            _, failed_column = raw_message.split(":")
            failed_column = failed_column.strip()
            
            # Extract only the column → username
            failed_column = failed_column.split(".")[-1]
            
            # Create user-friendly message
            user_message = (
                f"The value for '{failed_column}' already exists. "
                f"Please choose a different {failed_column}."
            )
        except Exception:
            # If parsing fails, fall back to default message
            pass
        
    # Log the technical error for developers (not shown to end user)
    logger.error(f"IntegrityError : {raw_message}")
    
    # Return a clean JSON error response to the client
    return error_response(error_type = "IntegrityError", 
                          message = user_message, 
                          status_code = status.HTTP_400_BAD_REQUEST, 
                          path = str(request.url))


# ---------------------------------------------------------------------------
# Handles FastAPI/Starlette default HTTP errors (e.g., 404 Not Found, 401 Unauthorized)
# ---------------------------------------------------------------------------
async def http_exception_handler(request : Request, exc : StarletteHTTPException):
    """
    Handles general HTTP errors such as:
    - 404 Not Found
    - 401 Unauthorized
    - 403 Forbidden
    - Any errors raised by:   raise HTTPException(status_code=..., detail="...")
    """
    
    logger.warning(f"HTTPException : {exc.detail}")
    
    return error_response(error_type = "HTTPException", 
                          message = exc.detail, 
                          status_code = exc.status_code, 
                          path = str(request.url))


# ---------------------------------------------------------------------------
# Handles Pydantic validation errors (invalid request bodies, wrong types, missing fields)
# ---------------------------------------------------------------------------
async def validation_exception_handler(request : Request, exc : RequestValidationError):
    """
    Handles input validation errors raised before hitting your route logic.
    
    Example:
    - Missing required fields in JSON body
    - Wrong data types
    - Failing Pydantic model validation
    """
    logger.warning(f"ValidationError : {exc.errors()}")
    
    # Extract only human-friendly error messages from Pydantic
    messages = "; ".join([err["msg"] for err in exc.errors()])
    
    return error_response(error_type = "RequestValidationError", 
                          message = messages, 
                          status_code = status.HTTP_422_UNPROCESSABLE_CONTENT, 
                          path = str(request.url))


# ---------------------------------------------------------------------------
# Catches ALL unhandled exceptions (our global fail-safe)
# ---------------------------------------------------------------------------
async def generic_exception_handler(request : Request, exc : Exception):
    """
    This is the "catch-all" exception handler.
    Any error not caught by previous handlers lands here.
    
    Useful for:
    - Unexpected bugs
    - Developer mistakes
    - Runtime errors not anticipated by other handlers
    """
    
    # Log full stack trace for debugging
    # traceback.format_exception() returns the complete error with file + line number
    logger.error("Unhandled Exception: " + "".join(traceback.format_exception(None, exc, exc.__traceback__)))
    
    # Send safe, generic error to user (never expose stack traces to client)
    return error_response(error_type = "InternalServerError", 
                          message = "Something went wrong. Please try again later.", 
                          status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          path = str(request.url))
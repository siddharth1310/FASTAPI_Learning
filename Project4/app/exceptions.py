# In-built packages (Standard Library modules)
import logging
import traceback

# External packages
from fastapi import Request
from starlette import status
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# Our Own Imports


logger = logging.getLogger("uvicorn.error")


def error_response(error_type : str, message : str, status_code : int, path : str):
    return JSONResponse(status_code = status_code, 
                        content = {
                            "error" : 
                                {
                                    "type" : error_type, 
                                    "message" : message, 
                                    "path" : path
                                }
                            })


async def integrity_error_handler(request : Request, exc : IntegrityError):
    raw_message = str(exc.orig) if exc.orig else str(exc)

    # Default message
    user_message = "Database constraint failed (duplicate or invalid data)."

    # Try to detect UNIQUE constraint column
    if "UNIQUE constraint failed" in raw_message:
        # Example: "UNIQUE constraint failed: users.username"
        try:
            _, failed_column = raw_message.split(":")
            failed_column = failed_column.strip()
            
            # Extract just the column name (users.username → username)
            failed_column = failed_column.split(".")[-1]
            
            user_message = f"The value for '{failed_column}' already exists. Please choose a different {failed_column}."
        except Exception:
            pass
        
    logger.error(f"IntegrityError : {raw_message}")
    
    return error_response(error_type = "IntegrityError", 
                          message = user_message, 
                          status_code = status.HTTP_400_BAD_REQUEST, 
                          path = str(request.url))


async def http_exception_handler(request : Request, exc : StarletteHTTPException):
    logger.warning(f"HTTPException : {exc.detail}")
    return error_response(error_type = "HTTPException", 
                          message = exc.detail, 
                          status_code = exc.status_code, 
                          path = str(request.url))


async def validation_exception_handler(request : Request, exc : RequestValidationError):
    logger.warning(f"ValidationError : {exc.errors()}")
    return error_response(error_type = "RequestValidationError", 
                          message =  "; ".join([err["msg"] for err in exc.errors()]), 
                          status_code = status.HTTP_422_UNPROCESSABLE_CONTENT, 
                          path = str(request.url))


async def generic_exception_handler(request : Request, exc : Exception):
    logger.error("Unhandled Exception: " + "".join(traceback.format_exception(None, exc, exc.__traceback__)))
    return error_response(error_type = "InternalServerError", 
                          message = "Something went wrong. Please try again later.", 
                          status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          path = str(request.url))

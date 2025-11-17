from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError
import traceback
import logging

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
    logger.error(f"IntegrityError : {str(exc)}")
    return error_response(error_type = "IntegrityError", 
                          message = "Database constraint failed (duplicate or invalid data).", 
                          status_code = 400, 
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
                          message = exc.errors(), 
                          status_code = 422, 
                          path = str(request.url))


async def generic_exception_handler(request : Request, exc : Exception):
    logger.error("Unhandled Exception: " + "".join(traceback.format_exception(None, exc, exc.__traceback__)))
    return error_response(error_type = "InternalServerError", 
                          message = "Something went wrong. Please try again later.", 
                          status_code = 500, 
                          path = str(request.url))

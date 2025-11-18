# In-built packages (Standard Library modules)

# External packages
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Our Own Imports
from .models import Base
from .database import engine
from app.routers import auth, todos, admin, users
from app.exceptions import http_exception_handler, validation_exception_handler, integrity_error_handler, generic_exception_handler


app = FastAPI()

Base.metadata.create_all(bind = engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

# Register global exception handlers
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
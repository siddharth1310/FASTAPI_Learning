# In-built packages (Standard Library modules)
from contextlib import asynccontextmanager

# External packages
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Our Own Imports
from .models import Base
from .database import engine
from app.logger import get_logger
from app.routers import auth, todos, admin, users
from app.exceptions import http_exception_handler, validation_exception_handler, integrity_error_handler, generic_exception_handler

# Create a module-specific logger (this log will be written into main.jsonl)
logger = get_logger(__file__)


# -----------------------------------------------------------------------------
# Lifespan: Replacement for FastAPI's old "startup" and "shutdown" events
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app : FastAPI):
    """
    The lifespan function manages application startup and shutdown.
    
    Think of it like:
    
        async with lifespan(app):
            run_app()
    
    Everything above 'yield' = Startup
    Everything below 'yield' = Shutdown
    """
    
    # ------------------------------ STARTUP LOGIC ------------------------------
    logger.info("FastAPI application has started")
    
    # yield hands control over to FastAPI to start serving requests
    yield
    
    # ------------------------------ SHUTDOWN LOGIC -----------------------------
    logger.info("FastAPI application is shutting down")


# -----------------------------------------------------------------------------
# Create FastAPI app with the custom lifespan manager
# -----------------------------------------------------------------------------
app = FastAPI(lifespan = lifespan)


# -----------------------------------------------------------------------------
# Create database tables (if they don't already exist)
# This executes once at startup.
# -----------------------------------------------------------------------------
Base.metadata.create_all(bind = engine)
# Note:
# In production, Alembic migrations should be used instead,
# but for small apps or fast prototypes, this is acceptable.


# -----------------------------------------------------------------------------
# Register API routers (these add all your endpoints)
# -----------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
# Each router corresponds to a separate file inside app/routers/
# This keeps your project modular and clean.


# -----------------------------------------------------------------------------
# Register Global Exception Handlers
# These override FastAPI's default error handling behavior.
# -----------------------------------------------------------------------------

# Handles DB constraint issues (duplicate username, foreign key errors, etc.)
app.add_exception_handler(IntegrityError, integrity_error_handler)

# Handles HTTP errors like 404, 401, 403, etc.
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

# Handles Pydantic validation errors (invalid request body)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Catch-all for ANY unhandled exception (prevents app crashes)
app.add_exception_handler(Exception, generic_exception_handler)
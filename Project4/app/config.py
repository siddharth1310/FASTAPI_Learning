# In-built packages (Standard Library modules)
from os import environ
from typing import Annotated

# External packages
from starlette import status
from dotenv import load_dotenv
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

# Our Own Imports
from app.logger import get_logger
from app.database import SessionLocal


# ---------------------------------------------- #
# Logger Setup
# ---------------------------------------------- #
# get_logger(__file__) automatically names the logger based on the filename
logger = get_logger(__file__)

# Load environment variables from the .env file into memory
# Example: SECRET_KEY="abcd1234"
load_dotenv()

# Create a password hashing context
# Here, you are using Argon2 (recommended modern hashing algorithm)
bcrypt_context = CryptContext(schemes = ["argon2"])


# ====================================================================
#                    DATABASE DEPENDENCY
# ====================================================================
def get_db():
    """
    Creates and returns a database session for each request.
    FastAPI will call this function whenever a route depends on `db_dependency`.
    The session is automatically closed after the request completes.
    """
    logger.debug("Creating database session")
    db = SessionLocal()
    try:
        yield db  # Provide the session to the path operation function
    finally:
        logger.debug("Closing database session")
        db.close()  # Always close the session (important to avoid DB connection leaks)


# Annotated is used to define dependency types in a clean manner
db_dependency = Annotated[Session, Depends(get_db)]


# ====================================================================
#                    USER AUTHENTICATION DEPENDENCY
# ====================================================================
# OAuth2PasswordBearer tells FastAPI how to extract the JWT token from the request.
# Clients must include: Authorization: Bearer <jwt_token>
oauth2_bearer = OAuth2PasswordBearer(tokenUrl = "auth/token")

# JWT signing algorithm (must match what you used while generating tokens)
ALGORITHM = "HS256"

async def get_current_user(token : Annotated[str, Depends(oauth2_bearer)]):
    """
    Extracts the current user from the JWT token.
    
    Steps:
    1. FastAPI extracts the token automatically via OAuth2PasswordBearer.
    2. We decode the token using SECRET_KEY.
    3. We validate the fields (username, user ID).
    4. If valid → return usable user info.
    5. If invalid → raise HTTP 401.
    """
    
    logger.debug("Decoding JWT token inside get_current_user()")
    
    try:
        # Decode and verify the JWT token
        payload = jwt.decode(token = token, 
                             key = environ.get("SECRET_KEY", ""), 
                             algorithms = ALGORITHM)
        
        # Extract expected fields from the JWT payload
        username : str = payload.get("sub")   # "sub" → subject (username or email)
        user_id : int = payload.get("id")
        user_role : str = payload.get("user_role")
        
        # If critical fields are missing → token is invalid
        if username is None or user_id is None:
            logger.warning("Token decoded but missing critical fields (username/id)")
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, 
                                detail = "Could not validate user.")
        
        logger.debug(f"Authenticated User → username={username}, id={user_id}, role={user_role}")
        
        # Return user information to any endpoint that depends on this
        return {"username" : username, "id" : user_id, "user_role" : user_role}
    except JWTError as e:
        # JWT error means invalid or expired token
        logger.error(f"JWT decoding failed: {e}")
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, 
                            detail = "Could not validate user.")


# FastAPI-style dependency for getting authenticated user info
user_dependency = Annotated[dict, Depends(get_current_user)]
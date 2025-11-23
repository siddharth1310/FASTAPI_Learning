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
from app.database import SessionLocal


# Load environment variables from .env file
load_dotenv()

bcrypt_context = CryptContext(schemes = ["argon2"])

#----------------------------------------------DB DEPENDENCY-----------------------------------------------------------------#
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#----------------------------------------------USER DEPENDENCY CREATION-------------------------------------------------------#
oauth2_bearer = OAuth2PasswordBearer(tokenUrl = "auth/token")
ALGORITHM = "HS256"

async def get_current_user(token : Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token = token, key = environ.get("SECRET_KEY", ""), algorithms = ALGORITHM)
        
        username : str = payload.get("sub")
        user_id : int = payload.get("id")
        user_role : str = payload.get("user_role")
        
        if username is None or user_id is None:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate user.")
        
        return {"username" : username, "id" : user_id, "user_role" : user_role}
    except JWTError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate user.")

user_dependency = Annotated[dict, Depends(get_current_user)]
# In-built packages (Standard Library modules)
from os import environ
from typing import Annotated
from dotenv import load_dotenv
from datetime import timedelta, datetime, timezone

# External packages
from jose import jwt
from starlette import status
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request

# Our Own Imports
from app.models import Users
from app.schemas import Token
from app.config import ALGORITHM
from app.config import db_dependency, bcrypt_context

# Load environment variables from .env file
load_dotenv()

router = APIRouter(prefix = "/auth", tags = ["auth"])


def authenticate_user(username : str, password : str, db_instance : db_dependency):
    user = db_instance.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username : str, user_id : int, user_role : str, expires_delta : timedelta):
    encode = {"sub" : username, "id" : user_id, "user_role"  : user_role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp" : expires})
    return jwt.encode(claims = encode, key = environ.get("SECRET_KEY", ""), algorithm = ALGORITHM)


@router.get("/users", status_code = status.HTTP_200_OK)
async def get_user(db : db_dependency):
    return db.query(Users).all()


@router.post("/token", response_model = Token)
async def login_for_access_token(form_data : Annotated[OAuth2PasswordRequestForm, Depends()], db : db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate user.")
    else:
        token = create_access_token(user.username, user.id, user.role, timedelta(minutes = 20))
        return {"access_token" : token, "token_type" : "bearer"}

templates = Jinja2Templates(directory = "templates")

@router.get("/login-page")
def render_login_page(request : Request):
    return templates.TemplateResponse("login.html", {"request" : request})

@router.get("/register-page")
def render_register_page(request : Request):
    return templates.TemplateResponse("register.html", {"request" : request})
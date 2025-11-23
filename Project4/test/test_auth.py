# In-built packages (Standard Library modules)
from os import environ
from dotenv import load_dotenv
from datetime import timedelta, datetime, timezone

# External packages
import pytest
from jose import jwt
from fastapi import HTTPException, status

# Our Own Imports
from app.config import ALGORITHM, get_current_user
from test.utils import TestingSessionLocal, client, test_user
from app.routers.auth import authenticate_user, create_access_token

# Load environment variables from .env file
load_dotenv()

# ============================================== TEST #1 ====================================================== #
def test_read_all_authenticated_users(test_user):
    """
    Test: GET /auth/users
    - Should return a list of all users
    - For simplicity, we remove the auto-generated 'id'
    """
    
    # Simulate HTTP GET request
    response = client.get("/auth/users")
    
    # Ensure endpoint returned 200 OK
    assert response.status_code == status.HTTP_200_OK
    
    # Remove unpredictable "id" before comparison
    data = response.json()
    for item in data:
        item.pop("id", None)
        item.pop("hashed_password", None)
    
    # Expected response
    expected = [{
        "username" : "Wolverine1310", 
        "first_name" : "Siddharth", 
        "last_name" : "Singh", 
        "is_active" : True, 
        "phone_number" : "7355208142", 
        "email" : "siddharthwolverine@gmail.com", 
        "role" : "admin"
    }]
    
    assert data == expected


# ============================================== TEST #2 ====================================================== #
def test_authenticate_user(test_user):
    user_name = test_user.username

    
    with TestingSessionLocal() as db:
        authenticated_user = authenticate_user(user_name, "abcdefgh", db)
        assert authenticated_user is not None
        assert authenticated_user.username == user_name
        
        non_existent_user = authenticate_user("Wrong_User_Name", "abcdefgh", db)
        assert non_existent_user is False
        
        wrong_password_user = authenticate_user(user_name, "Wrong_password", db)
        assert wrong_password_user is False


# ============================================== TEST #3 ====================================================== #
def test_create_access_token(test_user):
    user_name = test_user.username
    user_id = test_user.id
    user_role = test_user.role
    
    token = create_access_token(user_name, user_id, user_role, timedelta(minutes = 20))
    decoded_token = jwt.decode(token = token, key = environ.get("SECRET_KEY", ""), algorithms = ALGORITHM)
    
    assert decoded_token.get("sub") == user_name
    assert decoded_token.get("id") == user_id
    assert decoded_token.get("user_role") == user_role


# ============================================== TEST #4 ====================================================== #
@pytest.mark.asyncio
async def test_get_current_user_valid_token(test_user):
    user_name = test_user.username
    user_id = test_user.id
    user_role = test_user.role
    
    token = create_access_token(user_name, user_id, user_role, timedelta(minutes = 20))
    user = await get_current_user(token)
    
    assert user == {"username" : user_name, "id" : user_id, "user_role" : user_role}


# ============================================== TEST #5 ====================================================== #
@pytest.mark.asyncio
async def test_get_current_user_missing_payload(test_user):
    user_name = test_user.username
    encode = {"sub" : user_name}
    expires = datetime.now(timezone.utc) + timedelta(minutes = 20)
    
    encode.update({"exp" : expires})
    token = jwt.encode(claims = encode, key = environ.get("SECRET_KEY", ""), algorithm = ALGORITHM)
    
    with pytest.raises(HTTPException) as exception_info:
        await get_current_user(token)
    
    assert exception_info.value.status_code == 401
    assert exception_info.value.detail == "Could not validate user."



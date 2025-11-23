# In-built packages (Standard Library modules)

# External packages
from fastapi import status

# Our Own Imports
from app.models import Users
from test.utils import client, TestingSessionLocal, test_user, test_user_and_todo, bcrypt_context


# ============================================== TEST #1 ====================================================== #
def test_get_current_user_details(test_user):
    # Simulate HTTP GET request
    response = client.get("/users/get_user")
    
    # Ensure endpoint returned 200 OK
    assert response.status_code == status.HTTP_200_OK
    
    # API returns a single dictionary (not a list)
    data = response.json()
    
    # Remove fields that change automatically
    data.pop("id", None)
    data.pop("hashed_password", None)
    
    # Expected response
    expected = {
        "username" : "Wolverine1310", 
        "first_name" : "Siddharth", 
        "last_name" : "Singh", 
        "is_active" : True, 
        "phone_number" : "7355208142", 
        "email" : "siddharthwolverine@gmail.com", 
        "role" : "admin"
    }
    
    assert data == expected


# ============================================== TEST #2 ====================================================== #
def test_change_password(test_user):
    created_id = test_user.id
    
    payload_change_password = {
        "old_password" : "abcdefgh", 
        "new_password" : "Sid1412@", 
        "confirm_new_password" : "Sid1412@"
    }
    
    # Simulate HTTP POST request
    response = client.post("/users/change_password", json = payload_change_password)
    
    # Basic response checks
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data == {"message" : "Password updated successfully.", "id" : created_id}
    
    # --- DB Verification ---
    with TestingSessionLocal() as db:
        updated_todo = db.get(Users, created_id)  
        assert updated_todo is not None
        assert bcrypt_context.verify(payload_change_password["confirm_new_password"], updated_todo.hashed_password) is True


# ============================================== TEST #3 ====================================================== #
def test_update_user(test_user):
    created_id = test_user.id
    
    payload_update_user = {
        "email" : "srishti1412@gmail.com", 
        "username" : "Srishti1412@", 
        "first_name" : "Srishti", 
        "last_name" : "Singh", 
        "role" : "Normal-User", 
        "phone_number" : "1234567890"
    }
    
    # Simulate HTTP PUT request
    response = client.put(f"/users/user/{created_id}", json = payload_update_user)
    
    # Basic response checks
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data == {"message" : "User details updated successfully", "id" : created_id}
    
    # --- DB Verification ---
    with TestingSessionLocal() as db:
        updated_user = db.get(Users, created_id)  
        assert updated_user is not None
        
        for field, value in payload_update_user.items():
            assert getattr(updated_user, field) == value
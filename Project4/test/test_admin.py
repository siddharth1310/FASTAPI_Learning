# In-built packages (Standard Library modules)

# External packages
from fastapi import status

# Our Own Imports
from app.models import Users
from test.utils import client, TestingSessionLocal, test_user, test_user_and_todo


# ============================================== TEST #1 ====================================================== #
def test_read_all_users(test_user):
    # Simulate HTTP GET request
    response = client.get("/admin/users")
    
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
def test_create_user(test_user):
    payload = {
        "email" : "srishti1412@gmail.com", 
        "username" : "Srishti1412@", 
        "first_name" : "Srishti", 
        "last_name" : "Singh", 
        "password" : "Sid1310@", 
        "role" : "Normal-User", 
        "phone_number" : "1234567890"
    }
    
    # Create user
    response = client.post("/admin/user", json = payload)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["message"] == "User created successfully"
    assert isinstance(data.get("id"), int)
    
    created_id = data["id"]
    
    # Verify in DB
    with TestingSessionLocal() as db:
        saved_user = db.get(Users, created_id)
        assert saved_user is not None
        
        # Fields to validate (exclude password because DB stores hashed_password)
        expected_fields = {key : value for key, value in payload.items() if key != "password"}
        
        for field, value in expected_fields.items():
            assert getattr(saved_user, field) == value


# ============================================== TEST #3 ====================================================== #
def test_update_user(test_user):
    user_id = test_user.id
    
    payload = {
        "email" : "srishti1412@gmail.com", 
        "username" : "Srishti1412@", 
        "first_name" : "Srishti", 
        "last_name" : "Singh", 
        "role" : "Normal-User", 
        "phone_number" : "1234567890"
    }
    
    # Simulate HTTP PUT request
    response = client.put(f"/admin/user/{user_id}", json = payload)
    
    # API Response checks
    assert response.status_code == status.HTTP_200_OK
    
    assert response.json() == {
        "message" : "User details updated successfully", 
        "id" : user_id
        }
    
    # Verify in DB using a fresh session
    with TestingSessionLocal() as db:
        updated_user = db.get(Users, user_id)
        assert updated_user is not None
        
        for field, value in payload.items():
            assert getattr(updated_user, field) == value


# ============================================== TEST #4 ====================================================== #
def test_update_user_not_found(test_user):
    # Fixture ensures this new ID does not exist
    non_existent_user_id = test_user.id + 1
    
    payload = {
        "email" : "srishti1412@gmail.com", 
        "username" : "Srishti1412@", 
        "first_name" : "Srishti", 
        "last_name" : "Singh", 
        "role" : "Normal-User", 
        "phone_number" : "1234567890"
    }
    
    # Simulate HTTP GET request
    response = client.put(f"/admin/user/{non_existent_user_id}", json = payload)
    
    # API Response checks
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "error" : {
            "type" : "HTTPException", 
            "message" : "User Not Found.", 
            "path" : f"http://testserver/admin/user/{non_existent_user_id}"
            }
        }


# ============================================== TEST #5 ====================================================== #
def test_delete_user(test_user):
    payload = {
        "email" : "srishti1412@gmail.com", 
        "username" : "Srishti1412@", 
        "first_name" : "Srishti", 
        "last_name" : "Singh", 
        "password" : "Sid1310@", 
        "role" : "Normal-User", 
        "phone_number" : "1234567890"
    }
    
    # 1. Create the user
    response = client.post("/admin/user", json = payload)
    assert response.status_code == status.HTTP_201_CREATED
    
    created_id = response.json()["id"]
    
    # 2. Delete the user
    response = client.delete(f"/admin/user/{created_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message" : "User details deleted successfully", 
        "id" : created_id
        }
    
    # 3. Verify deletion from DB using fresh session
    with TestingSessionLocal() as db:
        deleted_user = db.get(Users, created_id)
        assert deleted_user is None


# ============================================== TEST #6 ====================================================== #
def test_delete_user_not_found(test_user):
    payload = {
        "email" : "srishti1412@gmail.com", 
        "username" : "Srishti1412@", 
        "first_name" : "Srishti", 
        "last_name" : "Singh", 
        "password" : "Sid1310@", 
        "role" : "Normal-User", 
        "phone_number" : "1234567890"
    }
    
    # 1. Create the user
    response = client.post("/admin/user", json = payload)
    assert response.status_code == status.HTTP_201_CREATED
    
    created_id = response.json()["id"]
    
    # 2. Delete the user
    response = client.delete(f"/admin/user/{created_id + 1}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "error" : {
            "type" : "HTTPException", 
            "message" : "User ID Not Found", 
            "path" : f"http://testserver/admin/user/{created_id + 1}"
            }
        }
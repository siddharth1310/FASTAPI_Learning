# In-built packages (Standard Library modules)

# External packages
from fastapi import status

# Our Own Imports
from test.utils import client, test_user


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
# In-built packages (Standard Library modules)

# External packages
from fastapi import status

# Our Own Imports
from app.models import Todos
from test.utils import client, TestingSessionLocal, test_user, test_user_and_todo


# ============================================== TEST #1 ====================================================== #
def test_read_all_todos(test_user_and_todo):
    response = client.get("/todo/")
    assert response.status_code == status.HTTP_200_OK
    
    # Remove unpredictable fields
    data = response.json()
    for item in data:
        item.pop("id", None)
        item.pop("owner_id", None)
    
    expected = [{
        "title" : "FASTAPI COURSE - Udemy", 
        "description" : "Complete FASTAPI Course by December 2025", 
        "priority" : 5, 
        "complete" : False, 
    }]
    
    assert data == expected


# ============================================== TEST #2 ====================================================== #
def test_read_one_todos(test_user_and_todo):
    # Get actual auto-generated ID from fixture
    todo_id = test_user_and_todo.id
    
    # Call the API endpoint dynamically using the correct ID
    response = client.get(f"/todo/read_todo/{todo_id}")
    assert response.status_code == status.HTTP_200_OK
    
    # API returns a single dictionary (not a list)
    data = response.json()
    
    # Remove fields that change automatically
    data.pop("id", None)
    data.pop("owner_id", None)
    
    expected = {
        "title" : "FASTAPI COURSE - Udemy", 
        "description" : "Complete FASTAPI Course by December 2025", 
        "priority" : 5, 
        "complete" : False
    }
    
    assert data == expected


# ============================================== TEST #3 ====================================================== #
def test_read_one_todos_not_found(test_user_and_todo):
    # Fixture ensures this new ID does not exist
    non_existent_id = test_user_and_todo.id + 1
    
    response = client.get(f"/todo/read_todo/{non_existent_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    assert response.json() == {
        "error" : {
            "type" : "HTTPException", 
            "message" : "Todo Not Found.", 
            "path" : f"http://testserver/todo/read_todo/{non_existent_id}"
            }
        }


# ============================================== TEST #4 ====================================================== #
def test_create_todo(test_user):
    payload = {
        "title" : "Learn Pytest", 
        "description" : "Write unit tests for todo creation", 
        "priority" : 3, 
        "complete" : False 
    }
    
    # Create TODO
    response = client.post("/todo/create_todo/", json = payload)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["message"] == "Todo item created successfully"
    assert isinstance(data.get("id"), int)
    
    todo_id = data["id"]
    
    # Verify in DB
    with TestingSessionLocal() as db:
        saved_todo = db.get(Todos, todo_id)
        assert saved_todo is not None
        
        # Validate all fields from payload
        for field, value in payload.items():
            assert getattr(saved_todo, field) == value
            
        # Validate owner
        assert saved_todo.owner_id == test_user.id


# ============================================== TEST #5 ====================================================== #
def test_update_todo(test_user_and_todo):
    todo = test_user_and_todo
    todo_id = todo.id
    
    payload = {
        "title" : "Learn Pytest", 
        "description" : "Write unit tests for todo creation", 
        "priority" : 3, 
        "complete" : True 
    }
    
    # API call
    response = client.put(f"/todo/update_todo/{todo_id}", json = payload)
    
    # Basic response checks
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data == {
        "message" : "Todo item details updated successfully",
        "id" : todo_id
    }
    
    # --- DB Verification ---
    with TestingSessionLocal() as db:
        updated_todo = db.get(Todos, todo_id)  
        assert updated_todo is not None
        
        # Validate all fields from payload
        for field, value in payload.items():
            assert getattr(updated_todo, field) == value
        
        assert updated_todo.owner_id == todo.owner_id


# ============================================== TEST #6 ====================================================== #
def test_update_todo_not_found(test_user_and_todo):
    # Fixture ensures this new ID does not exist
    non_existent_id = test_user_and_todo.id + 1
    
    payload = {
        "title" : "Learn Pytest",
        "description" : "Write unit tests for todo creation",
        "priority" : 3,
        "complete" : True
    }
    
    response = client.put(f"/todo/update_todo/{non_existent_id}", json = payload)
    
    # API Response checks
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "error" : {
            "type" : "HTTPException", 
            "message" : "Todo Not Found.", 
            "path" : f"http://testserver/todo/update_todo/{non_existent_id}"
            }
        }


# ============================================== TEST #7 ====================================================== #
def test_delete_todo(test_user_and_todo): 
    todo = test_user_and_todo
    todo_id = todo.id
    
    # --- API Call ---
    response = client.delete(f"/todo/delete_todo/{todo_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # --- Response Checks ---
    assert data == {
        "message": "Todo deleted successfully",
        "id": todo_id
    }
    
    # --- DB Verification ---
    with TestingSessionLocal() as db:
        deleted_todo = db.get(Todos, todo_id)
        assert deleted_todo is None


# ============================================== TEST #8 ====================================================== #
def test_delete_todo_not_found(test_user_and_todo):
    # Fixture ensures this new ID does not exist
    non_existent_id = test_user_and_todo.id + 1
    
    # Call API
    response = client.delete(f"/todo/delete_todo/{non_existent_id}")
    
    # API Response checks
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "error" : {
            "type" : "HTTPException", 
            "message" : "Todo Not Found.", 
            "path" : f"http://testserver/todo/delete_todo/{non_existent_id}"
            }
        }
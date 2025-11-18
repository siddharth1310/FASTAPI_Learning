# In-built packages (Standard Library modules)

# External packages
from starlette import status
from fastapi import HTTPException, Path, APIRouter

# Our Own Imports
from app.models import Users
from app.schemas import User_Update_Request_Body, User_Request_Body
from app.config import user_dependency, db_dependency,bcrypt_context

router = APIRouter(prefix = "/admin", tags = ["admin"])


@router.get("/users/", status_code = status.HTTP_200_OK)
async def read_all(user : user_dependency, db : db_dependency):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    if user.get("user_role") != "admin":
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Access Denied - Admin Privilege Required")
    
    return db.query(Users).all()


@router.post("/user/", status_code = status.HTTP_201_CREATED)
async def create_user(user : user_dependency, db : db_dependency, user_request : User_Request_Body):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    if user.get("user_role") != "admin":
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Access Denied - Admin Privilege Required")
    
    user_model_object = Users(email = user_request.email, 
                              username = user_request.username, 
                              first_name = user_request.first_name, 
                              last_name = user_request.last_name, 
                              hashed_password = bcrypt_context.hash(user_request.password), 
                              is_active = True, 
                              role = user_request.role)
    
    db.add(user_model_object)
    db.commit()
    
    return {"message" : "User created successfully"}


@router.put("/user/{user_id}", status_code = status.HTTP_200_OK)
async def update_user(user : user_dependency, 
                      db : db_dependency, 
                      user_request : User_Update_Request_Body, 
                      user_id : int = Path(gt = 0, description = "Primary key of the entry in User Table.")):
    # Authentication check
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    # Authorization check
    if user.get("user_role") != "admin":
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Access Denied - Admin Privilege Required")
    
    # Fetch user
    user_model_object = db.query(Users).filter(Users.id == user_id).first()
    
    if not user_model_object:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User Not Found.")
    
    # Update only provided fields
    update_data = user_request.model_dump(exclude_unset = True)
    for field, value in update_data.items():
        setattr(user_model_object, field, value)
    
    db.commit()
    return {"message" : "User details updated successfully"}


@router.post("/user/{user_id}", status_code = status.HTTP_200_OK)
async def delete_user(user : user_dependency, 
                      db : db_dependency, 
                      user_id : int = Path(gt = 0, description = "User ID that has to be deleted.")):
    # Authentication check
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    # Authorization check
    if user.get("user_role") != "admin":
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Access Denied - Admin Privilege Required")
    
    # Fetch user
    user_model_object = db.query(Users).filter(Users.id ==user_id).first()
    
    if user_model_object is not None:
        db.query(Users).filter(Users.id == user_id).delete()
        db.commit()
        return {"message" : "User details deleted successfully"}
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User ID Not Found")
# In-built packages (Standard Library modules)

# External packages
from starlette import status
from fastapi import APIRouter, HTTPException, Path

# Our Own Imports
from app.models import Users
from app.routers.auth import authenticate_user
from app.schemas import ChangePassword, User_Update_Request_Body, User_Request_Body
from app.config import db_dependency, bcrypt_context, user_dependency


router = APIRouter(prefix = "/users", tags = ["users"])

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_user(db : db_dependency, user_request : User_Request_Body):
    user_model_object = Users(email = user_request.email, 
                              username = user_request.username, 
                              first_name = user_request.first_name, 
                              last_name = user_request.last_name, 
                              hashed_password = bcrypt_context.hash(user_request.password), 
                              is_active = True, 
                              role = user_request.role, 
                              phone_number = user_request.phone_number
                              )
    
    db.add(user_model_object)
    db.commit()
    
    return {"message" : "User created successfully"}


@router.get("/get_user", status_code = status.HTTP_200_OK)
async def get_current_user_details(user : user_dependency, db : db_dependency):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.post("/change_password", status_code = status.HTTP_200_OK)
async def change_password(user : user_dependency, db : db_dependency, change_password_payload : ChangePassword):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    user = authenticate_user(user.get("username"), change_password_payload.old_password, db)
    
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate user.")
    else:
        if change_password_payload.new_password == change_password_payload.confirm_new_password:
            user.hashed_password = bcrypt_context.hash(change_password_payload.confirm_new_password)
            db.add(user)
            db.commit()
            return {"message" : "Password updated successfully."}
        else:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "New passwords do not match.")


@router.put("/user/{user_id}", status_code = status.HTTP_200_OK)
async def update_user(user : user_dependency, 
                      db : db_dependency, 
                      user_request : User_Update_Request_Body, 
                      user_id : int = Path(gt = 0, description = "Primary key of the entry in User Table.")):
    # 1. Authentication
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    # 2. Authorization
    if user.get("id") != user_id:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Access Denied. You can only make changes to your user account.")
    
    # 3. Fetch user
    user_obj = db.query(Users).filter(Users.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User Not Found.")
    
    # 4. Apply partial update (automatic field mapping)
    update_data = user_request.model_dump(exclude_unset = True)
    for field, value in update_data.items():
        setattr(user_obj, field, value)
    
    db.commit()
    
    return {"message" : "User details updated successfully"}
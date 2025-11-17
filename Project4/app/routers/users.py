from fastapi import  APIRouter, HTTPException, Path
from app.models import Users
from starlette import status
from app.schemas import User_Update_Request_Body, UserRequest
from app.config import db_dependency, bcrypt_context, user_dependency

router = APIRouter(prefix = "/users", tags = ["users"])

@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_user(db : db_dependency, user_request : UserRequest):
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


@router.put("/user/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def update_user(user : user_dependency, 
                      db : db_dependency, 
                      user_request : User_Update_Request_Body, 
                      user_id : int = Path(gt = 0, description = "Primary key of the entry in User Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    if user.get("id") != user_id:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Access Denied. You can only make changes to your user account.")
    
    user_model_object = db.query(Users).filter(Users.id == user_id).first()
    
    if user_model_object is not None:
        user_model_object.email = user_request.email if user_request.email else user_model_object.email
        user_model_object.username = user_request.username if user_request.username else user_model_object.username
        user_model_object.first_name = user_request.first_name if user_request.first_name else user_model_object.first_name    
        user_model_object.last_name = user_request.last_name if user_request.last_name else user_model_object.last_name 
        user_model_object.role = user_request.role if user_request.role else user_model_object.role
        
        db.add(user_model_object)
        db.commit()
        
        return {"message" : "User details updated successfully"}    
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User Not Found.")
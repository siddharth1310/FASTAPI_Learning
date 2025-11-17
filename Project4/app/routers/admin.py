from fastapi import  APIRouter
from app.models import Users
from fastapi import HTTPException, Path
from starlette import status
from app.schemas import User_Update_Request_Body, UserRequest
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
async def create_user(user : user_dependency, db : db_dependency, user_request : UserRequest):
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


@router.put("/user/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
async def update_user(user : user_dependency, 
                      db : db_dependency, 
                      user_request : User_Update_Request_Body, 
                      user_id : int = Path(gt = 0, description = "Primary key of the entry in User Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    if user.get("user_role") != "admin":
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Access Denied - Admin Privilege Required")
    
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


@router.post("/user/{user_id}", status_code = status.HTTP_200_OK)
async def delete_user(user : user_dependency, 
                      db : db_dependency, 
                      user_id : int = Path(gt = 0, description = "User ID that has to be deleted.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    if user.get("user_role") != "admin":
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Access Denied - Admin Privilege Required")
    
    user_model_object = db.query(Users).filter(Users.id ==user_id).first()
    
    if user_model_object is not None:
        db.query(Users).filter(Users.id == user_id).delete()
        db.commit()
        return {"message" : "User details deleted successfully"}
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User ID Not Found")


# @router.delete("/todo/{todo_id}", status_code = status.HTTP_200_OK)
# async def delete_todo(user : user_dependency, 
#                       db : db_dependency, 
#                       todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
#     if user is None:
#         raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
#     if user.get("user_role") != "admin":
#         raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Access Denied - Admin Privilege Required")
#     todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
#     if todo_model is not None:
#         db.query(Todos).filter(Todos.id == todo_id).delete()
#         db.commit()
#     else:
#         raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")
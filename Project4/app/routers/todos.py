# In-built packages (Standard Library modules)

# External packages
from starlette import status
from fastapi import  APIRouter
from fastapi import HTTPException, Path

# Our Own Imports
from app.models import Todos
from app.config import user_dependency, db_dependency
from app.schemas import TodoRequest

router = APIRouter(prefix = "/todo", tags = ["todo"])


@router.get("/", status_code = status.HTTP_200_OK)
async def read_all(user : user_dependency, db : db_dependency):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    if user.get("user_role") != "admin":
        return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
    else:
        return db.query(Todos).all()


@router.get("/read_todo/{todo_id}", status_code = status.HTTP_200_OK)
async def read_todo(user : user_dependency, 
                    db : db_dependency, 
                    todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")
    
    if user.get("user_role") != "admin" and todo.owner_id != user.get("id"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You are not allowed to view this todo.")
    
    return todo


@router.post("/create_todo/", status_code = status.HTTP_201_CREATED)
async def create_todo(user : user_dependency, db : db_dependency, todo_request : TodoRequest):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get("id"))
    
    db.add(todo_model)
    db.commit()
    
    return {"message" : "Todo item created successfully"}


@router.put("/update_todo/{todo_id}", status_code = status.HTTP_200_OK)
async def update_todo(user : user_dependency, 
                      db : db_dependency, 
                      todo_request : TodoRequest, 
                      todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")
    
    if user.get("user_role") != "admin" and todo.owner_id != user.get("id"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You are not allowed to update this todo.")
    
    for field, value in todo_request.model_dump().items():
        setattr(todo, field, value)
    
    db.commit()
    
    return {"message" : "Todo item details updated successfully"}


@router.delete("/delete_todo/{todo_id}", status_code = status.HTTP_200_OK)
async def delete_todo(user : user_dependency,
                      db : db_dependency,
                      todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")
    
    if user.get("user_role") == "admin":
        pass
    elif todo.owner_id != user.get("id"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You are not allowed to delete this todo.")
    
    db.delete(todo)
    db.commit()
    
    return {"message" : "Todo deleted successfully"}

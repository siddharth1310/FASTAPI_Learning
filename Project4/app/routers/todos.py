from fastapi import  APIRouter
from app.models import Todos
from fastapi import HTTPException, Path
from starlette import status
from pydantic import BaseModel, Field
from app.config import user_dependency, db_dependency

router = APIRouter()

class TodoRequest(BaseModel):
    title : str = Field(min_length = 3)
    description : str = Field(min_length = 3, max_length = 100)
    priority : int = Field(gt = 0, lt = 6)
    complete : bool


@router.get("/", status_code = status.HTTP_200_OK)
async def read_all(user : user_dependency, db : db_dependency):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/todo/{todo_id}", status_code = status.HTTP_200_OK)
async def read_todo(user : user_dependency, 
                    db : db_dependency, 
                    todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")


@router.post("/todo/", status_code = status.HTTP_201_CREATED)
async def create_todo(user : user_dependency, db : db_dependency, todo_request : TodoRequest):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code = status.HTTP_204_NO_CONTENT)
async def update_todo(user : user_dependency, 
                      db : db_dependency, 
                      todo_request : TodoRequest, 
                      todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete
        db.add(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")


@router.delete("/todo/{todo_id}", status_code = status.HTTP_200_OK)
async def delete_todo(user : user_dependency, 
                      db : db_dependency, 
                      todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
        db.commit()
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")

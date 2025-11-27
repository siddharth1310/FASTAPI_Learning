# In-built packages (Standard Library modules)

# External packages
from starlette import status
from fastapi import  APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import HTTPException, Path, Request

# Our Own Imports
from app.models import Todos
from app.schemas import TodoRequest
from app.config import get_current_user, user_dependency, db_dependency

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
    
    todo = db.get(Todos, todo_id)
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")
    
    if user.get("user_role") != "admin" and todo.owner_id != user.get("id"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You are not allowed to view this todo.")
    
    return todo


@router.post("/create_todo/", status_code = status.HTTP_201_CREATED)
async def create_todo(user : user_dependency, db : db_dependency, todo_request : TodoRequest):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    todo = Todos(**todo_request.model_dump(), owner_id = user.get("id"))
    
    db.add(todo)
    db.commit()
    
    db.refresh(todo)  # IMPORTANT → loads the assigned ID
    
    return {"message" : "Todo item created successfully", "id" : todo.id}


@router.put("/update_todo/{todo_id}", status_code = status.HTTP_200_OK)
async def update_todo(user : user_dependency, 
                      db : db_dependency, 
                      todo_request : TodoRequest, 
                      todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    todo = db.get(Todos, todo_id)
    
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")
    
    if user.get("user_role") != "admin" and todo.owner_id != user.get("id"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You are not allowed to update this todo.")
    
    for field, value in todo_request.model_dump().items():
        setattr(todo, field, value)
    
    db.commit()
    
    db.refresh(todo)  # IMPORTANT → loads the assigned ID
    
    return {"message" : "Todo item details updated successfully", "id" : todo.id}


@router.delete("/delete_todo/{todo_id}", status_code = status.HTTP_200_OK)
async def delete_todo(user : user_dependency,
                      db : db_dependency,
                      todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Authentication Failed")
    
    todo = db.get(Todos, todo_id)
    
    if not todo:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Todo Not Found.")
    
    if user.get("user_role") == "admin":
        pass
    elif todo.owner_id != user.get("id"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You are not allowed to delete this todo.")
    
    db.delete(todo)
    db.commit()
    
    return {"message" : "Todo deleted successfully", "id" : todo.id}

templates = Jinja2Templates(directory = "templates")


def redirect_to_login():
    redirect_response = RedirectResponse(url = "/auth/login-page", status_code = status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key = "access_token")
    return redirect_response


@router.get("/todo-page")
async def render_todo_page(request : Request, db : db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
        return templates.TemplateResponse("todo.html", {"request" : request, "todos" : todos, "user" : user})
    except Exception as e:
        return redirect_to_login()


@router.get("/register-page")
async def render_register_page(request : Request):
    return templates.TemplateResponse("register.html", {"request" : request})


@router.get("/add-todo-page")
async def render_add_todo_page(request : Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse("add-todo.html", {"request" : request, "user" : user})
    except Exception as e:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request : Request, db : db_dependency, todo_id : int = Path(gt = 0, description = "Primary key of the entry in TODO Table.")):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todo = db.get(Todos, todo_id)
        return templates.TemplateResponse("edit-todo.html", {"request" : request, "todo" : todo, "user" : user})
    except Exception as e:
        return redirect_to_login()

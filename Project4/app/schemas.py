# In-built packages (Standard Library modules)
from typing import Optional

# External packages
from pydantic import BaseModel, Field, model_validator

# Our Own Imports


class Token(BaseModel):
    access_token : str
    token_type : str


class TodoRequest(BaseModel):
    title : str = Field(min_length = 3)
    description : str = Field(min_length = 3, max_length = 100)
    priority : int = Field(gt = 0, lt = 6)
    complete : bool


class ChangePassword(BaseModel):
    old_password : str
    new_password : str
    confirm_new_password : str
    
    @model_validator(mode = "after")
    def validate_passwords(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("New password and confirmation password do not match.")
        return self



class User_Request_Body(BaseModel):
    email : str = Field(min_length = 3)
    username : str = Field(min_length = 3, max_length = 255)
    first_name : str = Field(min_length = 3, max_length = 255)
    last_name : str = Field(min_length = 3, max_length = 255)
    password : str
    role : str
    
    model_config = {
        "json_schema_extra" : {
            "example" : {
                "email" : "siddharth13101999singh@gmail.com",
                "username" : "Wolverine1310",
                "first_name" : "Siddharth",
                "last_name" : "Singh",
                "password" : "Sid1310@",
                "role" : "Admin"
            }
        }
    }


class User_Update_Request_Body(BaseModel):
    email : Optional[str] = Field(default = None, min_length = 3)
    username : Optional[str] = Field(default = None, min_length = 3, max_length = 255)
    first_name : Optional[str] = Field(default = None, min_length = 3, max_length = 255)
    last_name : Optional[str] = Field(default = None, min_length = 3, max_length = 255)
    role : Optional[str] = Field(default = None, min_length = 3, max_length = 255)
    
    model_config = {
        "json_schema_extra" : {
            "example" : {
                "email" : "siddharthwolverine@gmail.com",
                "username" : "Wolverine13101999",
                "first_name" : "Siddharth",
                "last_name" : "Singh",
                "role" : "admin"
            }
        }
    }
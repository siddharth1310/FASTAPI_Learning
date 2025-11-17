from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    access_token : str
    token_type : str

class UserRequest(BaseModel):
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
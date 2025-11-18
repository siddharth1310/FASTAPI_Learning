# In-built packages (Standard Library modules)
from typing import Annotated

# External packages
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy import Boolean, String, VARCHAR, Integer, ForeignKey

# Our Own Imports


int_pk = Annotated[int, mapped_column(Integer, primary_key = True, index = True)]

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"
    
    id : Mapped[int_pk]
    email : Mapped[str] = mapped_column(String(255), unique = True)
    username : Mapped[str] = mapped_column(String(255), unique = True)
    first_name : Mapped[str] = mapped_column(String(255))
    last_name : Mapped[str] = mapped_column(String(255))
    hashed_password : Mapped[str] = mapped_column(String)
    is_active : Mapped[bool] = mapped_column(Boolean, default = True)
    role : Mapped[str] = mapped_column(String)

class Todos(Base):
    __tablename__ = "todos"
    
    id : Mapped[int_pk]
    title : Mapped[str] = mapped_column(String(255))
    description : Mapped[str] = mapped_column(VARCHAR(2048))
    priority : Mapped[int] = mapped_column(Integer)
    complete : Mapped[bool] = mapped_column(Boolean, default = False)
    owner_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete = "CASCADE"))
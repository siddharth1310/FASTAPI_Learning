from typing_extensions import Annotated
from sqlalchemy import String, VARCHAR, Integer
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

int_pk = Annotated[int, mapped_column(Integer, primary_key = True, index = True)]

class Base(DeclarativeBase):
    pass

class KnowledgeBase (Base):
    __tablename__ = "todos"
    
    id : Mapped[int_pk]
    title : Mapped[str] = mapped_column(String(255))
    description : Mapped[str] = mapped_column(VARCHAR(2048))
    priority : Mapped[int] = mapped_column(int) 
    complete : Mapped[bool] = mapped_column(bool, default = False)
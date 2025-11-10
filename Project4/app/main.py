from .models import Base
from fastapi import FastAPI
from .database import engine

app = FastAPI()

Base.metadata.create_all(bind = engine)
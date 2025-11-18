# In-built packages (Standard Library modules)

# External packages
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Our Own Imports


SQLALCHEMY_DATABASE_URL = "sqlite:///./todos_app_database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args = {"check_same_thread" : False})

SessionLocal = sessionmaker(bind = engine, autoflush = False)

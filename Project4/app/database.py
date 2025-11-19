# In-built packages (Standard Library modules)
from os import environ

# External packages
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, URL

# Our Own Imports

load_dotenv()


#----------------------------FOR CONNECTING TO SQLITE-------------------------------------------#

# SQLALCHEMY_DATABASE_URL = "sqlite:///./todos_app_database.db"

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args = {"check_same_thread" : False})

# SessionLocal = sessionmaker(bind = engine, autoflush = False)


#---------------------------FOR CONNECTING TO POSTGRESQL----------------------------------------#

url = URL.create(drivername = environ.get("POSTGRES_DRIVER", ""), 
                 username = environ.get("POSTGRES_USER", ""), 
                 password = environ.get("POSTGRES_PASSWORD", ""), 
                 host = environ.get("POSTGRES_DATABASE_HOST", ""), 
                 database = environ.get("POSTGRES_DATABASE", ""), 
                 port = environ.get("POSTGRES_DATABASE_PORT_NO", ""), 
                 query = {"options" : f"-c search_path={environ.get("POSTGRES_SCHEMA", "")}"}
                 ).render_as_string(hide_password = False)

engine = create_engine(url)

SessionLocal = sessionmaker(bind = engine, autoflush = False)

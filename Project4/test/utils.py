# In-built packages (Standard Library modules)
from os import environ

# External packages
import pytest
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, URL, text

# Our Own Imports
from app.main import app
from app.models import Base, Todos, Users
from app.config import get_db, get_current_user, bcrypt_context

# Load environment variables from .env file
load_dotenv()

# ============================================ DATABASE SETUP ================================================== #
# You have two DB options:
#   (1) SQLite  → good for quick tests
#   (2) PostgreSQL → recommended for realistic behavior (FK checks, constraints)

# ============================================ FOR CONNECTING TO SQLITE ======================================== #

# SQLALCHEMY_DATABASE_URL = "sqlite:///./todos_test_app_database.db"

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args = {"check_same_thread" : False}, poolclass = StaticPool)

# ============================================ FOR CONNECTING TO POSTGRESQL ==================================== #

# Create proper database URL (includes schema override for TESTING schema)
# URL.create() is safer than manual string building.
url = URL.create(drivername = environ.get("POSTGRES_DRIVER", ""), 
                 username = environ.get("POSTGRES_USER", ""), 
                 password = environ.get("POSTGRES_PASSWORD", ""), 
                 host = environ.get("POSTGRES_DATABASE_HOST", ""), 
                 database = environ.get("POSTGRES_DATABASE", ""), 
                 port = environ.get("POSTGRES_DATABASE_PORT_NO", ""), 
                 # Force PostgreSQL to use TEST schema for isolation
                 query = {"options" : f"-c search_path={environ.get("POSTGRES_SCHEMA_TEST", "")}"}
                 ).render_as_string(hide_password = False)

# SQLAlchemy engine for test database
engine = create_engine(url)

# Create tables inside the TEST schema
Base.metadata.create_all(bind = engine)

# ============================================ DB OVERRIDES ==================================================== #
# FastAPI apps normally use "get_db" to get the production DB session.
# During testing, we MUST override that dependency so all test calls use
# this TestingSessionLocal instead.

TestingSessionLocal = sessionmaker(bind = engine, autoflush = False, autocommit = False)

def override_get_db():
    """
    Replaces the real database dependency with a test DB session.
    This ensures all API calls inside the test use TestingSessionLocal.
    """
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    """
    Used to bypass authentication during tests.
    Instead of reading JWT tokens, it returns a hardcoded user.
    """
    
    db = TestingSessionLocal()
    user = db.query(Users).filter(Users.username == "Wolverine1310").first()
    db.close()
    return {"username" : user.username, "id" : user.id, "user_role" : user.role}


# Inject overrides into your FastAPI app
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Client used to call API endpoints as if they were real HTTP requests
client = TestClient(app)

# ============================================== FIXTURES ====================================================== #
# Fixtures run BEFORE a test function and create test data.
# After the test completes, they clean up the database.

# ============================================== FIXTURES #1 =================================================== #
@pytest.fixture
def test_user():
    """
    Creates a temporary user in the database for testing user-related routes.
    This user is automatically deleted after the test.
    """
    
    user_obj = Users(email = "siddharthwolverine@gmail.com", 
                     username = "Wolverine1310", 
                     first_name = "Siddharth", 
                     last_name = "Singh", 
                     hashed_password = bcrypt_context.hash("abcdefgh"), 
                     role = "admin", 
                     phone_number = "7355208142")
    
    db = TestingSessionLocal()
    db.add(user_obj)
    db.commit()
    
    # User is now available inside the test
    yield user_obj
    
    # Cleanup after test is complete
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM Users;"))
        connection.commit()
    db.close()


# ============================================== FIXTURES #2 =================================================== #
@pytest.fixture
def test_user_and_todo():
    """
    Creates:
    - A test user
    - A test todo belonging to that user
    
    After the test, both records are deleted.
    """
    
    db = TestingSessionLocal()
    
    # Step 1 — create user
    user_obj = Users(email = "siddharthwolverine@gmail.com", 
                     username = "Wolverine1310", 
                     first_name = "Siddharth", 
                     last_name = "Singh", 
                     hashed_password = "abcdefgh", 
                     role = "Normal User", 
                     phone_number = "7355208142")
    db.add(user_obj)
    db.flush()  # ensures user_obj.id is assigned BEFORE commit
    
    # Step 2 — create todo linked using user_obj.id
    todo_obj = Todos(title = "FASTAPI COURSE - Udemy", description = "Complete FASTAPI Course by December 2025", 
                     priority = 5, complete = False, owner_id = user_obj.id)
    db.add(todo_obj)
    
    db.commit()
    yield todo_obj
    
    # Cleanup
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos;"))
        conn.execute(text("DELETE FROM users;"))
        conn.commit()
    
    db.close()
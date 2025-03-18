import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db import Base, get_db
import os
import shutil

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL =  "sqlite:///:memory:"

# Create engine with special configuration for in-memory SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool  # Use StaticPool for in-memory database
)

# Create session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up test upload directory
TEST_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_uploads")# os.path.join(os.path.dirname(__file__), "test_uploads")

@pytest.fixture(scope="function")
def upload_dir():
    """Create a temporary upload directory for tests"""
    os.environ["UPLOAD_DIR"] = TEST_UPLOAD_DIR
    os.makedirs(TEST_UPLOAD_DIR, exist_ok=True)
    yield TEST_UPLOAD_DIR
    # Clean up after test
    if os.path.exists(TEST_UPLOAD_DIR):
        shutil.rmtree(TEST_UPLOAD_DIR)

@pytest.fixture(scope="function")
def db_session():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for the test
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    # Clear dependency override after test
    app.dependency_overrides.clear()

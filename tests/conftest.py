import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db import Base, get_db
from app.auth.dependencies import get_current_user, verify_token
from app.customer.models import Customer
import os
import shutil

# 設置測試環境變量
os.environ["TESTING"] = "True"

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


@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for each test."""
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
    
    # 用於存儲當前測試用戶的全局變量
    current_test_user = {"line_id": "admin_test_id"}
    
    # 創建測試用戶並返回該用戶作為認證用戶
    def override_get_current_user():
        user = db_session.query(Customer).filter(Customer.line_id == current_test_user["line_id"]).first()
        if not user:
            # 如果測試用戶不存在，創建一個
            user = Customer(
                line_id=current_test_user["line_id"],
                name="Test User",
                line_name="Test User",
                line_pic_url="http://example.com/pic.jpg"
            )
            db_session.add(user)
            db_session.commit()
        return user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[verify_token] = override_get_current_user
    
    with TestClient(app) as test_client:
        # 添加認證頭部
        test_client.headers.update({"Authorization": f"Bearer {current_test_user['line_id']}"})        
        
        # 添加一個方法來臨時切換認證用戶
        def set_auth_user(line_id):
            current_test_user["line_id"] = line_id
            test_client.headers.update({"Authorization": f"Bearer {line_id}"})
        
        # 將方法附加到測試客戶端
        test_client.set_auth_user = set_auth_user
        
        yield test_client
    
    # Clear dependency override after test
    app.dependency_overrides.clear()

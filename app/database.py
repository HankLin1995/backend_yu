from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
import os

# 從環境變數獲取上傳目錄路徑，如果未設置則使用預設路徑
UPLOAD_DIR = os.getenv('UPLOAD_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

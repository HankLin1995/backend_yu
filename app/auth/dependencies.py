import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.customer.models import Customer

# 根據環境變量決定是否使用測試認證
TESTING = os.getenv("TESTING", "False").lower() == "true"

if TESTING:
    from app.auth.testing import TestHTTPBearer
    security = TestHTTPBearer()
else:
    security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    驗證 Bearer 令牌（LINE userId）並返回對應的用戶
    """
    try:
        token = credentials.credentials  # 獲取 Bearer 後的令牌值
        
        # 驗證令牌（在這個例子中是 LINE userId）
        # 檢查數據庫中是否存在此 userId 的用戶
        user = db.query(Customer).filter(Customer.line_id == token).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID or user not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 返回用戶對象供路由使用
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    獲取當前用戶，如果認證失敗則拋出異常
    """
    return verify_token(credentials, db)

def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security, use_cache=False), 
                      db: Session = Depends(get_db)):
    """
    獲取當前用戶，如果沒有認證則返回 None
    用於某些端點既可以匿名訪問又可以根據用戶提供個性化內容
    """
    try:
        return verify_token(credentials, db)
    except HTTPException:
        return None

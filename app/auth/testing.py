from fastapi.security import HTTPBearer
from typing import Optional

class TestHTTPBearer(HTTPBearer):
    """
    用於測試的 HTTPBearer 認證類，允許跳過認證
    """
    async def __call__(self, request):
        """
        重寫 __call__ 方法，返回一個模擬的認證憑證
        """
        class MockCredentials:
            def __init__(self, credentials: str):
                self.credentials = credentials
                self.scheme = "Bearer"
        
        # 從請求頭中獲取 Authorization
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, credentials = authorization.split()
            return MockCredentials(credentials=credentials)
        
        # 如果沒有 Authorization 頭，返回一個預設的測試用戶 ID
        return MockCredentials(credentials="test_line_id")

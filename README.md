# 濠鮮後端 API

這是濠鮮的後端 API 專案，使用 FastAPI 和 SQLite 資料庫開發。

## 專案結構

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 應用程式
│   ├── database.py      # 資料庫配置
│   ├── models.py        # SQLAlchemy 模型
│   ├── schemas.py       # Pydantic 模型
│   └── crud.py         # CRUD 操作
├── tests/
│   ├── __init__.py
│   ├── conftest.py     # 測試配置
│   └── test_api.py     # API 測試
├── requirements.txt    # 依賴套件
├── Dockerfile         # Docker 配置
└── docker-compose.yml # Docker Compose 配置
```

## 環境要求

- Python 3.11+
- Docker (選用)

## 安裝與執行

### 使用 Docker

1. 建立並啟動應用程式：
```bash
docker-compose up --build
```

2. 執行測試：
```bash
docker-compose run test
```

### 本地開發

1. 建立虛擬環境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 執行應用程式：
```bash
uvicorn app.main:app --reload
```

4. 執行測試：
```bash
pytest
```

## API 文件

啟動應用程式後，可以在以下位置查看 API 文件：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 資料庫

- 正式環境：`app.db`
- 測試環境：`test.db`

## 主要功能

1. 客戶管理
   - 新增客戶
   - 更新客戶資料

2. 商品管理
   - 新增商品
   - 更新商品資訊
   - 設定特價
   - 更新庫存

3. 類別管理
   - 新增商品類別
   - 刪除類別
   - 商品類別關聯

4. 訂單管理
   - 建立訂單
   - 更新訂單狀態
   - 訂單明細管理

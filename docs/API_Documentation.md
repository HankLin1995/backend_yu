## 基本資訊
- Base URL: `http://localhost:8000`
- 所有回應格式均為 JSON
- 所有日期時間格式為 ISO 8601 格式

## 客戶相關 API

### 取得所有客戶
- **端點**: `/customers/`
- **方法**: `GET`
- **回應** (200 OK):
  ```json
  [
    {
      "line_id": "string",
      "line_name": "string",
      "name": "string",
      "line_pic_url": "string",
      "phone": "string",
      "email": "string",
      "address": "string",
      "create_date": "datetime"
    }
  ]
  ```

### 取得單一客戶
- **端點**: `/customers/{line_id}`
- **方法**: `GET`
- **回應** (200 OK):
  ```json
  {
    "line_id": "string",
    "line_name": "string",
    "name": "string",
    "line_pic_url": "string",
    "phone": "string",
    "email": "string",
    "address": "string",
    "create_date": "datetime"
  }
  ```
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Customer not found"
  }
  ```

### 創建客戶
- **端點**: `/customers/`
- **方法**: `POST`
- **請求體**:
  ```json
  {
    "line_id": "string",
    "line_name": "string",
    "name": "string (optional)",
    "line_pic_url": "string (optional)",
    "phone": "string (optional)",
    "email": "string (optional)",
    "address": "string (optional)"
  }
  ```
- **回應** (200 OK):
  ```json
  {
    "line_id": "string",
    "line_name": "string",
    "name": "string",
    "line_pic_url": "string",
    "phone": "string",
    "email": "string",
    "address": "string",
    "create_date": "datetime"
  }
  ```
- **錯誤** (400 Bad Request):
  ```json
  {
    "detail": "Customer already exists"
  }
  ```

### 更新客戶資訊
- **端點**: `/customers/{line_id}`
- **方法**: `PUT`
- **請求體**:
  ```json
  {
    "line_name": "string",
    "name": "string (optional)",
    "line_pic_url": "string (optional)",
    "phone": "string (optional)",
    "email": "string (optional)",
    "address": "string (optional)"
  }
  ```
- **回應** (200 OK): 更新後的客戶資訊
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Customer not found"
  }
  ```

### 刪除客戶
- **端點**: `/customers/{line_id}`
- **方法**: `DELETE`
- **回應** (200 OK):
  ```json
  {
    "message": "Customer deleted successfully"
  }
  ```
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Customer not found"
  }
  ```

## 商品相關 API

### 創建商品
- **端點**: `/products/`
- **方法**: `POST`
- **請求體**:
  ```json
  {
    "product_name": "string",
    "price": "float",
    "description": "string",
    "stock_quantity": "integer",
    "special_price": "float (optional)"
  }
  ```
- **回應** (200 OK):
  ```json
  {
    "product_id": "integer",
    "product_name": "string",
    "price": "float",
    "special_price": "float",
    "description": "string",
    "stock_quantity": "integer",
    "create_time": "datetime",
    "is_deleted": false
  }
  ```

### 獲取商品
- **端點**: `/products/{product_id}`
- **方法**: `GET`
- **回應** (200 OK): 商品詳細資訊，包含類別和照片
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Product not found"
  }
  ```

### 更新商品
- **端點**: `/products/{product_id}`
- **方法**: `PUT`
- **請求體**:
  ```json
  {
    "product_name": "string",
    "price": "float",
    "description": "string",
    "stock_quantity": "integer",
    "special_price": "float (optional)"
  }
  ```
- **回應** (200 OK): 更新後的商品資訊
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Product not found"
  }
  ```

### 更新商品庫存
- **端點**: `/products/{product_id}/stock`
- **方法**: `PUT`
- **請求體**:
  ```json
  {
    "quantity": "integer"
  }
  ```
- **回應** (200 OK): 更新後的商品資訊
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Product not found"
  }
  ```

### 刪除商品
- **端點**: `/products/{product_id}`
- **方法**: `DELETE`
- **回應** (200 OK):
  ```json
  {
    "message": "Product deleted successfully"
  }
  ```
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Product not found"
  }
  ```

### 上傳商品圖片
- **端點**: `/products/{product_id}/upload/`
- **方法**: `POST`
- **請求體**: 
  - Content-Type: `multipart/form-data`
  - 參數: `file` (圖片檔案，支援: jpg, jpeg, png, gif)
- **回應** (200 OK):
  ```json
  {
    "photo_id": "integer",
    "file_path": "string",
    "image_hash": "string",
    "create_time": "datetime"
  }
  ```
- **錯誤**:
  - 400 Bad Request: 
    ```json
    {
      "detail": "File must be an image"
    }
    ```
  - 400 Bad Request:
    ```json
    {
      "detail": "相同的照片已經存在"
    }
    ```
  - 404 Not Found:
    ```json
    {
      "detail": "Product not found"
    }
    ```

### 新增商品數量折扣
- **端點**: `/products/{product_id}/discounts`
- **方法**: `POST`
- **請求體**:
  ```json
  {
    "quantity": "integer",
    "price": "float"
  }
  ```
- **回應** (200 OK):
  ```json
  {
    "discount_id": "integer",
    "product_id": "integer",
    "quantity": "integer",
    "price": "float"
  }
  ```
- **錯誤**:
  - 400 Bad Request:
    ```json
    {
      "detail": "Invalid quantity"
    }
    ```
  - 400 Bad Request:
    ```json
    {
      "detail": "Invalid price"
    }
    ```
  - 400 Bad Request:
    ```json
    {
      "detail": "Discount already exists"
    }
    ```
  - 404 Not Found:
    ```json
    {
      "detail": "Product not found"
    }
    ```

### 查詢商品數量折扣
- **端點**: `/products/{product_id}/discounts`
- **方法**: `GET`
- **查詢參數**:
  - `quantity`: 指定數量（可選）
- **回應** (200 OK):
  ```json
  [
    {
      "discount_id": "integer",
      "product_id": "integer",
      "quantity": "integer",
      "price": "float"
    }
  ]
  ```

### 刪除商品數量折扣
- **端點**: `/products/{product_id}/discounts/{discount_id}`
- **方法**: `DELETE`
- **回應** (200 OK):
  ```json
  {
    "message": "Discount deleted successfully"
  }
  ```
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Discount not found"
  }
  ```

## 類別相關 API

### 創建類別
- **端點**: `/categories/`
- **方法**: `POST`
- **請求體**:
  ```json
  {
    "category_name": "string"
  }
  ```
- **回應** (200 OK):
  ```json
  {
    "category_id": "integer",
    "category_name": "string",
    "create_time": "datetime"
  }
  ```

### 獲取所有類別
- **端點**: `/categories/`
- **方法**: `GET`
- **回應** (200 OK): 類別列表

### 更新類別
- **端點**: `/categories/{category_id}`
- **方法**: `PUT`
- **請求體**:
  ```json
  {
    "category_name": "string"
  }
  ```
- **回應** (200 OK): 更新後的類別資訊
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Category not found"
  }
  ```

### 刪除類別
- **端點**: `/categories/{category_id}`
- **方法**: `DELETE`
- **回應** (200 OK):
  ```json
  {
    "message": "Category deleted successfully"
  }
  ```
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Category not found"
  }
  ```

## 訂單相關 API

### 創建訂單
- **端點**: `/orders/`
- **方法**: `POST`
- **請求體**:
  ```json
  {
    "line_id": "string",
    "details": [
      {
        "product_id": "integer",
        "quantity": "integer"
      }
    ]
  }
  ```
- **回應** (200 OK):
  ```json
  {
    "order_id": "integer",
    "line_id": "string",
    "order_date": "datetime",
    "order_status": "pending",
    "total_amount": "float",
    "details": [
      {
        "order_detail_id": "integer",
        "product_id": "integer",
        "quantity": "integer",
        "unit_price": "float",
        "subtotal": "float",
        "product_deleted": false
      }
    ]
  }
  ```
- **錯誤**:
  - 404 Not Found:
    ```json
    {
      "detail": "Product {product_id} not found"
    }
    ```
  - 400 Bad Request:
    ```json
    {
      "detail": "Insufficient stock for product {product_id}"
    }
    ```

### 獲取訂單
- **端點**: `/orders/{order_id}`
- **方法**: `GET`
- **回應** (200 OK): 訂單詳細資訊，包含所有訂單明細
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Order not found"
  }
  ```

### 更新訂單狀態
- **端點**: `/orders/{order_id}/status`
- **方法**: `PUT`
- **請求體**:
  ```json
  {
    "status": "string"
  }
  ```
- **狀態轉換規則**:
  - `pending` -> `processing`, `cancelled`
  - `processing` -> `completed`, `cancelled`
  - `completed` -> (無法更改)
  - `cancelled` -> (無法更改)

- **回應** (200 OK): 更新後的訂單資訊
- **錯誤**:
  - 404 Not Found:
    ```json
    {
      "detail": "Order not found"
    }
    ```
  - 400 Bad Request:
    ```json
    {
      "detail": "Invalid status transition"
    }
    ```

### 更新訂單明細
- **端點**: `/orders/{order_id}/details/{detail_id}`
- **方法**: `PUT`
- **請求體**:
  ```json
  {
    "quantity": "integer"
  }
  ```
- **回應** (200 OK):
  ```json
  {
    "order_detail_id": "integer",
    "order_id": "integer",
    "product_id": "integer",
    "quantity": "integer",
    "unit_price": "float",
    "subtotal": "float",
    "product_deleted": false
  }
  ```
- **錯誤** (404 Not Found):
  ```json
  {
    "detail": "Order detail not found"
  }
  ```

## 錯誤處理
所有 API 端點在發生錯誤時會返回適當的 HTTP 狀態碼和錯誤訊息：

- `400 Bad Request`: 請求參數錯誤或業務邏輯錯誤
- `404 Not Found`: 請求的資源不存在
- `500 Internal Server Error`: 伺服器內部錯誤

錯誤回應格式：
```json
{
  "detail": "錯誤訊息描述"
}
```

## 取貨地點 API

### 1. 創建取貨地點

**端點:** POST /locations/

**請求體:**
```json
{
    "district": "北港",
    "name": "北港圖書館前",
    "address": "雲林縣北港鎮文化路123號",
    "coordinate_x": 120.123456,
    "coordinate_y": 23.123456,
    "photo_path": "optional/path/to/photo.jpg"
}
```

**回應:**
```json
{
    "location_id": 1,
    "district": "北港",
    "name": "北港圖書館前",
    "address": "雲林縣北港鎮文化路123號",
    "coordinate_x": 120.123456,
    "coordinate_y": 23.123456,
    "photo_path": "optional/path/to/photo.jpg",
    "create_time": "2025-04-04T13:30:00"
}
```

### 2. 獲取取貨地點列表

**端點:** GET /locations/

**查詢參數:**
- skip (optional): 跳過的記錄數，預設為0
- limit (optional): 返回的最大記錄數，預設為100

**回應:**
```json
[
    {
        "location_id": 1,
        "district": "北港",
        "name": "北港圖書館前",
        "address": "雲林縣北港鎮文化路123號",
        "coordinate_x": 120.123456,
        "coordinate_y": 23.123456,
        "photo_path": "optional/path/to/photo.jpg",
        "create_time": "2025-04-04T13:30:00"
    }
]
```

### 3. 獲取特定取貨地點

**端點:** GET /locations/{location_id}

**回應:**
```json
{
    "location_id": 1,
    "district": "北港",
    "name": "北港圖書館前",
    "address": "雲林縣北港鎮文化路123號",
    "coordinate_x": 120.123456,
    "coordinate_y": 23.123456,
    "photo_path": "optional/path/to/photo.jpg",
    "create_time": "2025-04-04T13:30:00"
}
```

### 4. 更新取貨地點

**端點:** PUT /locations/{location_id}

**請求體:**
```json
{
    "district": "北港",
    "name": "北港圖書館前(新)",
    "address": "雲林縣北港鎮文化路123號",
    "coordinate_x": 120.123456,
    "coordinate_y": 23.123456,
    "photo_path": "optional/path/to/photo.jpg"
}
```

**回應:**
```json
{
    "location_id": 1,
    "district": "北港",
    "name": "北港圖書館前(新)",
    "address": "雲林縣北港鎮文化路123號",
    "coordinate_x": 120.123456,
    "coordinate_y": 23.123456,
    "photo_path": "optional/path/to/photo.jpg",
    "create_time": "2025-04-04T13:30:00"
}
```

### 5. 刪除取貨地點

**端點:** DELETE /locations/{location_id}

**回應:**
```json
{
    "message": "Location deleted successfully"
}
```

## 日程表 API

### 1. 創建日程

**端點:** POST /schedules/

**請求體:**
```json
{
    "date": "2025-04-02",
    "location_id": 1,
    "pickup_start_time": "17:00:00",
    "pickup_end_time": "17:30:00",
    "status": "ACTIVE"
}
```

**回應:**
```json
{
    "schedule_id": 1,
    "date": "2025-04-02",
    "location_id": 1,
    "pickup_start_time": "17:00:00",
    "pickup_end_time": "17:30:00",
    "status": "ACTIVE",
    "create_time": "2025-04-04T13:30:00"
}
```

**注意:** 同一天同一地點不能重複排程

### 2. 獲取日程列表

**端點:** GET /schedules/

**查詢參數:**
- skip (optional): 跳過的記錄數，預設為0
- limit (optional): 返回的最大記錄數，預設為100
- date_filter (optional): 按日期篩選，格式：YYYY-MM-DD

**回應:**
```json
[
    {
        "schedule_id": 1,
        "date": "2025-04-02",
        "location_id": 1,
        "pickup_start_time": "17:00:00",
        "pickup_end_time": "17:30:00",
        "status": "ACTIVE",
        "create_time": "2025-04-04T13:30:00"
    }
]
```

### 3. 獲取特定日程

**端點:** GET /schedules/{schedule_id}

**回應:**
```json
{
    "schedule_id": 1,
    "date": "2025-04-02",
    "location_id": 1,
    "pickup_start_time": "17:00:00",
    "pickup_end_time": "17:30:00",
    "status": "ACTIVE",
    "create_time": "2025-04-04T13:30:00"
}
```

### 4. 更新日程

**端點:** PUT /schedules/{schedule_id}

**請求體:**
```json
{
    "date": "2025-04-02",
    "location_id": 1,
    "pickup_start_time": "17:30:00",
    "pickup_end_time": "18:00:00",
    "status": "ACTIVE"
}
```

**回應:**
```json
{
    "schedule_id": 1,
    "date": "2025-04-02",
    "location_id": 1,
    "pickup_start_time": "17:30:00",
    "pickup_end_time": "18:00:00",
    "status": "ACTIVE",
    "create_time": "2025-04-04T13:30:00"
}
```

### 5. 刪除日程

**端點:** DELETE /schedules/{schedule_id}

**回應:**
```json
{
    "message": "Schedule deleted successfully"
}
```

**錯誤處理：**

1. 當嘗試創建重複的日程（同一天同一地點）時：
```json
{
    "detail": "Schedule already exists for this date and location"
}
```

2. 當指定的取貨地點不存在時：
```json
{
    "detail": "Location not found"
}
```

3. 當指定的日程不存在時：
```json
{
    "detail": "Schedule not found"
}
```

## 注意事項
1. 所有刪除操作都是軟刪除，資料會被標記為已刪除但不會從資料庫中實際移除
2. 商品刪除時，相關的訂單明細會被標記為 `product_deleted = true`
3. 客戶刪除時，相關的訂單會被標記為 `customer_deleted = true`
4. 訂單狀態變更為 `cancelled` 時，系統會自動歸還商品庫存

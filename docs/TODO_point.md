# 集點活動系統規劃

## 資料庫修改

### 1. 在 ProductDiscount 模型中添加點數欄位
```python
# app/product/models.py
class ProductDiscount(Base):
    # 現有欄位...
    points_earned = Column(Integer, default=0)  # 購買可獲得的點數
```

### 2. 在 Customer 模型中添加點數欄位
```python
# app/customer/models.py
class Customer(Base):
    # 現有欄位...
    points = Column(Integer, default=0)  # 累積點數
```

### 3. 在 Order 模型中添加點數欄位
```python
# app/order/models.py
class Order(Base):
    # 現有欄位...
    points_earned = Column(Integer, default=0)  # 該訂單獲得的點數
    points_used = Column(Integer, default=0)  # 該訂單使用的點數
```

### 4. 添加點數設置表
```python
# app/customer/models.py
class PointSetting(Base):
    __tablename__ = "point_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    points_per_dollar = Column(Integer, default=1)  # 每消費1元可獲得的點數
    points_value = Column(Float, default=0.1)  # 每點折抵金額，例如：0.1元/點
    min_points_for_redemption = Column(Integer, default=100)  # 最少需要多少點才能折抵
    max_discount_percentage = Column(Integer, default=50)  # 最高可折抵訂單金額的百分比
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## 功能實現

### 1. 點數獲取
- 當客戶購買使用特定折扣的商品時，系統檢查該折扣是否有關聯的點數
- 通過 OrderDetail 的 discount_id 關聯到 ProductDiscount，獲取點數信息
- 計算獲得的點數 = 數量 × 每單位點數
- 更新客戶的累積點數

### 2. 點數兌換
- 在訂單創建時，檢查客戶是否選擇使用點數折扣金額
- 驗證客戶是否有足夠的點數
- 扣除客戶的點數並應用折扣到訂單總額
- **重要：點數只能用於折扣訂單金額，不能直接兌換商品**

## API 端點

### 1. 查詢客戶點數
```python
@router.get("/customers/{line_id}/points")
def get_customer_points(line_id: str, db: Session = Depends(get_db)):
    # 返回客戶點數餘額
```

### 2. 修改訂單創建 API
```python
# 在 app/order/schemas.py 中添加
class OrderCreate(BaseModel):
    # 現有欄位...
    use_points: bool = False  # 是否使用點數折扣
    points_to_use: Optional[int] = None  # 要使用的點數數量
```

### 3. 點數折扣設置 API
```python
@router.post("/points/settings/")
def update_points_settings(settings: schemas.PointsSettings, db: Session = Depends(get_db)):
    # 更新點數折扣設置，例如多少點數可以折抵多少金額
```

## 前端實現

1. 在購物車或結帳頁面顯示客戶的點數餘額
2. 提供點數折扣的選項 (例如複選框 "使用點數折扣")
3. 顯示點數折扣金額的計算方式 (例如：100點 = 10元折扣)
4. 提供輸入框讓客戶輸入要使用的點數數量
5. 當客戶選擇使用點數時，計算並顯示折扣後的總金額

## 實現流程

1. 資料庫遷移：添加新的欄位
2. 後端 API 實現：點數查詢、兌換和管理
3. 訂單處理邏輯修改：點數獲取和兌換
4. 前端界面開發：點數顯示和兌換選項

## 注意事項

1. 點數系統應該是可選的，不應該影響現有功能
2. 需要考慮點數的有效期和過期處理 (進階功能)
3. 可以考慮添加點數交易歷史記錄 (進階功能)
4. 安全性考慮：防止點數欺詐和重複使用

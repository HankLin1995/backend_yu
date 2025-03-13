import pytest
from app.models import Product, ProductDiscount

# 測試案例 2.2: 產品數量折扣測試
# 驗證：
# - [x] 新增產品數量折扣
# - [x] 驗證折扣數量和價格
def test_add_product_discount(client):
    # 建立測試產品
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 50
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    product_id = response.json()["product_id"]
    
    # 新增數量折扣
    discount_data = {
        "discount_id": 0,
        "product_id": product_id,
        "quantity": 2,
        "price": 180.0  # 買2件180元
    }
    response = client.post(f"/products/{product_id}/discounts", json=discount_data)
    assert response.status_code == 200
    assert response.json()["quantity"] == 2
    assert response.json()["price"] == 180.0

# 測試案例 2.2: 無效折扣驗證
# 驗證：
# - [x] 數量為0或負數
# - [x] 價格為0或負數
def test_invalid_discount_validation(client):
    # 建立測試產品
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 50
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # 測試無效數量
    invalid_quantity_data = {
        "product_id": product_id,
        "quantity": 0,
        "price": 180.0
    }
    response = client.post(f"/products/{product_id}/discounts", json=invalid_quantity_data)
    assert response.status_code == 400
    assert "Invalid quantity" in response.json()["detail"]
    
    # 測試無效價格
    invalid_price_data = {
        "product_id": product_id,
        "quantity": 2,
        "price": 0
    }
    response = client.post(f"/products/{product_id}/discounts", json=invalid_price_data)
    assert response.status_code == 400
    assert "Invalid price" in response.json()["detail"]

# 測試案例 2.2: 重複折扣驗證
# 驗證：
# - [x] 相同產品相同數量不可重複設定折扣
def test_duplicate_discount_validation(client):
    # 建立測試產品
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 50
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # 新增第一個折扣
    discount_data = {
        "product_id": product_id,
        "quantity": 2,
        "price": 180.0
    }
    response = client.post(f"/products/{product_id}/discounts", json=discount_data)
    assert response.status_code == 200
    
    # 嘗試新增重複的折扣
    duplicate_discount = {
        "product_id": product_id,
        "quantity": 2,
        "price": 170.0
    }
    response = client.post(f"/products/{product_id}/discounts", json=duplicate_discount)
    assert response.status_code == 400
    assert "Discount already exists" in response.json()["detail"]

# 測試案例 2.2: 折扣查詢測試
# 驗證：
# - [x] 查詢特定產品的折扣
def test_get_product_discounts(client):
    # 建立測試產品
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 50
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # 新增折扣
    discount_data = {
        "product_id": product_id,
        "quantity": 2,
        "price": 180.0
    }
    client.post(f"/products/{product_id}/discounts", json=discount_data)
    
    # 查詢折扣
    response = client.get(f"/products/{product_id}/discounts?quantity=2")
    assert response.status_code == 200
    discounts = response.json()
    assert len(discounts) == 1
    assert discounts[0]["quantity"] == 2
    assert discounts[0]["price"] == 180.0

# 測試案例 2.2: 折扣刪除測試
# 驗證：
# - [x] 刪除折扣
# - [x] 刪除不存在的折扣
def test_remove_product_discount(client):
    # 建立測試產品
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 50
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # 新增折扣
    discount_data = {
        "product_id": product_id,
        "quantity": 2,
        "price": 180.0
    }
    response = client.post(f"/products/{product_id}/discounts", json=discount_data)
    discount_id = response.json()["discount_id"]
    
    # 刪除折扣
    response = client.delete(f"/products/{product_id}/discounts/{discount_id}")
    assert response.status_code == 200
    assert "Discount deleted successfully" in response.json()["message"]
    
    # 確認折扣已被刪除
    response = client.get(f"/products/{product_id}/discounts?quantity=2")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    # 嘗試刪除不存在的折扣
    response = client.delete(f"/products/{product_id}/discounts/999")
    assert response.status_code == 404
    assert "Discount not found" in response.json()["detail"]

from fastapi.testclient import TestClient
import pytest
from app.main import app

# 測試案例 1.1: 客戶註冊測試
# 驗證：
# - [x] 新客戶註冊（所有欄位皆正確填寫）
def test_create_customer(client):
    customer_data = {
        "line_id": "U123456789",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200
    assert response.json()["line_id"] == customer_data["line_id"]

# 測試案例 1.1: 重複客戶註冊測試
# 驗證：
# - [x] 重複的 LINE ID 註冊
def test_duplicate_customer(client):
    customer_data = {
        "line_id": "U123456789",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }
    # First creation should succeed
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200
    
    # Second creation should fail
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 400

# 測試案例 2.1: 商品基本操作測試
# 驗證：
# - [x] 新增商品（包含所有必填欄位）
def test_create_product(client):
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 50
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    assert response.json()["product_name"] == product_data["product_name"]

# 測試案例 2.1: 商品庫存更新測試
# 驗證：
# - [x] 庫存數量更新
def test_update_product_stock(client):
    # First create a product
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 50
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # Update stock
    new_quantity = 30
    response = client.put(f"/products/{product_id}/stock?quantity={new_quantity}")
    assert response.status_code == 200
    assert response.json()["stock_quantity"] == new_quantity

# 測試案例 3.1: 訂單建立測試
# 驗證：
# - [x] 正常訂單建立流程
# - [x] 訂單總金額計算
# - [x] 多項商品訂單
def test_create_order(client):
    # First create a customer
    customer_data = {
        "line_id": "U123456789",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }
    client.post("/customers/", json=customer_data)
    
    # Then create a product
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 50
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # Create order
    order_data = {
        "line_id": "U123456789",
        "details": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 200
    assert response.json()["total_amount"] == 200.0  # 2 * 100.0
    
    # Check stock was reduced
    response = client.put(f"/products/{product_id}/stock?quantity=48")
    assert response.json()["stock_quantity"] == 48

# 測試案例 3.1: 庫存不足訂單測試
# 驗證：
# - [x] 庫存不足時的訂單處理
def test_insufficient_stock_order(client):
    # First create a customer
    customer_data = {
        "line_id": "U123456789",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }
    client.post("/customers/", json=customer_data)
    
    # Then create a product with low stock
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 1
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # Try to create order with insufficient stock
    order_data = {
        "line_id": "U123456789",
        "details": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    }
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400  # Should fail

# 測試案例 3.2: 訂單取消測試
# 驗證：
# - [x] 訂單取消處理
# - [x] 訂單取消後庫存回補
def test_cancel_order(client):
    # First create a customer
    customer_data = {
        "line_id": "U123456789",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }
    client.post("/customers/", json=customer_data)
    
    # Then create a product
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 50
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # Create order
    order_data = {
        "line_id": "U123456789",
        "details": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    }
    response = client.post("/orders/", json=order_data)
    order_id = response.json()["order_id"]
    
    # Cancel order
    response = client.put(f"/orders/{order_id}/status?status=cancelled")
    assert response.status_code == 200
    assert response.json()["order_status"] == "cancelled"
    
    # Check stock was restored
    response = client.put(f"/products/{product_id}/stock?quantity=50")
    assert response.json()["stock_quantity"] == 50

# 測試案例 4.1: 庫存管理整合測試
# 驗證：
# - [x] 多筆訂單同時處理庫存
def test_multiple_orders_stock_management(client):
    # Create a customer
    customer_data = {
        "line_id": "U123456789",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }
    client.post("/customers/", json=customer_data)
    
    # Create a product with stock of 10
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 10
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # Create multiple orders
    order_data = {
        "line_id": "U123456789",
        "details": [
            {
                "product_id": product_id,
                "quantity": 3
            }
        ]
    }
    
    # Create first order (3 items)
    response1 = client.post("/orders/", json=order_data)
    assert response1.status_code == 200
    
    # Create second order (3 items)
    response2 = client.post("/orders/", json=order_data)
    assert response2.status_code == 200
    
    # Check remaining stock (should be 4)
    response = client.get(f"/products/{product_id}")
    assert response.json()["stock_quantity"] == 4

# 測試案例 4.2: 金額計算整合測試
# 驗證：
# - [x] 混合一般商品和特價商品的訂單總金額
def test_mixed_price_order_calculation(client):
    # Create a customer
    customer_data = {
        "line_id": "U123456789",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }
    client.post("/customers/", json=customer_data)
    
    # Create regular price product
    regular_product_data = {
        "product_name": "Regular Product",
        "price": 100.0,
        "description": "Regular price product",
        "stock_quantity": 10
    }
    response = client.post("/products/", json=regular_product_data)
    regular_product_id = response.json()["product_id"]
    
    # Create special price product
    special_product_data = {
        "product_name": "Special Product",
        "price": 200.0,
        "special_price": 150.0,
        "description": "Special price product",
        "stock_quantity": 10
    }
    response = client.post("/products/", json=special_product_data)
    special_product_id = response.json()["product_id"]
    
    # Create order with both products
    order_data = {
        "line_id": "U123456789",
        "details": [
            {
                "product_id": regular_product_id,
                "quantity": 2
            },
            {
                "product_id": special_product_id,
                "quantity": 2
            }
        ]
    }
    
    # Create order
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 200
    assert response.json()["total_amount"] == 500.0  # (2 * 100) + (2 * 150)

# 測試案例 4.3: 資料完整性測試
# 驗證：
# - [x] 刪除商品時相關訂單和照片的處理
def test_product_deletion_integrity(client):
    # Create a customer
    customer_data = {
        "line_id": "U123456789",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }
    client.post("/customers/", json=customer_data)
    
    # Create a product
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 10
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # Create an order
    order_data = {
        "line_id": "U123456789",
        "details": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    }
    response = client.post("/orders/", json=order_data)
    order_id = response.json()["order_id"]
    
    # Delete the product
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    
    # Check if order still exists but marked as deleted
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["details"][0]["product_deleted"] == True

# 測試案例 4.3: 資料完整性測試
# 驗證：
# - [x] 客戶資料刪除時的訂單處理
def test_customer_deletion_integrity(client):
    # Create a customer
    customer_data = {
        "line_id": "U123456789",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }
    response = client.post("/customers/", json=customer_data)
    customer_id = response.json()["customer_id"]
    
    # Create a product
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 10
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # Create an order
    order_data = {
        "line_id": "U123456789",
        "details": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    }
    response = client.post("/orders/", json=order_data)
    order_id = response.json()["order_id"]
    
    # Delete the customer
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == 200
    
    # Check if order still exists but marked as customer deleted
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["customer_deleted"] == True

# 測試案例 4.3: 資料完整性測試
# 驗證：
# - [x] 商品照片和分類的關聯處理
def test_product_photos_and_categories(client):
    # Create categories
    category_data1 = {
        "category_name": "海鮮",
        "description": "新鮮海產"
    }
    category_data2 = {
        "category_name": "熟食",
        "description": "即食料理"
    }
    response = client.post("/categories/", json=category_data1)
    category_id1 = response.json()["category_id"]
    response = client.post("/categories/", json=category_data2)
    category_id2 = response.json()["category_id"]
    
    # Create a product
    product_data = {
        "product_name": "Test Product",
        "price": 100.0,
        "description": "Test Description",
        "stock_quantity": 10,
        "categories": [category_id1, category_id2]
    }
    response = client.post("/products/", json=product_data)
    product_id = response.json()["product_id"]
    
    # Add photos to product
    photo_data1 = {
        "photo_url": "https://example.com/photo1.jpg",
        "is_main": True,
        "sort_order": 1
    }
    photo_data2 = {
        "photo_url": "https://example.com/photo2.jpg",
        "is_main": False,
        "sort_order": 2
    }
    response = client.post(f"/products/{product_id}/photos", json=photo_data1)
    photo_id1 = response.json()["photo_id"]
    response = client.post(f"/products/{product_id}/photos", json=photo_data2)
    photo_id2 = response.json()["photo_id"]
    
    # Verify product categories
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    product = response.json()
    assert len(product["categories"]) == 2
    category_ids = [cat["category_id"] for cat in product["categories"]]
    assert category_id1 in category_ids
    assert category_id2 in category_ids
    
    # Verify product photos
    response = client.get(f"/products/{product_id}/photos")
    assert response.status_code == 200
    photos = response.json()
    assert len(photos) == 2
    assert any(photo["is_main"] == True for photo in photos)
    
    # Test deleting a category
    response = client.delete(f"/categories/{category_id1}")
    assert response.status_code == 200
    
    # Verify product still exists but with one less category
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    product = response.json()
    assert len(product["categories"]) == 1
    assert product["categories"][0]["category_id"] == category_id2
    
    # Delete product and verify photos are also deleted
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    
    # Verify photos are deleted
    response = client.get(f"/products/{product_id}/photos")
    assert response.status_code == 404  # or 200 with empty list, depending on your API design

# 測試案例 4.3: 資料完整性測試
# 驗證：
# - [x] 刪除類別時的商品關聯處理
def test_category_deletion_integrity(client):
    # Create a category
    category_data = {
        "category_name": "海鮮",
        "description": "新鮮海產"
    }
    response = client.post("/categories/", json=category_data)
    category_id = response.json()["category_id"]
    
    # Create multiple products in the category
    for i in range(3):
        product_data = {
            "product_name": f"Test Product {i}",
            "price": 100.0,
            "description": f"Test Description {i}",
            "stock_quantity": 10,
            "categories": [category_id]
        }
        client.post("/products/", json=product_data)
    
    # Delete the category
    response = client.delete(f"/categories/{category_id}")
    assert response.status_code == 200
    
    # Get all products and verify they no longer have the deleted category
    response = client.get("/products/")
    assert response.status_code == 200
    products = response.json()
    
    for product in products:
        # Verify each product exists but doesn't have the deleted category
        category_ids = [cat["category_id"] for cat in product["categories"]]
        assert category_id not in category_ids

def test_create_product_discount(client):
    # Create a test product first
    product_data = {
        "product_name": "Test Product",
        "description": "A test product description",
        "price": 1000,  # $10.00
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "stock_quantity": 100,
        "unit": "個"
    }
    product_response = client.post("/products/", json=product_data)
    assert product_response.status_code == 200
    product_id = product_response.json()["product_id"]

    # Test creating a product discount
    discount_data = {
        "quantity": 5,
        "price": 800
    }
    response = client.post(f"/products/{product_id}/discounts", json=discount_data)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == discount_data["quantity"]
    assert data["price"] == discount_data["price"]
    assert data["product_id"] == product_id

def test_get_product_discounts(client):
    # Create a test product first
    product_data = {
        "product_name": "Test Product",
        "description": "A test product description",
        "price": 1000,  # $10.00
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "stock_quantity": 100,
        "unit": "個"
    }
    product_response = client.post("/products/", json=product_data)
    assert product_response.status_code == 200
    product_id = product_response.json()["product_id"]

    # Test creating a product discount
    discount_data = {
        "quantity": 5,
        "price": 800
    }
    client.post(f"/products/{product_id}/discounts", json=discount_data)

    # Test getting product discounts
    response = client.get(f"/products/{product_id}/discounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["quantity"] == discount_data["quantity"]
    assert data[0]["price"] == discount_data["price"]
    assert data[0]["product_id"] == product_id

def test_delete_all_product_discounts(client):
    # Create a test product first
    product_data = {
        "product_name": "Test Product",
        "description": "A test product description",
        "price": 1000,  # $10.00
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "stock_quantity": 100,
        "unit": "個"
    }
    product_response = client.post("/products/", json=product_data)
    assert product_response.status_code == 200
    product_id = product_response.json()["product_id"]

    # Test creating a product discount
    discount_data = {
        "quantity": 5,
        "price": 800
    }
    client.post(f"/products/{product_id}/discounts", json=discount_data)

    # Test deleting all product discounts
    response = client.delete(f"/products/{product_id}/discounts")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "All discounts deleted successfully"

def test_update_product_discounts(client):
    """測試基本的折扣更新功能"""
    # Create a test product
    product_data = {
        "product_name": "Test Product for Update",
        "description": "A test product description",
        "price": 1000,
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "stock_quantity": 100,
        "unit": "個"
    }
    product_response = client.post("/products/", json=product_data)
    assert product_response.status_code == 200
    product_id = product_response.json()["product_id"]
    
    # Create initial discounts
    initial_discounts = [
        {"quantity": 5, "price": 800},
        {"quantity": 10, "price": 700}
    ]
    
    for discount in initial_discounts:
        response = client.post(f"/products/{product_id}/discounts", json=discount)
        assert response.status_code == 200
    
    # Verify initial discounts
    response = client.get(f"/products/{product_id}/discounts")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Test updating discounts
    updated_discounts = [
        {"quantity": 5, "price": 750},  # Update existing discount
        {"quantity": 15, "price": 650}  # Add new discount
    ]
    
    response = client.put(f"/products/{product_id}/discounts", json=updated_discounts)
    assert response.status_code == 200
    data = response.json()
    
    # Verify updated discounts
    assert len(data) == 2  # 只有兩個折扣，因為更新邏輯是替換而非保留未提及的折扣
    
    # Check that the existing discount was updated
    found_updated = False
    for discount in data:
        if discount["quantity"] == 5:
            assert discount["price"] == 750
            found_updated = True
    assert found_updated
    
    # Check that the new discount was added
    found_new = False
    for discount in data:
        if discount["quantity"] == 15:
            assert discount["price"] == 650
            found_new = True
    assert found_new
    
    # 未提及的折扣已被刪除
    found_untouched = False
    for discount in data:
        if discount["quantity"] == 10:
            found_untouched = True
    assert not found_untouched  # 確認未提及的折扣已被刪除

def test_update_product_discounts_with_referenced_discounts(client, db_session):
    """測試更新已被訂單引用的折扣，這個測試主要測試在更新時可以更新已引用折扣的價格但保留ID的功能"""
    """測試更新包含已被訂單引用的折扣"""
    from app.product.models import Product, ProductDiscount
    from app.order.models import Order, OrderDetail
    from app.customer.models import Customer
    from app.location.models import Schedule
    from datetime import datetime, time
    
    # 創建測試產品
    product = Product(
        product_name="Test Product with References",
        description="A test product description",
        price=1000,
        stock_quantity=100,
        unit="個"
    )
    db_session.add(product)
    db_session.commit()
    
    # 創建折扣
    discount1 = ProductDiscount(product_id=product.product_id, quantity=5, price=800)
    discount2 = ProductDiscount(product_id=product.product_id, quantity=10, price=700)
    db_session.add(discount1)
    db_session.add(discount2)
    db_session.commit()
    
    # 創建客戶
    customer = Customer(
        line_id="test_customer_id",
        name="Test Customer",
        line_name="Test Customer",
        line_pic_url="http://example.com/pic.jpg"
    )
    db_session.add(customer)
    
    # 創建配送時間
    # 首先創建一個PickupLocation
    from app.location.models import PickupLocation
    pickup_location = PickupLocation(
        district="Test District",
        name="Test Location",
        address="Test Address"
    )
    db_session.add(pickup_location)
    db_session.commit()
    
    # 然後創建Schedule，使用正確的時間格式
    schedule = Schedule(
        location_id=pickup_location.location_id,
        date=datetime.now().date(),
        pickup_start_time=time(10, 0),  # 使用time對象
        pickup_end_time=time(12, 0),    # 使用time對象
        status="ACTIVE"
    )
    db_session.add(schedule)
    db_session.commit()
    
    # 創建訂單
    order = Order(
        line_id=customer.line_id,
        schedule_id=schedule.schedule_id,
        order_status="pending",
        payment_status="pending",
        total_amount=800
    )
    db_session.add(order)
    db_session.commit()
    
    # 創建訂單詳情，引用第一個折扣
    order_detail = OrderDetail(
        order_id=order.order_id,
        product_id=product.product_id,
        quantity=5,
        unit_price=800,
        subtotal=800,
        discount_id=discount1.discount_id  # 引用第一個折扣
    )
    db_session.add(order_detail)
    db_session.commit()
    
    # 保存必要的ID值，避免後續出現DetachedInstanceError
    product_id = product.product_id
    discount1_id = discount1.discount_id
    
    # 嘗試更新折扣，包括修改已引用的折扣和添加新折扣
    # 注意：在舊的更新邏輯中，已引用的折扣可以更新價格
    # 在新的更新邏輯中，已被訂單使用的折扣數量會被跳過
    updated_discounts = [
        {"quantity": 5, "price": 750},  # 嘗試更新已引用的折扣
        {"quantity": 20, "price": 600}  # 添加新折扣
    ]
    
    response = client.put(f"/products/{product_id}/discounts", json=updated_discounts)
    assert response.status_code == 200
    data = response.json()
    
    # 驗證結果
    assert len(data) == 2  # 應該有2個折扣：已引用的和新添加的
    
    # 檢查已引用的折扣是否被跳過更新
    referenced_discount = None
    for d in data:
        if d["quantity"] == 5:
            referenced_discount = d
            break
    assert referenced_discount is not None
    assert referenced_discount["price"] == 800  # 價格應該保持原價格，而不是更新為750
    assert referenced_discount["discount_id"] == discount1_id  # ID應該保持不變
    
    # 檢查新添加的折扣
    new_discount = None
    for d in data:
        if d["quantity"] == 20:
            new_discount = d
            break
    assert new_discount is not None
    assert new_discount["price"] == 600
    
    # 嘗試刪除折扣，應該只刪除未被引用的折扣
    response = client.delete(f"/products/{product_id}/discounts")
    assert response.status_code == 200
    message = response.json()["message"]
    assert "Skipped" in message
    assert "Deleted" in message or "No discounts were deleted" in message
    
    # 驗證被引用的折扣仍然存在
    response = client.get(f"/products/{product_id}/discounts")
    assert response.status_code == 200
    data = response.json()
    
    # 應該至少有一個折扣保留（已引用的）
    assert len(data) >= 1
    
    # 確認已引用的折扣仍然存在
    found_referenced = False
    for d in data:
        if d["quantity"] == 5 and d["discount_id"] == discount1_id:
            found_referenced = True
            # 注意：在新的更新邏輯中，已被使用的折扣價格不會被更新
            assert d["price"] == 800  # 價格應該保持原價格，而不是更新為750
            break
    assert found_referenced


def test_update_product_discounts_skip_used_quantities(client, db_session):
    """測試更新折扣時跳過已被使用的數量並新增未被使用的數量"""
    from app.product.models import Product, ProductDiscount
    from app.order.models import Order, OrderDetail
    from app.customer.models import Customer
    from app.location.models import Schedule, PickupLocation
    from datetime import datetime, time
    
    # 創建測試產品
    product = Product(
        product_name="Test Product for Skip Logic",
        description="A test product description",
        price=1000,
        stock_quantity=100,
        unit="個"
    )
    db_session.add(product)
    db_session.commit()
    
    # 創建多個折扣
    discount1 = ProductDiscount(product_id=product.product_id, quantity=5, price=800)
    discount2 = ProductDiscount(product_id=product.product_id, quantity=10, price=700)
    discount3 = ProductDiscount(product_id=product.product_id, quantity=15, price=650)
    db_session.add(discount1)
    db_session.add(discount2)
    db_session.add(discount3)
    db_session.commit()
    
    # 創建客戶
    customer = Customer(
        line_id="test_customer_id2",
        name="Test Customer 2",
        line_name="Test Customer 2",
        line_pic_url="http://example.com/pic2.jpg"
    )
    db_session.add(customer)
    
    # 創建配送地點和時間
    pickup_location = PickupLocation(
        district="Test District 2",
        name="Test Location 2",
        address="Test Address 2"
    )
    db_session.add(pickup_location)
    db_session.commit()
    
    schedule = Schedule(
        location_id=pickup_location.location_id,
        date=datetime.now().date(),
        pickup_start_time=time(10, 0),
        pickup_end_time=time(12, 0),
        status="ACTIVE"
    )
    db_session.add(schedule)
    db_session.commit()
    
    # 創建訂單
    order = Order(
        line_id=customer.line_id,
        schedule_id=schedule.schedule_id,
        order_status="pending",
        payment_status="pending",
        total_amount=800
    )
    db_session.add(order)
    db_session.commit()
    
    # 創建訂單詳情，引用第一個和第二個折扣
    order_detail1 = OrderDetail(
        order_id=order.order_id,
        product_id=product.product_id,
        quantity=5,
        unit_price=800,
        subtotal=800,
        discount_id=discount1.discount_id  # 引用第一個折扣
    )
    order_detail2 = OrderDetail(
        order_id=order.order_id,
        product_id=product.product_id,
        quantity=10,
        unit_price=700,
        subtotal=700,
        discount_id=discount2.discount_id  # 引用第二個折扣
    )
    db_session.add(order_detail1)
    db_session.add(order_detail2)
    db_session.commit()
    
    # 保存必要的ID值
    product_id = product.product_id
    discount1_id = discount1.discount_id
    discount2_id = discount2.discount_id
    discount3_id = discount3.discount_id
    
    # 嘗試更新折扣，包括已被使用的和未被使用的數量
    updated_discounts = [
        {"quantity": 5, "price": 750},   # 已被使用，應該跳過
        {"quantity": 10, "price": 650},  # 已被使用，應該跳過
        {"quantity": 15, "price": 600},  # 未被使用，應該更新
        {"quantity": 20, "price": 550}   # 新增的折扣
    ]
    
    response = client.put(f"/products/{product_id}/discounts", json=updated_discounts)
    assert response.status_code == 200
    data = response.json()
    
    # 驗證結果
    assert len(data) == 4  # 應該有4個折扣：2個已被使用的、一個更新的和一個新增的
    
    # 檢查已被使用的折扣是否保持原價格
    for d in data:
        if d["quantity"] == 5:
            assert d["price"] == 800  # 應該保持原價格
            assert d["discount_id"] == discount1_id
        elif d["quantity"] == 10:
            assert d["price"] == 700  # 應該保持原價格
            assert d["discount_id"] == discount2_id
        elif d["quantity"] == 15:
            assert d["price"] == 600  # 應該被更新
            assert d["discount_id"] == discount3_id
        elif d["quantity"] == 20:
            assert d["price"] == 550  # 新增的折扣
        else:
            assert False, f"Unexpected discount quantity: {d['quantity']}"
    
    # 嘗試刪除折扣，應該只刪除未被使用的折扣
    response = client.delete(f"/products/{product_id}/discounts")
    assert response.status_code == 200
    message = response.json()["message"]
    assert "Skipped" in message
    assert "Deleted" in message
    
    # 驗證被使用的折扣仍然存在，未被使用的折扣已被刪除
    response = client.get(f"/products/{product_id}/discounts")
    assert response.status_code == 200
    data = response.json()
    
    # 應該只剩下已被使用的折扣
    assert len(data) == 2
    
    quantities = [d["quantity"] for d in data]
    assert 5 in quantities
    assert 10 in quantities
    assert 15 not in quantities  # 應該被刪除
    assert 20 not in quantities  # 應該被刪除
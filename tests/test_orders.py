import pytest
from datetime import datetime
from app.order.models import Order, OrderDetail
from app.customer.models import Customer
from app.product.models import Product
from app.location.models import Schedule, PickupLocation

@pytest.fixture
def test_customer(db_session):
    customer = Customer(
        line_id="admin_test_id",  # 使用與認證相同的 ID
        name="Test Customer",
        line_name="Test Line Name",
        line_pic_url="http://example.com/pic.jpg",
        phone="1234567890"
    )
    db_session.add(customer)
    db_session.commit()
    return customer

@pytest.fixture
def test_product(db_session):
    product = Product(
        product_name="Test Product",
        description="Test product description",
        price=100.00,
        one_set_price=90.00,
        one_set_quantity=5,
        stock_quantity=50,
        unit="piece"
    )
    db_session.add(product)
    db_session.commit()
    return product

@pytest.fixture
def test_pickup_location(db_session):
    location = PickupLocation(
        district="Test District",
        name="Test Location",
        address="Test Address"
    )
    db_session.add(location)
    db_session.commit()
    return location

@pytest.fixture
def test_schedule(db_session, test_pickup_location):
    schedule = Schedule(
        date=datetime.now().date(),
        location_id=test_pickup_location.location_id,
        pickup_start_time=datetime.now().time(),
        pickup_end_time=datetime.now().time(),
        status="ACTIVE"
    )
    db_session.add(schedule)
    db_session.commit()
    return schedule

def test_create_order(client, db_session, test_customer, test_product, test_schedule):
    # 先從數據庫中重新查詢對象
    customer = db_session.query(Customer).filter(Customer.line_id == test_customer.line_id).first()
    product = db_session.query(Product).filter(Product.product_id == test_product.product_id).first()
    schedule = db_session.query(Schedule).filter(Schedule.schedule_id == test_schedule.schedule_id).first()
    
    # 使用查詢到的對象創建請求數據
    line_id = customer.line_id
    schedule_id = schedule.schedule_id
    product_id = product.product_id
    product_price = float(product.price)
    
    # 儲存原始庫存數量以供驗證
    original_stock = product.stock_quantity
    
    order_data = {
        "line_id": line_id,
        "schedule_id": schedule_id,
        "payment_method": "cash",
        "order_details": [
            {
                "product_id": product_id,
                "quantity": 2,  # 訂購 2 組
                "unit_price": product_price,
                "subtotal": product_price * 2
            }
        ]
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 200
    data = response.json()
    
    # 驗證訂單基本資訊
    assert data["line_id"] == line_id
    assert data["schedule_id"] == schedule_id
    assert data["order_status"] == "pending"
    assert data["payment_status"] == "pending"
    assert len(data["order_details"]) == 1
    assert data["order_details"][0]["quantity"] == 2
    
    # 驗證庫存是否正確減少
    updated_product = db_session.query(Product).filter(Product.product_id == product_id).first()
    expected_stock = original_stock - (2 * product.one_set_quantity)  # 2組 * 每組數量
    assert updated_product.stock_quantity == expected_stock

def test_create_order_insufficient_stock(client, db_session, test_customer, test_product, test_schedule):
    # 設置產品庫存為較小的數量
    product = db_session.query(Product).filter(Product.product_id == test_product.product_id).first()
    product.stock_quantity = 3  # 設置庫存只有3個
    db_session.commit()
    
    order_data = {
        "line_id": test_customer.line_id,
        "schedule_id": test_schedule.schedule_id,
        "payment_method": "cash",
        "order_details": [
            {
                "product_id": product.product_id,
                "quantity": 1,  # 訂購1組，但因為一組需要5個（one_set_quantity），所以會超過庫存
                "unit_price": float(product.price),
                "subtotal": float(product.price)
            }
        ]
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]
    
    # 驗證庫存沒有變化
    updated_product = db_session.query(Product).filter(Product.product_id == product.product_id).first()
    assert updated_product.stock_quantity == 3

def test_create_order_multiple_items(client, db_session, test_customer, test_product, test_schedule):
    product = db_session.query(Product).filter(Product.product_id == test_product.product_id).first()
    original_stock = product.stock_quantity
    
    # 創建一個包含多個商品的訂單
    order_data = {
        "line_id": test_customer.line_id,
        "schedule_id": test_schedule.schedule_id,
        "payment_method": "cash",
        "order_details": [
            {
                "product_id": product.product_id,
                "quantity": 2,  # 訂購2組
                "unit_price": float(product.price),
                "subtotal": float(product.price) * 2
            },
            {
                "product_id": product.product_id,
                "quantity": 1,  # 再訂購1組
                "unit_price": float(product.price),
                "subtotal": float(product.price)
            }
        ]
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 200
    
    # 驗證庫存是否正確減少（總共訂購3組）
    updated_product = db_session.query(Product).filter(Product.product_id == product.product_id).first()
    expected_stock = original_stock - (3 * product.one_set_quantity)
    assert updated_product.stock_quantity == expected_stock

def test_get_orders(client, db_session, test_customer, test_product, test_schedule):
    # Create test order
    order = Order(
        line_id=test_customer.line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=200.00,
        payment_method="cash"
    )
    db_session.add(order)
    db_session.flush()

    order_detail = OrderDetail(
        order_id=order.order_id,
        product_id=test_product.product_id,
        quantity=2,
        unit_price=100.00,
        subtotal=200.00
    )
    db_session.add(order_detail)
    db_session.commit()

    response = client.get("/orders/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(o["order_id"] == order.order_id for o in data)

def test_get_orders_filter_by_line_id(client, db_session, test_customer, test_product, test_schedule):
    # Create test orders with different line_ids
    # First order - with test_customer's line_id
    order1 = Order(
        line_id=test_customer.line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=200.00,
        payment_method="cash"
    )
    db_session.add(order1)
    db_session.flush()
    
    # Store the order_id value to avoid SQLAlchemy session issues later
    order1_id = order1.order_id
    
    order_detail1 = OrderDetail(
        order_id=order1_id,
        product_id=test_product.product_id,
        quantity=2,
        unit_price=100.00,
        subtotal=200.00
    )
    db_session.add(order_detail1)
    
    # Second order - with different line_id
    different_customer = Customer(
        line_id="different_test_id",
        name="Different Customer",
        line_name="Different Line Name",
        line_pic_url="http://example.com/different_pic.jpg",
        phone="0987654321"
    )
    db_session.add(different_customer)
    db_session.flush()
    
    # Store different_customer.line_id to avoid session issues
    different_line_id = different_customer.line_id
    
    order2 = Order(
        line_id=different_line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=300.00,
        payment_method="cash"
    )
    db_session.add(order2)
    db_session.flush()
    
    # Store the order2 ID value
    order2_id = order2.order_id
    
    order_detail2 = OrderDetail(
        order_id=order2_id,
        product_id=test_product.product_id,
        quantity=3,
        unit_price=100.00,
        subtotal=300.00
    )
    db_session.add(order_detail2)
    db_session.commit()
    
    # Need to set headers for authentication (using test_customer as authenticated user)
    test_customer_line_id = test_customer.line_id
    headers = {"Authorization": f"Bearer {test_customer_line_id}"}
    
    # Test filtering by test_customer's line_id
    response = client.get(f"/orders/?line_id={test_customer_line_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # Check that only orders with test_customer's line_id are returned
    assert len(data) >= 1
    assert all(o["line_id"] == test_customer_line_id for o in data)
    
    # Make sure our specific order is in the results
    order1_found = False
    for order in data:
        if order["order_id"] == order1_id:
            order1_found = True
            break
    assert order1_found, "Expected order not found in results"
    
    # Make sure the different customer's order is not in the results
    order2_found = False
    for order in data:
        if order["order_id"] == order2_id:
            order2_found = True
            break
    assert not order2_found, "Order from different customer should not be included"
    
    # Test filtering by different_customer's line_id (need to use different_customer's auth)
    headers_different = {"Authorization": f"Bearer {different_line_id}"}
    response = client.get(f"/orders/?line_id={different_line_id}", headers=headers_different)
    assert response.status_code == 200
    data = response.json()
    
    # Check that only orders with different_customer's line_id are returned
    assert len(data) >= 1
    assert all(o["line_id"] == different_line_id for o in data)
    
    # Check orders individually to avoid SQLAlchemy session issues
    order2_found = False
    order1_found = False
    
    for order in data:
        if order["order_id"] == order2_id:
            order2_found = True
        if order["order_id"] == order1_id:
            order1_found = True
    
    assert order2_found, "Expected order2 not found in results"
    assert not order1_found, "Order1 should not be included in the results"

def test_get_orders_filter_by_date(client, db_session, test_customer, test_product, test_schedule):
    from datetime import datetime, timedelta, date
    import json
    print("\n==== Starting test_get_orders_filter_by_date ====")
    
    # Store test_customer.line_id to avoid session issues
    test_customer_line_id = test_customer.line_id
    
    # Get current schedule's date for reference
    schedule_date = test_schedule.date
    # Calculate dates for testing
    day_before = schedule_date - timedelta(days=1)
    day_after = schedule_date + timedelta(days=1)
    
    # Use the existing test_schedule
    
    # Create a test order with the existing schedule
    order = Order(
        line_id=test_customer_line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=200.00,
        payment_method="cash"
    )
    db_session.add(order)
    db_session.flush()
    order_id = order.order_id
    
    order_detail = OrderDetail(
        order_id=order_id,
        product_id=test_product.product_id,
        quantity=2,
        unit_price=100.00,
        subtotal=200.00
    )
    db_session.add(order_detail)
    db_session.commit()
    
    # Need to set headers for authentication
    headers = {"Authorization": f"Bearer {test_customer_line_id}"}
    print(f"\nTest setup details:")
    print(f"- Order ID: {order_id}, schedule date: {schedule_date}")
    print(f"- Authentication headers: {headers}")
    
    # Test filtering by exact schedule date
    # Use YYYY-MM-DD format which FastAPI expects for date
    test_date = schedule_date.strftime("%Y-%m-%d")
    print(f"\nSending request with start_date and end_date both equal to {test_date}")
    response = client.get(f"/orders/?start_date={test_date}&end_date={test_date}", headers=headers)
    print(f"Response status code: {response.status_code}")
    
    # Debug response content
    try:
        data = response.json()
        print(f"Response data length: {len(data)}")
        if len(data) > 0:
            print(f"First order in response: {json.dumps(data[0], indent=2)}")
        print(f"Order IDs in response: {[o.get('order_id') for o in data]}")
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response.content}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should include our order since it matches the date exactly
    assert any(o.get('order_id') == order_id for o in data), "Order with matching schedule date should be included"
    
    # Test filtering by date before schedule date
    before_date = day_before.strftime("%Y-%m-%d")
    print(f"\nSending request with end_date={before_date} (before schedule date)")
    response = client.get(f"/orders/?end_date={before_date}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # Should NOT include our order since schedule date is after the end_date
    assert not any(o.get('order_id') == order_id for o in data), "Order should not be included when end_date is before schedule date"
    
    # Test filtering by date after schedule date
    after_date = day_after.strftime("%Y-%m-%d")
    print(f"\nSending request with start_date={after_date} (after schedule date)")
    response = client.get(f"/orders/?start_date={after_date}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # Should NOT include our order since schedule date is before the start_date
    assert not any(o.get('order_id') == order_id for o in data), "Order should not be included when start_date is after schedule date"

def test_get_orders_pagination(client, db_session, test_customer, test_product, test_schedule):
    # Create multiple orders for pagination testing
    orders = []
    for i in range(5):  # Create 5 orders
        order = Order(
            line_id=test_customer.line_id,
            schedule_id=test_schedule.schedule_id,
            total_amount=100.00 * (i + 1),
            payment_method="cash"
        )
        db_session.add(order)
        db_session.flush()
        
        order_detail = OrderDetail(
            order_id=order.order_id,
            product_id=test_product.product_id,
            quantity=i + 1,
            unit_price=100.00,
            subtotal=100.00 * (i + 1)
        )
        db_session.add(order_detail)
        orders.append(order)
    
    db_session.commit()
    
    # Set authentication headers
    headers = {"Authorization": f"Bearer {test_customer.line_id}"}
    
    # Test pagination - first page (2 items)
    response = client.get("/orders/?skip=0&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Test pagination - second page (2 items)
    response = client.get("/orders/?skip=2&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Test pagination - third page (1 item remaining from our 5)
    response = client.get("/orders/?skip=4&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # At least our last order

def test_get_order_by_id(client, db_session, test_customer, test_product, test_schedule):
    # 先從數據庫中重新查詢對象
    customer = db_session.query(Customer).filter(Customer.line_id == test_customer.line_id).first()
    product = db_session.query(Product).filter(Product.product_id == test_product.product_id).first()
    schedule = db_session.query(Schedule).filter(Schedule.schedule_id == test_schedule.schedule_id).first()
    
    # 使用查詢到的對象創建訂單
    order = Order(
        line_id=customer.line_id,
        schedule_id=schedule.schedule_id,
        total_amount=200.00,
        payment_method="cash"
    )
    db_session.add(order)
    db_session.flush()

    order_detail = OrderDetail(
        order_id=order.order_id,
        product_id=product.product_id,
        quantity=2,
        unit_price=100.00,
        subtotal=200.00
    )
    db_session.add(order_detail)
    db_session.commit()
    
    # 保存訂單ID和客戶ID供後續使用
    order_id = order.order_id
    customer_line_id = customer.line_id

    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["line_id"] == customer_line_id

def test_get_customer_orders(client, db_session, test_customer, test_product, test_schedule):
    # Create test orders
    order1 = Order(
        line_id=test_customer.line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=200.00,
        payment_method="cash"
    )
    order2 = Order(
        line_id=test_customer.line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=300.00,
        payment_method="cash"
    )
    db_session.add_all([order1, order2])
    db_session.commit()

    response = client.get(f"/orders/customer/{test_customer.line_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert all(order["line_id"] == test_customer.line_id for order in data)

def test_update_order_status(client, db_session, test_customer, test_schedule):
    # Create test order
    order = Order(
        line_id=test_customer.line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=200.00,
        payment_method="cash"
    )
    db_session.add(order)
    db_session.commit()

    # Test valid status update
    status_update = {"order_status": "preparing"}
    response = client.patch(f"/orders/{order.order_id}/status", json=status_update)
    assert response.status_code == 200
    data = response.json()
    assert data["order_status"] == "preparing"

    # Test invalid status
    invalid_status = {"order_status": "invalid_status"}
    response = client.patch(f"/orders/{order.order_id}/status", json=invalid_status)
    assert response.status_code == 400

def test_update_payment_status(client, db_session, test_customer, test_schedule):
    # Create test order
    order = Order(
        line_id=test_customer.line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=200.00,
        payment_method="cash"
    )
    db_session.add(order)
    db_session.commit()

    # Test valid payment status update
    payment_update = {"payment_status": "paid"}
    response = client.patch(f"/orders/{order.order_id}/payment", json=payment_update)
    assert response.status_code == 200
    data = response.json()
    assert data["payment_status"] == "paid"

    # Test invalid payment status
    invalid_status = {"payment_status": "invalid_status"}
    response = client.patch(f"/orders/{order.order_id}/payment", json=invalid_status)
    assert response.status_code == 400

def test_order_not_found(client):
    # Test getting non-existent order
    response = client.get("/orders/99999")
    assert response.status_code == 404

    # Test updating non-existent order status
    status_update = {"order_status": "preparing"}
    response = client.patch("/orders/99999/status", json=status_update)
    assert response.status_code == 404

    # Test updating non-existent order payment
    payment_update = {"payment_status": "paid"}
    response = client.patch("/orders/99999/payment", json=payment_update)
    assert response.status_code == 404

    # Test deleting non-existent order
    response = client.delete("/orders/99999")
    assert response.status_code == 404


def test_delete_order(client, db_session, test_customer, test_schedule):
    # Create test order with pending status
    order = Order(
        line_id=test_customer.line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=200.00,
        payment_method="cash",
        order_status="pending"
    )
    db_session.add(order)
    db_session.commit()
    
    order_id = order.order_id  # Store the ID before deletion

    # Test successful deletion of pending order
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Order soft deleted successfully"

    # Clear the session and verify order is deleted from database
    db_session.expire_all()
    deleted_order = db_session.query(Order).filter(Order.order_id == order_id).first()
    assert deleted_order is None


def test_delete_completed_order(client, db_session, test_customer, test_schedule):
    # Create test order with completed status
    order = Order(
        line_id=test_customer.line_id,
        schedule_id=test_schedule.schedule_id,
        total_amount=200.00,
        payment_method="cash",
        order_status="completed"
    )
    db_session.add(order)
    db_session.commit()

    # Test cannot delete completed order
    response = client.delete(f"/orders/{order.order_id}")
    assert response.status_code == 400
    assert "Cannot delete completed orders" in response.json()["detail"]

    # Verify order still exists in database
    existing_order = db_session.query(Order).filter(Order.order_id == order.order_id).first()
    assert existing_order is not None
    assert existing_order.order_status == "completed"
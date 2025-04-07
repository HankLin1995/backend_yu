import pytest
from datetime import datetime
from app.order.models import Order, OrderDetail
from app.customer.models import Customer
from app.product.models import Product
from app.location.models import Schedule, PickupLocation

@pytest.fixture
def test_customer(db_session):
    customer = Customer(
        line_id="test_line_id",
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
    
    order_data = {
        "line_id": line_id,
        "schedule_id": schedule_id,
        "payment_method": "cash",
        "order_details": [
            {
                "product_id": product_id,
                "quantity": 2,
                "unit_price": product_price,
                "subtotal": product_price * 2
            }
        ]
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 200
    data = response.json()
    
    # 直接與請求數據比較，而不是與對象比較
    assert data["line_id"] == line_id
    assert data["schedule_id"] == schedule_id
    assert data["order_status"] == "pending"
    assert data["payment_status"] == "pending"
    assert len(data["order_details"]) == 1
    assert data["order_details"][0]["quantity"] == 2

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
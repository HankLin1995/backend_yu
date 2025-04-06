# import pytest
# from datetime import datetime
# from app.order.models import Order, OrderDetail
# from app.customer.models import Customer
# from app.product.models import Product
# from app.location.models import Schedule, PickupLocation


# @pytest.fixture
# def test_customer(db_session):
#     customer = Customer(
#         line_id="test_line_id",
#         name="Test Customer",
#         line_name="Test Line Name",
#         line_pic_url="http://example.com/pic.jpg",
#         phone="1234567890"
#     )
#     db_session.add(customer)
#     db_session.commit()
#     return customer


# @pytest.fixture
# def test_product(db_session):
#     product = Product(
#         product_name="Test Product",
#         price=100.00,
#         unit="piece",
#         stock_quantity=50
#     )
#     db_session.add(product)
#     db_session.commit()
#     return product


# @pytest.fixture
# def test_pickup_location(db_session):
#     location = PickupLocation(
#         district="Test District",
#         name="Test Location",
#         address="Test Address"
#     )
#     db_session.add(location)
#     db_session.commit()
#     return location

# @pytest.fixture
# def test_schedule(db_session, test_pickup_location):
#     schedule = Schedule(
#         date=datetime.now().date(),
#         location_id=test_pickup_location.location_id,
#         pickup_start_time=datetime.now().time(),
#         pickup_end_time=datetime.now().time(),
#         status="ACTIVE"
#     )
#     db_session.add(schedule)
#     db_session.commit()
#     return schedule


# def test_create_order(client, test_customer, test_product, test_schedule):
#     order_data = {
#         "line_id": test_customer.line_id,
#         "schedule_id": test_schedule.schedule_id,
#         "payment_method": "cash",
#         "order_details": [
#             {
#                 "product_id": test_product.product_id,
#                 "quantity": 2,
#                 "unit_price": float(test_product.price),
#                 "subtotal": float(test_product.price * 2)
#             }
#         ]
#     }

#     response = client.post("/orders/", json=order_data)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["line_id"] == test_customer.line_id
#     assert data["schedule_id"] == test_schedule.schedule_id
#     assert data["order_status"] == "pending"
#     assert data["payment_status"] == "pending"
#     assert len(data["order_details"]) == 1
#     assert data["order_details"][0]["quantity"] == 2


# def test_get_orders(client, db_session, test_customer, test_product, test_schedule):
#     # Create test order
#     order = Order(
#         line_id=test_customer.line_id,
#         schedule_id=test_schedule.schedule_id,
#         total_amount=200.00
#     )
#     db_session.add(order)
#     db_session.flush()

#     order_detail = OrderDetail(
#         order_id=order.order_id,
#         product_id=test_product.product_id,
#         quantity=2,
#         unit_price=100.00,
#         subtotal=200.00
#     )
#     db_session.add(order_detail)
#     db_session.commit()

#     response = client.get("/orders/")
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["order_id"] == order.order_id


# def test_get_order_by_id(client, db_session, test_customer, test_product, test_schedule):
#     # Create test order
#     order = Order(
#         line_id=test_customer.line_id,
#         schedule_id=test_schedule.schedule_id,
#         total_amount=200.00
#     )
#     db_session.add(order)
#     db_session.flush()

#     order_detail = OrderDetail(
#         order_id=order.order_id,
#         product_id=test_product.product_id,
#         quantity=2,
#         unit_price=100.00,
#         subtotal=200.00
#     )
#     db_session.add(order_detail)
#     db_session.commit()

#     response = client.get(f"/orders/{order.order_id}")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["order_id"] == order.order_id
#     assert data["line_id"] == test_customer.line_id


# def test_get_customer_orders(client, db_session, test_customer, test_product, test_schedule):
#     # Create test orders
#     order1 = Order(
#         line_id=test_customer.line_id,
#         schedule_id=test_schedule.schedule_id,
#         total_amount=200.00
#     )
#     order2 = Order(
#         line_id=test_customer.line_id,
#         schedule_id=test_schedule.schedule_id,
#         total_amount=300.00
#     )
#     db_session.add_all([order1, order2])
#     db_session.commit()

#     response = client.get(f"/orders/customer/{test_customer.line_id}")
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 2


# def test_update_order_status(client, db_session, test_customer, test_schedule):
#     # Create test order
#     order = Order(
#         line_id=test_customer.line_id,
#         schedule_id=test_schedule.schedule_id,
#         total_amount=200.00
#     )
#     db_session.add(order)
#     db_session.commit()

#     status_update = {"order_status": "paid"}
#     response = client.patch(f"/orders/{order.order_id}/status", json=status_update)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["order_status"] == "paid"


# def test_update_payment_status(client, db_session, test_customer, test_schedule):
#     # Create test order
#     order = Order(
#         line_id=test_customer.line_id,
#         schedule_id=test_schedule.schedule_id,
#         total_amount=200.00
#     )
#     db_session.add(order)
#     db_session.commit()

#     payment_update = {"payment_status": "paid"}
#     response = client.patch(f"/orders/{order.order_id}/payment", json=payment_update)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["payment_status"] == "paid"


# def test_invalid_order_status(client, db_session, test_customer, test_schedule):
#     # Create test order
#     order = Order(
#         line_id=test_customer.line_id,
#         schedule_id=test_schedule.schedule_id,
#         total_amount=200.00
#     )
#     db_session.add(order)
#     db_session.commit()

#     status_update = {"order_status": "invalid_status"}
#     response = client.patch(f"/orders/{order.order_id}/status", json=status_update)
#     assert response.status_code == 400


# def test_invalid_payment_status(client, db_session, test_customer, test_schedule):
#     # Create test order
#     order = Order(
#         line_id=test_customer.line_id,
#         schedule_id=test_schedule.schedule_id,
#         total_amount=200.00
#     )
#     db_session.add(order)
#     db_session.commit()

#     payment_update = {"payment_status": "invalid_status"}
#     response = client.patch(f"/orders/{order.order_id}/payment", json=payment_update)
#     assert response.status_code == 400

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

def test_create_product(client):
    # Create a test category first
    category_response = client.post("/categories/", json={
        "category_name": "Test Category"
    })
    assert category_response.status_code == 200
    category_id = category_response.json()["category_id"]

    # Test creating a product
    product_data = {
        "product_name": "Test Product",
        "description": "A test product description",
        "price": 1000,  # $10.00
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "stock_quantity": 100,
        "unit": "個",
        "arrival_date": "2025-06-01",
        "category_ids": [category_id]
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == product_data["product_name"]
    assert data["price"] == product_data["price"]
    assert data["stock_quantity"] == product_data["stock_quantity"]
    assert len(data["categories"]) == 1
    assert data["categories"][0]["category_id"] == category_id

def test_create_duplicate_product(client):
    # Create first product
    product_data = {
        "product_name": "Duplicate Product",
        "description": "Test description",
        "price": 1000,
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "stock_quantity": 100,
        "unit": "個",
        "arrival_date": "2025-06-10"
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200

    # Try to create duplicate product
    response = client.post("/products/", json=product_data)
    assert response.status_code == 400
    assert "Product name already exists" in response.json()["detail"]

def test_get_product(client):
    # Create a product first
    product_data = {
        "product_name": "Get Test Product",
        "description": "Test description",
        "price": 1000,
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "stock_quantity": 100,
        "unit": "個",
        "arrival_date": "2025-06-15"
    }
    create_response = client.post("/products/", json=product_data)
    assert create_response.status_code == 200
    product_id = create_response.json()["product_id"]

    # Test getting the product
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == product_data["product_name"]
    assert data["price"] == product_data["price"]

def test_list_products(client):
    # Create multiple products
    products = []
    for i in range(3):
        product_data = {
            "product_name": f"List Test Product {i}",
            "description": f"Test description {i}",
            "price": 1000 + i,
            "one_set_price": 1000 + i,
            "one_set_quantity": 5,
            "stock_quantity": 100 + i,
            "unit": "個",
            "arrival_date": f"2025-06-{20 + i}"
        }
        response = client.post("/products/", json=product_data)
        assert response.status_code == 200
        products.append(response.json())

    # Test listing products
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
def test_update_product(client):
    # Create a product first
    initial_data = {
        "product_name": "Update Test Product",
        "description": "Initial description",
        "price": 1000,
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "stock_quantity": 100,
        "unit": "個",
        "arrival_date": "2025-06-01"
    }
    create_response = client.post("/products/", json=initial_data)
    assert create_response.status_code == 200
    product_id = create_response.json()["product_id"]

    # Update the product
    update_data = {
        "product_name": "Updated Product Name",
        "description": "Updated description",
        "price": 2000,
        "one_set_price": 2000,
        "one_set_quantity": 5,
        "stock_quantity": 200,
        "unit": "組",
        "arrival_date": "2025-07-15"
    }
    response = client.put(f"/products/{product_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == update_data["product_name"]
    assert data["price"] == update_data["price"]
    assert data["stock_quantity"] == update_data["stock_quantity"]

def test_delete_product(client):
    # Create a product first
    product_data = {
        "product_name": "Delete Test Product",
        "description": "Test description",
        "price": 1000,
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "stock_quantity": 100,
        "unit": "個"
    }
    create_response = client.post("/products/", json=product_data)
    assert create_response.status_code == 200
    product_id = create_response.json()["product_id"]

    # Delete the product
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200

    # Verify product is not accessible
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404


# def test_create_original_product_discount(client):
#     # Create a product first
#     product_data = {
#         "product_name": "Original Discount Test Product",
#         "description": "Test description",
#         "price": 1000,
#         "one_set_price": 1000,
#         "one_set_quantity": 5,
#         "stock_quantity": 100,
#         "unit": "個"
#     }
#     create_response = client.post("/products/", json=product_data)
#     assert create_response.status_code == 200
#     product_id = create_response.json()["product_id"]

#     # Create a discount
#     discount_data = {
#         "quantity": 5,
#         "price": 800
#     }
#     response = client.post(f"/products/{product_id}/discounts", json=discount_data)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["quantity"] == discount_data["quantity"]
#     assert data["price"] == discount_data["price"]

#     # Try to create another discount
#     discount_data2={
#         "quantity": 5,
#         "price": 1000
#     }
#     response2 = client.post(f"/products/{product_id}/discounts", json=discount_data2)
#     assert response2.status_code == 200
#     data2 = response2.json()
#     assert data2["quantity"] == discount_data2["quantity"]
#     assert data2["price"] == discount_data2["price"]


# def test_update_stock(client):
#     # Create a product first
#     product_data = {
#         "product_name": "Stock Test Product",
#         "description": "Test description",
#         "price": 1000,
#         "stock_quantity": 100,
#         "unit": "個"
#     }
#     create_response = client.post("/products/", json=product_data)
#     assert create_response.status_code == 200
#     product_id = create_response.json()["product_id"]

#     # Update stock
#     new_quantity = 150
#     response = client.put(f"/products/{product_id}/stock?quantity={new_quantity}")
#     assert response.status_code == 200
#     assert response.json()["stock_quantity"] == new_quantity

# def test_invalid_stock_update(client):
#     # Create a product first
#     product_data = {
#         "product_name": "Invalid Stock Test Product",
#         "description": "Test description",
#         "price": 1000,
#         "stock_quantity": 100,
#         "unit": "個"
#     }
#     create_response = client.post("/products/", json=product_data)
#     assert create_response.status_code == 200
#     product_id = create_response.json()["product_id"]

#     # Try to update with invalid stock quantity
#     response = client.put(f"/products/{product_id}/stock?quantity=-1")
#     assert response.status_code == 422  # Validation error

# def test_product_photo_upload(client):
#     # Create a product first
#     product_data = {
#         "product_name": "Photo Test Product",
#         "description": "Test description",
#         "price": 1000,
#         "stock_quantity": 100,
#         "unit": "個"
#     }
#     create_response = client.post("/products/", json=product_data)
#     assert create_response.status_code == 200
#     product_id = create_response.json()["product_id"]

#     # Upload photo
#     test_image = create_test_image()
#     files = {"file": ("test.png", test_image, "image/png")}
#     data = {"description": "Test photo description"}
    
#     response = client.post(
#         f"/products/{product_id}/photos",
#         files=files,
#         data=data
#     )
#     assert response.status_code == 200
#     photo_data = response.json()
#     assert photo_data["product_id"] == product_id
#     assert photo_data["description"] == data["description"]
#     assert photo_data["image_hash"]
    
#     # Clean up test file
#     if os.path.exists(photo_data["file_path"]):
#         os.remove(photo_data["file_path"])

# def test_duplicate_photo_upload(client):
#     # Create a product first
#     product_data = {
#         "product_name": "Duplicate Photo Test Product",
#         "description": "Test description",
#         "price": 1000,
#         "stock_quantity": 100,
#         "unit": "個"
#     }
#     create_response = client.post("/products/", json=product_data)
#     assert create_response.status_code == 200
#     product_id = create_response.json()["product_id"]

#     # Upload first photo
#     test_image = create_test_image()
#     files = {"file": ("test.png", test_image, "image/png")}
#     first_response = client.post(
#         f"/products/{product_id}/photos",
#         files=files
#     )
#     assert first_response.status_code == 200
#     first_photo = first_response.json()

#     # Try to upload the same photo again
#     test_image.seek(0)
#     files = {"file": ("test2.png", test_image, "image/png")}
#     second_response = client.post(
#         f"/products/{product_id}/photos",
#         files=files
#     )
#     assert second_response.status_code == 400
#     assert "Duplicate image" in second_response.json()["detail"]

#     # Clean up test file
#     if os.path.exists(first_photo["file_path"]):
#         os.remove(first_photo["file_path"])

# def test_product_discount(client):
#     # Create a product first
#     product_data = {
#         "product_name": "Discount Test Product",
#         "description": "Test description",
#         "price": 1000,
#         "stock_quantity": 100,
#         "unit": "個"
#     }
#     create_response = client.post("/products/", json=product_data)
#     assert create_response.status_code == 200
#     product_id = create_response.json()["product_id"]

#     # Create discount
#     discount_data = {
#         "quantity": 10,
#         "price": 800  # Must be less than product price
#     }
#     response = client.post(f"/products/{product_id}/discounts", json=discount_data)
#     assert response.status_code == 200
#     discount = response.json()
#     assert discount["product_id"] == product_id
#     assert discount["quantity"] == discount_data["quantity"]
#     assert discount["price"] == discount_data["price"]

#     # List discounts
#     list_response = client.get(f"/products/{product_id}/discounts")
#     assert list_response.status_code == 200
#     discounts = list_response.json()
#     assert len(discounts) == 1
#     assert discounts[0]["quantity"] == discount_data["quantity"]

# def test_invalid_discount(client):
#     # Create a product first
#     product_data = {
#         "product_name": "Invalid Discount Test Product",
#         "description": "Test description",
#         "price": 1000,
#         "stock_quantity": 100,
#         "unit": "個"
#     }
#     create_response = client.post("/products/", json=product_data)
#     assert create_response.status_code == 200
#     product_id = create_response.json()["product_id"]

#     # Try to create invalid discount (price >= product price)
#     discount_data = {
#         "quantity": 10,
#         "price": 1000  # Same as product price
#     }
#     response = client.post(f"/products/{product_id}/discounts", json=discount_data)
#     assert response.status_code == 400
#     assert "Discount price must be less than product price" in response.json()["detail"]

# def test_delete_discount(client):
#     # Create a product first
#     product_data = {
#         "product_name": "Delete Discount Test Product",
#         "description": "Test description",
#         "price": 1000,
#         "stock_quantity": 100,
#         "unit": "個"
#     }
#     create_response = client.post("/products/", json=product_data)
#     assert create_response.status_code == 200
#     product_id = create_response.json()["product_id"]

#     # Create discount
#     discount_data = {
#         "quantity": 10,
#         "price": 800
#     }
#     discount_response = client.post(f"/products/{product_id}/discounts", json=discount_data)
#     assert discount_response.status_code == 200
#     discount_id = discount_response.json()["discount_id"]

#     # Delete discount
#     delete_response = client.delete(f"/products/{product_id}/discounts/{discount_id}")
#     assert delete_response.status_code == 200

#     # Verify discount is deleted
#     list_response = client.get(f"/products/{product_id}/discounts")
#     assert list_response.status_code == 200
#     assert len(list_response.json()) == 0

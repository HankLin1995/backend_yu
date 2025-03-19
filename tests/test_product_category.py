
def test_create_category(client):
    category_data = {
        "category_name": "Test Category"
    }
    response = client.post("/categories/", json=category_data)
    assert response.status_code == 200
    data = response.json()
    assert data["category_name"] == category_data["category_name"]
    assert data["category_id"] is not None  

    # Try to create duplicate category
    duplicate_response = client.post("/categories/", json=category_data)
    assert duplicate_response.status_code == 400
    assert "Category name already exists" in duplicate_response.json()["detail"]

def test_get_category(client):
    # Create a category first
    category_data = {
        "category_name": "Get Test Category"
    }
    create_response = client.post("/categories/", json=category_data)
    assert create_response.status_code == 200

def test_get_categories(client):
    # Create multiple categories
    categories = []
    for i in range(3):
        category_data = {
            "category_name": f"List Test Category {i}"
        }
        response = client.post("/categories/", json=category_data)
        assert response.status_code == 200
        categories.append(response.json())

    # Test listing categories
    response = client.get("/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

def test_create_product_category(client):
    # Create a category first
    category_data = {
        "category_name": "Product Category"
    }
    category_response = client.post("/categories/", json=category_data)
    assert category_response.status_code == 200
    category = category_response.json()

    # Create a product
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
    product = product_response.json()

    # Create a product category
    product_category_data = {
        "product_id": product["product_id"],
        "category_id": category["category_id"]
    }

    response = client.post("/products-categories/", json=product_category_data)
    assert response.status_code == 200
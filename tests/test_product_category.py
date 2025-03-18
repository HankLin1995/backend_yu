
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

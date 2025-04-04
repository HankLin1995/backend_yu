import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_customer():
    return {
        "line_id": "test_line_id",
        "name": "Test User",
        "line_name": "Test User",
        "line_pic_url": "https://example.com/pic.jpg",
        "phone": "0912345678",
        "email": "test@example.com",
        "address": "Test Address"
    }


def test_create_customer(client: TestClient, test_customer):
    response = client.post("/customers/", json=test_customer)
    assert response.status_code == 200
    data = response.json()
    assert data["line_id"] == test_customer["line_id"]
    assert data["line_name"] == test_customer["line_name"]
    assert "create_date" in data


def test_create_duplicate_customer(client: TestClient, test_customer):
    # First creation
    client.post("/customers/", json=test_customer)
    # Second creation should fail
    response = client.post("/customers/", json=test_customer)
    assert response.status_code == 400


def test_get_customer(client: TestClient, test_customer):
    # Create customer first
    client.post("/customers/", json=test_customer)
    # Get the customer
    response = client.get(f"/customers/{test_customer['line_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["line_id"] == test_customer["line_id"]
    assert data["line_name"] == test_customer["line_name"]


def test_get_nonexistent_customer(client: TestClient):
    response = client.get("/customers/nonexistent")
    assert response.status_code == 404


def test_list_customers(client: TestClient, test_customer):
    # Create a customer first
    client.post("/customers/", json=test_customer)
    # List customers
    response = client.get("/customers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(customer["line_id"] == test_customer["line_id"] for customer in data)


def test_update_customer(client: TestClient, test_customer):
    # Create customer first
    client.post("/customers/", json=test_customer)
    # Update the customer
    update_data = {
        "line_name": "Updated Name",
        "phone": "0987654321"
    }
    response = client.put(f"/customers/{test_customer['line_id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["line_name"] == update_data["line_name"]
    assert data["phone"] == update_data["phone"]
    assert data["email"] == test_customer["email"]  # Unchanged field


def test_update_nonexistent_customer(client: TestClient):
    response = client.put("/customers/nonexistent", json={"line_name": "New Name"})
    assert response.status_code == 404


def test_delete_customer(client: TestClient, test_customer):
    # Create customer first
    client.post("/customers/", json=test_customer)
    # Delete the customer
    response = client.delete(f"/customers/{test_customer['line_id']}")
    assert response.status_code == 200
    # Verify customer is deleted
    get_response = client.get(f"/customers/{test_customer['line_id']}")
    assert get_response.status_code == 404


def test_delete_nonexistent_customer(client: TestClient):
    response = client.delete("/customers/nonexistent")
    assert response.status_code == 404

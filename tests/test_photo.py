import pytest
from fastapi.testclient import TestClient
import io
from PIL import Image
import os
import hashlib
from app.photo.routes import get_upload_dir

def create_test_image():
    """Helper function to create a test image"""
    file = io.BytesIO()
    image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file

def test_upload_photo(client):
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

    # Upload photo
    test_image = create_test_image()
    files = {"file": ("test.png", test_image, "image/png")}
    form_data = {"product_id": product_id}

    response = client.post(
        f"/photos/upload/",
        files=files,
        data=form_data
    )
    assert response.status_code == 200
    assert response.json()["product_id"] == product_id
    assert response.json()["file_path"].endswith(".png")
    assert response.json()["image_hash"]
    
    # Clean up test file
    file_path = os.path.join(get_upload_dir(), response.json()["file_path"])
    if os.path.exists(file_path):
        os.remove(file_path)

def test_upload_duplicate_photo(client):
    # Create a test product
    product_data = {
        "product_name": "Test Product 2",
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

    # Upload first photo
    test_image = create_test_image()
    files = {"file": ("test.png", test_image, "image/png")}
    form_data = {"product_id": product_id}
    first_response = client.post(
        f"/photos/upload/",
        files=files,
        data=form_data
    )
    assert first_response.status_code == 200
    first_file_path = os.path.join(get_upload_dir(), first_response.json()["file_path"])

    # Try to upload the same photo again
    test_image.seek(0)
    files = {"file": ("test2.png", test_image, "image/png")}
    second_response = client.post(
        f"/photos/upload/",
        files=files,
        data=form_data
    )
    assert second_response.status_code == 400
    assert "This photo already exists" in second_response.json()["detail"]

    # Clean up test file
    if os.path.exists(first_file_path):
        os.remove(first_file_path)

def test_get_photo(client):
    # Create a test product
    product_data = {
        "product_name": "Test Product 3",
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

    # Upload photo
    test_image = create_test_image()
    files = {"file": ("test.png", test_image, "image/png")}
    form_data = {"product_id": product_id}
    upload_response = client.post(
        f"/photos/upload/",
        files=files,
        data=form_data
    )
    assert upload_response.status_code == 200
    photo_id = upload_response.json()["photo_id"]
    file_path = os.path.join(get_upload_dir(), upload_response.json()["file_path"])

    # Get photo
    response = client.get(f"/photos/{photo_id}")
    assert response.status_code == 200
    assert response.json()["photo_id"] == photo_id
    assert response.json()["product_id"] == product_id

    # Clean up test file
    if os.path.exists(file_path):
        os.remove(file_path)

def test_delete_photo(client):
    # Create a test product
    product_data = {
        "product_name": "Test Product 4",
        "description": "Test Description",
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "price": 1000,
        "stock_quantity": 100,
        "unit": "個"
    }
    product_response = client.post("/products/", json=product_data)
    assert product_response.status_code == 200
    product_id = product_response.json()["product_id"]

    # Upload photo
    test_image = create_test_image()
    files = {"file": ("test.png", test_image, "image/png")}
    form_data = {"product_id": product_id}
    upload_response = client.post(
        f"/photos/upload/",
        files=files,
        data=form_data
    )
    assert upload_response.status_code == 200
    photo_id = upload_response.json()["photo_id"]
    file_path = os.path.join(get_upload_dir(), upload_response.json()["file_path"])

    # Verify file exists
    assert os.path.exists(file_path)

    # Delete photo
    delete_response = client.delete(f"/photos/{photo_id}")
    assert delete_response.status_code == 200

    # Verify photo is deleted from database
    get_response = client.get(f"/photos/{photo_id}")
    assert get_response.status_code == 404

    # Verify file is deleted from filesystem
    assert not os.path.exists(file_path)

def test_delete_product_photos(client):
    # Create a test product
    product_data = {
        "product_name": "Test Product 5",
        "description": "Test Description",
        "one_set_price": 1000,
        "one_set_quantity": 5,
        "price": 1000,
        "stock_quantity": 100,
        "unit": "個"
    }
    product_response = client.post("/products/", json=product_data)
    assert product_response.status_code == 200
    product_id = product_response.json()["product_id"]

    # Upload photo
    test_image = create_test_image()
    files = {"file": ("test.png", test_image, "image/png")}
    form_data = {"product_id": product_id}
    upload_response = client.post(
        f"/photos/upload/",
        files=files,
        data=form_data
    )
    assert upload_response.status_code == 200
    photo_id = upload_response.json()["photo_id"]
    file_path = os.path.join(get_upload_dir(), upload_response.json()["file_path"])

    assert os.path.exists(file_path)

    # # Upload another photo
    # test_image2 = create_test_image()
    # files = {"file": ("test2.png", test_image2, "image/png")}
    # form_data = {"product_id": product_id}
    # upload_response2 = client.post(
    #     f"/photos/upload/",
    #     files=files,
    #     data=form_data
    # )
    # assert upload_response2.status_code == 200
    # photo_id2 = upload_response2.json()["photo_id"]
    # file_path2 = os.path.join(get_upload_dir(), upload_response2.json()["file_path"])

    # # Verify file exists
    # assert os.path.exists(file_path2)

    # Delete all photos of a product
    delete_response = client.delete(f"/photos/product/{product_id}")
    assert delete_response.status_code == 200

    # Verify photo is deleted from database
    get_response = client.get(f"/photos/{photo_id}")
    assert get_response.status_code == 404

    # get_response2 = client.get(f"/photos/{photo_id2}")
    # assert get_response2.status_code == 404

    # Verify file is deleted from filesystem
    assert not os.path.exists(file_path)
    # assert not os.path.exists(file_path2)
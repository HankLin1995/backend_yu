from datetime import date, time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.location import models
from tests.conftest import db_session

def test_create_pickup_location(client: TestClient):
    response = client.post(
        "/locations/",
        json={
            "district": "北港",
            "name": "北港圖書館前",
            "address": "雲林縣北港鎮文化路123號",
            "coordinate_x": 120.123456,
            "coordinate_y": 23.123456
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["district"] == "北港"
    assert data["name"] == "北港圖書館前"
    assert "location_id" in data

def test_get_pickup_locations(client: TestClient,db_session:db_session):
    # 創建測試數據
    location = models.PickupLocation(
        district="北斗",
        name="北斗國小",
        address="彰化縣北斗鎮文化路456號"
    )
    db_session.add(location)
    db_session.commit()

    response = client.get("/locations/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["district"] == "北斗"

def test_create_schedule(client: TestClient):
    # 先創建一個取貨地點
    location_response = client.post(
        "/locations/",
        json={
            "district": "莿桐",
            "name": "莿桐中華電信",
            "address": "雲林縣莿桐鄉中正路789號"
        }
    )
    location_id = location_response.json()["location_id"]

    response = client.post(
        "/schedules/",
        json={
            "date": "2025-04-02",
            "location_id": location_id,
            "pickup_start_time": "17:00:00",
            "pickup_end_time": "17:30:00",
            "status": "ACTIVE"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["location_id"] == location_id
    assert data["status"] == "ACTIVE"

def test_duplicate_schedule(client: TestClient):
    # 先創建一個取貨地點
    location_response = client.post(
        "/locations/",
        json={
            "district": "西螺",
            "name": "西螺文昌國小",
            "address": "雲林縣西螺鎮中正路321號"
        }
    )
    location_id = location_response.json()["location_id"]

    # 創建第一個排程
    schedule_data = {
        "date": "2025-04-02",
        "location_id": location_id,
        "pickup_start_time": "18:00:00",
        "pickup_end_time": "18:30:00",
        "status": "ACTIVE"
    }
    response1 = client.post("/schedules/", json=schedule_data)
    assert response1.status_code == 200

    # 嘗試創建重複的排程
    response2 = client.post("/schedules/", json=schedule_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

def test_get_schedules_by_date(client: TestClient):
    # 先創建一個取貨地點
    location_response = client.post(
        "/locations/",
        json={
            "district": "虎尾",
            "name": "虎尾科大",
            "address": "雲林縣虎尾鎮文化路123號"
        }
    )
    location_id = location_response.json()["location_id"]

    # 創建排程
    schedule_data = {
        "date": "2025-04-03",
        "location_id": location_id,
        "pickup_start_time": "17:00:00",
        "pickup_end_time": "17:30:00",
        "status": "ACTIVE"
    }
    client.post("/schedules/", json=schedule_data)

    # 用日期查詢排程
    response = client.get("/schedules/?date_filter=2025-04-03")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["date"] == "2025-04-03"

def test_update_schedule(client: TestClient):
    # 先創建一個取貨地點
    location_response = client.post(
        "/locations/",
        json={
            "district": "斗六",
            "name": "斗六火車站",
            "address": "雲林縣斗六市中山路123號"
        }
    )
    location_id = location_response.json()["location_id"]

    # 創建排程
    schedule_response = client.post(
        "/schedules/",
        json={
            "date": "2025-04-04",
            "location_id": location_id,
            "pickup_start_time": "17:00:00",
            "pickup_end_time": "17:30:00",
            "status": "ACTIVE"
        }
    )
    schedule_id = schedule_response.json()["schedule_id"]

    # 更新排程
    response = client.put(
        f"/schedules/{schedule_id}",
        json={
            "date": "2025-04-04",
            "location_id": location_id,
            "pickup_start_time": "17:30:00",
            "pickup_end_time": "18:00:00",
            "status": "ACTIVE"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["pickup_start_time"] == "17:30:00"
    assert data["pickup_end_time"] == "18:00:00"

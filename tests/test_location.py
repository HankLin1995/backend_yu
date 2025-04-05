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

def test_get_schedules_by_location(client: TestClient, db_session: Session):
    # 清理現有的排程數據
    db_session.query(models.Schedule).delete()
    db_session.commit()
    # 先創建一個取貨地點
    location_response = client.post(
        "/locations/",
        json={
            "district": "土庫",
            "name": "土庫國小",
            "address": "雲林縣土庫鎮中正路456號"
        }
    )
    location_id = location_response.json()["location_id"]

    # 創建一個過去的排程（昨天）
    past_schedule = {
        "date": "2025-04-04",  # 假設今天是2025-04-05
        "location_id": location_id,
        "pickup_start_time": "17:00:00",
        "pickup_end_time": "17:30:00",
        "status": "ACTIVE"
    }
    client.post("/schedules/", json=past_schedule)

    # 創建一個今天的排程
    today_schedule = {
        "date": "2025-04-05",
        "location_id": location_id,
        "pickup_start_time": "17:00:00",
        "pickup_end_time": "17:30:00",
        "status": "ACTIVE"
    }
    client.post("/schedules/", json=today_schedule)

    # 創建一個未來的排程
    future_schedule = {
        "date": "2025-04-06",
        "location_id": location_id,
        "pickup_start_time": "17:00:00",
        "pickup_end_time": "17:30:00",
        "status": "ACTIVE"
    }
    client.post("/schedules/", json=future_schedule)

    # 測試取得特定地點的排程
    response = client.get(f"/schedules/location/{location_id}")
    assert response.status_code == 200
    data = response.json()
    # 確認只返回今天和未來的排程（應該有2個）
    assert len(data) == 2
    
    # 確認所有返回的排程日期都是今天或之後
    for schedule in data:
        assert schedule["date"] >= "2025-04-05"  # 今天的日期
        assert schedule["location_id"] == location_id

    # 測試不存在的地點
    response = client.get("/schedules/location/99999")
    assert response.status_code == 404
    assert "Location not found" in response.json()["detail"]

import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta


@pytest.fixture
def test_usage_today():
    """今日的用量記錄"""
    return {
        "date": str(date.today()),
        "push_count": 10
    }


@pytest.fixture
def test_usage_yesterday():
    """昨日的用量記錄"""
    yesterday = date.today() - timedelta(days=1)
    return {
        "date": str(yesterday),
        "push_count": 15
    }


@pytest.fixture
def test_usage_last_week():
    """上週的用量記錄"""
    last_week = date.today() - timedelta(days=7)
    return {
        "date": str(last_week),
        "push_count": 20
    }


def test_create_usage_record(client: TestClient, test_usage_today):
    """測試創建用量記錄"""
    response = client.post("/linebot-usage/", json=test_usage_today)
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == test_usage_today["date"]
    assert data["push_count"] == test_usage_today["push_count"]


def test_create_duplicate_usage_record(client: TestClient, test_usage_today):
    """測試創建重複日期的用量記錄應該失敗"""
    # 第一次創建
    client.post("/linebot-usage/", json=test_usage_today)
    # 第二次創建應該失敗
    response = client.post("/linebot-usage/", json=test_usage_today)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_usage_by_date(client: TestClient, test_usage_today):
    """測試查詢特定日期的用量"""
    # 先創建記錄
    client.post("/linebot-usage/", json=test_usage_today)
    # 查詢記錄
    response = client.get(f"/linebot-usage/{test_usage_today['date']}")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == test_usage_today["date"]
    assert data["push_count"] == test_usage_today["push_count"]


def test_get_nonexistent_usage(client: TestClient):
    """測試查詢不存在的日期"""
    future_date = date.today() + timedelta(days=365)
    response = client.get(f"/linebot-usage/{future_date}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_usage(client: TestClient, test_usage_today, test_usage_yesterday, test_usage_last_week):
    """測試列出所有用量記錄"""
    # 創建多筆記錄
    client.post("/linebot-usage/", json=test_usage_today)
    client.post("/linebot-usage/", json=test_usage_yesterday)
    client.post("/linebot-usage/", json=test_usage_last_week)
    
    # 列出所有記錄
    response = client.get("/linebot-usage/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # 驗證是否按日期降序排列（最新的在前）
    dates = [record["date"] for record in data]
    assert dates == sorted(dates, reverse=True)


def test_list_usage_with_pagination(client: TestClient, test_usage_today, test_usage_yesterday):
    """測試分頁功能"""
    # 創建記錄
    client.post("/linebot-usage/", json=test_usage_today)
    client.post("/linebot-usage/", json=test_usage_yesterday)
    
    # 測試 limit
    response = client.get("/linebot-usage/?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    
    # 測試 skip
    response = client.get("/linebot-usage/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_increment_today_usage_new_record(client: TestClient):
    """測試增加今日用量（新記錄）"""
    response = client.post("/linebot-usage/increment")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == str(date.today())
    assert data["push_count"] == 1


def test_increment_today_usage_existing_record(client: TestClient):
    """測試增加今日用量（已存在記錄）"""
    # 第一次增加
    response1 = client.post("/linebot-usage/increment")
    assert response1.status_code == 200
    assert response1.json()["push_count"] == 1
    
    # 第二次增加
    response2 = client.post("/linebot-usage/increment")
    assert response2.status_code == 200
    assert response2.json()["push_count"] == 2
    
    # 第三次增加
    response3 = client.post("/linebot-usage/increment")
    assert response3.status_code == 200
    assert response3.json()["push_count"] == 3


def test_increment_multiple_times(client: TestClient):
    """測試多次增加用量"""
    increment_times = 5
    for i in range(increment_times):
        response = client.post("/linebot-usage/increment")
        assert response.status_code == 200
        assert response.json()["push_count"] == i + 1
    
    # 驗證最終計數
    today = date.today()
    response = client.get(f"/linebot-usage/{today}")
    assert response.status_code == 200
    assert response.json()["push_count"] == increment_times


def test_update_usage(client: TestClient, test_usage_today):
    """測試更新用量"""
    # 先創建記錄
    client.post("/linebot-usage/", json=test_usage_today)
    
    # 更新記錄
    update_data = {"push_count": 100}
    response = client.put(f"/linebot-usage/{test_usage_today['date']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["push_count"] == 100
    assert data["date"] == test_usage_today["date"]


def test_update_nonexistent_usage(client: TestClient):
    """測試更新不存在的記錄"""
    future_date = date.today() + timedelta(days=365)
    update_data = {"push_count": 50}
    response = client.put(f"/linebot-usage/{future_date}", json=update_data)
    assert response.status_code == 404


def test_get_monthly_stats(client: TestClient):
    """測試查詢月度統計"""
    today = date.today()
    
    # 創建本月的多筆記錄
    for i in range(5):
        usage_date = today - timedelta(days=i)
        usage_data = {
            "date": str(usage_date),
            "push_count": (i + 1) * 10  # 10, 20, 30, 40, 50
        }
        client.post("/linebot-usage/", json=usage_data)
    
    # 查詢本月統計
    response = client.get(f"/linebot-usage/stats/monthly?year={today.year}&month={today.month}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["year"] == today.year
    assert data["month"] == today.month
    assert data["total_pushes"] == 150  # 10+20+30+40+50
    assert data["average_pushes"] == 30.0  # 150/5
    assert data["max_pushes"] == 50
    assert data["days_recorded"] == 5


def test_get_monthly_stats_empty_month(client: TestClient):
    """測試查詢沒有資料的月份"""
    # 查詢未來的月份
    future_year = date.today().year + 1
    response = client.get(f"/linebot-usage/stats/monthly?year={future_year}&month=1")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_pushes"] == 0
    assert data["average_pushes"] == 0
    assert data["max_pushes"] == 0
    assert data["days_recorded"] == 0


def test_get_monthly_stats_december(client: TestClient):
    """測試查詢 12 月的統計（邊界測試）"""
    # 創建去年 12 月的記錄
    last_year = date.today().year - 1
    dec_date = date(last_year, 12, 25)
    usage_data = {
        "date": str(dec_date),
        "push_count": 100
    }
    client.post("/linebot-usage/", json=usage_data)
    
    # 查詢去年 12 月統計
    response = client.get(f"/linebot-usage/stats/monthly?year={last_year}&month=12")
    assert response.status_code == 200
    data = response.json()
    
    assert data["year"] == last_year
    assert data["month"] == 12
    assert data["total_pushes"] == 100


def test_delete_usage(client: TestClient, test_usage_yesterday):
    """測試刪除用量記錄"""
    # 先創建記錄
    client.post("/linebot-usage/", json=test_usage_yesterday)
    
    # 刪除記錄
    response = client.delete(f"/linebot-usage/{test_usage_yesterday['date']}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # 驗證記錄已被刪除
    get_response = client.get(f"/linebot-usage/{test_usage_yesterday['date']}")
    assert get_response.status_code == 404


def test_delete_nonexistent_usage(client: TestClient):
    """測試刪除不存在的記錄"""
    future_date = date.today() + timedelta(days=365)
    response = client.delete(f"/linebot-usage/{future_date}")
    assert response.status_code == 404


def test_usage_workflow(client: TestClient):
    """測試完整的工作流程"""
    # 1. 使用 increment 增加今日用量
    for _ in range(3):
        client.post("/linebot-usage/increment")
    
    # 2. 查詢今日用量
    today = date.today()
    response = client.get(f"/linebot-usage/{today}")
    assert response.status_code == 200
    assert response.json()["push_count"] == 3
    
    # 3. 手動更新用量
    update_response = client.put(f"/linebot-usage/{today}", json={"push_count": 10})
    assert update_response.status_code == 200
    assert update_response.json()["push_count"] == 10
    
    # 4. 再次增加用量
    increment_response = client.post("/linebot-usage/increment")
    assert increment_response.status_code == 200
    assert increment_response.json()["push_count"] == 11
    
    # 5. 查詢列表
    list_response = client.get("/linebot-usage/")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1


def test_zero_push_count(client: TestClient):
    """測試推送次數為 0 的情況"""
    today = date.today()
    usage_data = {
        "date": str(today),
        "push_count": 0
    }
    response = client.post("/linebot-usage/", json=usage_data)
    assert response.status_code == 200
    assert response.json()["push_count"] == 0


def test_large_push_count(client: TestClient):
    """測試大量推送次數"""
    today = date.today()
    usage_data = {
        "date": str(today),
        "push_count": 999999
    }
    response = client.post("/linebot-usage/", json=usage_data)
    assert response.status_code == 200
    assert response.json()["push_count"] == 999999

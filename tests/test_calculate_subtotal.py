import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from app.order.routes import calculate_item_subtotal
from app.product.models import Product, ProductDiscount

def test_basic_price_calculation():
    """測試基本價格計算（無折扣）"""
    # 創建模擬的產品和資料庫
    product = MagicMock(spec=Product)
    product.price = Decimal("100")
    product.one_set_quantity = None
    product.one_set_price = None
    
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    # 測試不同數量的計算
    for qty in [1, 2, 5]:
        result = calculate_item_subtotal(product, qty, mock_db)
        expected_price = float(product.price) * qty
        
        assert result["price"] == expected_price
        assert result["originalPrice"] == expected_price
        assert result["savedAmount"] == 0
        
    print("✅ 基本價格計算測試通過")

def test_set_price_calculation():
    """測試套裝價格計算"""
    # 創建模擬的套裝產品
    product = MagicMock(spec=Product)
    product.price = Decimal("50")
    product.one_set_quantity = 5
    product.one_set_price = Decimal("200")
    
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    # 測試不同數量的計算
    for qty in [1, 2, 3]:
        result = calculate_item_subtotal(product, qty, mock_db)
        expected_price = float(product.one_set_price) * qty
        
        assert result["price"] == expected_price
        assert result["originalPrice"] == expected_price
        assert result["savedAmount"] == 0
        
    print("✅ 套裝價格計算測試通過")

def test_discount_calculation():
    """測試折扣計算"""
    # 創建模擬的產品
    product = MagicMock(spec=Product)
    product.product_id = 1
    product.price = Decimal("120")
    product.one_set_quantity = None
    product.one_set_price = None
    
    # 創建模擬的折扣
    discount_2 = MagicMock(spec=ProductDiscount)
    discount_2.quantity = 2
    discount_2.price = Decimal("200")
    
    discount_5 = MagicMock(spec=ProductDiscount)
    discount_5.quantity = 5
    discount_5.price = Decimal("450")
    
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [discount_2, discount_5]
    
    # 測試案例：[數量, 預期價格, 預期節省金額]
    test_cases = [
        (1, 120, 0),     # 1個，無折扣
        (2, 200, 40),    # 2個，使用買2個折扣
        (3, 320, 40),    # 3個，使用買2個折扣 + 1個原價
        (4, 400, 80),    # 4個，使用買2個折扣 + 2個原價
        (5, 450, 150),   # 5個，使用買5個折扣
        (6, 570, 150),   # 6個，使用買5個折扣 + 1個原價
        (7, 690, 150),   # 7個，使用買5個折扣 + 2個原價
    ]
    
    for qty, expected_price, expected_saved in test_cases:
        result = calculate_item_subtotal(product, qty, mock_db)
        
        assert round(result["price"], 2) == expected_price, f"數量 {qty} 的價格計算錯誤"
        assert round(result["originalPrice"], 2) == qty * float(product.price), f"數量 {qty} 的原始價格計算錯誤"
        assert round(result["savedAmount"], 2) == expected_saved, f"數量 {qty} 的節省金額計算錯誤"
        
    print("✅ 折扣計算測試通過")

def test_frontend_consistency():
    """測試前端和後端計算邏輯一致性"""
    # 創建模擬的產品
    product = MagicMock(spec=Product)
    product.product_id = 1
    product.price = Decimal("100")
    product.one_set_quantity = None
    product.one_set_price = None
    
    # 創建模擬的折扣
    discount_2 = MagicMock(spec=ProductDiscount)
    discount_2.quantity = 2
    discount_2.price = Decimal("180")
    
    discount_5 = MagicMock(spec=ProductDiscount)
    discount_5.quantity = 5
    discount_5.price = Decimal("400")
    
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [discount_2, discount_5]
    
    # 模擬前端的 calculateItemPrice 函數
    def calculate_item_price_frontend(item):
        quantity = item["quantity"]
        discounts = item.get("discounts", [])
        base_price = item.get("originalUnitPrice") or (item.get("one_set_price") if item.get("one_set_quantity") else item["price"])
        original_total = base_price * quantity
        
        if discounts and len(discounts) > 0:
            # 按數量降序排序
            sorted_discounts = sorted(discounts, key=lambda d: d["quantity"], reverse=True)
            applicable_discount = next((d for d in sorted_discounts if quantity >= d["quantity"]), None)
            
            if applicable_discount:
                # 如果找到符合的折扣，使用折扣價格
                discount_sets = quantity // applicable_discount["quantity"]
                remaining_quantity = quantity % applicable_discount["quantity"]
                
                # 計算折扣價格和剩餘數量的原價
                final_price = (discount_sets * applicable_discount["price"]) + (remaining_quantity * base_price)
                
                return {
                    "price": final_price,
                    "originalPrice": original_total,
                    "savedAmount": original_total - final_price
                }
        
        return {
            "price": original_total,
            "originalPrice": original_total,
            "savedAmount": 0
        }
    
    # 轉換為前端格式的折扣
    frontend_discounts = [
        {"quantity": d.quantity, "price": float(d.price)}
        for d in [discount_2, discount_5]
    ]
    
    # 測試案例
    test_quantities = [1, 2, 3, 4, 5, 6, 7, 10]
    
    for qty in test_quantities:
        # 後端計算
        backend_result = calculate_item_subtotal(product, qty, mock_db)
        
        # 前端計算
        frontend_item = {
            "product_id": product.product_id,
            "price": float(product.price),
            "quantity": qty,
            "discounts": frontend_discounts
        }
        frontend_result = calculate_item_price_frontend(frontend_item)
        
        # 比較結果
        assert round(backend_result["price"], 2) == round(frontend_result["price"], 2), f"數量 {qty} 的價格計算不一致"
        assert round(backend_result["originalPrice"], 2) == round(frontend_result["originalPrice"], 2), f"數量 {qty} 的原始價格計算不一致"
        assert round(backend_result["savedAmount"], 2) == round(frontend_result["savedAmount"], 2), f"數量 {qty} 的節省金額計算不一致"
    
    print("✅ 前後端計算一致性測試通過")

if __name__ == "__main__":
    print("開始測試 calculate_item_subtotal 函數...")
    test_basic_price_calculation()
    test_set_price_calculation()
    test_discount_calculation()
    test_frontend_consistency()
    print("所有測試通過！✅")

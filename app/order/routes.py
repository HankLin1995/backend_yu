from typing import List, Optional
from decimal import Decimal
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.customer.models import Customer
from app.product.models import Product, ProductDiscount
from app.photo.models import ProductPhoto
from app.order import models, schemas
from app.auth.dependencies import get_current_user
from app.location.models import PickupLocation, Schedule
from typing import Dict, Any

router = APIRouter(prefix="/orders", tags=["orders"])


def calculate_item_subtotal(product: Product, quantity: int, db: Session) -> Dict[str, Any]:
    """
    Calculate item subtotal based on the same logic as calculateItemPrice in CartPage.jsx
    
    Args:
        product: The product object
        quantity: The quantity ordered
        db: Database session
        
    Returns:
        Dictionary with price, originalPrice, and savedAmount
    """
    # 使用原始單價（如果有），否則使用商品的單價
    # 注意：後端沒有 originalUnitPrice 的概念，所以只檢查 one_set_price 和 price
    base_price = float(product.one_set_price if product.one_set_quantity else product.price)
    original_total = base_price * quantity
    
    # 檢查是否有適用的折扣
    discounts = db.query(ProductDiscount)\
        .filter(ProductDiscount.product_id == product.product_id)\
        .all()
    
    if discounts:
        # 按數量降序排序，找到符合當前數量的最大折扣
        sorted_discounts = sorted(discounts, key=lambda d: d.quantity, reverse=True)
        
        # 尋找第一個適用的折扣（數量大於等於折扣要求數量）
        applicable_discount = next((d for d in sorted_discounts if quantity >= d.quantity), None)
        
        if applicable_discount:
            # 如果找到符合的折扣，使用折扣價格
            discount_sets = quantity // applicable_discount.quantity
            remaining_quantity = quantity % applicable_discount.quantity
            
            # 計算折扣價格和剩餘數量的原價
            final_price = (discount_sets * float(applicable_discount.price)) + (remaining_quantity * base_price)
            
            return {
                "price": final_price,
                "originalPrice": original_total,
                "savedAmount": original_total - final_price
            }
    
    # 如果沒有折扣，使用原價
    return {
        "price": original_total,
        "originalPrice": original_total,
        "savedAmount": 0
    }


@router.post("/{order_id}/details", response_model=schemas.Order)
def add_order_detail(order_id: int, detail: schemas.OrderDetailCreate,  db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    product = db.query(Product).filter(Product.product_id == detail.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    actual_quantity = detail.quantity
    if hasattr(product, 'one_set_quantity') and product.one_set_quantity and product.one_set_quantity > 0:
        actual_quantity = detail.quantity * product.one_set_quantity
    if product.stock_quantity < actual_quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.product_id}")
    product.stock_quantity -= actual_quantity
    db_detail = models.OrderDetail(
        order_id=order_id,
        product_id=detail.product_id,
        quantity=detail.quantity,
        unit_price=detail.unit_price,
        subtotal=detail.subtotal,
        discount_id=detail.discount_id
    )
    db.add(db_detail)
    # Recalculate total
    db_order.total_amount = sum(d.subtotal for d in db.query(models.OrderDetail).filter(models.OrderDetail.order_id == order_id)) + Decimal(str(detail.subtotal))
    db.commit()
    db.refresh(db_order)
    return db_order


@router.put("/{order_id}/details/{detail_id}", response_model=schemas.Order)
def update_order_detail(order_id: int, detail_id: int, detail: schemas.OrderDetailUpdate,  db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db_detail = db.query(models.OrderDetail).filter(models.OrderDetail.order_detail_id == detail_id, models.OrderDetail.order_id == order_id).first()
    if not db_detail:
        raise HTTPException(status_code=404, detail="Order detail not found")
    product = db.query(Product).filter(Product.product_id == detail.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    # 處理庫存差異
    old_actual = db_detail.quantity
    new_actual = detail.quantity
    if hasattr(product, 'one_set_quantity') and product.one_set_quantity and product.one_set_quantity > 0:
        old_actual = db_detail.quantity * product.one_set_quantity
        new_actual = detail.quantity * product.one_set_quantity
    diff = new_actual - old_actual
    if diff > 0 and product.stock_quantity < diff:
        raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.product_id}")
    product.stock_quantity -= diff
    db_detail.product_id = detail.product_id
    db_detail.quantity = detail.quantity
    db_detail.unit_price = detail.unit_price
    db_detail.subtotal = detail.subtotal
    db_detail.discount_id = detail.discount_id
    # Recalculate total
    db_order.total_amount = sum(d.subtotal for d in db.query(models.OrderDetail).filter(models.OrderDetail.order_id == order_id))
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{order_id}/details/{detail_id}", response_model=schemas.Order)
def delete_order_detail(order_id: int, detail_id: int, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db_detail = db.query(models.OrderDetail).filter(models.OrderDetail.order_detail_id == detail_id, models.OrderDetail.order_id == order_id).first()
    if not db_detail:
        raise HTTPException(status_code=404, detail="Order detail not found")
    product = db.query(Product).filter(Product.product_id == db_detail.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    actual_quantity = db_detail.quantity
    if hasattr(product, 'one_set_quantity') and product.one_set_quantity and product.one_set_quantity > 0:
        actual_quantity = db_detail.quantity * product.one_set_quantity
    product.stock_quantity += actual_quantity
    db.delete(db_detail)
    # Recalculate total
    db_order.total_amount = sum(d.subtotal for d in db.query(models.OrderDetail).filter(models.OrderDetail.order_id == order_id))
    db.commit()
    db.refresh(db_order)
    return db_order


@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # Create new order
    total_amount = order.total_amount # 取用前端過來的 total_amount

    # 檢查是否為超商取貨或宅配，這些情況下不需要 schedule_id
    if hasattr(order, 'delivery_method') and order.delivery_method in ['convenience_store', 'home_delivery']:
        # 創建訂單時不包含 schedule_id
        db_order = models.Order(
            line_id=order.line_id,
            payment_method=order.payment_method,
            total_amount=total_amount,
            delivery_method=order.delivery_method  # 確保保存配送方式
        )
        # 如果有提供配送地址，保存它
        if hasattr(order, 'delivery_address') and order.delivery_address:
            db_order.delivery_address = order.delivery_address
            
        # 記錄配送方式到日誌
        print(f"Creating order with delivery method: {order.delivery_method} and address: {getattr(order, 'delivery_address', 'Not provided')}")

    else:
        # 店鋪取貨，需要 schedule_id
        db_order = models.Order(
            line_id=order.line_id,
            schedule_id=order.schedule_id,
            payment_method=order.payment_method,
            total_amount=total_amount,
            delivery_method="store_pickup"  # 設定為店鋪取貨
        )
        # 記錄店鋪取貨到日誌
        print(f"Creating order with store pickup, schedule_id: {order.schedule_id}")
    
    db.add(db_order)
    db.flush()  # Get order_id without committing

    # Create order details and calculate total
    for detail in order.order_details:
        # Verify product exists and get current price
        product = db.query(Product).filter(Product.product_id == detail.product_id).first()
        if not product:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Product {detail.product_id} not found")
        
        # 計算實際需要的庫存數量
        actual_quantity = detail.quantity
        if product.one_set_quantity and product.one_set_quantity > 0:
            # 如果有設定一組數量，需要將訂購數量轉換為實際庫存數量
            actual_quantity = detail.quantity * product.one_set_quantity

        # Check if there's enough stock
        if product.stock_quantity < actual_quantity:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.product_id}. Available: {product.stock_quantity}, Requested: {actual_quantity} (Order quantity: {detail.quantity})"
            )
        
        # Reduce stock
        product.stock_quantity -= actual_quantity
        
        # 獲取產品價格並檢查折扣
        unit_price = float(product.price)  # 默認使用基本價格
        discount_id = None
        
        # 優先檢查前端傳來的折扣 ID
        if detail.discount_id:
            # 驗證折扣是否存在且適用於該產品
            discount = db.query(ProductDiscount).filter(
                ProductDiscount.discount_id == detail.discount_id,
                ProductDiscount.product_id == product.product_id
            ).first()
            
            # 如果找到有效的折扣，使用其價格
            if discount:
                discount_id = discount.discount_id
                unit_price = float(discount.price)  # 使用折扣價格
                # 折扣價格已經是總價，不需要再乘以數量
                subtotal = unit_price
                
                # 創建訂單詳情，使用後端計算的價格
                db_detail = models.OrderDetail(
                    order_id=db_order.order_id,
                    product_id=detail.product_id,
                    quantity=detail.quantity,
                    # unit_price=unit_price,  # 使用後端計算的單價
                    # subtotal=subtotal,      # 使用後端計算的小計
                    unit_price=detail.unit_price, # 使用前端傳來的單價
                    subtotal=detail.subtotal, # 使用前端傳來的小計
                    discount_id=discount_id
                )
                db.add(db_detail)
                total_amount += subtotal
                
                # 跳過後面的計算，直接處理下一個訂單項目
                continue
        
        # 如果沒有前端折扣 ID 或折扣無效，則根據數量查詢折扣
        # 直接尋找與購買數量完全匹配的折扣
        discount = db.query(ProductDiscount).filter(
            ProductDiscount.product_id == product.product_id,
            ProductDiscount.quantity == detail.quantity  # 購買數量完全匹配折扣要求數量
        ).first()
        
        # 如果找到完全匹配的折扣，使用其價格
        if discount:
            discount_id = discount.discount_id
            unit_price = float(discount.price)  # 使用折扣價格
            # 折扣價格已經是總價，不需要再乘以數量
            subtotal = unit_price
        # 如果沒有找到完全匹配的折扣但產品有套裝價格，使用套裝價格
        elif hasattr(product, 'one_set_price') and product.one_set_price:  
            unit_price = float(product.one_set_price)
            # 套裝價格需要乘以數量
            subtotal = unit_price * detail.quantity
        else:
            # 一般價格需要乘以數量
            subtotal = unit_price * detail.quantity
        
        # 創建訂單詳情，使用後端計算的價格
        db_detail = models.OrderDetail(
            order_id=db_order.order_id,
            product_id=detail.product_id,
            quantity=detail.quantity,
            # unit_price=unit_price,  # 使用後端計算的單價
            # subtotal=subtotal,      # 使用後端計算的小計
            unit_price=detail.unit_price, # 使用前端傳來的單價
            subtotal=detail.subtotal, # 使用前端傳來的小計
            discount_id=discount_id
        )
        db.add(db_detail)
        # total_amount += subtotal

    # Update order total
    # db_order.total_amount = total_amount
    
    try:
        db.commit()
        db.refresh(db_order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create order")
    
    return db_order


@router.get("/", response_model=List[schemas.Order])
def get_orders(
    skip: int = 0, 
    limit: int = 100, 
    line_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,

    current_user: Customer = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # 建立基本查詢，使用 join 來關聯 Schedule
    query = db.query(models.Order).join(Schedule)
    
    # 應用過濾條件
    if line_id:
        query = query.filter(models.Order.line_id == line_id)
    
    if start_date:
        # 根據 Schedule 的日期進行過濾
        query = query.filter(Schedule.date >= start_date)
    
    if end_date:
        # 根據 Schedule 的日期進行過濾
        query = query.filter(Schedule.date <= end_date)
    
    # 應用分頁
    orders = query.offset(skip).limit(limit).all()
    
    # 產品資訊已通過 SQLAlchemy 關聯自動載入
    # 不需要額外處理
    
    return orders


@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # 先檢查訂單是否存在
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 如果存在，再檢查授權
    # if current_user.line_id != order.line_id:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this order")
    
    # 增強訂單詳細資訊
    for detail in order.order_details:
        product = detail.product
        # 設置產品基本資訊
        detail.product_name = product.product_name
        detail.product_description = product.description
        
        # 獲取產品照片
        photo = db.query(ProductPhoto)\
            .filter(ProductPhoto.product_id == product.product_id)\
            .first()
        detail.product_photo_path = photo.file_path if photo else None
        
        # 使用當前價格和折扣重新計算價格
        item_subtotal = calculate_item_subtotal(product, detail.quantity, db)
        
        # 添加計算後的價格信息
        detail.current_price = item_subtotal["price"]
        detail.original_price = item_subtotal["originalPrice"]
        detail.saved_amount = item_subtotal["savedAmount"]
    
    return order


@router.get("/customer/{line_id}", response_model=List[schemas.Order])
def get_customer_orders(line_id: str, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # 先檢查客戶是否存在
    customer = db.query(Customer).filter(Customer.line_id == line_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # 如果存在，再檢查授權
    if current_user.line_id != line_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    # 使用 joinedload 預加載關聯數據
    orders = db.query(models.Order)\
        .filter(models.Order.line_id == line_id)\
        .all()
    
    return orders


@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, status_update: schemas.OrderStatusUpdate, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # 先檢查訂單是否存在
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # # 如果存在，再檢查授權
    # if current_user.line_id != order.line_id:
    #     raise HTTPException(status_code=403, detail="Not authorized to update this order")

    valid_statuses = ["pending", "paid", "preparing", "ready_for_pickup", "partial_completed", "completed", "cancelled"]
    if status_update.order_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    order.order_status = status_update.order_status
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/payment", response_model=schemas.Order)
def update_payment_status(order_id: int, payment_update: schemas.PaymentStatusUpdate, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # 先檢查訂單是否存在
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 如果存在，再檢查授權
    if current_user.line_id != order.line_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this order")

    valid_statuses = ["pending", "paid", "refunded"]
    if payment_update.payment_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    order.payment_status = payment_update.payment_status
    db.commit()
    db.refresh(order)
    return order

@router.patch("/{order_id}/schedule")
def update_order_schedule(order_id: int, schedule_update: schemas.OrderScheduleUpdate, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if order exists
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if the order status allows schedule changes
    if order.order_status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot update schedule for completed or cancelled orders"
        )
    
    # Check if the new schedule exists
    schedule = db.query(Schedule).filter(Schedule.schedule_id == schedule_update.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Update schedule_id
    order.schedule_id = schedule_update.schedule_id
    order.update_time = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return {"message": "Order schedule updated successfully", "schedule_id": order.schedule_id}

@router.delete("/{order_id}")
def delete_order(order_id: int, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # 先檢查訂單是否存在
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 如果存在，再檢查授權
    if current_user.line_id != order.line_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this order")
    
    if order.order_status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete completed orders"
        )
    
    # If order is in processing state, restore stock
    if order.order_status == "pending":
        for detail in order.order_details:
            product = detail.product
            # 計算實際需要的庫存數量
            actual_quantity = detail.quantity
            if product.one_set_quantity and product.one_set_quantity > 0:
                # 如果有設定一組數量，需要將訂購數量轉換為實際庫存數量
                actual_quantity = detail.quantity * product.one_set_quantity
            product.stock_quantity += actual_quantity
    
    # Delete the order (cascade will handle order_details)
    db.delete(order)
    db.commit()
    
    return {"message": "Order soft deleted successfully"}

STATUS_MAPPING = {
    "pending": "待處理",
    "paid": "已付款",
    "preparing": "準備中",
    "ready_for_pickup": "可取貨",
    #部分完成
    "partial_completed": "分批取貨",
    "completed": "已完成",
    "cancelled": "已取消"
}

@router.get("/list/all")
def get_orders_list(current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get all orders
    orders = db.query(models.Order).all()
    
    # Create a list to store all order data
    all_order_data = []
    
    # Process all orders
    for order in orders:
        # Get related data
        customer = db.query(Customer).filter(Customer.line_id == order.line_id).first()
        schedule = db.query(Schedule).filter(Schedule.schedule_id == order.schedule_id).first()
        location = db.query(PickupLocation).filter(PickupLocation.location_id == schedule.location_id).first() if schedule else None
        
        # Process each order detail
        for order_detail in order.order_details:
            product = db.query(Product).filter(Product.product_id == order_detail.product_id).first()
            
            # Format unit display
            if product and product.one_set_quantity > 1:
                unit_display = f"組(每組{product.one_set_quantity}{product.unit})"
                remark = ""
            else:
                unit_display = product.unit if product else ""
                remark = ""
            
            if product.arrival_date and product.arrival_date > date.today():
                remark = "未到貨"
            else:
                remark = ""
            
            # Calculate item subtotal based on CartPage.jsx calculateItemPrice logic
            item_subtotal = calculate_item_subtotal(product, order_detail.quantity, db)
            
            # Add this order detail to our list
            all_order_data.append({
                '訂單編號': order.order_id,
                # '訂單金額': order.total_amount,
                '訂購人': customer.name if customer else '',
                '電話': customer.phone if customer and customer.phone else '',
                '日期': schedule.date if schedule else '',
                '地點': location.name if location else '',
                '商品名稱': product.product_name if product else '',
                '數量': order_detail.quantity,
                '單位': unit_display,
                "小計金額": float(item_subtotal["price"]),
                '備註': remark,
                '明細編號': order_detail.order_detail_id,
                '領取狀態': "已領取" if order_detail.is_finish else "未領取",
                '訂單狀態': STATUS_MAPPING.get(order.order_status, ''),
                "配送方式": order.delivery_method,
                "配送地址": order.delivery_address,
                # "小計金額": float(item_subtotal["price"]),
                # "原始金額": float(item_subtotal["originalPrice"]),
                # "節省金額": float(item_subtotal["savedAmount"])
            })
    
    return all_order_data


@router.put("/{order_id}/details/{detail_id}/finish")
def update_order_detail_finish_status(order_id: int, detail_id: int, is_finish: bool, db: Session = Depends(get_db)):
    # 檢查訂單是否存在
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 檢查訂單明細是否存在
    order_detail = db.query(models.OrderDetail).filter(
        models.OrderDetail.order_detail_id == detail_id,
        models.OrderDetail.order_id == order_id
    ).first()
    if order_detail is None:
        raise HTTPException(status_code=404, detail="Order detail not found")
    
    # 更新領取狀態
    order_detail.is_finish = is_finish
    db.commit()
    db.refresh(order_detail)
    
    return {"message": "Order detail finish status updated successfully", "is_finish": order_detail.is_finish}

@router.get("/by-product/{product_id}/simple")
def get_orders_by_product_simple(product_id: int, db: Session = Depends(get_db)):
    """
    Get simplified information for all orders containing a specific product ID.
    Returns only essential order information: order ID, customer name, pickup location, 
    pickup date, pickup time, order amount, and order items.
    """
    # 查詢包含特定產品的所有訂單
    orders = db.query(models.Order)\
        .join(models.OrderDetail, models.Order.order_id == models.OrderDetail.order_id)\
        .filter(models.OrderDetail.product_id == product_id)\
        .distinct()\
        .all()
    
    result = []
    
    for order in orders:
        # 獲取客戶資訊
        customer = db.query(Customer).filter(Customer.line_id == order.line_id).first()
        
        # 獲取取貨時間與地點資訊
        schedule = db.query(Schedule).filter(Schedule.schedule_id == order.schedule_id).first()
        location = None
        if schedule:
            location = db.query(PickupLocation).filter(PickupLocation.location_id == schedule.location_id).first()
        
        # 獲取訂單項目
        order_items = []
        for detail in order.order_details:
            product = db.query(Product).filter(Product.product_id == detail.product_id).first()
            if product:
                order_items.append({
                    "product_name": product.product_name,
                    "quantity": detail.quantity,
                    "unit": product.unit,
                    "subtotal": float(detail.subtotal)
                })
        
        # 建立簡化的訂單資訊
        order_info = {
            "訂單編號": order.order_id,
            "訂購人": customer.name if customer else "",
            "取貨地點": location.name if location else "",
            "取貨日期": schedule.date.isoformat() if schedule and schedule.date else "",
            "取貨時間": f"{schedule.pickup_start_time} - {schedule.pickup_end_time}" if schedule else "",
            "訂購金額": float(order.total_amount),
            "訂購項目": order_items
        }
        
        result.append(order_info)
    
    return result


@router.put("/{order_id}/amount", response_model=schemas.Order)
def update_order_amount(order_id: int, amount_update: schemas.OrderAmountUpdate, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update the total amount of an order.
    
    This endpoint allows updating the total amount of an existing order.
    Only the order owner can update their order amount.
    """
    # 檢查訂單是否存在
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 檢查訂單狀態，已完成或已取消的訂單不允許更新金額
    if order.order_status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update amount for {order.order_status} orders"
        )
    
    # 更新訂單金額
    order.total_amount = amount_update.total_amount
    order.update_time = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order

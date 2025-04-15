from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.order import models, schemas
from app.product.models import Product
from app.photo.models import ProductPhoto
from app.customer.models import Customer
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # Create new order
    total_amount = 0
    db_order = models.Order(
        line_id=order.line_id,
        schedule_id=order.schedule_id,
        payment_method=order.payment_method,
        total_amount=total_amount
    )
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

        # Create order detail
        db_detail = models.OrderDetail(
            order_id=db_order.order_id,
            product_id=detail.product_id,
            quantity=detail.quantity,
            unit_price=detail.unit_price,  # 使用前端傳來的單價
            subtotal=detail.subtotal,      # 使用前端傳來的小計
            discount_id=detail.discount_id
        )
        db.add(db_detail)
        total_amount += detail.subtotal

    # Update order total
    db_order.total_amount = total_amount
    
    try:
        db.commit()
        db.refresh(db_order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create order")
    
    return db_order


@router.get("/", response_model=List[schemas.Order])
def get_orders(skip: int = 0, limit: int = 100, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    
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
    if current_user.line_id != order.line_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this order")
    
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
    
    # 產品資訊已通過 SQLAlchemy 關聯自動載入
    # 不需要額外處理
    
    return orders


@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, status_update: schemas.OrderStatusUpdate, current_user: Customer = Depends(get_current_user), db: Session = Depends(get_db)):
    # 先檢查訂單是否存在
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 如果存在，再檢查授權
    if current_user.line_id != order.line_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this order")

    valid_statuses = ["pending", "paid", "preparing", "ready_for_pickup", "completed", "cancelled"]
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
    if order.order_status == "processing":
        for detail in order.order_details:
            product = detail.product
            product.stock += detail.quantity
    
    # Delete the order (cascade will handle order_details)
    db.delete(order)
    db.commit()
    
    return {"message": "Order soft deleted successfully"}

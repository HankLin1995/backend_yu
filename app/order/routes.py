from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.order import models, schemas
from app.product.models import Product
from app.photo.models import ProductPhoto

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
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

        # Create order detail
        subtotal = product.price * detail.quantity
        db_detail = models.OrderDetail(
            order_id=db_order.order_id,
            product_id=detail.product_id,
            quantity=detail.quantity,
            # unit_price=product.price,
            # subtotal=subtotal,
            unit_price=detail.unit_price,  # 使用前端单价
            subtotal=detail.subtotal,      # 使用前端小计
            discount_id=detail.discount_id
        )
        db.add(db_detail)
        total_amount += detail.subtotal

    # Update order total
    db_order.total_amount = total_amount
    db.commit()
    db.refresh(db_order)
    
    # 增強訂單詳細資訊
    for detail in db_order.order_details:
        product = detail.product
        # 設置產品基本資訊
        detail.product_name = product.product_name
        detail.product_description = product.description
        
        # 獲取產品照片
        photo = db.query(ProductPhoto)\
            .filter(ProductPhoto.product_id == product.product_id)\
            .first()
        detail.product_photo_path = photo.file_path if photo else None
    
    return db_order


@router.get("/", response_model=List[schemas.Order])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    
    # 增強訂單詳細資訊
    for order in orders:
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
    
    return orders


@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
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
def get_customer_orders(line_id: str, db: Session = Depends(get_db)):
    # 使用 joinedload 預加載關聯數據
    orders = db.query(models.Order)\
        .filter(models.Order.line_id == line_id)\
        .all()
    
    # 增強訂單詳細資訊
    for order in orders:
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
    
    return orders


@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    valid_statuses = ["pending", "paid", "preparing", "ready_for_pickup", "completed", "cancelled"]
    if status_update.order_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    order.order_status = status_update.order_status
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/payment", response_model=schemas.Order)
def update_payment_status(order_id: int, payment_update: schemas.PaymentStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    valid_statuses = ["pending", "paid", "refunded"]
    if payment_update.payment_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    order.payment_status = payment_update.payment_status
    db.commit()
    db.refresh(order)
    return order

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
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

from sqlalchemy.orm import Session, joinedload
from . import models, schemas
from fastapi import HTTPException
from typing import List, Optional
import os

# Customer CRUD operations
def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    try:
        db.commit()
        db.refresh(db_customer)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Customer already exists")
    return db_customer

def update_customer(db: Session, line_id: str, customer: schemas.CustomerBase):
    db_customer = db.query(models.Customer).filter(models.Customer.line_id == line_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, value in customer.model_dump().items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, line_id: str):
    db_customer = db.query(models.Customer).filter(models.Customer.line_id == line_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Mark related orders as customer_deleted=True instead of actually deleting them
    customer_orders = db.query(models.Order).filter(models.Order.line_id == line_id).all()
    for order in customer_orders:
        order.customer_deleted = True
    
    db.delete(db_customer)
    db.commit()
    return {"message": "Customer deleted successfully"}

# Product CRUD operations
def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.product_id == product_id).first()

def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

# def update_product_stock(db: Session, product_id: int, quantity: int):
#     db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
#     if not db_product:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     db_product.stock_quantity = quantity
#     db.commit()
#     db.refresh(db_product)
#     return db_product

def delete_product(db: Session, product_id: int):
    # Get the product
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Mark all order details for this product as deleted
    order_details = db.query(models.OrderDetail).filter(models.OrderDetail.product_id == product_id).all()
    for detail in order_details:
        detail.product_deleted = True
    
    # Remove product from all categories
    db_product.categories = []
    
    # Delete all product files

    for photo in db_product.photos:
        file_path=photo.file_path
        if file_path:
            try:
                os.remove(file_path)
            except OSError:
                pass

    # Delete all product photos
    for photo in db_product.photos:
        db.delete(photo)

    # Delete the product
    db.delete(db_product)
    db.commit()
    
    return {"message": "Product deleted successfully"}

# Category CRUD operations

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def add_product_to_categories(db: Session, product_id: int, category_ids: List[int]):
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    categories = db.query(models.Category).filter(models.Category.category_id.in_(category_ids)).all()
    db_product.categories.extend(categories)
    db.commit()
    return db_product

def remove_product_category(db: Session, product_id: int, category_id: int):
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    category = db.query(models.Category).filter(models.Category.category_id == category_id).first()
    if category in db_product.categories:
        db_product.categories.remove(category)
        db.commit()
    return db_product

def delete_category(db: Session, category_id: int):
    db_category = db.query(models.Category).filter(models.Category.category_id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Remove all product associations
    db_category.products = []
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}

# Order CRUD operations
def create_order(db: Session, order: schemas.OrderCreate):
    # Create order
    total_amount = 0
    order_details = []
    
    # Verify stock and calculate total
    for detail in order.details:
        product = db.query(models.Product).filter(models.Product.product_id == detail.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {detail.product_id} not found")
        
        if product.stock_quantity < detail.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {detail.product_id}")
        
        unit_price = product.special_price if product.special_price is not None else product.price
        subtotal = unit_price * detail.quantity
        total_amount += subtotal
        
        # Create order detail
        order_detail = models.OrderDetail(
            product_id=detail.product_id,
            quantity=detail.quantity,
            unit_price=unit_price,
            subtotal=subtotal
        )
        order_details.append(order_detail)
        
        # Update stock
        product.stock_quantity -= detail.quantity
    
    # Create main order
    db_order = models.Order(
        line_id=order.line_id,
        order_status="pending",
        total_amount=total_amount,
        details=order_details
    )
    
    db.add(db_order)
    try:
        db.commit()
        db.refresh(db_order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating order")
    
    return db_order

def get_order(db: Session, order_id: int):
    return db.query(models.Order).options(
        joinedload(models.Order.details)
    ).filter(models.Order.order_id == order_id).first()

def update_order_status(db: Session, order_id: int, status: str):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate status transition
    valid_transitions = {
        "pending": ["processing", "cancelled"],
        "processing": ["completed", "cancelled"],
        "completed": [],
        "cancelled": []
    }
    
    if status not in valid_transitions.get(db_order.order_status, []):
        raise HTTPException(status_code=400, detail="Invalid status transition")
    
    # Handle stock updates for cancellation
    if status == "cancelled":
        for detail in db_order.details:
            product = db.query(models.Product).filter(models.Product.product_id == detail.product_id).first()
            if product:
                product.stock_quantity += detail.quantity
    
    db_order.order_status = status
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order_detail(db: Session, order_id: int, detail_id: int, quantity: int):
    detail = db.query(models.OrderDetail).filter(
        models.OrderDetail.order_id == order_id,
        models.OrderDetail.order_detail_id == detail_id
    ).first()
    
    if not detail:
        raise HTTPException(status_code=404, detail="Order detail not found")
    
    # Update quantity and recalculate subtotal
    detail.quantity = quantity
    detail.subtotal = detail.unit_price * quantity
    
    # Update order total
    order = detail.order
    order.total_amount = sum(d.subtotal for d in order.details)
    
    db.commit()
    db.refresh(detail)
    return detail

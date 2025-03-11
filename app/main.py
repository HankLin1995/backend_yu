from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="濠鮮後端 API")

# Customer endpoints
@app.post("/customers/", response_model=schemas.Customer, tags=["customers"])
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, customer=customer)

@app.put("/customers/{line_id}", response_model=schemas.Customer, tags=["customers"])
def update_customer(line_id: str, customer: schemas.CustomerBase, db: Session = Depends(get_db)):
    return crud.update_customer(db=db, line_id=line_id, customer=customer)

@app.delete("/customers/{line_id}", tags=["customers"])
def delete_customer(line_id: str, db: Session = Depends(get_db)):
    return crud.delete_customer(db=db, line_id=line_id)

# Product endpoints
@app.post("/products/", response_model=schemas.Product, tags=["products"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@app.get("/products/{product_id}", response_model=schemas.Product, tags=["products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=schemas.Product, tags=["products"])
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    return crud.update_product(db=db, product_id=product_id, product=product)

@app.put("/products/{product_id}/stock", response_model=schemas.Product, tags=["products"])
def update_product_stock(product_id: int, quantity: int, db: Session = Depends(get_db)):
    return crud.update_product_stock(db=db, product_id=product_id, quantity=quantity)

@app.delete("/products/{product_id}", tags=["products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    return crud.delete_product(db=db, product_id=product_id)

# Category endpoints
@app.post("/products/{product_id}/categories", tags=["categories"])
def add_product_categories(product_id: int, category_ids: List[int], db: Session = Depends(get_db)):
    return crud.add_product_to_categories(db=db, product_id=product_id, category_ids=category_ids)

@app.delete("/products/{product_id}/categories/{category_id}", tags=["categories"])
def remove_product_category(product_id: int, category_id: int, db: Session = Depends(get_db)):
    return crud.remove_product_category(db=db, product_id=product_id, category_id=category_id)

@app.post("/categories/", response_model=schemas.Category, tags=["categories"])
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db=db, category=category)

@app.delete("/categories/{category_id}", tags=["categories"])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    return crud.delete_category(db=db, category_id=category_id)

# Order endpoints
@app.post("/orders/", response_model=schemas.Order, tags=["orders"])
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

@app.get("/orders/{order_id}", response_model=schemas.Order, tags=["orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    try:
        order = crud.get_order(db=db, order_id=order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        print(f"Error getting order: {str(e)}")  # For debugging
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/orders/{order_id}/status", tags=["orders"])
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    return crud.update_order_status(db=db, order_id=order_id, status=status)

@app.put("/orders/{order_id}/details/{detail_id}", tags=["orders"])
def update_order_detail(
    order_id: int, detail_id: int, quantity: int, db: Session = Depends(get_db)
):
    return crud.update_order_detail(db=db, order_id=order_id, detail_id=detail_id, quantity=quantity)

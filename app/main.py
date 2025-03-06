from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="濠鮮後端 API")

# Customer endpoints
@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, customer=customer)

@app.put("/customers/{line_id}", response_model=schemas.Customer)
def update_customer(line_id: str, customer: schemas.CustomerBase, db: Session = Depends(get_db)):
    return crud.update_customer(db=db, line_id=line_id, customer=customer)

# Product endpoints
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    return crud.update_product(db=db, product_id=product_id, product=product)

@app.put("/products/{product_id}/stock", response_model=schemas.Product)
def update_product_stock(product_id: int, quantity: int, db: Session = Depends(get_db)):
    return crud.update_product_stock(db=db, product_id=product_id, quantity=quantity)

# Category endpoints
@app.post("/products/{product_id}/categories")
def add_product_categories(product_id: int, category_ids: List[int], db: Session = Depends(get_db)):
    return crud.add_product_to_categories(db=db, product_id=product_id, category_ids=category_ids)

@app.delete("/products/{product_id}/categories/{category_id}")
def remove_product_category(product_id: int, category_id: int, db: Session = Depends(get_db)):
    return crud.remove_product_category(db=db, product_id=product_id, category_id=category_id)

@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    return crud.delete_category(db=db, category_id=category_id)

# Order endpoints
@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    return crud.update_order_status(db=db, order_id=order_id, status=status)

@app.put("/orders/{order_id}/details/{detail_id}")
def update_order_detail(
    order_id: int, detail_id: int, quantity: int, db: Session = Depends(get_db)
):
    return crud.update_order_detail(db=db, order_id=order_id, detail_id=detail_id, quantity=quantity)

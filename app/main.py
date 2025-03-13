from fastapi import FastAPI, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import engine, get_db
from .database import UPLOAD_DIR
import os
import datetime
import hashlib
import shutil

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

@app.get("/products/", response_model=List[schemas.Product], tags=["products"])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_products(db=db, skip=skip, limit=limit)

@app.get("/products/{product_id}", response_model=schemas.Product, tags=["products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=schemas.Product, tags=["products"])
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    return crud.update_product(db=db, product_id=product_id, product=product)

# @app.put("/products/{product_id}/stock", response_model=schemas.Product, tags=["products"])
# def update_product_stock(product_id: int, quantity: int, db: Session = Depends(get_db)):
#     return crud.update_product_stock(db=db, product_id=product_id, quantity=quantity)

@app.delete("/products/{product_id}", tags=["products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    return crud.delete_product(db=db, product_id=product_id)

@app.post("/products/{product_id}/discounts", tags=["products"])
def add_product_discount(product_id: int, discount: schemas.ProductDiscount, db: Session = Depends(get_db)):
    # check if product exist and quantity used
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # check if quantity is valid
    if discount.quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid quantity")
    
    # check if price is valid
    if discount.price <= 0:
        raise HTTPException(status_code=400, detail="Invalid price")
    
    # check if discount already exists
    existing_discount = db.query(models.ProductDiscount).filter(
        models.ProductDiscount.product_id == product_id,
        models.ProductDiscount.quantity == discount.quantity
    ).first()
    if existing_discount:
        raise HTTPException(status_code=400, detail="Discount already exists")
    
    # add discount
    db_discount = models.ProductDiscount(
        product_id=product_id,
        quantity=discount.quantity,
        price=discount.price
    )
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

@app.get("/products/{product_id}/discounts", response_model=List[schemas.ProductDiscount], tags=["products"])
def get_product_discounts(product_id: int, quantity: int, db: Session = Depends(get_db)):
    return crud.get_product_discounts(db=db, product_id=product_id, quantity=quantity)

@app.delete("/products/{product_id}/discounts/{discount_id}", tags=["products"])
def remove_product_discount(product_id: int, discount_id: int, db: Session = Depends(get_db)):
    return crud.remove_product_discount(db=db, product_id=product_id, discount_id=discount_id)



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

# Files

@app.post("/products/{product_id}/upload/", response_model=schemas.Photo, tags=["photos"])
async def upload_photo(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上傳照片檔案的端點
    
    Args:
        file: 上傳的檔案，必須是圖片格式
        product_id: 商品ID
    """
    # 檢查商品是否存在
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 驗證文件格式
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # 讀取文件內容
        contents = await file.read()
        
        # 計算圖片雜湊值
        image_hash = hashlib.md5(contents).hexdigest()
        
        # 檢查重複圖片
        existing_photo = db.query(models.ProductPhoto).filter(
            models.ProductPhoto.image_hash == image_hash,
            models.ProductPhoto.product_id == product_id
        ).first()
        
        if existing_photo:
            raise HTTPException(status_code=400, detail="相同的照片已經存在")
        
        # 生成唯一的文件名
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{product_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
        
        # 保存文件到指定目錄
        file_path = os.path.join(UPLOAD_DIR, "products", unique_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # 創建資料庫記錄
        db_photo = models.ProductPhoto(
            product_id=product_id,
            file_path=file_path,
            description=file.filename,
            image_hash=image_hash
        )
        
        db.add(db_photo)
        db.commit()
        db.refresh(db_photo)
        
        return {
            "photo_id": db_photo.photo_id,
            "file_path": db_photo.file_path,
            "image_hash": db_photo.image_hash,
            "create_time": db_photo.created_date
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # 如果發生錯誤，清理上傳的檔案
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"檔案上傳失敗: {str(e)}")

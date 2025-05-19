from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_,insert
from typing import List, Optional
import hashlib
from datetime import datetime
import os

from ..db import get_db
from . import models, schemas

router = APIRouter()

@router.post("/products/", response_model=schemas.Product, tags=["Products"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Check for duplicate product name
    existing_product = db.query(models.Product).filter(models.Product.product_name == product.product_name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product name already exists")
    
    # Create new product
    db_product = models.Product(
        product_name=product.product_name,
        description=product.description,
        price=product.price,
        one_set_price=product.one_set_price,
        one_set_quantity=product.one_set_quantity,
        stock_quantity=product.stock_quantity,
        unit=product.unit,
        arrival_date=product.arrival_date
    )
    
    # Add categories if provided
    if product.category_ids:
        categories = db.query(models.Category).filter(
            models.Category.category_id.in_(product.category_ids)
        ).all()
        if len(categories) != len(product.category_ids):
            raise HTTPException(status_code=400, detail="Invalid category ID")
        db_product.categories = categories
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products/", response_model=List[schemas.Product], tags=["Products"])
def list_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)
    if category_id:
        query = query.join(models.Product.categories).filter(models.Category.category_id == category_id)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/products/{product_id}", response_model=schemas.Product, tags=["Products"])

def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/products/{product_id}", tags=["Products"])

def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.put("/products/{product_id}", response_model=schemas.Product, tags=["Products"])

def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check for duplicate name if name is being changed
    if product.product_name != db_product.product_name:
        existing_product = db.query(models.Product).filter(models.Product.product_name == product.product_name).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Product name already exists")
    
    # Update product fields
    for field, value in product.model_dump(exclude_unset=True).items():
        if field == 'category_ids':
            if value:
                categories = db.query(models.Category).filter(
                    models.Category.category_id.in_(value)
                ).all()
                if len(categories) != len(value):
                    raise HTTPException(status_code=400, detail="Invalid category ID")
                db_product.categories = categories
        else:
            setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

# Category Routes

@router.post("/categories/", response_model=schemas.Category, tags=["Categories"])

def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    # Check for duplicate category name
    existing_category = db.query(models.Category).filter(models.Category.category_name == category.category_name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    # Create new category
    db_category = models.Category(
        category_name=category.category_name
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories/", response_model=List[schemas.Category], tags=["Categories"])

def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@router.get("/categories/{category_id}", response_model=schemas.Category, tags=["Categories"])

def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/categories/{category_id}", tags=["Categories"])

def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}

# Product Category Routes

@router.post("/products-categories/", tags=["Product Categories"])

def create_product_category(
    product_category: schemas.ProductCategoryCreate, db: Session = Depends(get_db)
):
    # Check if the product and category exist in the database
    product = db.query(models.Product).filter(models.Product.product_id == product_category.product_id).first()
    category = db.query(models.Category).filter(models.Category.category_id == product_category.category_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_product_category = models.ProductsCategories(
        product_id=product_category.product_id,
        category_id=product_category.category_id
    )
    db.add(db_product_category)
    db.commit()

    return {
        "product_id": product_category.product_id,
        "category_id": product_category.category_id
    }

# def add_product_category(product_category:schemas.ProductCategory, db: Session = Depends(get_db)):
#     product = db.query(models.Product).filter(models.Product.product_id ==  product_category.product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     category = db.query(models.Category).filter(models.Category.category_id == product_category.category_id).first()
#     if not category:
#         raise HTTPException(status_code=404, detail="Category not found")
    
#     db_product_category = models.ProductsCategories(
#         product_id = product_category.product_id,
#         category_id = product_category.category_id
#     )
#     db.add(db_product_category)
#     db.commit()
#     return {"message": "Category added successfully"}

@router.delete("/products/{product_id}/categories", tags=["Product Categories"])

def delete_all_product_categories(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.categories = []
    db.commit()
    return {"message": "All categories deleted successfully"}

# Product Discount Routes

@router.post("/products/{product_id}/discounts", response_model=schemas.ProductDiscount, tags=["Product Discounts"])

def create_product_discount(product_id: int, discount: schemas.ProductDiscountCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_discount = models.ProductDiscount(
        product_id=product_id,
        quantity=discount.quantity,
        price=discount.price
    )
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

@router.get("/products/{product_id}/discounts", response_model=List[schemas.ProductDiscount], tags=["Product Discounts"])

def list_product_discounts(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.discounts

@router.delete("/products/{product_id}/discounts", tags=["Product Discounts"])
def delete_all_product_discounts(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 獲取該產品的所有折扣
    discounts = db.query(models.ProductDiscount).filter(
        models.ProductDiscount.product_id == product_id
    ).all()
    
    if not discounts:
        return {"message": "No discounts found for this product"}
    
    # 從order_details中獲取被引用的折扣ID列表
    from app.order.models import OrderDetail
    referenced_discount_ids = db.query(models.ProductDiscount.discount_id).join(
        OrderDetail,
        OrderDetail.discount_id == models.ProductDiscount.discount_id
    ).filter(models.ProductDiscount.product_id == product_id).distinct().all()
    
    # 轉換為簡單列表
    referenced_ids = [id[0] for id in referenced_discount_ids]
    
    # 計數器
    deleted_count = 0
    skipped_count = 0
    
    # 逐個檢查並刪除未被引用的折扣
    for discount in discounts:
        if discount.discount_id in referenced_ids:
            # 跳過被引用的折扣
            skipped_count += 1
        else:
            # 刪除未被引用的折扣
            db.delete(discount)
            deleted_count += 1
    
    db.commit()
    
    # 返回結果訊息
    if skipped_count > 0 and deleted_count > 0:
        return {
            "message": f"Deleted {deleted_count} discounts successfully. Skipped {skipped_count} discounts that are referenced in orders."
        }
    elif skipped_count > 0:
        return {
            "message": f"No discounts were deleted. Skipped {skipped_count} discounts that are referenced in orders."
        }
    else:
        return {"message": "All discounts deleted successfully"}

@router.put("/products/{product_id}/discounts", response_model=List[schemas.ProductDiscount], tags=["Product Discounts"])
def update_product_discounts(product_id: int, discounts: List[schemas.ProductDiscountCreate], db: Session = Depends(get_db)):
    """
    更新產品折扣，採用安全策略：
    1. 檢查每個折扣的quantity是否已被訂單使用
    2. 如果已被使用，則跳過該折扣的更新
    3. 如果未被使用，則新增或更新該折扣
    """
    # 檢查產品是否存在
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 從訂單詳情中獲取被使用的折扣數量
    from app.order.models import OrderDetail
    used_quantities = db.query(models.ProductDiscount.quantity).join(
        OrderDetail,
        OrderDetail.discount_id == models.ProductDiscount.discount_id
    ).filter(models.ProductDiscount.product_id == product_id).distinct().all()
    used_quantities = [q[0] for q in used_quantities]  # 轉換為簡單列表
    
    # 獲取當前所有折扣
    current_discounts = db.query(models.ProductDiscount).filter(
        models.ProductDiscount.product_id == product_id
    ).all()
    
    # 創建當前折扣的映射 (quantity -> discount)
    current_discount_map = {d.quantity: d for d in current_discounts}
    
    # 記錄跳過和處理的折扣
    skipped_discounts = []
    processed_discounts = []
    
    # 處理每個新折扣
    for discount_data in discounts:
        # 檢查該數量是否已被訂單使用
        if discount_data.quantity in used_quantities:
            # 如果已被使用，則跳過該折扣
            if discount_data.quantity in current_discount_map:
                skipped_discounts.append(current_discount_map[discount_data.quantity])
        else:
            # 如果未被使用，則新增或更新
            if discount_data.quantity in current_discount_map:
                # 更新現有折扣
                existing_discount = current_discount_map[discount_data.quantity]
                existing_discount.price = discount_data.price
                processed_discounts.append(existing_discount)
            else:
                # 創建新折扣
                new_discount = models.ProductDiscount(
                    product_id=product_id,
                    quantity=discount_data.quantity,
                    price=discount_data.price
                )
                db.add(new_discount)
                processed_discounts.append(new_discount)
    
    # 刪除未被使用且不在新列表中的折扣
    new_quantities = {d.quantity for d in discounts}
    for discount in current_discounts:
        if discount.quantity not in new_quantities and discount.quantity not in used_quantities:
            db.delete(discount)
    
    db.commit()
    
    # 重新獲取所有折扣以確保數據最新
    updated_discounts = db.query(models.ProductDiscount).filter(
        models.ProductDiscount.product_id == product_id
    ).all()
    
    # 如果有跳過的折扣，添加警告訊息
    if skipped_discounts:
        skipped_quantities = [str(d.quantity) for d in skipped_discounts]
        warning_message = f"Warning: Discounts for quantities {', '.join(skipped_quantities)} are already in use and were not updated."
        # 在正常情況下，我們可以使用響應標頭或其他方式返回警告
        # 但在這裡，我們只能返回折扣列表
        # 可以在日誌中記錄警告或考慮其他方式通知用戶
        print(warning_message)  # 在日誌中記錄
    
    return updated_discounts


# @router.get("/products/{product_id}", response_model=schemas.Product)
# def get_product(product_id: int, db: Session = Depends(get_db)):
#     product = db.query(models.Product).filter(
#         and_(
#             models.Product.product_id == product_id,
#             models.Product.is_deleted == False
#         )
#     ).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product

# @router.put("/products/{product_id}", response_model=schemas.Product)
# def update_product(
#     product_id: int,
#     product: schemas.ProductUpdate,
#     db: Session = Depends(get_db)
# ):
#     db_product = db.query(models.Product).filter(
#         and_(
#             models.Product.product_id == product_id,
#             models.Product.is_deleted == False
#         )
#     ).first()
#     if not db_product:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     # Check for duplicate name if name is being changed
#     if product.product_name != db_product.product_name:
#         existing_product = db.query(models.Product).filter(
#             and_(
#                 models.Product.product_name == product.product_name,
#                 models.Product.is_deleted == False,
#                 models.Product.product_id != product_id
#             )
#         ).first()
#         if existing_product:
#             raise HTTPException(status_code=400, detail="Product name already exists")
    
#     # Update product fields
#     for field, value in product.model_dump(exclude_unset=True).items():
#         if field == 'category_ids':
#             if value:
#                 categories = db.query(models.Category).filter(
#                     models.Category.category_id.in_(value)
#                 ).all()
#                 if len(categories) != len(value):
#                     raise HTTPException(status_code=400, detail="Invalid category ID")
#                 db_product.categories = categories
#         else:
#             setattr(db_product, field, value)
    
#     db.commit()
#     db.refresh(db_product)
#     return db_product

# @router.delete("/products/{product_id}")
# def delete_product(product_id: int, db: Session = Depends(get_db)):
#     db_product = db.query(models.Product).filter(
#         and_(
#             models.Product.product_id == product_id,
#             models.Product.is_deleted == False
#         )
#     ).first()
#     if not db_product:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     # Implement soft delete
#     db_product.is_deleted = True
    
#     # Mark related order details as product_deleted
#     for order_detail in db_product.orders:
#         order_detail.product_deleted = True
    
#     db.commit()
#     return {"message": "Product deleted successfully"}

# @router.put("/products/{product_id}/stock")
# def update_stock(
#     product_id: int,
#     quantity: int = Query(..., gt=0),
#     db: Session = Depends(get_db)
# ):
#     db_product = db.query(models.Product).filter(
#         and_(
#             models.Product.product_id == product_id,
#             models.Product.is_deleted == False
#         )
#     ).first()
#     if not db_product:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     db_product.stock_quantity = quantity
#     db.commit()
#     db.refresh(db_product)
#     return db_product

# @router.post("/products/{product_id}/photos", response_model=schemas.Photo)
# async def upload_photo(
#     product_id: int,
#     file: UploadFile = File(...),
#     description: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     # Validate product exists
#     product = db.query(models.Product).filter(
#         and_(
#             models.Product.product_id == product_id,
#             models.Product.is_deleted == False
#         )
#     ).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     # Validate file type
#     if not file.content_type.startswith('image/'):
#         raise HTTPException(status_code=400, detail="File must be an image")
    
#     # Calculate file hash
#     contents = await file.read()
#     file_hash = hashlib.md5(contents).hexdigest()
    
#     # Check for duplicate image
#     existing_photo = db.query(models.ProductPhoto).filter(
#         models.ProductPhoto.image_hash == file_hash
#     ).first()
#     if existing_photo:
#         raise HTTPException(status_code=400, detail="Duplicate image")
    
#     # Create unique filename
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     extension = os.path.splitext(file.filename)[1]
#     filename = f"{product_id}_{timestamp}{extension}"
    
#     # Save file
#     file_path = f"uploads/products/{filename}"
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)
#     with open(file_path, "wb") as f:
#         f.write(contents)
    
#     # Create photo record
#     db_photo = models.ProductPhoto(
#         product_id=product_id,
#         file_path=file_path,
#         description=description,
#         image_hash=file_hash
#     )
#     db.add(db_photo)
#     db.commit()
#     db.refresh(db_photo)
#     return db_photo

# @router.post("/products/{product_id}/discounts", response_model=schemas.ProductDiscount)
# def create_discount(
#     product_id: int,
#     discount: schemas.ProductDiscountCreate,
#     db: Session = Depends(get_db)
# ):
#     # Validate product exists
#     product = db.query(models.Product).filter(
#         and_(
#             models.Product.product_id == product_id,
#             models.Product.is_deleted == False
#         )
#     ).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
    
#     # Check for existing discount with same quantity
#     existing_discount = db.query(models.ProductDiscount).filter(
#         and_(
#             models.ProductDiscount.product_id == product_id,
#             models.ProductDiscount.quantity == discount.quantity
#         )
#     ).first()
#     if existing_discount:
#         raise HTTPException(status_code=400, detail="Discount already exists for this quantity")
    
#     # Validate discount price
#     if discount.price >= product.price:
#         raise HTTPException(status_code=400, detail="Discount price must be less than product price")
    
#     db_discount = models.ProductDiscount(
#         product_id=product_id,
#         quantity=discount.quantity,
#         price=discount.price
#     )
#     db.add(db_discount)
#     db.commit()
#     db.refresh(db_discount)
#     return db_discount

# @router.get("/products/{product_id}/discounts", response_model=List[schemas.ProductDiscount])
# def list_discounts(
#     product_id: int,
#     quantity: Optional[int] = None,
#     db: Session = Depends(get_db)
# ):
#     query = db.query(models.ProductDiscount).filter(models.ProductDiscount.product_id == product_id)
#     if quantity:
#         query = query.filter(models.ProductDiscount.quantity == quantity)
#     return query.all()

# @router.delete("/products/{product_id}/discounts/{discount_id}")
# def delete_discount(product_id: int, discount_id: int, db: Session = Depends(get_db)):
#     discount = db.query(models.ProductDiscount).filter(
#         and_(
#             models.ProductDiscount.product_id == product_id,
#             models.ProductDiscount.discount_id == discount_id
#         )
#     ).first()
#     if not discount:
#         raise HTTPException(status_code=404, detail="Discount not found")
    
#     db.delete(discount)
#     db.commit()
#     return {"message": "Discount deleted successfully"}
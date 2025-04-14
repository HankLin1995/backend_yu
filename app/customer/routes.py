from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from . import models, schemas

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.line_id == customer.line_id).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Customer already exists")
    
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/{line_id}", response_model=schemas.Customer)
def get_customer(line_id: str, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.line_id == line_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


@router.get("/", response_model=List[schemas.Customer])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return customers


@router.put("/{line_id}", response_model=schemas.Customer)
def update_customer(line_id: str, customer: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.line_id == line_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, value in customer.model_dump(exclude_unset=True).items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


# @router.delete("/{line_id}")
# def delete_customer(line_id: str, db: Session = Depends(get_db)):
#     db_customer = db.query(models.Customer).filter(models.Customer.line_id == line_id).first()
#     if not db_customer:
#         raise HTTPException(status_code=404, detail="Customer not found")
    
#     db.delete(db_customer)
#     db.commit()
#     return {"message": "Customer deleted successfully"}

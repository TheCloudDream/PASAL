from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.products import schemas
from app.products.models import Product
from app.auth.models import Seller
from app.auth.dependencies import get_current_seller

router = APIRouter(prefix="/products", tags=["Products Catalog"])

# 1. READ: Browse & Filter Catalog (Public Access)
@router.get("", response_model=List[schemas.ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search products by title"),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if search:
        query = query.filter(Product.title.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

# 2. READ: Get a single product details (Public Access)
@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

# 3. CREATE: List a new item (Restricted to Sellers)
@router.post("", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: schemas.ProductCreate,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    new_product = Product(
        seller_id=current_seller.user_id,
        title=payload.title,
        price=payload.price,
        stock=payload.stock
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# 4. UPDATE: Modify properties/stock levels (Restricted to Product Owner)
@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    payload: schemas.ProductUpdate,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Security Barrier: Enforce that sellers can only mutate their own items
    if product.seller_id != current_seller.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Operation unauthorized. You do not own this product listing."
        )

    # Apply updates dynamically
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
        
    db.commit()
    db.refresh(product)
    return product

# 5. DELETE: Remove inventory listing (Restricted to Product Owner)
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_seller: Seller = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product.seller_id != current_seller.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Operation unauthorized. You do not own this product listing."
        )

    db.delete(product)
    db.commit()
    return None

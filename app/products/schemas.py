from pydantic import BaseModel, Field, condecimal
from typing import Optional

class ProductBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    price: condecimal(max_digits=10, decimal_places=2, ge=0.01) # Enforces positive numeric entries
    stock: int = Field(..., ge=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    price: Optional[condecimal(max_digits=10, decimal_places=2, ge=0.01)] = None
    stock: Optional[int] = Field(None, ge=0)

class ProductResponse(ProductBase):
    product_id: int
    seller_id: int

    class Config:
        from_attributes = True

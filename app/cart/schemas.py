from pydantic import BaseModel, Field

class CartItemUpdate(BaseModel):
    product_id: int = Field(..., description="The ID of the item being added or adjusted")
    quantity: int = Field(..., ge=0, description="The targeted item volume. Setting to 0 removes the item entirely.")

class CartItemResponse(BaseModel):
    product_id: int
    title: str
    price: float
    quantity: int
    subtotal: float

class CartResponse(BaseModel):
    buyer_id: int
    items: list[CartItemResponse]
    grand_total: float

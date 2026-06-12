from pydantic import BaseModel, Field, condecimal
from datetime import datetime
from typing import List, Optional

# --- Nested Sub-Tier Items ---
class OrderItemResponse(BaseModel):
    item_id: int
    product_id: int
    quantity: int
    unit_price: condecimal(max_digits=10, decimal_places=2)

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    payment_id: int
    status: str
    payment_method: str
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Root Order Frameworks ---
class OrderResponse(BaseModel):
    order_id: int
    buyer_id: int
    total_amount: condecimal(max_digits=10, decimal_places=2)
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
    payment: Optional[PaymentResponse] = None

    class Config:
        from_attributes = True

# --- Payment Input Processing ---
class PaymentProcess(BaseModel):
    payment_method: str = Field(..., example="esewa", description="Target merchant payment vehicle name")

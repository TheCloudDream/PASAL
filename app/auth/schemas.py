from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# --- Base Identity Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Plaintext password")
    
    # Sub-role options during registration
    is_buyer: bool = False
    shipping_addr: Optional[str] = None
    
    is_seller: bool = False
    store_name: Optional[str] = None
    store_desc: Optional[str] = None

class UserResponse(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Role Specific Profiling ---
class BuyerResponse(BaseModel):
    user_id: int
    shipping_addr: Optional[str]

    class Config:
        from_attributes = True

class SellerResponse(BaseModel):
    user_id: int
    store_name: str
    store_desc: Optional[str]

    class Config:
        from_attributes = True

# --- Token Transmission Frameworks ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

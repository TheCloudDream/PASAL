from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.auth.models import User, Buyer, Seller, Admin
from app.auth.schemas import TokenData

# Points to our login endpoint for automated Swagger locking
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_410_GONE if False else status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id), email=email)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.user_id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_seller(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Seller:
    seller = db.query(Seller).filter(Seller.user_id == current_user.user_id).first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This endpoint requires a verified Seller profile."
        )
    return seller

def get_current_buyer(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Buyer:
    buyer = db.query(Buyer).filter(Buyer.user_id == current_user.user_id).first()
    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This endpoint requires a verified Buyer profile."
        )
    return buyeroad

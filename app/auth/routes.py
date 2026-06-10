from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.models import User, Buyer, Seller
from app.auth import schemas, utils

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Enforce global unique constraints on email
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    # 2. Cryptographically lock down the credentials
    hashed_pwd = utils.hash_password(payload.password)
    
    # 3. Instantiate the root User identity
    new_user = User(email=payload.email, password_hash=hashed_pwd)
    db.add(new_user)
    db.flush()  # Generates the user_id without committing the transaction yet

    # 4. Conditionally instantiate specialization profiles based on the ERD flags
    if payload.is_buyer:
        new_buyer = Buyer(user_id=new_user.user_id, shipping_addr=payload.shipping_addr)
        db.add(new_buyer)

    if payload.is_seller:
        if not payload.store_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Store name is required to register as a seller."
            )
        # Check if store name is unique
        existing_store = db.query(Seller).filter(Seller.store_name == payload.store_name).first()
        if existing_store:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Store name is already taken."
            )
        new_seller = Seller(
            user_id=new_user.user_id, 
            store_name=payload.store_name, 
            store_desc=payload.store_desc
        )
        db.add(new_seller)

    # Commit all changes atomically
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm parses form-data fields 'username' and 'password'
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not utils.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Pack identifying payloads inside the token claims
    token_claims = {"sub": str(user.user_id), "email": user.email}
    access_token = utils.create_access_token(data=token_claims)
    
    return {"access_token": access_token, "token_type": "bearer"}

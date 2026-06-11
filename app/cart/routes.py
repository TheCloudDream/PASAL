from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from redis import Redis

from app.database import get_db
from app.cache import get_redis_client
from app.cart import schemas, services
from app.auth.models import Buyer
from app.auth.dependencies import get_current_buyer

router = APIRouter(prefix="/cart", tags=["Shopping Cart Operations"])

@router.get("", response_model=schemas.CartResponse)
def view_cart(
    current_buyer: Buyer = Depends(get_current_buyer),
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Retrieves the buyer's fast memory cart layout and binds current catalog item metadata.
    """
    return services.fetch_hydrated_cart(redis_client, db, current_buyer.user_id)


@router.post("/items", response_model=schemas.CartResponse)
def update_cart_item(
    payload: schemas.CartItemUpdate,
    current_buyer: Buyer = Depends(get_current_buyer),
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Adds items or overwrites volume capacities inside Redis cache memory strings.
    """
    services.update_cart_item_in_cache(
        redis_client=redis_client,
        buyer_id=current_buyer.user_id,
        product_id=payload.product_id,
        quantity=payload.quantity
    )
    return services.fetch_hydrated_cart(redis_client, db, current_buyer.user_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def empty_cart(
    current_buyer: Buyer = Depends(get_current_buyer),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Flushes the memory hash trace for the authenticated buyer instantly.
    """
    services.clear_cart_cache(redis_client, current_buyer.user_id)
    return None

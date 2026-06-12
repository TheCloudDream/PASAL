from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from redis import Redis
from decimal import Decimal

from app.database import get_db
from app.cache import get_redis_client
from app.auth.models import Buyer
from app.auth.dependencies import get_current_buyer
from app.products.models import Product
from app.orders.models import Order, OrderItem, Payment
from app.orders import schemas

router = APIRouter(prefix="/orders", tags=["Orders & Checkout Processing"])

# 1. TRANSACTIONAL CHECKOUT: Turn Redis Session state into ACID Database logs
@router.post("/checkout", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout_cart(
    current_buyer: Buyer = Depends(get_current_buyer),
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client)
):
    cart_key = f"cart:{current_buyer.user_id}"
    cached_cart = redis_client.hgetall(cart_key)

    if not cached_cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot execute checkout processing. Your shopping cart is empty."
        )

    # Convert mapping keys & string inputs to primitive integers
    items_to_process = {int(k): int(v) for k, v in cached_cart.items()}
    product_ids = list(items_to_process.keys())

    # Initialize order totals tracking metrics 
    grand_total = Decimal("0.00")
    order_items_buffer = []

    try:
        # Enforce explicit database transactional isolation locking sequence
        # with_for_update() locks these exact matching records against concurrent reads or adjustment modifications
        db_products = (
            db.query(Product)
            .filter(Product.product_id.in_(product_ids))
            .with_for_update()
            .all()
        )
        product_map = {p.product_id: p for p in db_products}

        # Validate existence and capacity levels for every targeted entry
        for prod_id, requested_qty in items_to_process.items():
            if prod_id not in product_map:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product identification number {prod_id} no longer exists in market records."
                )
            
            product = product_map[prod_id]

            if product.stock < requested_qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient inventory depth for item '{product.title}'. Requested: {requested_qty}, Remaining Stock: {product.stock}"
                )

            # Mutate active PostgreSQL record state configurations
            product.stock -= requested_qty
            
            # Map subtotal equations cleanly
            item_subtotal = product.price * requested_qty
            grand_total += item_subtotal

            # Stage records into local memory arrays for batch pipeline logging
            order_items_buffer.append({
                "product_id": product.product_id,
                "quantity": requested_qty,
                "unit_price": product.price
            })

        # Persist root Parent tracking instance down to PostgreSQL engine context
        new_order = Order(
            buyer_id=current_buyer.user_id,
            total_amount=grand_total,
            status="pending"
        )
        db.add(new_order)
        db.flush()  # Generates our valid primary key 'order_id' instantly

        # Map nested children relationships explicitly
        for item_data in order_items_buffer:
            child_record = OrderItem(
                order_id=new_order.order_id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"]
            )
            db.add(child_record)

        # Everything succeeded in relational storage, wipe out cache storage tracks safely
        db.commit()
        redis_client.delete(cart_key)
        
        db.refresh(new_order)
        return new_order

    except Exception as exc:
        db.rollback()  # Instantly release active row locks and restore stock levels if anything faults out
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Critical transaction processing failure encountered: {str(exc)}"
        )


# 2. READ: Fetch comprehensive detail profile layout specs for an order
@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order_details(
    order_id: int,
    current_buyer: Buyer = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order reference log matching key data records not found.")
    
    # Restrict viewing authorization explicitly to the buyer who spawned it
    if order.buyer_id != current_buyer.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorization denied. You do not hold ownership access tokens over this order record invoice tracking log."
        )
    return order


# 3. TRANSACTIONAL SETTLEMENT: Complete payment transaction processes
@router.post("/{order_id}/pay", response_model=schemas.OrderResponse)
def simulate_payment_settlement(
    order_id: int,
    payload: schemas.PaymentProcess,
    current_buyer: Buyer = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.order_id == order_id).with_for_update().first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order tracking record entity reference data not found.")

    if order.buyer_id != current_buyer.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation disallowed. Ownership account values conflict with requested parameters."
        )

    if order.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Redundant execution call path. Targeted order statement profile records are already marked settled."
        )

    # Update transactional states across database layers natively
    order.status = "paid"

    # Instantiate the formal tracking logger layout inside the payments matrix
    new_payment = Payment(
        order_id=order.order_id,
        status="completed",
        payment_method=payload.payment_method
    )
    db.add(new_payment)
    
    db.commit()
    db.refresh(order)
    return order

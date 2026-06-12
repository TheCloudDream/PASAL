from fastapi import APIRouter, Depends, HTTPException, status, Form
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

# [Checkout Route stays the same as previous step, pulling from Redis and locking DB stock]
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

    items_to_process = {int(k): int(v) for k, v in cached_cart.items()}
    product_ids = list(items_to_process.keys())

    grand_total = Decimal("0.00")
    order_items_buffer = []

    try:
        db_products = (
            db.query(Product)
            .filter(Product.product_id.in_(product_ids))
            .with_for_update()
            .all()
        )
        product_map = {p.product_id: p for p in db_products}

        for prod_id, requested_qty in items_to_process.items():
            if prod_id not in product_map:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product identification number {prod_id} no longer exists."
                )
            
            product = product_map[prod_id]

            if product.stock < requested_qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient inventory for '{product.title}'. Requested: {requested_qty}, Stock: {product.stock}"
                )

            product.stock -= requested_qty
            grand_total += product.price * requested_qty

            order_items_buffer.append({
                "product_id": product.product_id,
                "quantity": requested_qty,
                "unit_price": product.price
            })

        new_order = Order(
            buyer_id=current_buyer.user_id,
            total_amount=grand_total,
            status="pending"
        )
        db.add(new_order)
        db.flush() 

        for item_data in order_items_buffer:
            child_record = OrderItem(
                order_id=new_order.order_id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"]
            )
            db.add(child_record)

        db.commit()
        redis_client.delete(cart_key)
        
        db.refresh(new_order)
        return new_order

    except Exception as exc:
        db.rollback()
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=str(exc))


# --- SCALABLE GATEWAY INTEGRATION HOOK ---
def execute_external_gateway_handshake(order_id: int, amount: float) -> dict:
    """
    FUTURE SCALABILITY GAP:
    When you are ready to add payment integrations (eSewa, Khalti, etc.),
    initialize their SDK or standard payload requests right here.
    """
    # TODO: Implement requests.post("https://uat.esewa.com.np/... ", data=payload)
    # For now, it cleanly returns a simulated successful verification token handshake.
    return {"gateway_status": "success", "transaction_reference": "MOCK_GW_TXN_9921A"}


# 3. TRANSACTIONAL SETTLEMENT: Processes payment choice with gateway abstraction
@router.post("/{order_id}/pay", response_model=schemas.OrderResponse)
def simulate_payment_settlement(
    order_id: int,
    # Changing this from a JSON body schema to an explicit Form parameter forces the Swagger dropdown!
    payment_method: schemas.PaymentMethodEnum = Form(..., description="Select your preferred settlement option"),
    current_buyer: Buyer = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.order_id == order_id).with_for_update().first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order record not found.")

    if order.buyer_id != current_buyer.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if order.status == "paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order statement is already settled.")

    # Process based on selection
    if payment_method == schemas.PaymentMethodEnum.ONLINE:
        # Gateway Hook Scalability Gap
        gateway_result = {"gateway_status": "success"} # Mocking successful handshake
        if gateway_result.get("gateway_status") != "success":
            raise HTTPException(status_code=402, detail="External gateway payment failed.")
        
        order.status = "paid"
        payment_status = "completed"
    else:
        order.status = "pending_delivery"
        payment_status = "pending_cash_collection"

    # Log inside tracking tables
    new_payment = Payment(
        order_id=order.order_id,
        status=payment_status,
        payment_method=payment_method.value # Extracted from Enum selection
    )
    db.add(new_payment)
    
    db.commit()
    db.refresh(order)
    return order

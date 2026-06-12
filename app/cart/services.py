from sqlalchemy.orm import Session
from redis import Redis
from app.products.models import Product

def get_buyer_cart_key(buyer_id: int) -> str:
    return f"cart:{buyer_id}"

def update_cart_item_in_cache(redis_client: Redis, buyer_id: int, product_id: int, quantity: int):
    cart_key = get_buyer_cart_key(buyer_id)
    if quantity <= 0:
        # If item volume drops to 0 or below, wipe the field from the hash map completely
        redis_client.hdel(cart_key, str(product_id))
    else:
        redis_client.hset(cart_key, str(product_id), quantity)

def fetch_hydrated_cart(redis_client: Redis, db: Session, buyer_id: int) -> dict:
    cart_key = get_buyer_cart_key(buyer_id)
    cached_items = redis_client.hgetall(cart_key)  # Returns dict like: {"1": "3", "2": "1"}

    items_list = []
    grand_total = 0.0

    if not cached_items:
        return {"buyer_id": buyer_id, "items": [], "grand_total": 0.0}

    # Fetch all referenced matching database rows in a single clean query batch
    product_ids = [int(pid) for pid in cached_items.keys()]
    db_products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
    product_map = {p.product_id: p for p in db_products}

    for prod_id_str, qty_str in cached_items.items():
        prod_id = int(prod_id_str)
        qty = int(qty_str)
        
        # If a product was deleted by a seller in the DB but still sits in the user's cache
        if prod_id not in product_map:
            redis_client.hdel(cart_key, prod_id_str)
            continue
            
        product = product_map[prod_id]
        subtotal = float(product.price) * qty
        grand_total += subtotal

        items_list.append({
            "product_id": product.product_id,
            "title": product.title,
            "price": float(product.price),
            "quantity": qty,
            "subtotal": subtotal
        })

    return {
        "buyer_id": buyer_id,
        "items": items_list,
        "grand_total": round(grand_total, 2)
    }

def clear_cart_cache(redis_client: Redis, buyer_id: int):
    cart_key = get_buyer_cart_key(buyer_id)
    redis_client.delete(cart_key)

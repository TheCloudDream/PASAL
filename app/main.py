from fastapi import FastAPI
from app.database import Base, engine
from app.auth.routes import router as auth_router
from app.products.routes import router as product_router
from app.cart.routes import router as cart_router
from app.orders.routes import router as order_router

# Core database execution context
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PASAL API", version="1.0.0")

# Mount your clean modular domain routes
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)

@app.get("/")
def read_root():
    return {"status": "online", "project": "PASAL"}

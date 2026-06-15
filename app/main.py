from fastapi import FastAPI
from app.database import Base, engine
from app.auth.routes import router as auth_router
from app.products.routes import router as product_router
from app.cart.routes import router as cart_router
from app.orders.routes import router as order_router

from fastapi.middleware.cors import CORSMiddleware

# Core database execution context
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PASAL API", version="1.0.0")

#allow cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",

        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount your clean modular domain routes
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)

@app.get("/")
def read_root():
    return {"status": "online", "project": "PASAL"}

@app.get("/health")
def health():
    return {
        "status" : "healthy"
    }

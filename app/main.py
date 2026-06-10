from fastapi import FastAPI
from app.database import Base, engine

# Import models so SQLAlchemy registers them
from app.auth.models import User, Buyer, Seller, Admin
from app.products.models import Product
from app.orders.models import Order, OrderItem, Payment

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Local Marketplace API",
    description="Monolithic Backend API for High-Speed Marketplace Operations",
    version="1.0.0"
)

@app.get("/")
def greet():
    return {"message": "Hello developer"}

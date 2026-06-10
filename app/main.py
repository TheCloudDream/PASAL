from fastapi import FastAPI
from app.database import Base, engine
from app.auth.routes import router as auth_router

# Core database execution context
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PASAL API", version="1.0.0")

# Mount your clean modular domain routes
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"status": "online", "project": "PASAL"}

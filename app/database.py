from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

#engine manages database connections
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# SessionLocal instances are the actual transactional context boundaries
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

#declarative_base class for data models to inherit from
Base = declarative_base()

#Fastapi dependency provider to cleanly open/close DB connections per HTTP request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

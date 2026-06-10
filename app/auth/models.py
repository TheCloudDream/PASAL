from decimal import Clamped
from typing import Text

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, null, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import user
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    #'is a' relationships 
    buyer = relationship("Buyer", uselist=False, back_populates="user", cascade="all, delete-orphan")
    seller = relationship("Seller", uselist=False, back_populates="user", cascade="all, delete-orphan")
    admin = relationship("Admin", uselist=False, back_populates="user", cascade="all, delete-orphan")

class Buyer(Base):
    __tablename__ = "buyers"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    shipping_addr = Column(Text, nullable=True)

    user = relationship("User", back_populates="buyer")
    orders = relationship("Order", back_populates="buyer")

class Seller(Base):
    __tablename__ = "sellers"

    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    store_name = Column(String, nullable=False)
    store_description = Column(Text, nullable=False)

    user = relationship("User", back_populates="seller")
    products = relationship("Product", back_populates="seller")

class Admin(Base):
    __tablename__ = "admins"
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    permissions = Column(Text, nullable=False)

    user = relationship("User", back_populates="admin")




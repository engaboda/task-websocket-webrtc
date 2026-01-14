from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship

from .engine import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # store hashed passwords!

    bids = relationship("Bids", back_populates="user")
    rooms = relationship("Room", back_populates="user")


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)

    bids = relationship("Bids", back_populates="product")
    rooms = relationship("Room", back_populates="product")


class Bids(Base):
    __tablename__ = "bids"
    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    product = relationship("Product", back_populates="bids")

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="bids")

    amount = Column(Float, nullable=False)
    placed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_winning = Column(Boolean, default=False)


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    product = relationship("Product", back_populates="rooms")

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="rooms")

from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey,
    Integer, String, Text,
)
from sqlalchemy.orm import relationship
from database import Base


class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(200), nullable=False)
    category    = Column(String(100), nullable=False)
    price       = Column(Integer, nullable=False)   # VNĐ
    weight      = Column(String(50))
    expiry      = Column(String(50))
    image_path  = Column(String(300))               # tên file ảnh, vd "IMG_2152.JPG"
    badge       = Column(String(50), nullable=True) # "Đặc Biệt" | "Bán Chạy" | "Cao Cấp" | null
    description = Column(Text, nullable=True)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id               = Column(Integer, primary_key=True, index=True)
    customer_name    = Column(String(150), nullable=False)
    customer_phone   = Column(String(20),  nullable=False)
    customer_address = Column(String(300), nullable=False)
    notes            = Column(Text, nullable=True)
    total            = Column(Integer, nullable=False)   # VNĐ
    # pending → confirmed → shipping → completed | cancelled
    status           = Column(String(20), default="pending")
    # cod | bank_transfer
    payment_method   = Column(String(20), default="cod")
    # unpaid | paid
    payment_status   = Column(String(20), default="unpaid")
    created_at       = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id           = Column(Integer, primary_key=True, index=True)
    order_id     = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id   = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(200))   # lưu tên tại thời điểm đặt
    quantity     = Column(Integer, nullable=False)
    unit_price   = Column(Integer, nullable=False)

    order   = relationship("Order",   back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Admin(Base):
    __tablename__ = "admins"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(80), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)

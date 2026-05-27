from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator


# ─────────────────────────────────────────────────────
# Product
# ─────────────────────────────────────────────────────
class ProductBase(BaseModel):
    name:        str
    category:    str
    price:       int
    weight:      Optional[str] = None
    expiry:      Optional[str] = None
    image_path:  Optional[str] = None
    badge:       Optional[str] = None
    description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name:        Optional[str]  = None
    category:    Optional[str]  = None
    price:       Optional[int]  = None
    weight:      Optional[str]  = None
    expiry:      Optional[str]  = None
    image_path:  Optional[str]  = None
    badge:       Optional[str]  = None
    description: Optional[str]  = None
    is_active:   Optional[bool] = None


class ProductOut(ProductBase):
    id:        int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────────────
class OrderItemIn(BaseModel):
    product_id:   Optional[int] = None
    product_name: str
    quantity:     int
    unit_price:   int


class OrderCreate(BaseModel):
    customer_name:    str
    customer_phone:   str
    customer_address: str
    notes:            Optional[str] = None
    payment_method:   str = "cod"
    items:            List[OrderItemIn]

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v):
        if not v:
            raise ValueError("Giỏ hàng không được trống")
        return v


class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        allowed = {"pending", "confirmed", "shipping", "completed", "cancelled"}
        if v not in allowed:
            raise ValueError(f"Status phải là một trong: {allowed}")
        return v


class OrderPaymentUpdate(BaseModel):
    payment_status: str

    @field_validator("payment_status")
    @classmethod
    def valid_payment_status(cls, v):
        if v not in {"unpaid", "paid"}:
            raise ValueError("payment_status phải là 'unpaid' hoặc 'paid'")
        return v


class OrderItemOut(BaseModel):
    id:           int
    product_id:   Optional[int]
    product_name: str
    quantity:     int
    unit_price:   int

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id:               int
    customer_name:    str
    customer_phone:   str
    customer_address: str
    notes:            Optional[str]
    total:            int
    status:           str
    payment_method:   str
    payment_status:   str
    created_at:       datetime
    items:            List[OrderItemOut]

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# ─────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_orders:    int
    pending_orders:  int
    total_revenue:   int
    total_products:  int

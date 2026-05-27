"""
Đình Thìn – Backend API
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from typing import List, Optional
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
import os

import models, schemas, auth
from database import Base, engine, get_db
from email_utils import send_order_notification, send_contact_notification

# ── Tạo bảng nếu chưa có ──
Base.metadata.create_all(bind=engine)

# ── Rate Limiter ──
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Đình Thìn API",
    description="API backend cho website bánh trung thu Đình Thìn",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS: cho phép frontend truy cập ──
_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in _origins_env.split(",")] if _origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve ảnh sản phẩm từ frontend/img/ ──
IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "img")
if os.path.isdir(IMG_DIR):
    app.mount("/images", StaticFiles(directory=IMG_DIR), name="images")


# ════════════════════════════════════════════════════
#  CONTACT
# ════════════════════════════════════════════════════

class ContactRequest(schemas.BaseModel if hasattr(schemas, "BaseModel") else object):
    pass

from pydantic import BaseModel as PydanticBase
class ContactForm(PydanticBase):
    name:    str
    email:   str
    phone:   Optional[str] = None
    subject: str
    message: str

@app.post("/api/contact", status_code=200, tags=["Contact"])
@limiter.limit("5/minute")   # tối đa 5 lần liên hệ/phút
def submit_contact(request: Request, data: ContactForm, background_tasks: BackgroundTasks):
    """Gửi form liên hệ – email thông báo tới admin."""
    background_tasks.add_task(
        send_contact_notification,
        data.name, data.email, data.phone or "", data.subject, data.message,
    )
    return {"message": "Đã nhận tin nhắn, chúng tôi sẽ phản hồi sớm nhất!"}


# ════════════════════════════════════════════════════
#  AUTH
# ════════════════════════════════════════════════════

@app.post("/api/auth/login", response_model=schemas.TokenOut, tags=["Auth"])
@limiter.limit("5/minute")   # tối đa 5 lần đăng nhập/phút — chặn brute force
def login(request: Request, payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Đăng nhập admin – trả về JWT token."""
    admin = db.query(models.Admin).filter(models.Admin.username == payload.username).first()
    if not admin or not auth.verify_password(payload.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai tên đăng nhập hoặc mật khẩu")
    token = auth.create_access_token({"sub": admin.username})
    return {"access_token": token, "token_type": "bearer"}


# ════════════════════════════════════════════════════
#  PRODUCTS  (public GET, admin POST/PUT/DELETE)
# ════════════════════════════════════════════════════

@app.get("/api/products", response_model=List[schemas.ProductOut], tags=["Products"])
def list_products(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lấy danh sách sản phẩm đang bán (is_active=True)."""
    q = db.query(models.Product).filter(models.Product.is_active == True)
    if category:
        q = q.filter(models.Product.category == category)
    return q.order_by(models.Product.id).all()


@app.get("/api/products/{product_id}", response_model=schemas.ProductOut, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    return p


@app.post("/api/products", response_model=schemas.ProductOut, status_code=201, tags=["Products"])
def create_product(
    data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(auth.get_current_admin),
):
    """[Admin] Thêm sản phẩm mới."""
    p = models.Product(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.put("/api/products/{product_id}", response_model=schemas.ProductOut, tags=["Products"])
def update_product(
    product_id: int,
    data: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(auth.get_current_admin),
):
    """[Admin] Cập nhật thông tin sản phẩm."""
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(p, field, value)
    db.commit()
    db.refresh(p)
    return p


@app.delete("/api/products/{product_id}", status_code=204, tags=["Products"])
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(auth.get_current_admin),
):
    """[Admin] Ẩn sản phẩm (soft delete)."""
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Không tìm thấy sản phẩm")
    p.is_active = False
    db.commit()


# ════════════════════════════════════════════════════
#  ORDERS  (public POST, admin GET/PUT)
# ════════════════════════════════════════════════════

@app.post("/api/orders", response_model=schemas.OrderOut, status_code=201, tags=["Orders"])
@limiter.limit("10/minute")   # tối đa 10 đơn/phút/IP — chặn spam đặt hàng
def create_order(
    request: Request,
    data: schemas.OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Khách đặt hàng – lưu đơn vào database và gửi email thông báo."""
    total = sum(i.quantity * i.unit_price for i in data.items)
    order = models.Order(
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        customer_address=data.customer_address,
        notes=data.notes,
        total=total,
        payment_method=data.payment_method,
        payment_status="unpaid",
    )
    db.add(order)
    db.flush()   # lấy order.id trước khi commit

    for item in data.items:
        db.add(models.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
        ))

    db.commit()
    db.refresh(order)

    # Gửi email thông báo cho admin (chạy nền, không làm chậm response)
    background_tasks.add_task(send_order_notification, order)

    return order


@app.get("/api/orders/lookup", response_model=List[schemas.OrderOut], tags=["Orders"])
def lookup_orders(phone: str = Query(..., description="Số điện thoại khách hàng"), db: Session = Depends(get_db)):
    """Khách tra cứu đơn hàng theo số điện thoại."""
    orders = (
        db.query(models.Order)
        .filter(models.Order.customer_phone == phone)
        .order_by(models.Order.created_at.desc())
        .all()
    )
    return orders


@app.get("/api/orders", response_model=List[schemas.OrderOut], tags=["Orders"])
def list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: models.Admin = Depends(auth.get_current_admin),
):
    """[Admin] Danh sách tất cả đơn hàng."""
    q = db.query(models.Order)
    if status_filter:
        q = q.filter(models.Order.status == status_filter)
    return q.order_by(models.Order.created_at.desc()).all()


@app.get("/api/orders/{order_id}", response_model=schemas.OrderOut, tags=["Orders"])
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(auth.get_current_admin),
):
    """[Admin] Chi tiết một đơn hàng."""
    o = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not o:
        raise HTTPException(404, "Không tìm thấy đơn hàng")
    return o


@app.put("/api/orders/{order_id}/status", response_model=schemas.OrderOut, tags=["Orders"])
def update_order_status(
    order_id: int,
    data: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(auth.get_current_admin),
):
    """[Admin] Cập nhật trạng thái đơn hàng."""
    o = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not o:
        raise HTTPException(404, "Không tìm thấy đơn hàng")
    o.status = data.status
    db.commit()
    db.refresh(o)
    return o


@app.put("/api/orders/{order_id}/payment", response_model=schemas.OrderOut, tags=["Orders"])
def update_order_payment(
    order_id: int,
    data: schemas.OrderPaymentUpdate,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(auth.get_current_admin),
):
    """[Admin] Cập nhật trạng thái thanh toán."""
    o = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not o:
        raise HTTPException(404, "Không tìm thấy đơn hàng")
    o.payment_status = data.payment_status
    db.commit()
    db.refresh(o)
    return o


# ════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════

@app.get("/api/admin/dashboard", response_model=schemas.DashboardStats, tags=["Admin"])
def dashboard(
    db: Session = Depends(get_db),
    _: models.Admin = Depends(auth.get_current_admin),
):
    """[Admin] Thống kê tổng quan."""
    from sqlalchemy import func

    total_orders   = db.query(models.Order).count()
    pending_orders = db.query(models.Order).filter(models.Order.status == "pending").count()
    revenue_row    = db.query(func.sum(models.Order.total)).filter(
        models.Order.status.in_(["confirmed", "shipping", "completed"])
    ).scalar()
    total_products = db.query(models.Product).filter(models.Product.is_active == True).count()

    return schemas.DashboardStats(
        total_orders=total_orders,
        pending_orders=pending_orders,
        total_revenue=revenue_row or 0,
        total_products=total_products,
    )

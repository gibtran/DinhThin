"""
Đình Thìn – Backend API
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from typing import List, Optional
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# ── Tạo admin mặc định nếu chưa có ──
def _seed_admin():
    import bcrypt
    from sqlalchemy.orm import Session
    with Session(engine) as db:
        if not db.query(models.Admin).first():
            username = os.getenv("ADMIN_USERNAME", "admin")
            password = os.getenv("ADMIN_PASSWORD", "admin123")
            hashed  = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            db.add(models.Admin(username=username, hashed_password=hashed))
            db.commit()
            print(f"[init] Đã tạo admin mặc định: {username}")

_seed_admin()

# ── Thêm sản phẩm mặc định nếu chưa có ──
def _seed_products():
    from sqlalchemy.orm import Session
    with Session(engine) as db:
        if db.query(models.Product).first():
            return  # đã có sản phẩm, bỏ qua
        products = [
            # ── Bánh Nướng Đặc Biệt ──
            dict(name="Bánh Nướng Nhân Trà Xanh",                category="Bánh Nướng Đặc Biệt",          price=80000, weight="210gr", expiry="7 ngày",  badge="Đặc Biệt", image_path="IMG_2213.JPG",  description="Vỏ bánh trà xanh thơm nhẹ, nhân đậu xanh nhuyễn mịn đặc trưng. Hương vị thanh mát, sang trọng – lựa chọn tuyệt vời cho người yêu thích trà xanh."),
            dict(name="Bánh Nướng Cacao Nhân Trứng Muối",         category="Bánh Nướng Đặc Biệt",          price=85000, weight="210gr", expiry="7 ngày",  badge="Đặc Biệt", image_path="IMG_6320.JPG",  description="Vỏ cacao đậm đà, nhân trứng muối béo bùi đặc sắc. Sự kết hợp táo bạo giữa vị đắng của cacao và vị mặn ngọt của trứng muối."),
            # ── Bánh Nhân Nhuyễn Cổ Truyền ──
            dict(name="Bánh Nướng-Dẻo Nhân Đậu Xanh",            category="Bánh Nhân Nhuyễn Cổ Truyền",   price=65000, weight="200gr", expiry="7 ngày",  badge=None,        image_path="IMG_2152.JPG",  description="Nhân đậu xanh nhuyễn mịn, thơm bùi tự nhiên. Vỏ bánh vàng óng, mềm xốp – hương vị truyền thống đúng chất Đình Thìn hơn 60 năm."),
            dict(name="Bánh Nướng-Dẻo Nhân Đậu Xanh Trứng Muối", category="Bánh Nhân Nhuyễn Cổ Truyền",   price=75000, weight="210gr", expiry="7 ngày",  badge="Bán Chạy",  image_path="IMG_6332.JPG",  description="Nhân đậu xanh nhuyễn hòa quyện cùng trứng muối béo ngậy. Vị cổ truyền quen thuộc, không thể thiếu trong dịp Trung Thu."),
            dict(name="Bánh Nướng-Dẻo Nhân Sen Xát",              category="Bánh Nhân Nhuyễn Cổ Truyền",   price=90000, weight="210gr", expiry="7 ngày",  badge="Cao Cấp",   image_path="IMG_6340.JPG",  description="Nhân hạt sen xát nhuyễn tinh tế, thơm ngào ngạt. Hương sen thanh khiết mang lại cảm giác thư thái, dành tặng những người thân yêu."),
            dict(name="Bánh Dẻo Chay Nhân Cốm Xào",               category="Bánh Nhân Nhuyễn Cổ Truyền",   price=70000, weight="200gr", expiry="5 ngày",  badge=None,        image_path="IMG_6348.JPG",  description="Nhân cốm xào thơm dẻo đặc trưng của mùa thu Hà Nội. Bánh chay thanh tịnh, thích hợp cho gia đình ăn chay hoặc làm lễ vật."),
            # ── Bánh Nhân Thập Cẩm Cổ Truyền ──
            dict(name="Bánh Nhân Thập Cẩm Gà Quay Trứng Muối",   category="Bánh Nhân Thập Cẩm Cổ Truyền", price=95000, weight="230gr", expiry="10 ngày", badge="Cao Cấp",   image_path="IMG_2153.JPG",  description="Nhân thập cẩm gà quay đậm đà kết hợp trứng muối bùi béo. Phong phú hương vị nhất trong dòng thập cẩm – lựa chọn sang trọng."),
            dict(name="Bánh Nướng-Dẻo Nhân Thập Cẩm Dăm Bông",   category="Bánh Nhân Thập Cẩm Cổ Truyền", price=80000, weight="200gr", expiry="10 ngày", badge=None,        image_path="IMG_6321.JPG",  description="Nhân thập cẩm dăm bông thơm ngon hài hòa. Hương vị quen thuộc, đậm chất truyền thống, dễ thưởng thức."),
            dict(name="Bánh Nhân Thập Cẩm Dăm Bông Trứng Muối",  category="Bánh Nhân Thập Cẩm Cổ Truyền", price=90000, weight="230gr", expiry="10 ngày", badge="Bán Chạy",  image_path="IMG_2179.PNG",  description="Dăm bông thơm ngon kết hợp trứng muối bùi béo. Hương vị cân bằng, đầy đủ, rất được ưa chuộng mỗi mùa Trung Thu."),
            dict(name="Bánh Nướng-Dẻo Nhân Thập Cẩm Xá Xíu",     category="Bánh Nhân Thập Cẩm Cổ Truyền", price=90000, weight="230gr", expiry="10 ngày", badge=None,        image_path="IMG_6900.JPG",  description="Nhân xá xíu đặc trưng, đậm đà vị cổ truyền. Hương vị khó quên, gợi nhớ ký ức Trung Thu tuổi thơ."),
            dict(name="Bánh Nướng-Dẻo Nhân Thập Cẩm Lạp Xưởng",  category="Bánh Nhân Thập Cẩm Cổ Truyền", price=65000, weight="200gr", expiry="10 ngày", badge=None,        image_path="IMG_6901.JPG",  description="Nhân thập cẩm lạp xưởng thơm bùi, đặc sắc theo cách rất riêng. Sự lựa chọn tiết kiệm mà vẫn tròn vị cổ truyền."),
        ]
        for p in products:
            db.add(models.Product(**p))
        db.commit()
        print(f"[init] Đã thêm {len(products)} sản phẩm mặc định")

_seed_products()

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve ảnh sản phẩm từ frontend/img/ ──
IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "img")
if os.path.isdir(IMG_DIR):
    app.mount("/images", StaticFiles(directory=IMG_DIR), name="images")


# ════════════════════════════════════════════════════
#  DEBUG – test email (xóa sau khi debug xong)
# ════════════════════════════════════════════════════

@app.get("/api/debug/email", tags=["Debug"])
def test_email():
    """Gửi email test để kiểm tra cấu hình Resend."""
    import resend as _resend
    api_key  = os.getenv("RESEND_API_KEY", "")
    email_to = os.getenv("EMAIL_TO", "")
    if not api_key or not email_to:
        return {"status": "error", "detail": "Thiếu RESEND_API_KEY hoặc EMAIL_TO"}
    try:
        _resend.api_key = api_key
        r = _resend.Emails.send({
            "from":    "Đình Thìn <onboarding@resend.dev>",
            "to":      [email_to],
            "subject": "Test email Đình Thìn",
            "html":    "<p>✅ Email từ Resend đang hoạt động!</p>",
        })
        return {"status": "ok", "sent_to": email_to, "id": str(r)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


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
            product_id=None,          # không ràng buộc FK — tránh lỗi nếu product bị xóa
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
        ))

    db.commit()
    db.refresh(order)

    # Truyền data thô vào background task — tránh SQLAlchemy session bị đóng
    order_data = {
        "id":               order.id,
        "customer_name":    order.customer_name,
        "customer_phone":   order.customer_phone,
        "customer_address": order.customer_address,
        "notes":            order.notes or "",
        "total":            order.total,
        "payment_method":   order.payment_method,
        "items": [
            {
                "product_name": item.product_name,
                "quantity":     item.quantity,
                "unit_price":   item.unit_price,
            }
            for item in order.items   # đọc trong khi session còn mở
        ],
    }
    background_tasks.add_task(send_order_notification, order_data)

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
        models.Order.status == "completed",
        models.Order.payment_status == "paid",
    ).scalar()
    total_products = db.query(models.Product).filter(models.Product.is_active == True).count()

    return schemas.DashboardStats(
        total_orders=total_orders,
        pending_orders=pending_orders,
        total_revenue=revenue_row or 0,
        total_products=total_products,
    )

# Đình Thìn – Bánh Mứt Kẹo Dân Tộc (Since 1957)

Website bán bánh trung thu truyền thống. Backend FastAPI + Frontend HTML/JS thuần.

---

## Cấu trúc dự án

```
DinhThin/
├── backend/                  ← FastAPI API server
│   ├── main.py               ← Toàn bộ routes/endpoints
│   ├── models.py             ← SQLAlchemy ORM models
│   ├── schemas.py            ← Pydantic schemas (validate input/output)
│   ├── auth.py               ← JWT authentication, bcrypt password
│   ├── database.py           ← Kết nối DB (SQLite dev / PostgreSQL prod)
│   ├── email_utils.py        ← Gửi email qua Resend API
│   ├── requirements.txt      ← Python dependencies
│   ├── .env                  ← Secrets (KHÔNG commit lên git)
│   └── .env.example          ← Template env vars
├── frontend/
│   ├── index.html            ← Trang chủ, danh sách sản phẩm
│   ├── cart.html             ← Giỏ hàng + checkout 3 bước
│   ├── admin.html            ← Trang quản trị (đăng nhập JWT)
│   ├── contact.html          ← Form liên hệ
│   ├── config.js             ← API_BASE URL (auto dev/prod)
│   └── img/                  ← Ảnh sản phẩm (IMG_*.JPG)
├── .claude/
│   └── CLAUDE.md             ← File này
├── netlify.toml              ← Config deploy Netlify
└── .gitignore
```

---

## Tech Stack

| Layer | Công nghệ |
|---|---|
| Backend | FastAPI + Uvicorn + Gunicorn |
| Database | PostgreSQL (prod) / SQLite (dev) |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt |
| Email | Resend API |
| Rate limiting | slowapi |
| Frontend | HTML + React (CDN) + Babel standalone |
| Hosting | Render (backend) + Netlify (frontend) |
| Code | GitHub (gibtran/DinhThin) |

---

## Chạy local (development)

```bash
# Terminal 1 — Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
python3 -m http.server 3000
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

---

## Production URLs

| Service | URL |
|---|---|
| Frontend (Netlify) | https://dinhthin.netlify.app |
| Backend (Render) | https://dinhthin-api.onrender.com |
| Admin panel | https://dinhthin.netlify.app/admin.html |
| API docs | https://dinhthin-api.onrender.com/docs |

---

## Environment Variables

### backend/.env (local)
```
SECRET_KEY=...
DATABASE_URL=sqlite:///./dinhthin.db
EMAIL_TO=giabaothichcho@gmail.com
RESEND_API_KEY=re_...
ADMIN_USERNAME=admin
ADMIN_PASSWORD=...
```

### Render Environment (production)
Các biến tương tự nhưng:
- `DATABASE_URL` = PostgreSQL Internal URL từ Render
- `RESEND_API_KEY` = key từ resend.com

---

## API Endpoints

### Public
| Method | Endpoint | Mô tả |
|---|---|---|
| GET | /api/products | Danh sách sản phẩm (is_active=True) |
| GET | /api/products/{id} | Chi tiết sản phẩm |
| POST | /api/orders | Đặt hàng mới |
| GET | /api/orders/lookup?phone=... | Tra cứu đơn theo SĐT |
| POST | /api/contact | Gửi form liên hệ |
| POST | /api/auth/login | Đăng nhập admin → JWT token |

### Admin (cần JWT Bearer token)
| Method | Endpoint | Mô tả |
|---|---|---|
| GET | /api/orders | Tất cả đơn hàng |
| GET | /api/orders/{id} | Chi tiết đơn |
| PUT | /api/orders/{id}/status | Cập nhật trạng thái |
| PUT | /api/orders/{id}/payment | Cập nhật thanh toán |
| POST | /api/products | Thêm sản phẩm |
| PUT | /api/products/{id} | Sửa sản phẩm |
| DELETE | /api/products/{id} | Ẩn sản phẩm (soft delete) |
| GET | /api/admin/dashboard | Thống kê tổng quan |

---

## Models

### Product
- `name`, `category`, `price` (VNĐ), `weight`, `expiry`
- `image_path` (tên file ảnh, vd: "IMG_2152.JPG")
- `badge`: "Đặc Biệt" | "Bán Chạy" | "Cao Cấp" | null
- `is_active`: soft delete

### Order
- `customer_name`, `customer_phone`, `customer_address`, `notes`
- `status`: pending → confirmed → shipping → completed | cancelled
- `payment_method`: cod | bank_transfer
- `payment_status`: unpaid | paid

### OrderItem
- `product_id` (nullable — tránh FK error khi product bị xóa)
- `product_name`, `quantity`, `unit_price` (lưu tại thời điểm đặt)

---

## Business Logic quan trọng

- **Doanh thu** chỉ tính khi `status=completed` VÀ `payment_status=paid`
- **Email thông báo** gửi qua Resend API (không dùng SMTP vì Render chặn port 465/587)
- **Background tasks**: email chạy nền sau khi response trả về — truyền dict thay vì ORM object để tránh SQLAlchemy detached session error
- **CORS**: `allow_origins=["*"]`, `allow_credentials=False` — JWT dùng Authorization header, không dùng cookie
- **Admin seed**: tự tạo admin account khi khởi động nếu chưa có (dùng `ADMIN_USERNAME`, `ADMIN_PASSWORD` env vars)
- **Product seed**: tự thêm 11 sản phẩm mặc định khi DB trống

---

## Danh sách sản phẩm mặc định (11 sản phẩm)

| Tên | Loại | Giá | Badge |
|---|---|---|---|
| Bánh Nướng Nhân Trà Xanh | Bánh Nướng Đặc Biệt | 80.000đ | Đặc Biệt |
| Bánh Nướng Cacao Nhân Trứng Muối | Bánh Nướng Đặc Biệt | 85.000đ | Đặc Biệt |
| Bánh Nướng-Dẻo Nhân Đậu Xanh | Bánh Nhân Nhuyễn Cổ Truyền | 65.000đ | — |
| Bánh Nướng-Dẻo Nhân Đậu Xanh Trứng Muối | Bánh Nhân Nhuyễn Cổ Truyền | 75.000đ | Bán Chạy |
| Bánh Nướng-Dẻo Nhân Sen Xát | Bánh Nhân Nhuyễn Cổ Truyền | 90.000đ | Cao Cấp |
| Bánh Dẻo Chay Nhân Cốm Xào | Bánh Nhân Nhuyễn Cổ Truyền | 70.000đ | — |
| Bánh Nhân Thập Cẩm Gà Quay Trứng Muối | Bánh Nhân Thập Cẩm Cổ Truyền | 95.000đ | Cao Cấp |
| Bánh Nướng-Dẻo Nhân Thập Cẩm Dẩm Bông | Bánh Nhân Thập Cẩm Cổ Truyền | 80.000đ | — |
| Bánh Nhân Thập Cẩm Dẩm Bông Trứng Muối | Bánh Nhân Thập Cẩm Cổ Truyền | 90.000đ | Bán Chạy |
| Bánh Nướng-Dẻo Nhân Thập Cẩm Xá Xíu | Bánh Nhân Thập Cẩm Cổ Truyền | 85.000đ | — |
| Bánh Nướng-Dẻo Nhân Thập Cẩm Lạp Xưởng | Bánh Nhân Thập Cẩm Cổ Truyền | 85.000đ | — |

---

## Deploy workflow

```bash
# Sửa code → commit → push → tự động deploy
git add .
git commit -m "mô tả thay đổi"
git push
# Render tự redeploy backend (~2-3 phút)
# Netlify tự redeploy frontend (~30 giây)
```

---

## Lưu ý / Gotchas

- Render **free tier ngủ** sau 15 phút không có request → lần đầu truy cập chờ ~50 giây
- PostgreSQL Render free tier **tự xóa sau 90 ngày** → cần backup hoặc gia hạn
- Ảnh sản phẩm phục vụ từ Netlify (static), không từ Render
- `product_id` trong OrderItem là **nullable** — tránh FK violation khi product bị xóa
- Debug email: GET `https://dinhthin-api.onrender.com/api/debug/email`

# Đình Thìn – Backend API

## Yêu cầu
- Python 3.10 trở lên
- pip

---

## Cài đặt lần đầu

Mở Terminal, cd vào thư mục `backend`:

```bash
cd "/Users/briantran396/Documents/DinhThin/img/backend"
```

### 1. Cài thư viện

```bash
pip install -r requirements.txt
```

### 2. Khởi tạo database & seed dữ liệu

```bash
python init_db.py
```

Lệnh này tạo file `dinhthin.db` và tự động thêm:
- 11 sản phẩm từ menu Đình Thìn
- Tài khoản admin: **admin / dinhthin2024**

### 3. Chạy server

```bash
uvicorn main:app --reload --port 8000
```

Server chạy tại: **http://localhost:8000**

---

## Tài liệu API

Truy cập **http://localhost:8000/docs** để xem toàn bộ API và thử trực tiếp.

---

## Sử dụng website

| File | Mô tả |
|------|-------|
| `index.html` | Website bán hàng cho khách |
| `admin.html` | Trang quản trị (đăng nhập: admin / dinhthin2024) |

Mở hai file trên bằng trình duyệt (Chrome/Safari).

---

## API Endpoints chính

| Method | URL | Mô tả |
|--------|-----|-------|
| POST | `/api/auth/login` | Đăng nhập admin |
| GET  | `/api/products` | Lấy danh sách sản phẩm |
| POST | `/api/products` | Thêm sản phẩm (admin) |
| PUT  | `/api/products/{id}` | Sửa sản phẩm (admin) |
| DELETE | `/api/products/{id}` | Ẩn sản phẩm (admin) |
| POST | `/api/orders` | Đặt hàng (khách) |
| GET  | `/api/orders` | Xem đơn hàng (admin) |
| PUT  | `/api/orders/{id}/status` | Cập nhật trạng thái đơn (admin) |
| GET  | `/api/admin/dashboard` | Thống kê tổng quan (admin) |

# Workflow Rules — Quy trình làm việc Đình Thìn

## Quy trình thay đổi code

1. **Sửa code** trên máy local
2. **Test local** trước khi push (chạy backend + frontend)
3. **Commit rõ ràng** theo format:
   - `feat:` thêm tính năng mới
   - `fix:` sửa bug
   - `docs:` cập nhật tài liệu
   - `style:` thay đổi UI/CSS
   - `refactor:` cải thiện code, không thêm tính năng
4. **Push lên GitHub** → tự động deploy
5. **Kiểm tra** Render logs + Netlify deploy

```bash
git add <file cụ thể>   # không dùng git add -A để tránh commit nhầm .env
git commit -m "fix: mô tả ngắn gọn"
git push
```

## Quy trình thêm tính năng mới

1. Suy nghĩ về impact: ảnh hưởng đến backend hay frontend hay cả hai?
2. Sửa **backend trước** (models → schemas → routes)
3. Nếu thêm column DB mới → cần migration (PostgreSQL không tự thêm column)
4. Sửa **frontend sau**
5. Test toàn bộ flow end-to-end

## Khi có lỗi production

1. Kiểm tra **Render Logs** trước
2. Kiểm tra **Browser Console** (F12)
3. Thử gọi API trực tiếp qua Swagger: https://dinhthin-api.onrender.com/docs
4. Nếu CORS error → thường do server đang ngủ hoặc ALLOWED_ORIGINS sai
5. Nếu 500 error → xem Render logs để đọc traceback

## File KHÔNG được commit

```
backend/.env
backend/dinhthin.db
.claude/CLAUDE.local.md
.claude/settings.local.json
__pycache__/
venv/
```

## Khi deploy lên production

- Backend (Render): tự redeploy khi push code mới đến GitHub
- Frontend (Netlify): tự redeploy khi push code mới đến GitHub
- Thay đổi env vars trên Render → Render tự restart

## Database migration (PostgreSQL)

PostgreSQL **không tự thêm column mới** như SQLite. Nếu thêm column:
```python
# Chạy qua Render Shell hoặc one-off job:
ALTER TABLE orders ADD COLUMN new_field VARCHAR(50);
```
Hoặc drop và recreate table nếu data chưa quan trọng.

## Backup database

PostgreSQL trên Render free tier **hết hạn sau 90 ngày**. Trước khi hết hạn:
1. Export data ra JSON/CSV
2. Tạo PostgreSQL mới
3. Import lại

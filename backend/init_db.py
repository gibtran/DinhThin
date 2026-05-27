"""
Khởi tạo database + seed dữ liệu mẫu.
Chạy một lần duy nhất: python init_db.py

Tạo ra:
  - 11 sản phẩm từ menu Đình Thìn
  - Tài khoản admin: admin / dinhthin2024
"""

from database import Base, engine, SessionLocal
import models
from auth import hash_password

PRODUCTS = [
    # ── Bánh Nướng Đặc Biệt
    dict(
        name="Bánh Nướng Nhân Trà Xanh",
        category="Bánh Nướng Đặc Biệt",
        price=80_000, weight="210gr", expiry="7 ngày",
        image_path="IMG_2213.JPG", badge="Đặc Biệt",
        description=(
            "Vỏ bánh trà xanh thơm nhẹ, nhân đậu xanh nhuyễn mịn đặc trưng. "
            "Hương vị thanh mát, sang trọng – lựa chọn tuyệt vời cho người yêu thích trà xanh."
        ),
    ),
    dict(
        name="Bánh Nướng Cacao Nhân Trứng Muối",
        category="Bánh Nướng Đặc Biệt",
        price=85_000, weight="210gr", expiry="7 ngày",
        image_path="IMG_6320.JPG", badge="Đặc Biệt",
        description=(
            "Vỏ cacao đậm đà, nhân trứng muối béo bùi đặc sắc. "
            "Sự kết hợp táo bạo giữa vị đắng của cacao và vị mặn ngọt của trứng muối."
        ),
    ),
    # ── Bánh Nhân Nhuyễn Cổ Truyền
    dict(
        name="Bánh Nướng-Dẻo Nhân Đậu Xanh",
        category="Bánh Nhân Nhuyễn Cổ Truyền",
        price=65_000, weight="200gr", expiry="7 ngày",
        image_path="IMG_2152.JPG", badge=None,
        description=(
            "Nhân đậu xanh nhuyễn mịn, thơm bùi tự nhiên. "
            "Vỏ bánh vàng óng, mềm xốp – hương vị truyền thống đúng chất Đình Thìn hơn 60 năm."
        ),
    ),
    dict(
        name="Bánh Nướng-Dẻo Nhân Đậu Xanh Trứng Muối",
        category="Bánh Nhân Nhuyễn Cổ Truyền",
        price=75_000, weight="210gr", expiry="7 ngày",
        image_path="IMG_6332.JPG", badge="Bán Chạy",
        description=(
            "Nhân đậu xanh nhuyễn hòa quyện cùng trứng muối béo ngậy. "
            "Vị cổ truyền quen thuộc, không thể thiếu trong dịp Trung Thu."
        ),
    ),
    dict(
        name="Bánh Nướng-Dẻo Nhân Sen Xát",
        category="Bánh Nhân Nhuyễn Cổ Truyền",
        price=90_000, weight="210gr", expiry="7 ngày",
        image_path="IMG_6340.JPG", badge="Cao Cấp",
        description=(
            "Nhân hạt sen xát nhuyễn tinh tế, thơm ngào ngạt. "
            "Hương sen thanh khiết mang lại cảm giác thư thái, dành tặng những người thân yêu."
        ),
    ),
    dict(
        name="Bánh Dẻo Chay Nhân Cốm Xào",
        category="Bánh Nhân Nhuyễn Cổ Truyền",
        price=70_000, weight="200gr", expiry="5 ngày",
        image_path="IMG_6348.JPG", badge=None,
        description=(
            "Nhân cốm xào thơm dẻo đặc trưng của mùa thu Hà Nội. "
            "Bánh chay thanh tịnh, thích hợp cho gia đình ăn chay hoặc làm lễ vật."
        ),
    ),
    # ── Bánh Nhân Thập Cẩm Cổ Truyền
    dict(
        name="Bánh Nhân Thập Cẩm Gà Quay Trứng Muối",
        category="Bánh Nhân Thập Cẩm Cổ Truyền",
        price=95_000, weight="230gr", expiry="10 ngày",
        image_path="IMG_2153.JPG", badge="Cao Cấp",
        description=(
            "Nhân thập cẩm gà quay đậm đà kết hợp trứng muối bùi béo. "
            "Phong phú hương vị nhất trong dòng thập cẩm – lựa chọn sang trọng."
        ),
    ),
    dict(
        name="Bánh Nướng-Dẻo Nhân Thập Cẩm Dăm Bông",
        category="Bánh Nhân Thập Cẩm Cổ Truyền",
        price=80_000, weight="200gr", expiry="10 ngày",
        image_path="IMG_6321.JPG", badge=None,
        description=(
            "Nhân thập cẩm dăm bông thơm ngon hài hòa. "
            "Hương vị quen thuộc, đậm chất truyền thống, dễ thưởng thức."
        ),
    ),
    dict(
        name="Bánh Nhân Thập Cẩm Dăm Bông Trứng Muối",
        category="Bánh Nhân Thập Cẩm Cổ Truyền",
        price=90_000, weight="230gr", expiry="10 ngày",
        image_path="IMG_2179.PNG", badge="Bán Chạy",
        description=(
            "Dăm bông thơm ngon kết hợp trứng muối bùi béo. "
            "Hương vị cân bằng, đầy đủ, rất được ưa chuộng mỗi mùa Trung Thu."
        ),
    ),
    dict(
        name="Bánh Nướng-Dẻo Nhân Thập Cẩm Xá Xíu",
        category="Bánh Nhân Thập Cẩm Cổ Truyền",
        price=90_000, weight="230gr", expiry="10 ngày",
        image_path="IMG_6900.JPG", badge=None,
        description=(
            "Nhân xá xíu đặc trưng, đậm đà vị cổ truyền. "
            "Hương vị khó quên, gợi nhớ ký ức Trung Thu tuổi thơ."
        ),
    ),
    dict(
        name="Bánh Nướng-Dẻo Nhân Thập Cẩm Lạp Xưởng",
        category="Bánh Nhân Thập Cẩm Cổ Truyền",
        price=65_000, weight="200gr", expiry="10 ngày",
        image_path="IMG_6901.JPG", badge=None,
        description=(
            "Nhân thập cẩm lạp xưởng thơm bùi, đặc sắc theo cách rất riêng. "
            "Sự lựa chọn tiết kiệm mà vẫn tròn vị cổ truyền."
        ),
    ),
]


def seed():
    print("⏳ Tạo bảng database...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # ── Admin
        if not db.query(models.Admin).filter_by(username="admin").first():
            db.add(models.Admin(
                username="admin",
                hashed_password=hash_password("dinhthin2024"),
            ))
            print("✅ Tạo tài khoản admin  →  admin / dinhthin2024")
        else:
            print("⚠️  Tài khoản admin đã tồn tại, bỏ qua.")

        # ── Products
        existing = db.query(models.Product).count()
        if existing == 0:
            for p in PRODUCTS:
                db.add(models.Product(**p))
            print(f"✅ Thêm {len(PRODUCTS)} sản phẩm vào database.")
        else:
            print(f"⚠️  Database đã có {existing} sản phẩm, bỏ qua seed.")

        db.commit()
        print("\n🎉 Khởi tạo xong! Chạy server:")
        print("   uvicorn main:app --reload --port 8000\n")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

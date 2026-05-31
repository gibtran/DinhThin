# Design Rules — Đình Thìn UI/UX

## Màu sắc (Brand Colors)

```css
--red-dark:   #8B1A1A;   /* màu chủ đạo — header, button chính, title */
--red-light:  #A52020;   /* hover state */
--gold:       #C9A84C;   /* accent — badge, highlight, đường viền đặc biệt */
--gold-light: #F5E6C8;   /* background nhẹ, tag */
--cream:      #FFF8F0;   /* background card, section */
--border:     #E0D4C0;   /* viền nhẹ */
--text-dark:  #2C1810;   /* text chính */
--text-muted: #7A6050;   /* text phụ */
```

## Typography

- Font chính: `'Playfair Display'` (serif) — tên sản phẩm, tiêu đề
- Font phụ: `'Inter'` hoặc `Arial` — nội dung, giá, mô tả
- Giá tiền: màu `#8B1A1A`, font-weight bold, suffix "đ"

## UI Components

### Button chính
```css
background: #8B1A1A; color: white; border-radius: 6px; padding: 12px 28px;
```

### Badge sản phẩm
- "Đặc Biệt" → màu vàng gold trên nền đỏ
- "Bán Chạy" → màu đỏ
- "Cao Cấp" → màu tối/premium

### Card sản phẩm
- Nền trắng, border-radius 12px, shadow nhẹ
- Ảnh chiếm ~60% chiều cao card
- Badge ở góc trên trái

### Toast notification
- Thành công: nền xanh lá
- Lỗi: nền đỏ
- Vị trí: bottom-right

## Nguyên tắc Design

1. **Truyền thống + hiện đại**: Giữ hơi hướng cổ điển Việt Nam nhưng layout hiện đại
2. **Màu đỏ-vàng**: Đặc trưng thương hiệu, dùng nhất quán
3. **Ảnh sản phẩm**: Luôn có fallback icon 🎑 nếu ảnh lỗi
4. **Mobile-first**: Responsive, grid tự động co lại trên mobile
5. **Tiếng Việt**: Toàn bộ UI bằng tiếng Việt, format tiền theo kiểu VN (85.000đ)

## Tên danh mục sản phẩm (dùng đúng chính xác)

- `Bánh Nướng Đặc Biệt`
- `Bánh Nhân Nhuyễn Cổ Truyền`
- `Bánh Nhân Thập Cẩm Cổ Truyền`

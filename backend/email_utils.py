import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key  = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM_NAME = "Đình Thìn"
EMAIL_FROM_ADDR = "onboarding@resend.dev"   # dùng domain mặc định Resend (free, không cần verify)
EMAIL_TO        = os.getenv("EMAIL_TO", "")


def _send(subject: str, html: str) -> None:
    """Gửi email qua Resend API."""
    if not resend.api_key or not EMAIL_TO:
        print("⚠️  Chưa cấu hình RESEND_API_KEY hoặc EMAIL_TO")
        return
    try:
        r = resend.Emails.send({
            "from":    f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDR}>",
            "to":      [EMAIL_TO],
            "subject": subject,
            "html":    html,
        })
        print(f"✅ Email đã gửi: {r}")
    except Exception as e:
        print(f"❌ Gửi email thất bại: {e}")


def send_contact_notification(name: str, email: str, phone: str, subject: str, message: str) -> None:
    """Gửi email thông báo khi có người liên hệ qua form."""
    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333">
      <div style="max-width:560px;margin:auto;border:1px solid #e0d4c0;border-radius:8px;overflow:hidden">
        <div style="background:#8B1A1A;padding:20px;text-align:center">
          <h2 style="color:#C9A84C;margin:0">📬 Đình Thìn – Tin nhắn mới</h2>
        </div>
        <div style="padding:24px">
          <table style="width:100%;border-collapse:collapse;margin-bottom:16px">
            <tr><td style="padding:6px;width:120px;color:#666">Họ tên</td><td style="padding:6px"><strong>{name}</strong></td></tr>
            <tr><td style="padding:6px;color:#666">Email</td><td style="padding:6px">{email}</td></tr>
            <tr><td style="padding:6px;color:#666">SĐT</td><td style="padding:6px">{phone or "—"}</td></tr>
            <tr><td style="padding:6px;color:#666">Chủ đề</td><td style="padding:6px"><strong>{subject}</strong></td></tr>
          </table>
          <div style="background:#fff8f0;border-left:4px solid #C9A84C;padding:16px;border-radius:4px;font-size:14px;line-height:1.7">
            {message}
          </div>
        </div>
        <div style="background:#f5ece0;padding:12px;text-align:center;font-size:12px;color:#888">
          Đình Thìn – Bánh Mứt Kẹo Dân Tộc
        </div>
      </div>
    </body></html>
    """
    _send(f"📬 Liên hệ mới từ {name} – {subject}", html)


def send_order_notification(order: dict) -> None:
    """Gửi email thông báo đơn hàng mới cho admin."""
    items_rows = "".join(
        f"""<tr>
          <td style="padding:8px;border:1px solid #ddd">{item['product_name']}</td>
          <td style="padding:8px;border:1px solid #ddd;text-align:center">{item['quantity']}</td>
          <td style="padding:8px;border:1px solid #ddd;text-align:right">{item['unit_price']:,.0f}đ</td>
          <td style="padding:8px;border:1px solid #ddd;text-align:right">{item['quantity']*item['unit_price']:,.0f}đ</td>
        </tr>"""
        for item in order["items"]
    )
    notes_row = f"<tr><td style='padding:6px;color:#666'>Ghi chú</td><td style='padding:6px'>{order['notes']}</td></tr>" if order["notes"] else ""

    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#333">
      <div style="max-width:600px;margin:auto;border:1px solid #e0d4c0;border-radius:8px;overflow:hidden">
        <div style="background:#8B1A1A;padding:20px;text-align:center">
          <h2 style="color:#C9A84C;margin:0">🎑 Đình Thìn – Đơn hàng mới</h2>
        </div>
        <div style="padding:24px">
          <p style="font-size:16px">Có đơn hàng mới <strong>#{order['id']}</strong> vừa được đặt.</p>
          <h3 style="color:#8B1A1A">Thông tin khách hàng</h3>
          <table style="width:100%;border-collapse:collapse;margin-bottom:16px">
            <tr><td style="padding:6px;width:140px;color:#666">Họ tên</td><td style="padding:6px"><strong>{order['customer_name']}</strong></td></tr>
            <tr><td style="padding:6px;color:#666">Số điện thoại</td><td style="padding:6px">{order['customer_phone']}</td></tr>
            <tr><td style="padding:6px;color:#666">Địa chỉ</td><td style="padding:6px">{order['customer_address']}</td></tr>
            {notes_row}
          </table>
          <h3 style="color:#8B1A1A">Chi tiết đơn hàng</h3>
          <table style="width:100%;border-collapse:collapse">
            <thead><tr style="background:#f5ece0">
              <th style="padding:8px;border:1px solid #ddd;text-align:left">Sản phẩm</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:center">SL</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:right">Đơn giá</th>
              <th style="padding:8px;border:1px solid #ddd;text-align:right">Thành tiền</th>
            </tr></thead>
            <tbody>{items_rows}</tbody>
            <tfoot><tr style="background:#fff8f0">
              <td colspan="3" style="padding:10px;border:1px solid #ddd;text-align:right"><strong>Tổng cộng</strong></td>
              <td style="padding:10px;border:1px solid #ddd;text-align:right;color:#8B1A1A;font-size:18px"><strong>{order['total']:,.0f}đ</strong></td>
            </tr></tfoot>
          </table>
          <div style="margin-top:24px;text-align:center">
            <a href="https://dinhthin.netlify.app/admin.html"
               style="background:#8B1A1A;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:bold">
              Xem trong trang Admin
            </a>
          </div>
        </div>
        <div style="background:#f5ece0;padding:12px;text-align:center;font-size:12px;color:#888">
          Đình Thìn – Bánh Mứt Kẹo Dân Tộc
        </div>
      </div>
    </body></html>
    """
    _send(f"🛒 Đơn hàng mới #{order['id']} – {order['customer_name']}", html)

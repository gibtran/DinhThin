// ═══════════════════════════════════════
//  Đình Thìn – API Config
//  Dev:        API_BASE = http://localhost:8000/api
//  Production: API_BASE = https://dinhthin-api.onrender.com/api
// ═══════════════════════════════════════

const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:8000/api"           // đang chạy local
  : "https://dinhthin-api.onrender.com/api"; // ← đổi thành URL Render cấp cho bạn

#!/bin/bash
# ═══════════════════════════════════════════════
#  Đình Thìn – Database Backup Script
#  Dùng: bash backup.sh
#  Tự động: thêm vào cron chạy mỗi ngày lúc 2:00 sáng
#  Cron: 0 2 * * * /var/www/dinhthin/backend/backup.sh
# ═══════════════════════════════════════════════

# Đường dẫn
DB_FILE="/var/www/dinhthin/backend/dinhthin.db"   # đổi khi deploy
BACKUP_DIR="/var/backups/dinhthin"                 # thư mục lưu backup
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/dinhthin_$DATE.db"
KEEP_DAYS=7   # giữ backup trong 7 ngày gần nhất

# Tạo thư mục backup nếu chưa có
mkdir -p "$BACKUP_DIR"

# Backup database
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_FILE"
    echo "✅ Backup thành công: $BACKUP_FILE"
else
    echo "❌ Không tìm thấy database: $DB_FILE"
    exit 1
fi

# Xoá backup cũ hơn 7 ngày
find "$BACKUP_DIR" -name "dinhthin_*.db" -mtime +$KEEP_DAYS -delete
echo "🗑️  Đã xoá backup cũ hơn $KEEP_DAYS ngày"

# Tổng kết
TOTAL=$(ls "$BACKUP_DIR" | wc -l)
echo "📦 Hiện có $TOTAL file backup trong $BACKUP_DIR"

"""
config.py - Cấu hình ứng dụng Flask cho Tiệm bánh Yuu Cake.

Kiến thức áp dụng:
- Chương 3: Cấu hình JSON hiển thị tiếng Việt có dấu (JSON_AS_ASCII / app.json.ensure_ascii = False).
- Chương 5: SECRET_KEY bắt buộc để mã hoá Session (giỏ hàng) và sinh CSRF token cho Flask-WTF.
- Chương 6: Kết nối CSDL SQLite đặt trong thư mục instance/yuucake.db.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    # Khoá bí mật dùng để ký cookie Session và bảo vệ CSRF (ưu tiên biến môi trường khi triển khai)
    SECRET_KEY = os.environ.get("SECRET_KEY", "yuu-cake-husc-pmmnm-2026-secret")

    # Đường dẫn CSDL SQLite lưu trong thư mục instance/ (chuẩn Flask & Chương 6)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'yuucake.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Giữ tiếng Việt có dấu khi Flask trả về JSON (Chương 3)
    JSON_AS_ASCII = False

    # Cấu hình nghiệp vụ giao hàng (theo bài tập tổng hợp Chương 5-6)
    SHIPPING_FEE = 20_000          # Phí giao hàng tiêu chuẩn: 20.000 đ
    FREE_SHIPPING_MIN = 200_000    # Miễn phí giao hàng khi tạm tính >= 200.000 đ
    PRODUCTS_PER_PAGE = 8          # Số sản phẩm mỗi trang khi phân trang

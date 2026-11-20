"""
extensions.py - Khởi tạo các tiện ích mở rộng (Extensions) của Flask.

Tách riêng extensions.py giúp tránh lỗi vòng lặp import (circular import)
giữa app.py, models.py và các file routes/*.py.

Kiến thức áp dụng:
- Chương 5: CSRFProtect bảo vệ toàn bộ form POST khỏi tấn công giả mạo yêu cầu (CSRF).
- Chương 6: SQLAlchemy 2.0 với DeclarativeBase và Flask-Migrate hỗ trợ nâng cấp lược đồ CSDL.
"""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Lớp cơ sở chuẩn SQLAlchemy 2.0 để khai báo các bảng bằng Mapped / mapped_column."""
    pass


# Khởi tạo đối tượng db, csrf, migrate chưa gắn app (gắn trong app.py bằng init_app)
db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
migrate = Migrate()

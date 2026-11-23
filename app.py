"""
app.py - Điểm khởi chạy chính của ứng dụng web Tiệm bánh Yuu Cake.

Tổng hợp đầy đủ kiến thức Chương 3, 4, 5, 6:
- Cấu hình Flask, SQLAlchemy 2.0, Flask-WTF CSRF, Flask-Migrate.
- Custom Jinja2 template filter: `vnd` (52000 -> "52.000 đ") và `date_vn`.
- Context processor tự động truyền `cart_count` và `nav_categories` cho thanh menu mọi trang.
- Đăng ký các Blueprint (store, cart, checkout, api) và error handlers (400/404/405).
- Đăng ký lệnh Flask CLI `flask --app app seed` để nạp dữ liệu mẫu từ terminal.
"""

from datetime import datetime
from pathlib import Path

from flask import Flask, session
from sqlalchemy import select

from config import Config
from extensions import csrf, db, migrate
from models import Category
from routes.admin import admin_bp
from routes.api import api_bp
from routes.cart import cart_bp
from routes.checkout import checkout_bp
from routes.errors import register_error_handlers
from routes.store import store_bp
from seed import seed_database


def create_app(config_class=Config) -> Flask:
    """Application Factory khởi tạo và cấu hình ứng dụng Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Đảm bảo thư mục instance/ luôn tồn tại trước khi SQLite tạo file yuucake.db
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # Giữ tiếng Việt có dấu cho toàn bộ JSON response (Flask 3.x - Chương 3)
    app.json.ensure_ascii = False

    # Gắn các tiện ích mở rộng vào ứng dụng
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # --- Chương 4: Custom Jinja2 Template Filters ---
    @app.template_filter("vnd")
    def format_vnd(amount) -> str:
        """Định dạng tiền Việt Nam: 52000 -> '52.000 đ'."""
        if amount is None:
            return "—"
        return f"{int(amount):,}".replace(",", ".") + " đ"

    @app.template_filter("date_vn")
    def format_date_vn(dt: datetime, with_time: bool = False) -> str:
        """Định dạng ngày giờ kiểu Việt Nam: 23/12/2024 hoặc 23/12/2024 09:15."""
        if dt is None:
            return "—"
        return dt.strftime("%d/%m/%Y %H:%M" if with_time else "%d/%m/%Y")

    # --- Chương 4 & 5: Context Processor cho thanh Navbar ở mọi trang ---
    @app.context_processor
    def inject_global_context():
        """
        Tự động đưa tổng số bánh trong giỏ (cart_count) và danh mục bánh (nav_categories)
        vào mọi template kế thừa base.html.
        """
        cart = session.get("cart", {})
        cart_count = sum(int(v) for v in cart.values() if isinstance(v, int) and v > 0) if isinstance(cart, dict) else 0
        try:
            nav_categories = db.session.scalars(select(Category).order_by(Category.id.asc())).all()
        except Exception:
            nav_categories = []
        return {
            "cart_count": cart_count,
            "nav_categories": nav_categories,
            "current_year": datetime.now().year,
        }

    # --- Đăng ký các Blueprint & Error Handler ---
    app.register_blueprint(store_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    register_error_handlers(app)

    # --- Chương 3 & 6: Lệnh Flask CLI tuỳ biến ---
    @app.cli.command("seed")
    def seed_command():
        """Nạp dữ liệu mẫu từ terminal bằng lệnh: flask --app app seed"""
        db.create_all()
        result = seed_database()
        if result["seeded"]:
            print(
                f"Đã nạp dữ liệu mẫu: {result['categories']} danh mục, "
                f"{result['products']} sản phẩm, {result['blogs']} bài viết."
            )
        else:
            print(f"CSDL đã có sẵn dữ liệu ({result['products']} sản phẩm).")

    # Tạo bảng và tự động nạp dữ liệu mẫu lần đầu nếu CSDL chưa có dữ liệu
    with app.app_context():
        db.create_all()
        seed_database()

    return app


# Biến app ở mức module để chạy trực tiếp bằng: flask --app app run --debug --port 8000
app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=8000)

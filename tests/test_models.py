"""
tests/test_models.py - Kiểm thử các Model ORM SQLAlchemy 2.0 (Chương 6).
"""

from datetime import datetime
from extensions import db
from models import (
    BlogPost,
    Category,
    Order,
    OrderItem,
    OrderStatusHistory,
    Product,
    User,
    ORDER_STATUS_PENDING,
)


def test_category_model(app):
    with app.app_context():
        cat = Category(
            name="Bánh Mousse Mới",
            slug="banh-mousse-moi",
            description="Mousse mềm béo",
            image="images/categories/banh-donut.avif",
        )
        assert repr(cat) == "<Category Bánh Mousse Mới>"
        assert cat.slug == "banh-mousse-moi"


def test_product_model_and_to_dict(app):
    with app.app_context():
        p = Product(
            id=999,
            name="Bánh Mousse Chanh Leo",
            slug="banh-mousse-chanh-leo",
            price=45000,
            stock=12,
            short_desc="Chua ngọt thanh mát",
            description="Mô tả chi tiết bánh",
            image="images/products/donut-1.avif",
            category_id=1,
            is_featured=True,
        )
        assert repr(p) == "<Product Bánh Mousse Chanh Leo (45000đ)>"
        d = p.to_dict()
        assert d["id"] == 999
        assert d["name"] == "Bánh Mousse Chanh Leo"
        assert d["price"] == 45000
        assert d["in_stock"] is True


def test_order_and_order_item_models(app):
    with app.app_context():
        o = Order(
            customer_name="Trần Thị B",
            phone="0912345678",
            address="456 Le Loi, Hue",
            payment_method="cod",
            status=ORDER_STATUS_PENDING,
            total_amount=90000,
        )
        assert o.payment_label == "Tiền mặt khi nhận hàng"
        assert o.status == ORDER_STATUS_PENDING

        item = OrderItem(
            order_id=1,
            product_id=1,
            product_name="Bánh Donut Dâu",
            unit_price=25000,
            quantity=3,
        )
        assert item.line_total == 75000


def test_order_status_history_model(app):
    with app.app_context():
        h = OrderStatusHistory(
            order_id=1,
            status="Đang giao",
            changed_at=datetime.now(),
        )
        assert h.status == "Đang giao"


def test_blog_post_model(app):
    with app.app_context():
        blog = BlogPost(
            title="Bí quyết làm bánh su kem",
            slug="bi-quyet-lam-banh-su-kem",
            category_label="Mẹo làm bánh",
            excerpt="Tóm tắt bài viết",
            content="Nội dung chi tiết bài viết",
            image="images/blog/blog-1.avif",
        )
        assert blog.slug == "bi-quyet-lam-banh-su-kem"


def test_user_password_hashing(app):
    with app.app_context():
        u = User(
            username="admin_test",
            email="admin_test@yuucake.vn",
            full_name="Quản trị viên Test",
            role="admin",
        )
        u.set_password("mat_khau_bao_mat_123")
        assert u.password_hash is not None
        assert u.password_hash != "mat_khau_bao_mat_123"
        assert u.check_password("mat_khau_bao_mat_123") is True
        assert u.check_password("sai_mat_khau") is False

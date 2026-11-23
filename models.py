"""
models.py - Định nghĩa các mô hình dữ liệu (ORM Models) theo chuẩn SQLAlchemy 2.0.

Kiến thức Chương 6:
- Sử dụng Mapped[] và mapped_column() thay cho db.Column kiểu cũ.
- Thiết lập quan hệ khoá ngoại 1-Nhiều (ForeignKey + relationship):
    + Category (1)  ---> (N) Product
    + Order (1)     ---> (N) OrderItem
    + Order (1)     ---> (N) OrderStatusHistory (chuẩn bị sẵn cho phần Admin làm ở giai đoạn sau)
- Lưu đơn giá tại thời điểm đặt hàng (OrderItem.unit_price) để khi giá bánh thay đổi,
  lịch sử hoá đơn cũ không bị sai lệch.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

# Hằng số trạng thái đơn hàng thống nhất (dùng cho cả Phần A bán hàng và Phần B quản trị sau này)
ORDER_STATUS_PENDING = "Chờ xác nhận"
ORDER_STATUS_SHIPPING = "Đang giao"
ORDER_STATUS_COMPLETED = "Hoàn tất"
ORDER_STATUS_CANCELLED = "Đã huỷ"

PAYMENT_METHODS = {
    "cod": "Tiền mặt khi nhận hàng",
    "bank": "Chuyển khoản ngân hàng",
}


class Category(db.Model):
    """Bảng danh mục bánh (Bánh Donut, Phụ kiện bánh, Bánh quy, Bánh sinh nhật, Bánh Cupcake)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, default="")
    image: Mapped[str] = mapped_column(String(255), nullable=False)

    # Quan hệ 1-Nhiều: một danh mục có nhiều sản phẩm
    products: Mapped[List["Product"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Product(db.Model):
    """Bảng sản phẩm bánh / phụ kiện của tiệm bánh Yuu Cake."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)        # Giá bán (VNĐ)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    short_desc: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # Khoá ngoại trỏ về bảng categories
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="products")

    # Liên kết với các dòng đơn hàng (phục vụ kiểm tra không xoá bánh đã bán ở phần Admin)
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")

    def to_dict(self) -> dict:
        """Chuyển đối tượng Product sang dict để trả về qua API JSON (Chương 3)."""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "category": self.category.name if self.category else None,
            "category_slug": self.category.slug if self.category else None,
            "price": self.price,
            "stock": self.stock,
            "in_stock": self.stock > 0,
            "short_desc": self.short_desc,
            "image": self.image,
            "is_featured": self.is_featured,
        }

    def __repr__(self) -> str:
        return f"<Product {self.name} ({self.price}đ)>"


class Order(db.Model):
    """Bảng đơn đặt hàng của khách."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False, default="cod")
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shipping_fee: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default=ORDER_STATUS_PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    history: Mapped[List["OrderStatusHistory"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderStatusHistory.changed_at.asc()",
    )

    @property
    def payment_label(self) -> str:
        """Tên hiển thị tiếng Việt của phương thức thanh toán."""
        return PAYMENT_METHODS.get(self.payment_method, self.payment_method)


class OrderItem(db.Model):
    """Bảng chi tiết từng dòng sản phẩm trong một đơn hàng."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(150), nullable=False)
    # Lưu đơn giá tại thời điểm đặt hàng theo yêu cầu Chương 6
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")

    @property
    def line_total(self) -> int:
        return self.unit_price * self.quantity


class OrderStatusHistory(db.Model):
    """Lịch sử mốc thời gian chuyển trạng thái đơn hàng (sẵn sàng cho Màn hình ⑪ Admin)."""

    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="history")


class BlogPost(db.Model):
    """Bảng bài viết Blog hiển thị trên trang chủ và mục Bài viết giống video giao diện."""

    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False, index=True)
    category_label: Mapped[str] = mapped_column(String(80), nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class User(db.Model):
    """
    Bảng người dùng hệ thống (Admin & Quản lý).
    Kiến thức Chương 6:
    - Băm mật khẩu an toàn bằng werkzeug.security (Chương 5 & 6).
    - Cung cấp phương thức set_password và check_password.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="admin", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


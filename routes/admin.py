import unicodedata
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, session, url_for, flash, redirect
from sqlalchemy import func, select
from extensions import db
from models import Category, Order, Product, ORDER_STATUS_PENDING, ORDER_STATUS_SHIPPING, ORDER_STATUS_COMPLETED, ORDER_STATUS_CANCELLED

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(view_func):
    """Decorator tạm thời (ở Commit 14 sẽ bổ sung kiểm tra session login thật)."""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    return wrapped_view

@admin_bp.route("/")
@admin_required
def dashboard():
    """
    Màn hình ⑥: Dashboard / Tổng quan Quản trị.
    - Thống kê doanh thu, đơn hàng, sản phẩm, danh mục bằng các hàm tổng hợp SQL (Chương 6).
    - Cảnh báo tồn kho thấp (stock <= 5).
    - Danh sách 5 đơn hàng mới nhất cần xử lý.
    """
    total_products = db.session.scalar(select(func.count(Product.id))) or 0
    total_categories = db.session.scalar(select(func.count(Category.id))) or 0
    total_orders = db.session.scalar(select(func.count(Order.id))) or 0

    revenue_all = db.session.scalar(
        select(func.sum(Order.total_amount)).where(Order.status != ORDER_STATUS_CANCELLED)
    ) or 0
    revenue_completed = db.session.scalar(
        select(func.sum(Order.total_amount)).where(Order.status == ORDER_STATUS_COMPLETED)
    ) or 0

    orders_pending = db.session.scalar(
        select(func.count(Order.id)).where(Order.status == ORDER_STATUS_PENDING)
    ) or 0
    orders_shipping = db.session.scalar(
        select(func.count(Order.id)).where(Order.status == ORDER_STATUS_SHIPPING)
    ) or 0
    orders_completed = db.session.scalar(
        select(func.count(Order.id)).where(Order.status == ORDER_STATUS_COMPLETED)
    ) or 0
    orders_cancelled = db.session.scalar(
        select(func.count(Order.id)).where(Order.status == ORDER_STATUS_CANCELLED)
    ) or 0

    low_stock_products = db.session.scalars(
        select(Product).where(Product.stock <= 5).order_by(Product.stock.asc())
    ).all()
    out_of_stock_count = sum(1 for p in low_stock_products if p.stock == 0)

    recent_orders = db.session.scalars(
        select(Order).order_by(Order.created_at.desc()).limit(5)
    ).all()

    return render_template(
        "admin/dashboard.html",
        total_products=total_products,
        total_categories=total_categories,
        total_orders=total_orders,
        revenue_all=revenue_all,
        revenue_completed=revenue_completed,
        orders_pending=orders_pending,
        orders_shipping=orders_shipping,
        orders_completed=orders_completed,
        orders_cancelled=orders_cancelled,
        low_stock_products=low_stock_products,
        out_of_stock_count=out_of_stock_count,
        recent_orders=recent_orders,
        ORDER_STATUS_PENDING=ORDER_STATUS_PENDING,
        ORDER_STATUS_SHIPPING=ORDER_STATUS_SHIPPING,
        ORDER_STATUS_COMPLETED=ORDER_STATUS_COMPLETED,
        ORDER_STATUS_CANCELLED=ORDER_STATUS_CANCELLED,
    )



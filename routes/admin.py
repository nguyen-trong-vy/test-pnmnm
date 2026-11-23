import os, re, unicodedata, time
from datetime import datetime
from functools import wraps
from pathlib import Path
from flask import Blueprint, render_template, request, session, url_for, flash, redirect, abort, current_app
from sqlalchemy import func, select, or_
from werkzeug.utils import secure_filename
from extensions import db
from forms import ProductAdminForm, CategoryAdminForm
from models import Category, Order, Product, OrderItem, ORDER_STATUS_PENDING, ORDER_STATUS_SHIPPING, ORDER_STATUS_COMPLETED, ORDER_STATUS_CANCELLED

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(view_func):
    """Decorator tạm thời (ở Commit 14 sẽ bổ sung kiểm tra session login thật)."""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    return wrapped_view

def slugify_vn(text: str) -> str:
    """Tạo slug chuẩn URL từ chuỗi tiếng Việt có dấu (vd: 'Bánh Donut Dâu' -> 'banh-donut-dau')."""
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "d")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", text)


def _unique_product_slug(base_slug: str, exclude_id: int | None = None) -> str:
    """Đảm bảo slug sản phẩm là duy nhất trong CSDL (thêm hậu tố -2, -3 nếu trùng)."""
    slug = base_slug
    counter = 2
    while True:
        stmt = select(Product).where(Product.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Product.id != exclude_id)
        existing = db.session.scalar(stmt)
        if not existing:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


def _unique_category_slug(base_slug: str, exclude_id: int | None = None) -> str:
    """Đảm bảo slug danh mục là duy nhất trong CSDL (thêm hậu tố -2, -3 nếu trùng)."""
    slug = base_slug
    counter = 2
    while True:
        stmt = select(Category).where(Category.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Category.id != exclude_id)
        existing = db.session.scalar(stmt)
        if not existing:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


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


# === MÀN HÌNH ⑦: QUẢN LÝ DANH SÁCH SẢN PHẨM ===
@admin_bp.route("/san-pham")
@admin_required
def products():
    """
    Màn hình ⑦: Danh sách sản phẩm dành cho quản trị viên.
    - Tìm kiếm theo tên bánh / mô tả (?q=...)
    - Lọc theo danh mục (?category_id=...)
    - Lọc theo tình trạng kho (?stock=all | in_stock | low_stock | out_of_stock)
    - Phân trang chuẩn SQLAlchemy db.paginate (10 món/trang)
    """
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    stock_filter = request.args.get("stock", "all").strip()
    page = request.args.get("page", 1, type=int)

    stmt = select(Product)

    if q:
        kw = f"%{q}%"
        stmt = stmt.where(or_(Product.name.ilike(kw), Product.short_desc.ilike(kw)))

    if category_id:
        stmt = stmt.where(Product.category_id == category_id)

    if stock_filter == "in_stock":
        stmt = stmt.where(Product.stock > 5)
    elif stock_filter == "low_stock":
        stmt = stmt.where(Product.stock > 0, Product.stock <= 5)
    elif stock_filter == "out_of_stock":
        stmt = stmt.where(Product.stock == 0)

    stmt = stmt.order_by(Product.id.desc())

    pagination = db.paginate(stmt, page=page, per_page=10, error_out=False)
    categories = db.session.scalars(select(Category).order_by(Category.name.asc())).all()

    return render_template(
        "admin/products.html",
        pagination=pagination,
        products=pagination.items,
        categories=categories,
        q=q,
        selected_category_id=category_id,
        selected_stock=stock_filter,
    )


# === MÀN HÌNH ⑧: THÊM MỚI SẢN PHẨM ===
@admin_bp.route("/san-pham/them", methods=["GET", "POST"])
@admin_required
def product_add():
    """
    Màn hình ⑧: Thêm bánh mới vào thực đơn.
    - Form Flask-WTF có CSRF protection.
    - Upload file ảnh an toàn hoặc chọn ảnh có sẵn.
    - Tự động sinh slug duy nhất.
    """
    categories = db.session.scalars(select(Category).order_by(Category.name.asc())).all()
    form = ProductAdminForm()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        base_slug = slugify_vn(form.name.data)
        slug = _unique_product_slug(base_slug)

        image_path = "images/products/sinh-nhat-1.avif"
        file = form.image_file.data
        if file and getattr(file, "filename", None):
            ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "avif"
            filename = f"banh_{base_slug[:30]}_{int(time.time())}.{ext}"
            filename = secure_filename(filename)

            upload_dir = Path(current_app.root_path) / "static" / "images" / "products"
            upload_dir.mkdir(parents=True, exist_ok=True)
            file.save(upload_dir / filename)
            image_path = f"images/products/{filename}"
        elif form.existing_image.data and form.existing_image.data.strip():
            image_path = form.existing_image.data.strip()

        new_product = Product(
            name=form.name.data.strip(),
            slug=slug,
            category_id=form.category_id.data,
            price=form.price.data,
            stock=form.stock.data,
            is_featured=form.is_featured.data,
            short_desc=form.short_desc.data.strip(),
            description=form.description.data.strip(),
            image=image_path,
        )

        db.session.add(new_product)
        db.session.commit()
        flash(f"Đã thêm bánh '{new_product.name}' vào hệ thống thành công!", "success")
        return redirect(url_for("admin.products"))

    return render_template(
        "admin/product_form.html",
        form=form,
        is_edit=False,
        product=None,
    )


# === MÀN HÌNH ⑧: CHỈNH SỬA SẢN PHẨM ===
@admin_bp.route("/san-pham/sua/<int:product_id>", methods=["GET", "POST"])
@admin_required
def product_edit(product_id: int):
    """
    Màn hình ⑧: Chỉnh sửa thông tin bánh.
    - Nếu không tải ảnh mới lên thì giữ nguyên product.image hiện tại.
    """
    product = db.session.get(Product, product_id)
    if not product:
        flash("Không tìm thấy sản phẩm cần chỉnh sửa.", "danger")
        return redirect(url_for("admin.products"))

    categories = db.session.scalars(select(Category).order_by(Category.name.asc())).all()
    form = ProductAdminForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        base_slug = slugify_vn(form.name.data)
        slug = _unique_product_slug(base_slug, exclude_id=product.id)

        product.name = form.name.data.strip()
        product.slug = slug
        product.category_id = form.category_id.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.is_featured = form.is_featured.data
        product.short_desc = form.short_desc.data.strip()
        product.description = form.description.data.strip()

        file = form.image_file.data
        if file and getattr(file, "filename", None):
            ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "avif"
            filename = f"banh_{base_slug[:30]}_{int(time.time())}.{ext}"
            filename = secure_filename(filename)

            upload_dir = Path(current_app.root_path) / "static" / "images" / "products"
            upload_dir.mkdir(parents=True, exist_ok=True)
            file.save(upload_dir / filename)
            product.image = f"images/products/{filename}"
        elif form.existing_image.data and form.existing_image.data.strip():
            product.image = form.existing_image.data.strip()

        db.session.commit()
        flash(f"Đã cập nhật thông tin bánh '{product.name}' thành công!", "success")
        return redirect(url_for("admin.products"))

    return render_template(
        "admin/product_form.html",
        form=form,
        is_edit=True,
        product=product,
    )


# === XOÁ SẢN PHẨM (CÓ BẢO TOÀN DỮ LIỆU) ===
@admin_bp.route("/san-pham/xoa/<int:product_id>", methods=["POST"])
@admin_required
def product_delete(product_id: int):
    """
    Xoá sản phẩm an toàn:
    - Kiểm tra xem bánh đã từng nằm trong hoá đơn cũ (OrderItem) chưa.
    - Nếu đã từng bán: chặn xoá để không vi phạm ràng buộc toàn vẹn tham chiếu.
    """
    product = db.session.get(Product, product_id)
    if not product:
        flash("Sản phẩm không tồn tại.", "danger")
        return redirect(url_for("admin.products"))

    order_count = db.session.scalar(
        select(func.count(OrderItem.id)).where(OrderItem.product_id == product.id)
    ) or 0

    if order_count > 0:
        flash(
            f"Không thể xoá bánh '{product.name}' vì đã xuất hiện trong {order_count} đơn hàng cũ. "
            f"Vui lòng chỉnh sửa số lượng tồn kho về 0 (Hết hàng) thay vì xoá vĩnh viễn.",
            "warning",
        )
        return redirect(url_for("admin.products"))

    product_name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f"Đã xoá bánh '{product_name}' khỏi hệ thống thành công.", "success")
    return redirect(url_for("admin.products"))


# === MÀN HÌNH ⑨: QUẢN LÝ DANH MỤC SẢN PHẨM ===
@admin_bp.route("/danh-muc", methods=["GET", "POST"])
@admin_required
def categories():
    """
    Màn hình ⑨: Quản lý danh mục bánh.
    - Xem danh sách danh mục và số lượng bánh thuộc từng danh mục (outerjoin + func.count).
    - Thêm danh mục mới hoặc chỉnh sửa danh mục hiện có (?edit=<id>).
    """
    edit_id = request.args.get("edit", type=int)
    edit_cat = None
    if edit_id:
        edit_cat = db.session.get(Category, edit_id)

    form = CategoryAdminForm(obj=edit_cat) if (edit_cat and request.method == "GET") else CategoryAdminForm()

    if form.validate_on_submit():
        base_slug = slugify_vn(form.name.data)

        # Xử lý upload ảnh
        image_path = edit_cat.image if edit_cat else "images/categories/banh-donut.avif"
        file = form.image_file.data
        if file and getattr(file, "filename", None):
            ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "avif"
            filename = f"cat_{base_slug[:30]}_{int(time.time())}.{ext}"
            filename = secure_filename(filename)

            upload_dir = Path(current_app.root_path) / "static" / "images" / "categories"
            upload_dir.mkdir(parents=True, exist_ok=True)
            file.save(upload_dir / filename)
            image_path = f"images/categories/{filename}"
        elif form.existing_image.data and form.existing_image.data.strip():
            image_path = form.existing_image.data.strip()

        if edit_cat:
            slug = _unique_category_slug(base_slug, exclude_id=edit_cat.id)
            edit_cat.name = form.name.data.strip()
            edit_cat.slug = slug
            edit_cat.description = form.description.data.strip() if form.description.data else ""
            edit_cat.image = image_path
            db.session.commit()
            flash(f"Đã cập nhật danh mục '{edit_cat.name}' thành công!", "success")
        else:
            slug = _unique_category_slug(base_slug)
            new_cat = Category(
                name=form.name.data.strip(),
                slug=slug,
                description=form.description.data.strip() if form.description.data else "",
                image=image_path,
            )
            db.session.add(new_cat)
            db.session.commit()
            flash(f"Đã thêm mới danh mục '{new_cat.name}' thành công!", "success")

        return redirect(url_for("admin.categories"))

    # Lấy danh sách kèm số lượng sản phẩm bằng outerjoin + group_by (Chương 6)
    stmt = (
        select(Category, func.count(Product.id).label("product_count"))
        .outerjoin(Product, Category.id == Product.category_id)
        .group_by(Category.id)
        .order_by(Category.id.asc())
    )
    categories_with_count = db.session.execute(stmt).all()

    return render_template(
        "admin/categories.html",
        categories_with_count=categories_with_count,
        form=form,
        edit_cat=edit_cat,
    )


@admin_bp.route("/danh-muc/xoa/<int:category_id>", methods=["POST"])
@admin_required
def category_delete(category_id: int):
    """
    Xoá danh mục an toàn:
    - Kiểm tra xem danh mục còn sản phẩm bên trong không.
    - Nếu còn: CHẶN xoá để đảm bảo toàn vẹn tham chiếu (Referential Integrity).
    """
    category = db.session.get(Category, category_id)
    if not category:
        flash("Danh mục không tồn tại.", "danger")
        return redirect(url_for("admin.categories"))

    product_count = db.session.scalar(
        select(func.count(Product.id)).where(Product.category_id == category.id)
    ) or 0

    if product_count > 0:
        flash(
            f"Không thể xoá danh mục '{category.name}' vì đang có {product_count} sản phẩm bánh thuộc danh mục này. "
            f"Vui lòng xoá hoặc chuyển các bánh sang danh mục khác trước.",
            "warning",
        )
        return redirect(url_for("admin.categories"))

    cat_name = category.name
    db.session.delete(category)
    db.session.commit()
    flash(f"Đã xoá danh mục '{cat_name}' thành công.", "success")
    return redirect(url_for("admin.categories"))


# === MÀN HÌNH ⑩: DANH SÁCH ĐƠN ĐẶT HÀNG ===
@admin_bp.route("/don-hang")
@admin_required
def orders():
    """
    Màn hình ⑩: Danh sách đơn hàng trong hệ thống.
    - Tìm kiếm theo mã đơn, họ tên khách hoặc số điện thoại (?q=...)
    - Lọc theo trạng thái (?status=all | Chờ xác nhận | Đang giao | Hoàn tất | Đã huỷ)
    - Thống kê nhanh số lượng đơn theo từng trạng thái để làm các tab lọc
    - Phân trang chuẩn db.paginate (10 đơn/trang)
    """
    q = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "all").strip()
    page = request.args.get("page", 1, type=int)

    count_all = db.session.scalar(select(func.count(Order.id))) or 0
    count_pending = db.session.scalar(
        select(func.count(Order.id)).where(Order.status == ORDER_STATUS_PENDING)
    ) or 0
    count_shipping = db.session.scalar(
        select(func.count(Order.id)).where(Order.status == ORDER_STATUS_SHIPPING)
    ) or 0
    count_completed = db.session.scalar(
        select(func.count(Order.id)).where(Order.status == ORDER_STATUS_COMPLETED)
    ) or 0
    count_cancelled = db.session.scalar(
        select(func.count(Order.id)).where(Order.status == ORDER_STATUS_CANCELLED)
    ) or 0

    stmt = select(Order)

    if q:
        kw = f"%{q}%"
        if q.isdigit():
            stmt = stmt.where(or_(Order.id == int(q), Order.customer_name.ilike(kw), Order.phone.ilike(kw)))
        else:
            stmt = stmt.where(or_(Order.customer_name.ilike(kw), Order.phone.ilike(kw)))

    if status_filter != "all" and status_filter:
        stmt = stmt.where(Order.status == status_filter)

    stmt = stmt.order_by(Order.created_at.desc())
    pagination = db.paginate(stmt, page=page, per_page=10, error_out=False)

    return render_template(
        "admin/orders.html",
        pagination=pagination,
        orders=pagination.items,
        q=q,
        selected_status=status_filter,
        count_all=count_all,
        count_pending=count_pending,
        count_shipping=count_shipping,
        count_completed=count_completed,
        count_cancelled=count_cancelled,
        ORDER_STATUS_PENDING=ORDER_STATUS_PENDING,
        ORDER_STATUS_SHIPPING=ORDER_STATUS_SHIPPING,
        ORDER_STATUS_COMPLETED=ORDER_STATUS_COMPLETED,
        ORDER_STATUS_CANCELLED=ORDER_STATUS_CANCELLED,
    )


# === MÀN HÌNH ⑪: CHI TIẾT ĐƠN HÀNG & CẬP NHẬT TRẠNG THÁI ===
@admin_bp.route("/don-hang/<int:order_id>", methods=["GET", "POST"])
@admin_required
def order_detail(order_id: int):
    """
    Màn hình ⑪: Chi tiết đơn hàng và lịch sử chuyển trạng thái.
    - Xem thông tin khách hàng, địa chỉ, phương thức thanh toán, danh sách OrderItem.
    - Form cập nhật trạng thái đơn hàng (OrderStatusUpdateForm).
    - Tự động ghi nhận mốc thời gian vào OrderStatusHistory khi trạng thái thay đổi.
    """
    order = db.session.get(Order, order_id)
    if not order:
        flash("Không tìm thấy đơn hàng yêu cầu.", "danger")
        return redirect(url_for("admin.orders"))

    form = OrderStatusUpdateForm(status=order.status)

    if form.validate_on_submit():
        new_status = form.status.data
        if new_status != order.status:
            old_status = order.status
            order.status = new_status

            # Ghi vết lịch sử vào bảng OrderStatusHistory (Chương 6)
            history_entry = OrderStatusHistory(
                order_id=order.id,
                status=new_status,
                changed_at=datetime.now(),
            )
            db.session.add(history_entry)
            db.session.commit()

            flash(
                f"Đã cập nhật trạng thái đơn hàng #{order.id} từ '{old_status}' sang '{new_status}' thành công!",
                "success",
            )
        else:
            flash("Trạng thái đơn hàng không thay đổi.", "info")

        return redirect(url_for("admin.order_detail", order_id=order.id))

    return render_template(
        "admin/order_detail.html",
        order=order,
        form=form,
        ORDER_STATUS_PENDING=ORDER_STATUS_PENDING,
        ORDER_STATUS_SHIPPING=ORDER_STATUS_SHIPPING,
        ORDER_STATUS_COMPLETED=ORDER_STATUS_COMPLETED,
        ORDER_STATUS_CANCELLED=ORDER_STATUS_CANCELLED,
    )
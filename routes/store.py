"""
routes/store.py - Các tuyến đường trang bán hàng, danh mục, tìm kiếm an toàn và Blog.

Kiến thức áp dụng:
- Chương 3:
    + Khai báo route với converter (<int:product_id>, <slug>).
    + Lấy tham số truy vấn bằng request.args (lọc danh mục, tìm kiếm, phân trang).
    + Chuyển hướng 301 vĩnh viễn cho link rút gọn /sp/<int:product_id> -> /san-pham/<int:product_id>.
    + Xuất dữ liệu CSV tải xuống bằng make_response (Content-Type & Content-Disposition).
    + Tìm kiếm an toàn chống XSS (giữ lại từ khoá và escape an toàn).
    + Gọi abort(404, description=...) khi không tìm thấy dữ liệu.
- Chương 4: Render giao diện kế thừa từ base.html bằng Jinja2.
- Chương 6: Truy vấn SQLAlchemy 2.0 (select, paginate, func.count, func.avg, func.sum).
"""

import csv
import io

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from markupsafe import escape
from sqlalchemy import func, or_, select

from extensions import db
from forms import AddToCartForm
from models import BlogPost, Category, Product
from seed import seed_database

store_bp = Blueprint("store", __name__)


def _get_cart_dict() -> dict[str, int]:
    """Hàm phụ đọc giỏ hàng hiện tại từ Session (Chương 5)."""
    cart = session.get("cart", {})
    return cart if isinstance(cart, dict) else {}


@store_bp.route("/")
def home():
    """
    Trang chủ Tiệm bánh Yuu Cake - tái hiện đầy đủ các phân khu như video giao diện:
    1. Hero Slider toàn chiều rộng
    2. Thanh chạy chữ thông báo (Marquee)
    3. Khu vực 'Kiệt tác bánh ngọt, chinh phục mọi giác quan'
    4. Danh mục sản phẩm (lấy động từ CSDL)
    5. Sản phẩm nổi bật (lấy động từ CSDL)
    6. Blog (3 bài viết mới nhất)
    """
    categories = db.session.scalars(select(Category).order_by(Category.id.asc())).all()
    featured_products = db.session.scalars(
        select(Product)
        .where(Product.is_featured.is_(True))
        .order_by(Product.id.asc())
        .limit(8)
    ).all()
    latest_posts = db.session.scalars(
        select(BlogPost).order_by(BlogPost.published_at.desc()).limit(3)
    ).all()

    # Thống kê nhanh bằng func.count và func.avg (kiến thức Chương 6)
    total_products = db.session.scalar(select(func.count(Product.id))) or 0
    total_categories = db.session.scalar(select(func.count(Category.id))) or 0

    return render_template(
        "home.html",
        categories=categories,
        featured_products=featured_products,
        latest_posts=latest_posts,
        total_products=total_products,
        total_categories=total_categories,
    )


@store_bp.route("/san-pham")
def products():
    """
    Màn hình ① Danh sách sản phẩm:
    - Tìm kiếm theo tên bánh hoặc mô tả (?q=...)
    - Lọc theo danh mục động từ CSDL (?category=banh-donut)
    - Lọc theo tình trạng hàng (?stock=in_stock)
    - Sắp xếp (?sort=price_asc | price_desc | newest)
    - Phân trang giữ nguyên bộ lọc (?page=1)
    """
    q = request.args.get("q", "").strip()
    category_slug = request.args.get("category", "").strip().lower()
    stock_filter = request.args.get("stock", "").strip()
    sort_by = request.args.get("sort", "newest").strip()
    page = request.args.get("page", 1, type=int)

    stmt = select(Product)
    active_category = None

    if category_slug:
        active_category = db.session.scalar(
            select(Category).where(func.lower(Category.slug) == category_slug)
        )
        if active_category:
            stmt = stmt.where(Product.category_id == active_category.id)
        else:
            # Danh mục không tồn tại -> trả danh sách rỗng
            stmt = stmt.where(Product.id == -1)

    if q:
        keyword = f"%{q}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(keyword),
                Product.short_desc.ilike(keyword),
                Product.description.ilike(keyword),
            )
        )

    if stock_filter == "in_stock":
        stmt = stmt.where(Product.stock > 0)

    if sort_by == "price_asc":
        stmt = stmt.order_by(Product.price.asc(), Product.id.asc())
    elif sort_by == "price_desc":
        stmt = stmt.order_by(Product.price.desc(), Product.id.asc())
    else:
        stmt = stmt.order_by(Product.is_featured.desc(), Product.id.asc())

    per_page = current_app.config.get("PRODUCTS_PER_PAGE", 8)
    pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    # Truy vấn số lượng sản phẩm theo từng danh mục bằng group_by + func.count (Chương 6)
    cat_counts_rows = db.session.execute(
        select(Category, func.count(Product.id).label("product_count"))
        .outerjoin(Product, Category.id == Product.category_id)
        .group_by(Category.id)
        .order_by(Category.id.asc())
    ).all()

    return render_template(
        "products.html",
        products=pagination.items,
        pagination=pagination,
        cat_counts=cat_counts_rows,
        active_category=active_category,
        category_slug=category_slug,
        q=q,
        stock_filter=stock_filter,
        sort_by=sort_by,
    )


@store_bp.route("/san-pham/<int:product_id>")
def product_detail(product_id: int):
    """
    Màn hình ② Chi tiết sản phẩm:
    - Hiển thị breadcrumb, ảnh, giá, tồn kho, mô tả chi tiết.
    - Tính tối đa số lượng có thể thêm = stock - số lượng đã có trong giỏ hàng Session.
    - Kèm link rút gọn /sp/<id> (chuyển hướng 301) và nút tải thông tin CSV (Chương 3).
    """
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404, description=f"Không tìm thấy sản phẩm với mã ID = {product_id}.")

    cart = _get_cart_dict()
    in_cart = int(cart.get(str(product.id), 0))
    max_addable = max(0, product.stock - in_cart)

    form = AddToCartForm()
    related_products = db.session.scalars(
        select(Product)
        .where(Product.category_id == product.category_id, Product.id != product.id)
        .limit(4)
    ).all()

    return render_template(
        "product_detail.html",
        product=product,
        form=form,
        in_cart=in_cart,
        max_addable=max_addable,
        related_products=related_products,
    )


@store_bp.route("/sp/<int:product_id>")
def product_short_redirect(product_id: int):
    """
    Link rút gọn sản phẩm (kiến thức Chương 3 - Câu 4):
    Chuyển hướng vĩnh viễn mã 301 sang trang chi tiết chuẩn /san-pham/<product_id>.
    Mọi header Location sinh bằng url_for(), không viết cứng URL.
    """
    return redirect(url_for("store.product_detail", product_id=product_id), code=301)


@store_bp.route("/san-pham/<int:product_id>/export")
def export_product_csv(product_id: int):
    """
    Xuất thông tin sản phẩm ra file CSV tải xuống (kiến thức Chương 3 - Câu 5):
    Sử dụng make_response thiết lập header Content-Type và Content-Disposition.
    """
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404, description=f"Không tìm thấy sản phẩm với mã ID = {product_id}.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ma_sp", "ten_banh", "danh_muc", "gia_vnd", "ton_kho", "mo_ta_ngan"])
    writer.writerow([
        product.id,
        product.name,
        product.category.name,
        product.price,
        product.stock,
        product.short_desc,
    ])

    # Thêm UTF-8 BOM (﻿) giúp mở file CSV tiếng Việt trên Excel không bị lỗi phông
    response = make_response("﻿" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=banh_{product.id}.csv"
    return response


@store_bp.route("/tim-kiem")
def search():
    """
    Trang tìm kiếm an toàn chống XSS (kiến thức Chương 3 - Câu 6):
    - Form GET giữ lại từ khoá đã nhập trong ô <input value="{{ q }}">.
    - Jinja2 tự động escape dữ liệu ở cả hai chỗ (trong thuộc tính value và tiêu đề kết quả).
    - Ta cũng minh hoạ markupsafe.escape() cho chuỗi mô tả an toàn khi kiểm thử payload:
      /tim-kiem?q=<script>alert(1)</script> và /tim-kiem?q="><script>alert(1)</script>.
    """
    q = request.args.get("q", "").strip()
    # escape(q) chuyển < > " ' thành thực thể HTML an toàn khi cần xử lý ở tầng Python
    safe_q_preview = str(escape(q))
    results = []

    if q:
        keyword = f"%{q}%"
        results = db.session.scalars(
            select(Product)
            .join(Category)
            .where(
                or_(
                    Product.name.ilike(keyword),
                    Product.short_desc.ilike(keyword),
                    Category.name.ilike(keyword),
                )
            )
            .order_by(Product.id.asc())
        ).all()

    return render_template(
        "search.html",
        q=q,
        safe_q_preview=safe_q_preview,
        results=results,
    )


@store_bp.route("/bai-viet")
def blog_list():
    """Danh sách bài viết Blog của Tiệm bánh Yuu Cake."""
    tag = request.args.get("tag", "").strip()
    stmt = select(BlogPost).order_by(BlogPost.published_at.desc())
    if tag:
        stmt = stmt.where(BlogPost.category_label == tag)
    posts = db.session.scalars(stmt).all()
    tags = db.session.scalars(select(BlogPost.category_label).distinct()).all()
    return render_template("blog_list.html", posts=posts, tags=tags, active_tag=tag)


@store_bp.route("/bai-viet/<slug>")
def blog_detail(slug: str):
    """Trang chi tiết một bài viết Blog theo đường dẫn thân thiện (slug)."""
    post = db.session.scalar(select(BlogPost).where(BlogPost.slug == slug))
    if post is None:
        abort(404, description=f"Không tìm thấy bài viết với đường dẫn '{slug}'.")
    other_posts = db.session.scalars(
        select(BlogPost).where(BlogPost.id != post.id).order_by(BlogPost.published_at.desc())
    ).all()
    return render_template("blog_detail.html", post=post, other_posts=other_posts)


@store_bp.route("/hoi-dap")
def faq():
    """Trang Hỏi đáp (FAQ) về đặt bánh, bảo quản và giao hàng tại Yuu Cake."""
    faqs = [
        (
            "Yuu Cake có miễn phí giao hàng không?",
            "Có! Yuu Cake miễn phí giao hàng trong phạm vi 2km hoặc cho mọi đơn hàng có tạm tính từ 200.000 đ trở lên. Đơn dưới 200.000 đ có phí giao hàng đồng giá 20.000 đ.",
        ),
        (
            "Nên đặt bánh sinh nhật trước bao lâu?",
            "Với các mẫu bánh kem tươi và mousse có sẵn trên website, bạn có thể đặt giao trong ngày (từ 2–3 giờ). Với bánh thiết kế theo yêu cầu riêng, vui lòng đặt trước ít nhất 24 giờ.",
        ),
        (
            "Bánh bảo quản được trong bao lâu?",
            "Bánh Donut và Cupcake ngon nhất khi dùng trong 24 giờ ở nhiệt độ mát. Bánh sinh nhật bảo quản ngăn mát tủ lạnh (2–5°C) dùng ngon trong 2–3 ngày. Bánh quy hộp kín bảo quản được 10–14 ngày.",
        ),
        (
            "Tôi có thể thanh toán bằng hình thức nào?",
            "Website hỗ trợ hai phương thức: Tiền mặt khi nhận hàng (COD) và Chuyển khoản ngân hàng. Bạn có thể chọn trực tiếp ở bước Đặt hàng.",
        ),
        (
            "Nếu giỏ hàng báo sản phẩm hết hàng hoặc không đủ tồn kho thì sao?",
            "Hệ thống luôn kiểm tra tồn kho thực tế từ cơ sở dữ liệu ở cả bước thêm vào giỏ và bước xác nhận đặt hàng để đảm bảo quyền lợi cho khách hàng.",
        ),
    ]
    return render_template("faq.html", faqs=faqs)


@store_bp.route("/ve-yuucake")
def about():
    """Trang giới thiệu Về YuuCake kèm số liệu thống kê thực tế từ CSDL (func.count, func.avg, func.sum)."""
    stats = {
        "total_categories": db.session.scalar(select(func.count(Category.id))) or 0,
        "total_products": db.session.scalar(select(func.count(Product.id))) or 0,
        "total_stock": db.session.scalar(select(func.sum(Product.stock))) or 0,
        "avg_price": int(db.session.scalar(select(func.avg(Product.price))) or 0),
    }
    return render_template("about.html", stats=stats)


@store_bp.route("/them-mau")
def load_sample_data():
    """
    Route tiện ích /them-mau (theo kiến thức Chương 6 trong tài liệu nguồn):
    Nạp nhanh dữ liệu mẫu nếu CSDL đang trống, sau đó flash thông báo và chuyển về trang chủ.
    """
    result = seed_database()
    if result["seeded"]:
        flash(
            f"Đã nạp dữ liệu mẫu thành công: {result['categories']} danh mục, "
            f"{result['products']} sản phẩm và {result['blogs']} bài viết.",
            "success",
        )
    else:
        flash(
            f"Cơ sở dữ liệu đã có sẵn dữ liệu mẫu ({result['products']} sản phẩm).",
            "info",
        )
    return redirect(url_for("store.home"))

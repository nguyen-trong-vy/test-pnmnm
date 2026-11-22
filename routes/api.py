"""
routes/api.py - Giao diện lập trình API JSON tổng hợp kiến thức Chương 3 (Câu 7 & Câu 8).

Các endpoint tiêu biểu (kiểm thử trực tiếp bằng curl):
1. GET /api/products
   - Hỗ trợ lọc kết hợp: ?category=banh-donut&min_price=50000&q=kem
   - Phân biệt rõ trường hợp THIẾU min_price (bỏ qua) và SAI KIỂU min_price=abc (trả 400).
2. GET /api/products/<int:product_id>
   - Trả dict chi tiết sản phẩm; không tồn tại -> 404 JSON.
3. GET /api/categories
   - Thống kê danh mục kèm số lượng sản phẩm và giá trung bình (func.count, func.avg - Chương 6).
4. /api/cart/items/<int:product_id> (GET, PUT, DELETE; POST -> 405 JSON):
   - GET: xem số lượng sản phẩm trong giỏ Session (chưa có -> 404).
   - PUT ?qty=2: chưa có trong giỏ -> 201 + header Location sinh bằng url_for; đã có -> 200;
                 thiếu/sai kiểu/<=0/vượt tồn kho -> 400.
   - DELETE: xoá khỏi giỏ -> 204 body rỗng (chưa có -> 404).
"""

from flask import Blueprint, abort, jsonify, make_response, request, url_for
from sqlalchemy import func, or_, select

from extensions import csrf, db
from models import Category, Product
from routes.cart import get_cart, save_cart

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Các API JSON kiểm thử qua curl không gửi cookie form HTML nên miễn CSRF riêng cho blueprint API
csrf.exempt(api_bp)


@api_bp.route("/products", methods=["GET"])
def api_list_products():
    """
    GET /api/products?category=...&min_price=...&q=...
    Chú ý tiêu chí Chương 3 Câu 7: phân biệt rõ thiếu min_price và sai kiểu min_price!
    """
    category_slug = request.args.get("category", "").strip().lower()
    q = request.args.get("q", "").strip()
    min_price_raw = request.args.get("min_price")  # None nếu không truyền tham số

    min_price = None
    if min_price_raw is not None and min_price_raw != "":
        try:
            min_price = int(min_price_raw)
            if min_price < 0:
                abort(400, description="Tham số min_price không được nhỏ hơn 0.")
        except ValueError:
            abort(400, description=f"Tham số min_price='{min_price_raw}' không phải số nguyên hợp lệ.")

    stmt = select(Product).join(Category)

    if category_slug:
        stmt = stmt.where(func.lower(Category.slug) == category_slug)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if q:
        keyword = f"%{q}%"
        stmt = stmt.where(or_(Product.name.ilike(keyword), Product.short_desc.ilike(keyword)))

    products = db.session.scalars(stmt.order_by(Product.id.asc())).all()
    return jsonify([p.to_dict() for p in products])


@api_bp.route("/products/<int:product_id>", methods=["GET"])
def api_product_detail(product_id: int):
    """GET /api/products/<id> - Trả JSON chi tiết 1 sản phẩm, không tồn tại -> 404."""
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404, description=f"Không có sản phẩm với ID = {product_id}.")
    return jsonify(product.to_dict())


@api_bp.route("/categories", methods=["GET"])
def api_categories_stats():
    """GET /api/categories - Thống kê từng danh mục bằng group_by, func.count, func.avg."""
    rows = db.session.execute(
        select(
            Category,
            func.count(Product.id).label("product_count"),
            func.avg(Product.price).label("avg_price"),
        )
        .outerjoin(Product, Category.id == Product.category_id)
        .group_by(Category.id)
        .order_by(Category.id.asc())
    ).all()

    data = [
        {
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "product_count": int(count or 0),
            "avg_price": round(float(avg_p), 2) if avg_p is not None else None,
        }
        for cat, count, avg_p in rows
    ]
    return jsonify(data)


@api_bp.route("/cart/items/<int:product_id>", methods=["GET", "PUT", "DELETE"])
def api_cart_item(product_id: int):
    """
    Quản lý một mặt hàng trong giỏ bằng 1 route duy nhất (mô phỏng Câu 8 Chương 3):
    - GET    -> 200 {"product_id", "name", "quantity", "unit_price", "line_total"} hoặc 404
    - PUT    -> ?qty=N: thêm mới -> 201 + header Location; sửa -> 200; lỗi -> 400
    - DELETE -> xoá khỏi giỏ -> 204 body rỗng; chưa có -> 404
    - POST   -> không khai báo trong methods -> Flask tự động báo 405 JSON
    """
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404, description=f"Không có sản phẩm với ID = {product_id}.")

    cart = get_cart()
    key = str(product.id)

    if request.method == "GET":
        if key not in cart:
            abort(404, description=f"Sản phẩm ID = {product_id} chưa có trong giỏ hàng.")
        qty = cart[key]
        return jsonify({
            "product_id": product.id,
            "name": product.name,
            "quantity": qty,
            "unit_price": product.price,
            "line_total": product.price * qty,
        })

    if request.method == "PUT":
        qty_raw = request.args.get("qty")
        if qty_raw is None or qty_raw.strip() == "":
            abort(400, description="Thiếu tham số truy vấn 'qty' (ví dụ: ?qty=2).")
        try:
            qty = int(qty_raw)
        except ValueError:
            abort(400, description=f"Giá trị qty='{qty_raw}' phải là số nguyên.")

        if qty < 1 or qty > product.stock:
            abort(
                400,
                description=f"Số lượng phải nằm trong khoảng [1, {product.stock}].",
            )

        is_new = key not in cart
        cart[key] = qty
        save_cart(cart)

        total_items = sum(cart.values())
        payload = {
            "product_id": product.id,
            "name": product.name,
            "quantity": qty,
            "unit_price": product.price,
            "line_total": product.price * qty,
            "cart_total_items": total_items,
        }
        if is_new:
            resp = make_response(jsonify(payload), 201)
            # Header Location sinh hoàn toàn bằng url_for() theo yêu cầu Chương 3
            resp.headers["Location"] = url_for("api.api_cart_item", product_id=product.id)
            return resp
        return jsonify(payload), 200

    # request.method == "DELETE"
    if key not in cart:
        abort(404, description=f"Sản phẩm ID = {product_id} không có trong giỏ hàng để xoá.")
    cart.pop(key, None)
    save_cart(cart)
    return "", 204

"""
routes/cart.py - Quản lý Giỏ hàng lưu bằng Flask Session (Màn hình ③).

Kiến thức Chương 5 & 6:
- Giỏ hàng lưu trong session["cart"] dạng dict: {"<product_id>": <quantity>}.
- KHÔNG lưu giá trong session: mọi tính toán luôn truy vấn giá mới nhất từ CSDL SQLite.
- Mọi thao tác thay đổi giỏ hàng (thêm, tăng, giảm, xoá, xoá tất cả) đều là POST có CSRF token
  và kết thúc bằng redirect() theo mô hình PRG (Post-Redirect-Get) để tránh gửi lặp khi F5.
- Kiểm tra tồn kho chặt chẽ phía server (không tin tưởng dữ liệu gửi từ trình duyệt).
"""

from urllib.parse import urlparse

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select

from extensions import db
from models import Product

cart_bp = Blueprint("cart", __name__)


def get_cart() -> dict[str, int]:
    """Lấy bản sao dict giỏ hàng từ Session."""
    raw = session.get("cart", {})
    if not isinstance(raw, dict):
        return {}
    clean = {}
    for k, v in raw.items():
        try:
            qty = int(v)
            if qty > 0:
                clean[str(k)] = qty
        except (TypeError, ValueError):
            continue
    return clean


def save_cart(cart: dict[str, int]) -> None:
    """Lưu lại giỏ hàng vào Session và đánh dấu session đã thay đổi."""
    session["cart"] = cart
    session.modified = True


def build_cart_details() -> tuple[list[dict], int]:
    """
    Truy vấn thông tin và giá MỚI NHẤT từ CSDL cho các sản phẩm trong giỏ.
    Trả về (danh_sach_dong_gio_hang, tong_tam_tinh).
    """
    cart = get_cart()
    if not cart:
        return [], 0

    product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
    products = db.session.scalars(select(Product).where(Product.id.in_(product_ids))).all()
    product_map = {str(p.id): p for p in products}

    items = []
    subtotal = 0
    changed = False

    for pid_str in list(cart.keys()):
        product = product_map.get(pid_str)
        if product is None:
            # Sản phẩm đã bị xoá khỏi CSDL -> tự động bỏ khỏi giỏ
            cart.pop(pid_str, None)
            changed = True
            continue
        qty = cart[pid_str]
        line_total = product.price * qty
        subtotal += line_total
        items.append({
            "product": product,
            "quantity": qty,
            "line_total": line_total,
            "at_max": qty >= product.stock,
            "out_of_stock": product.stock <= 0 or qty > product.stock,
        })

    if changed:
        save_cart(cart)

    return items, subtotal


def _safe_redirect_back(default_endpoint: str = "store.products") -> str:
    """
    Chống lỗi Open Redirect: chỉ quay lại URL nội bộ (cùng host) từ trường 'next' hoặc Referer.
    """
    target = request.form.get("next") or request.referrer
    if target:
        parsed = urlparse(target)
        # Chỉ chấp nhận đường dẫn tương đối hoặc cùng netloc với server hiện tại
        if not parsed.netloc or parsed.netloc == request.host:
            return target
    return url_for(default_endpoint)


@cart_bp.route("/gio-hang")
def view_cart():
    """Màn hình ③: Hiển thị chi tiết giỏ hàng, đơn giá mới nhất từ CSDL và tổng tiền."""
    items, subtotal = build_cart_details()
    return render_template("cart.html", items=items, subtotal=subtotal)


@cart_bp.route("/gio-hang/them/<int:product_id>", methods=["POST"])
def add_to_cart(product_id: int):
    """
    Thêm bánh vào giỏ hàng (dùng cho cả nút '+ Thêm vào giỏ' ở danh sách lẫn form số lượng ở chi tiết).
    Kiểm tra phía server: số lượng thêm phải từ 1 đến (tồn kho - số đã có trong giỏ).
    """
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404, description=f"Không tìm thấy sản phẩm với mã ID = {product_id}.")

    if product.stock <= 0:
        flash(f'Sản phẩm "{product.name}" hiện đã hết hàng.', "danger")
        return redirect(_safe_redirect_back())

    # Đọc số lượng từ form (mặc định là 1 nếu bấm nhanh từ thẻ sản phẩm)
    qty_raw = request.form.get("quantity", "1").strip()
    try:
        qty = int(qty_raw)
    except ValueError:
        flash("Số lượng không hợp lệ. Vui lòng nhập số nguyên dương.", "danger")
        return redirect(_safe_redirect_back())

    cart = get_cart()
    current_in_cart = cart.get(str(product.id), 0)
    max_addable = product.stock - current_in_cart

    if qty < 1:
        flash("Số lượng thêm vào giỏ phải lớn hơn hoặc bằng 1.", "danger")
        return redirect(_safe_redirect_back())

    if max_addable <= 0:
        flash(
            f'Bạn đã có {current_in_cart} "{product.name}" trong giỏ (đạt tối đa tồn kho).',
            "warning",
        )
        return redirect(_safe_redirect_back())

    if qty > max_addable:
        flash(
            f'Chỉ có thể thêm tối đa {max_addable} "{product.name}" '
            f"(tồn kho {product.stock}, đã có {current_in_cart} trong giỏ).",
            "danger",
        )
        return redirect(_safe_redirect_back())

    # Cộng dồn số lượng trong Session
    cart[str(product.id)] = current_in_cart + qty
    save_cart(cart)

    flash(f'Đã thêm {qty} × "{product.name}" vào giỏ hàng.', "success")
    return redirect(_safe_redirect_back())


@cart_bp.route("/gio-hang/cap-nhat/<int:product_id>", methods=["POST"])
def update_cart_item(product_id: int):
    """
    Tăng (+1) hoặc giảm (-1) số lượng một sản phẩm trong giỏ.
    - Giảm về 0 -> tự động xoá sản phẩm khỏi giỏ.
    - Tăng vượt tồn kho -> từ chối và flash cảnh báo.
    """
    product = db.session.get(Product, product_id)
    if product is None:
        abort(404, description=f"Không tìm thấy sản phẩm với mã ID = {product_id}.")

    action = request.form.get("action", "").strip()
    cart = get_cart()
    key = str(product.id)

    if key not in cart:
        flash("Sản phẩm không có trong giỏ hàng.", "warning")
        return redirect(url_for("cart.view_cart"))

    current_qty = cart[key]
    if action == "inc":
        if current_qty + 1 > product.stock:
            flash(
                f'"{product.name}" chỉ còn {product.stock} sản phẩm trong kho.',
                "warning",
            )
        else:
            cart[key] = current_qty + 1
            save_cart(cart)
    elif action == "dec":
        if current_qty - 1 <= 0:
            cart.pop(key, None)
            save_cart(cart)
            flash(f'Đã bỏ "{product.name}" khỏi giỏ hàng.', "info")
        else:
            cart[key] = current_qty - 1
            save_cart(cart)

    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/gio-hang/xoa/<int:product_id>", methods=["POST"])
def remove_cart_item(product_id: int):
    """Xoá hoàn toàn một dòng sản phẩm khỏi giỏ hàng (POST + CSRF + PRG)."""
    cart = get_cart()
    key = str(product_id)
    if key in cart:
        product = db.session.get(Product, product_id)
        cart.pop(key, None)
        save_cart(cart)
        name = product.name if product else f"#{product_id}"
        flash(f'Đã xoá "{name}" khỏi giỏ hàng.', "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/gio-hang/xoa-tat-ca", methods=["POST"])
def clear_cart():
    """Xoá sạch toàn bộ giỏ hàng (có hộp thoại xác nhận ở giao diện)."""
    save_cart({})
    flash("Đã xoá toàn bộ giỏ hàng.", "info")
    return redirect(url_for("cart.view_cart"))

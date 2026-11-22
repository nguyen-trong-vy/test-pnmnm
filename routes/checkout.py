"""
routes/checkout.py - Quy trình Đặt hàng (Màn hình ④) & Xác nhận đơn hàng (Màn hình ⑤).

Kiến thức Chương 3, 5 & 6:
- Xác thực biểu mẫu khách hàng bằng Flask-WTF (CheckoutForm).
- Tính phí giao hàng: 20.000 đ, miễn phí khi tạm tính >= 200.000 đ.
- Trước khi tạo đơn: kiểm tra lại tồn kho toàn bộ mặt hàng trong giỏ; nếu có bánh không đủ hàng
  thì không tạo đơn, quay về /gio-hang và báo rõ tên bánh nào.
- Khi hợp lệ: tạo Order (trạng thái "Chờ xác nhận"), các OrderItem (lưu unit_price lúc đặt),
  bản ghi lịch sử OrderStatusHistory đầu tiên, trừ stock trong CSDL, xoá giỏ hàng Session,
  và chuyển sang /don-hang/<id>.
- Hỗ trợ xuất hoá đơn CSV (/don-hang/<id>/export) bằng make_response (Chương 3).
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
    url_for,
)

from extensions import db
from forms import CheckoutForm
from models import ORDER_STATUS_PENDING, Order, OrderItem, OrderStatusHistory
from routes.cart import build_cart_details, save_cart

checkout_bp = Blueprint("checkout", __name__)


def calculate_shipping(subtotal: int) -> int:
    """Tính phí giao hàng: miễn phí nếu tạm tính đạt ngưỡng tối thiểu (200.000 đ)."""
    free_min = current_app.config.get("FREE_SHIPPING_MIN", 200_000)
    fee = current_app.config.get("SHIPPING_FEE", 20_000)
    return 0 if subtotal >= free_min else fee


@checkout_bp.route("/dat-hang", methods=["GET", "POST"])
def checkout():
    """Màn hình ④: Nhập thông tin khách hàng và xác nhận đặt hàng."""
    items, subtotal = build_cart_details()

    # Giỏ rỗng mà vào /dat-hang -> chuyển về /gio-hang kèm flash cảnh báo
    if not items:
        flash("Giỏ hàng đang trống. Vui lòng chọn bánh trước khi đặt hàng.", "warning")
        return redirect(url_for("cart.view_cart"))

    shipping_fee = calculate_shipping(subtotal)
    grand_total = subtotal + shipping_fee
    form = CheckoutForm()

    if form.validate_on_submit():
        # Kiểm tra lại tồn kho thực tế trong CSDL trước khi chốt đơn
        insufficient = []
        for entry in items:
            product = entry["product"]
            qty = entry["quantity"]
            if product.stock < qty:
                insufficient.append(
                    f'"{product.name}" (chỉ còn {product.stock}, bạn đặt {qty})'
                )

        if insufficient:
            flash(
                "Không thể tạo đơn vì sản phẩm không đủ hàng: " + ", ".join(insufficient) + ".",
                "danger",
            )
            return redirect(url_for("cart.view_cart"))

        # Tạo đơn hàng mới trong 1 transaction nguyên tử (atomic)
        order = Order(
            customer_name=form.customer_name.data.strip(),
            phone=form.phone.data.strip(),
            email=(form.email.data or "").strip() or None,
            address=form.address.data.strip(),
            note=(form.note.data or "").strip() or None,
            payment_method=form.payment_method.data,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total_amount=grand_total,
            status=ORDER_STATUS_PENDING,
        )
        db.session.add(order)
        db.session.flush()  # Lấy order.id trước khi tạo OrderItem và OrderStatusHistory

        for entry in items:
            product = entry["product"]
            qty = entry["quantity"]
            # Lưu đơn giá tại thời điểm đặt hàng (unit_price)
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=qty,
            )
            db.session.add(order_item)
            # Trừ tồn kho sản phẩm
            product.stock -= qty

        # Ghi mốc lịch sử trạng thái đầu tiên (phục vụ màn hình ⑪ Admin ở phần sau)
        db.session.add(OrderStatusHistory(order_id=order.id, status=ORDER_STATUS_PENDING))
        db.session.commit()

        # Xoá giỏ hàng trong Session sau khi đặt thành công
        save_cart({})
        flash(f"Đặt hàng thành công! Mã đơn hàng của bạn là #{order.id}.", "success")
        return redirect(url_for("checkout.order_success", order_id=order.id))

    return render_template(
        "checkout.html",
        form=form,
        items=items,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        grand_total=grand_total,
        free_shipping_min=current_app.config.get("FREE_SHIPPING_MIN", 200_000),
    )


@checkout_bp.route("/don-hang/<int:order_id>")
def order_success(order_id: int):
    """Màn hình ⑤: Hiển thị xác nhận đơn hàng vừa đặt thành công."""
    order = db.session.get(Order, order_id)
    if order is None:
        abort(404, description=f"Không tìm thấy đơn hàng #{order_id}.")
    return render_template("order_success.html", order=order)


@checkout_bp.route("/don-hang/<int:order_id>/export")
def export_order_csv(order_id: int):
    """Xuất hoá đơn đặt hàng thành tệp CSV tải xuống bằng make_response (Chương 3)."""
    order = db.session.get(Order, order_id)
    if order is None:
        abort(404, description=f"Không tìm thấy đơn hàng #{order_id}.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ma_don", "khach_hang", "so_dien_thoai", "trang_thai", "ngay_dat"])
    writer.writerow([
        f"#{order.id}",
        order.customer_name,
        order.phone,
        order.status,
        order.created_at.strftime("%d/%m/%Y %H:%M"),
    ])
    writer.writerow([])
    writer.writerow(["ten_banh", "don_gia_luc_dat", "so_luong", "thanh_tien"])
    for item in order.items:
        writer.writerow([item.product_name, item.unit_price, item.quantity, item.line_total])
    writer.writerow([])
    writer.writerow(["tam_tinh", order.subtotal])
    writer.writerow(["phi_giao_hang", order.shipping_fee])
    writer.writerow(["tong_thanh_toan", order.total_amount])

    response = make_response("﻿" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=don_hang_{order.id}.csv"
    return response

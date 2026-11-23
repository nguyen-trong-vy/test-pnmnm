"""
tests/test_cart_and_checkout.py - Kiểm thử giỏ hàng Session, quy trình đặt hàng, tính phí ship và trừ kho (Chương 5 & 6).
"""

from extensions import db
from models import Order, Product


def test_cart_workflow(client):
    # 1. Xem giỏ hàng trống ban đầu
    res = client.get("/gio-hang")
    assert res.status_code == 200
    assert "Giỏ hàng trống" in res.get_data(as_text=True)

    # 2. Thêm sản phẩm vào giỏ (PRG pattern -> redirect 302)
    res_add = client.post("/gio-hang/them/1", data={"quantity": 2})
    assert res_add.status_code == 302

    # Kiểm tra Session đã lưu bánh 1 số lượng 2
    with client.session_transaction() as sess:
        assert sess["cart"]["1"] == 2

    # 3. Cập nhật tăng số lượng
    res_inc = client.post("/gio-hang/cap-nhat/1", data={"action": "inc"})
    assert res_inc.status_code == 302
    with client.session_transaction() as sess:
        assert sess["cart"]["1"] == 3

    # 4. Cập nhật giảm số lượng
    res_dec = client.post("/gio-hang/cap-nhat/1", data={"action": "dec"})
    assert res_dec.status_code == 302
    with client.session_transaction() as sess:
        assert sess["cart"]["1"] == 2

    # 5. Xoá sản phẩm khỏi giỏ
    res_del = client.post("/gio-hang/xoa/1")
    assert res_del.status_code == 302
    with client.session_transaction() as sess:
        assert "1" not in sess.get("cart", {})

    # 6. Thêm lại và xoá sạch giỏ hàng
    client.post("/gio-hang/them/1", data={"quantity": 1})
    res_clear = client.post("/gio-hang/xoa-tat-ca")
    assert res_clear.status_code == 302
    with client.session_transaction() as sess:
        assert len(sess.get("cart", {})) == 0


def test_checkout_workflow_and_stock_deduction(client, app):
    # Thêm bánh vào giỏ trước khi đặt hàng
    client.post("/gio-hang/them/1", data={"quantity": 2})

    # Mở trang đặt hàng
    res_get = client.get("/dat-hang")
    assert res_get.status_code == 200
    assert "Thông tin khách hàng" in res_get.get_data(as_text=True)

    # Kiểm tra validate: số điện thoại sai định dạng (không đủ 10 số hoặc không bắt đầu bằng 0)
    res_invalid = client.post("/dat-hang", data={
        "customer_name": "Nguyen Van A",
        "phone": "12345",
        "address": "123 Duong Le Loi, TP Hue",
        "payment_method": "cod",
    })
    assert res_invalid.status_code == 200
    assert "Số điện thoại gồm đúng 10 chữ số" in res_invalid.get_data(as_text=True)

    # Lấy số lượng tồn kho trước khi đặt
    with app.app_context():
        p_before = db.session.get(Product, 1)
        stock_before = p_before.stock

    # Gửi thông tin đặt hàng hợp lệ
    res_order = client.post("/dat-hang", data={
        "customer_name": "Nguyen Van A",
        "phone": "0912345678",
        "address": "123 Duong Le Loi, TP Hue",
        "payment_method": "cod",
        "note": "Giao vào buổi sáng",
    })
    assert res_order.status_code == 302
    assert "/don-hang/" in res_order.headers.get("Location")

    # Kiểm tra tồn kho đã bị trừ đúng 2 cái
    with app.app_context():
        p_after = db.session.get(Product, 1)
        assert p_after.stock == stock_before - 2

        # Kiểm tra Order đã được tạo trong CSDL
        order = db.session.scalar(db.select(Order).where(Order.customer_name == "Nguyen Van A"))
        assert order is not None
        assert order.status == "Chờ xác nhận"
        assert len(order.items) == 1
        assert len(order.history) >= 1
        order_id = order.id

    # Xem trang đặt hàng thành công
    res_success = client.get(f"/don-hang/{order_id}")
    assert res_success.status_code == 200
    assert "Đặt hàng thành công" in res_success.get_data(as_text=True)

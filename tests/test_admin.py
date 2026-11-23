"""
tests/test_admin.py - Kiểm thử phân hệ Quản trị viên (/admin), xác thực login, CRUD và bảo vệ route.
"""

from extensions import db
from models import Category, Order, OrderItem, OrderStatusHistory, Product, ORDER_STATUS_SHIPPING, ORDER_STATUS_PENDING


def test_admin_auth_protection(client):
    # Chưa đăng nhập truy cập /admin/ -> Chuyển hướng 302 về /admin/login
    res = client.get("/admin/")
    assert res.status_code == 302
    assert "/admin/login" in res.headers.get("Location")

    # Mở trang đăng nhập
    res_login_page = client.get("/admin/login")
    assert res_login_page.status_code == 200
    assert "Đăng nhập Quản trị" in res_login_page.get_data(as_text=True)

    # Đăng nhập sai mật khẩu
    res_fail = client.post("/admin/login", data={"username": "admin", "password": "wrongpassword"})
    assert res_fail.status_code == 200
    assert "Tên đăng nhập hoặc mật khẩu không chính xác" in res_fail.get_data(as_text=True)

    # Đăng nhập đúng tài khoản mẫu
    res_success = client.post("/admin/login", data={"username": "admin", "password": "admin123"})
    assert res_success.status_code == 302
    assert res_success.headers.get("Location") in ["/admin/", "/admin"]

    # Đăng xuất
    res_logout = client.get("/admin/logout")
    assert res_logout.status_code == 302
    assert "/admin/login" in res_logout.headers.get("Location")


def test_admin_dashboard(admin_client):
    res = admin_client.get("/admin/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Tổng quan kinh doanh" in html or "Bảng điều khiển kinh doanh" in html
    assert "Sản phẩm đang bán" in html or "Doanh thu" in html or "Đơn đặt hàng" in html


def test_admin_product_management(admin_client, app):
    # 1. Danh sách sản phẩm
    res_list = admin_client.get("/admin/san-pham")
    assert res_list.status_code == 200

    # 2. Mở form thêm sản phẩm
    res_form = admin_client.get("/admin/san-pham/them")
    assert res_form.status_code == 200

    # 3. Thêm sản phẩm mới qua POST
    res_add = admin_client.post("/admin/san-pham/them", data={
        "name": "Bánh Test Pytest Mới",
        "category_id": 1,
        "price": 35000,
        "stock": 15,
        "short_desc": "Mô tả ngắn test",
        "description": "Mô tả chi tiết bài kiểm thử pytest tự động",
        "existing_image": "images/products/donut-1.avif",
    })
    assert res_add.status_code == 302

    with app.app_context():
        new_prod = db.session.scalar(db.select(Product).where(Product.name == "Bánh Test Pytest Mới"))
        assert new_prod is not None
        assert new_prod.price == 35000
        new_prod_id = new_prod.id

    # 4. Sửa sản phẩm
    res_edit = admin_client.post(f"/admin/san-pham/sua/{new_prod_id}", data={
        "name": "Bánh Test Pytest Mới Đã Sửa",
        "category_id": 1,
        "price": 39000,
        "stock": 20,
        "short_desc": "Mô tả ngắn test",
        "description": "Mô tả chi tiết bài kiểm thử pytest tự động",
        "existing_image": "images/products/donut-1.avif",
    })
    assert res_edit.status_code == 302

    # 5. Xoá sản phẩm an toàn (bánh chưa bán nên xoá được)
    res_del = admin_client.post(f"/admin/san-pham/xoa/{new_prod_id}")
    assert res_del.status_code == 302


def test_admin_category_management(admin_client, app):
    # 1. Danh sách danh mục
    res_cat = admin_client.get("/admin/danh-muc")
    assert res_cat.status_code == 200

    # 2. Thêm danh mục mới
    res_add_cat = admin_client.post("/admin/danh-muc", data={
        "name": "Danh mục Pytest Test",
        "description": "Mô tả danh mục test",
        "existing_image": "images/categories/banh-donut.avif",
    })
    assert res_add_cat.status_code == 302

    with app.app_context():
        cat = db.session.scalar(db.select(Category).where(Category.name == "Danh mục Pytest Test"))
        assert cat is not None
        cat_id = cat.id

    # 3. Xoá danh mục rỗng (không có bánh -> xoá thành công)
    res_del_cat = admin_client.post(f"/admin/danh-muc/xoa/{cat_id}")
    assert res_del_cat.status_code == 302

    # 4. Xoá danh mục đang có bánh -> bị chặn xoá an toàn
    res_blocked = admin_client.post("/admin/danh-muc/xoa/1", follow_redirects=True)
    assert "Không thể xoá danh mục" in res_blocked.get_data(as_text=True)


def test_admin_order_management(admin_client, app):
    # Tạo đơn hàng mẫu trong CSDL để kiểm thử
    with app.app_context():
        order = Order(
            customer_name="Khách Hàng Test Admin",
            phone="0901234567",
            address="789 Đường Lê Lợi, TP Huế",
            payment_method="cod",
            subtotal=80000,
            shipping_fee=20000,
            total_amount=100000,
            status=ORDER_STATUS_PENDING,
        )
        db.session.add(order)
        db.session.flush()
        db.session.add(OrderItem(order_id=order.id, product_id=1, product_name="Bánh Donut", unit_price=40000, quantity=2))
        db.session.add(OrderStatusHistory(order_id=order.id, status=ORDER_STATUS_PENDING))
        db.session.commit()
        order_id = order.id

    # 1. Danh sách đơn hàng
    res_orders = admin_client.get("/admin/don-hang")
    assert res_orders.status_code == 200
    assert "Khách Hàng Test Admin" in res_orders.get_data(as_text=True)

    # 2. Chi tiết đơn hàng
    res_detail = admin_client.get(f"/admin/don-hang/{order_id}")
    assert res_detail.status_code == 200
    assert "Chi tiết đơn hàng" in res_detail.get_data(as_text=True)

    # 3. Cập nhật trạng thái đơn (POST /admin/don-hang/<id>)
    res_update = admin_client.post(f"/admin/don-hang/{order_id}", data={"status": ORDER_STATUS_SHIPPING})
    assert res_update.status_code == 302

    with app.app_context():
        updated_order = db.session.get(Order, order_id)
        assert updated_order.status == ORDER_STATUS_SHIPPING

    # 4. Xuất hoá đơn CSV đơn hàng
    res_csv = admin_client.get(f"/don-hang/{order_id}/export")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.content_type

"""
tests/test_store_routes.py - Kiểm thử các route bán hàng, tìm kiếm chống XSS, 301 redirect và xuất CSV (Chương 3 & 4).
"""


def test_home_page(client):
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Yuu Cake" in html
    assert "Bánh Donut" in html


def test_products_list_and_filter(client):
    # Xem tất cả
    res = client.get("/san-pham")
    assert res.status_code == 200
    assert "Tất cả sản phẩm" in res.get_data(as_text=True)

    # Lọc theo danh mục
    res_cat = client.get("/san-pham?category=banh-donut")
    assert res_cat.status_code == 200

    # Tìm kiếm có kết quả
    res_search = client.get("/san-pham?q=donut")
    assert res_search.status_code == 200


def test_product_detail_page(client):
    res = client.get("/san-pham/1")
    assert res.status_code == 200
    assert "Bánh" in res.get_data(as_text=True)

    # Bánh không tồn tại trả về 404
    res_404 = client.get("/san-pham/99999")
    assert res_404.status_code == 404


def test_short_link_301_redirect(client):
    # Route /sp/<id> chuyển hướng vĩnh viễn 301 sang /san-pham/<id>
    res = client.get("/sp/1")
    assert res.status_code == 301
    assert "/san-pham/1" in res.headers.get("Location")

    # Đi theo chuyển hướng đến trang đích
    res_followed = client.get("/sp/1", follow_redirects=True)
    assert res_followed.status_code == 200

    # ID không tồn tại khi đi theo redirect sẽ nhận 404 từ trang chi tiết
    res_404 = client.get("/sp/99999", follow_redirects=True)
    assert res_404.status_code == 404


def test_search_xss_protection(client):
    # Kiểm tra XSS: payload chèn script phải được Jinja2 escape an toàn
    payload = '<script>alert("XSS")</script>'
    res = client.get(f"/tim-kiem?q={payload}")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "<script>alert" not in html
    assert "&lt;script&gt;alert" in html or "alert" in html


def test_blog_and_static_pages(client):
    # Danh sách bài viết
    res_blog = client.get("/bai-viet")
    assert res_blog.status_code == 200

    # Chi tiết bài viết
    res_blog_detail = client.get("/bai-viet/giang-sinh-ngap-tran-nhan-uu-dai-giam-gia")
    assert res_blog_detail.status_code == 200
    assert "Giáng sinh" in res_blog_detail.get_data(as_text=True)

    # Trang FAQ và Giới thiệu
    assert client.get("/hoi-dap").status_code == 200
    assert client.get("/ve-yuucake").status_code == 200


def test_export_products_csv(client):
    res = client.get("/san-pham/1/export")
    assert res.status_code == 200
    assert "text/csv" in res.content_type
    assert "ma_sp" in res.get_data(as_text=True)

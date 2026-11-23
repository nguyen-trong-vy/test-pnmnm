"""
tests/test_api.py - Kiểm thử các endpoint RESTful JSON API (Chương 3).
"""


def test_api_list_products(client):
    res = client.get("/api/products")
    assert res.status_code == 200
    assert res.is_json
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) >= 20
    assert "id" in data[0]
    assert "name" in data[0]
    assert "price" in data[0]

    # Kiểm tra lọc theo category
    res_cat = client.get("/api/products?category=banh-donut")
    assert res_cat.status_code == 200
    assert len(res_cat.get_json()) > 0

    # Kiểm tra tham số min_price hợp lệ và không hợp lệ
    res_min = client.get("/api/products?min_price=50000")
    assert res_min.status_code == 200
    res_bad = client.get("/api/products?min_price=abc")
    assert res_bad.status_code == 400


def test_api_get_product_detail(client):
    res = client.get("/api/products/1")
    assert res.status_code == 200
    assert res.is_json
    data = res.get_json()
    assert data["id"] == 1
    assert "name" in data
    assert "price" in data

    # ID không tồn tại trả về 404 JSON
    res_404 = client.get("/api/products/99999")
    assert res_404.status_code == 404
    assert res_404.is_json
    error_data = res_404.get_json()
    assert "error" in error_data or "detail" in error_data


def test_api_list_categories(client):
    res = client.get("/api/categories")
    assert res.status_code == 200
    assert res.is_json
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert "product_count" in data[0]
    assert "avg_price" in data[0]


def test_api_cart_crud_restful(client):
    # 1. Thêm bánh vào giỏ qua API PUT lần đầu -> 201 Created kèm Location header
    res_create = client.put("/api/cart/items/1?qty=2")
    assert res_create.status_code == 201
    assert res_create.is_json
    assert res_create.headers.get("Location") == "/api/cart/items/1"
    assert res_create.get_json()["quantity"] == 2

    # 2. Xem số lượng qua GET
    res_get = client.get("/api/cart/items/1")
    assert res_get.status_code == 200
    assert res_get.get_json()["quantity"] == 2

    # 3. Cập nhật số lượng qua API PUT -> 200 OK
    res_update = client.put("/api/cart/items/1?qty=5")
    assert res_update.status_code == 200
    assert res_update.get_json()["quantity"] == 5

    # 4. Lỗi số lượng không hợp lệ -> 400 Bad Request
    res_bad = client.put("/api/cart/items/1?qty=-1")
    assert res_bad.status_code == 400
    assert res_bad.is_json

    # 5. Xoá sản phẩm khỏi giỏ qua API DELETE -> 204 No Content
    res_delete = client.delete("/api/cart/items/1")
    assert res_delete.status_code == 204

    # 6. Kiểm tra lại sau khi xoá -> 404
    res_get_deleted = client.get("/api/cart/items/1")
    assert res_get_deleted.status_code == 404

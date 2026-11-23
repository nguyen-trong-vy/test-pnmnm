"""
seed.py - Dữ liệu mẫu chuẩn cho Tiệm bánh Yuu Cake.

Sử dụng toàn bộ hình ảnh trong thư mục static/images/ (được trích từ bộ ảnh người dùng cung cấp).
Hàm seed_database() chạy an toàn nhiều lần (idempotent): chỉ nạp nếu bảng chưa có dữ liệu.
"""

from datetime import datetime
from sqlalchemy import func, select

from extensions import db
from models import BlogPost, Category, Product, User


def seed_admin_user() -> bool:
    """Nạp tài khoản Admin mặc định (admin / admin123) nếu chưa có trong CSDL."""
    admin_exists = db.session.scalar(select(User).where(User.username == "admin"))
    if not admin_exists:
        admin = User(
            username="admin",
            email="admin@yuucake.vn",
            full_name="Quản trị viên Yuu Cake",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        return True
    return False


def seed_database() -> dict:
    """
    Nạp dữ liệu mẫu cho 5 danh mục, 20 sản phẩm bánh và 3 bài viết Blog.
    Trả về dict thống kê số bản ghi hiện có trong CSDL.
    """
    existing_categories = db.session.scalar(select(func.count(Category.id))) or 0
    seed_admin_user()
    if existing_categories > 0:
        return {
            "seeded": False,
            "categories": existing_categories,
            "products": db.session.scalar(select(func.count(Product.id))) or 0,
            "blogs": db.session.scalar(select(func.count(BlogPost.id))) or 0,
        }

    # 1. Tạo 5 danh mục đúng thứ tự như giao diện video Yuu Cake
    categories_data = [
        {
            "name": "Bánh Donut",
            "slug": "banh-donut",
            "description": "Donut chiên vàng xốp mềm, phủ kem cốm, sô-cô-la và dâu tây ngọt dịu.",
            "image": "images/categories/banh-donut.avif",
        },
        {
            "name": "Phụ kiện bánh",
            "slug": "phu-kien-banh",
            "description": "Topper chúc mừng sinh nhật, nến nghệ thuật, bóng bay và thiệp trang trí.",
            "image": "images/categories/phu-kien-banh.avif",
        },
        {
            "name": "Bánh quy",
            "slug": "banh-quy",
            "description": "Bánh quy bơ giòn rụm, quy sô-cô-la chip và quy hạnh nhân nướng mới mỗi sáng.",
            "image": "images/categories/banh-quy.avif",
        },
        {
            "name": "Bánh sinh nhật",
            "slug": "banh-sinh-nhat",
            "description": "Bánh kem tươi, mousse sô-cô-la và bánh sinh nhật thiết kế tinh tế cho ngày trọn vẹn.",
            "image": "images/categories/banh-sinh-nhat.avif",
        },
        {
            "name": "Bánh Cupcake",
            "slug": "banh-cupcake",
            "description": "Cupcake cốt bông lan mềm ẩm kết hợp lớp kem bơ tạo hình bắt mắt.",
            "image": "images/categories/banh-cupcake.avif",
        },
    ]

    cat_map = {}
    for item in categories_data:
        cat = Category(**item)
        db.session.add(cat)
        cat_map[item["slug"]] = cat

    db.session.flush()  # Lấy ID danh mục trước khi gắn cho sản phẩm

    # 2. Tạo danh sách sản phẩm phong phú (cố ý đặt 1 sản phẩm stock=0 để minh hoạ trạng thái Hết hàng)
    products_data = [
        # --- Nhóm Bánh Donut ---
        {
            "name": "Bánh Donut kem cốm",
            "slug": "banh-donut-kem-com",
            "category_slug": "banh-donut",
            "price": 52_000,
            "stock": 25,
            "is_featured": True,
            "image": "images/products/donut-4.avif",
            "short_desc": "Bánh donut – Miếng bánh tròn xoe, ngọt ngào, mềm xốp, vị cứng mê.",
            "description": (
                "Chiếc bánh Donut kem cốm trứ danh của Yuu Cake được ủ bột tự nhiên suốt 6 giờ, "
                "chiên vàng nhẹ không ngấy dầu và phủ lớp kem dâu mịn cùng cốm màu giòn vui miệng."
            ),
        },
        {
            "name": "Bánh Donut matcha trà xanh",
            "slug": "banh-donut-matcha-tra-xanh",
            "category_slug": "banh-donut",
            "price": 48_000,
            "stock": 18,
            "is_featured": False,
            "image": "images/products/donut-2.avif",
            "short_desc": "Phủ sốt dâu tây Đà Lạt chua ngọt thanh nhẹ, thơm mùi sữa tươi.",
            "description": (
                "Cốt bánh mềm bông kết hợp lớp glaze dâu tây tự nhiên giúp cân bằng vị ngọt, "
                "thích hợp dùng kèm trà sữa hoặc cà phê sữa đá buổi sáng."
            ),
        },
        {
            "name": "Bánh Donut sô-cô-la hạt phỉ",
            "slug": "banh-donut-socola-hat-phi",
            "category_slug": "banh-donut",
            "price": 55_000,
            "stock": 15,
            "is_featured": True,
            "image": "images/products/donut-3.avif",
            "short_desc": "Sô-cô-la đen Bỉ 55% đậm đà kết hợp đường vân sữa béo ngậy.",
            "description": (
                "Sự lựa chọn hoàn hảo cho tín đồ sô-cô-la: lớp ganache phủ dày mượt mà trên cốt bánh "
                "xốp mịn, điểm xuyết vân sô-cô-la trắng tinh tế."
            ),
        },
        {
            "name": "Bánh Donut khoai môn kem sữa",
            "slug": "banh-donut-khoai-mon-kem-sua",
            "category_slug": "banh-donut",
            "price": 54_000,
            "stock": 4,  # Sắp hết hàng (<= 5)
            "is_featured": False,
            "image": "images/products/donut-1.avif",
            "short_desc": "Phủ sốt caramel mặn ngọt hài hoà cùng hạnh nhân lát nướng thơm.",
            "description": (
                "Sốt caramel tự nấu có chút muối biển dịu nhẹ giúp hương vị thêm sâu sắc, "
                "rắc thêm hạnh nhân lát rang giòn mỗi mẻ nướng."
            ),
        },

        # --- Nhóm Bánh quy ---
        {
            "name": "Bánh quy 01",
            "slug": "banh-quy-01",
            "category_slug": "banh-quy",
            "price": 34_000,
            "stock": 30,
            "is_featured": True,
            "image": "images/featured/banh-quy.avif",
            "short_desc": "Bánh quy sô cô la chip – Miếng bánh giòn tan, vị ngọt ngào khó cưỡng.",
            "description": (
                "Công thức bánh quy bơ truyền thống kết hợp sô-cô-la chip nướng chảy nhẹ bên trong, "
                "vỏ ngoài giòn thơm nức mùi bơ lạt New Zealand."
            ),
        },
        {
            "name": "Bánh quy bơ vani hộp thiếc",
            "slug": "banh-quy-bo-vani-hop-thiec",
            "category_slug": "banh-quy",
            "price": 75_000,
            "stock": 20,
            "is_featured": False,
            "image": "images/products/banh-quy-2.avif",
            "short_desc": "Bánh quy bơ tan ngay trong miệng, đóng gói sang trọng làm quà tặng.",
            "description": (
                "Mỗi chiếc bánh quy được bắt bông thủ công tỉ mỉ, nướng chậm ở nhiệt độ chuẩn "
                "cho màu vàng ươm và hương vani tự nhiên dịu nhẹ."
            ),
        },
        {
            "name": "Bánh quy trà xanh matcha",
            "slug": "banh-quy-tra-xanh-matcha",
            "category_slug": "banh-quy",
            "price": 45_000,
            "stock": 14,
            "is_featured": False,
            "image": "images/products/banh-quy-3.avif",
            "short_desc": "Vị trà xanh Nhật Bản thanh mát, ít ngọt, hợp thưởng trà chiều.",
            "description": (
                "Sử dụng bột matcha Uji nguyên chất giúp bánh có màu xanh tự nhiên đẹp mắt, "
                "hậu vị chát nhẹ cân bằng hoàn hảo với độ béo của bơ sữa."
            ),
        },
        {
            "name": "Bánh quy hạt điều bơ mặn",
            "slug": "banh-quy-hat-dieu-bo-man",
            "category_slug": "banh-quy",
            "price": 50_000,
            "stock": 0,  # Cố ý đặt = 0 để kiểm thử trạng thái "Hết hàng" (Bài Nhà sách Sông Hương)
            "is_featured": False,
            "image": "images/products/banh-quy-4.avif",
            "short_desc": "Bánh quy giòn rụm kèm hạt điều rang bùi béo, vị mặn ngọt hài hoà.",
            "description": (
                "Hạt điều Bình Phước tuyển chọn giã dập trộn đều trong khối bột bơ mặn, "
                "tạo nên hương vị gây nghiện ngay từ miếng đầu tiên."
            ),
        },

        # --- Nhóm Phụ kiện bánh ---
        {
            "name": "Topper Happy birthday 2",
            "slug": "topper-happy-birthday-2",
            "category_slug": "phu-kien-banh",
            "price": 22_000,
            "stock": 40,
            "is_featured": True,
            "image": "images/products/phu-kien-2.avif",
            "short_desc": "Một phụ kiện trang trí không thể thiếu trong những dịp đặc biệt.",
            "description": (
                "Que cắm topper Happy Birthday màu sắc pastel tươi tắn, chất liệu giấy mỹ thuật dày dặn, "
                "giúp chiếc bánh sinh nhật thêm nổi bật và rực rỡ trong khung hình."
            ),
        },
        {
            "name": "Bong bóng số ánh kim",
            "slug": "bong-bong-so-anh-kim",
            "category_slug": "phu-kien-banh",
            "price": 15_000,
            "stock": 50,
            "is_featured": True,
            "image": "images/products/phu-kien-3.avif",
            "short_desc": "Bong bóng YuuCake – Thổi bùng niềm vui cho mọi bữa tiệc sinh nhật!",
            "description": (
                "Set bong bóng trang trí tông màu xanh pastel và trắng tinh khôi, cao su dày an toàn, "
                "dễ phối hợp cùng bánh kem và phông nền tiệc gia đình."
            ),
        },
        {
            "name": "Topper Magical Day Cáo Nhỏ",
            "slug": "topper-magical-day-cao-nho",
            "category_slug": "phu-kien-banh",
            "price": 25_000,
            "stock": 35,
            "is_featured": False,
            "image": "images/products/phu-kien-1.avif",
            "short_desc": "Hộp 12 cây nến dài ánh kim sang trọng, ít khói, kèm chân cắm sạch sẽ.",
            "description": (
                "Nến sáp thực vật cao cấp cháy đều, không nhỏ giọt lên mặt bánh, "
                "giữ trọn vẻ đẹp tinh tế cho bánh kem sinh nhật."
            ),
        },
        {
            "name": "Thiệp chúc mừng thủ công Yuu",
            "slug": "thiep-chuc-mung-thu-cong-yuu",
            "category_slug": "phu-kien-banh",
            "price": 18_000,
            "stock": 22,
            "is_featured": False,
            "image": "images/products/phu-kien-4.avif",
            "short_desc": "Thiệp giấy mỹ thuật in màu dịu dàng, tặng kèm phong bì đồng bộ.",
            "description": (
                "Gửi gắm lời chúc yêu thương viết tay bên cạnh chiếc bánh ngọt ngào — "
                "món quà nhỏ nhưng chứa đựng trọn vẹn sự chân thành."
            ),
        },

        # --- Nhóm Bánh sinh nhật ---
        {
            "name": "Bánh sinh nhật Mousse Sô-cô-la Đen",
            "slug": "banh-sinh-nhat-mousse-socola-den",
            "category_slug": "banh-sinh-nhat",
            "price": 320_000,
            "stock": 12,
            "is_featured": True,
            "image": "images/products/sinh-nhat-3.avif",
            "short_desc": "Kiệt tác bánh mousse sô-cô-la Bỉ đậm vị, trang trí sô-cô-la uốn nghệ thuật.",
            "description": (
                "Ba tầng mousse sô-cô-la mịn mượt tan chảy trên nền bông lan ca cao ẩm nhẹ. "
                "Mặt bánh phủ vụn sô-cô-la đen và vòng xoắn sô-cô-la thủ công đầy đẳng cấp."
            ),
        },
        {
            "name": "Bánh kem Dâu Tây Tươi Chantilly",
            "slug": "banh-kem-dau-tay-tuoi-chantilly",
            "category_slug": "banh-sinh-nhat",
            "price": 290_000,
            "stock": 10,
            "is_featured": False,
            "image": "images/products/sinh-nhat-1.avif",
            "short_desc": "Kem tươi đánh bông nhẹ thanh, xen kẽ lớp dâu tây tươi cắt lát.",
            "description": (
                "Sử dụng 100% whipping cream động vật ít ngọt kết hợp dâu tây tuyển chọn mỗi ngày, "
                "phù hợp cho tiệc sinh nhật gia đình và trẻ nhỏ."
            ),
        },
        {
            "name": "Bánh sinh nhật Tiramisu Cà Phê Ý",
            "slug": "banh-sinh-nhat-tiramisu-ca-phe-y",
            "category_slug": "banh-sinh-nhat",
            "price": 340_000,
            "stock": 8,
            "is_featured": False,
            "image": "images/products/sinh-nhat-2.avif",
            "short_desc": "Phô mai Mascarpone béo mịn quyện hương espresso rang mộc thơm nồng.",
            "description": (
                "Đế bánh thấm cà phê espresso đậm vị, xen kẽ lớp kem phô mai Mascarpone mềm mượt "
                "và phủ bột ca cao nguyên chất bề mặt."
            ),
        },
        {
            "name": "Bánh kem Hoa Quả Nhiệt Đới",
            "slug": "banh-kem-hoa-qua-nhiet-doi",
            "category_slug": "banh-sinh-nhat",
            "price": 275_000,
            "stock": 5,  # Sắp hết hàng
            "is_featured": False,
            "image": "images/products/sinh-nhat-4.avif",
            "short_desc": "Bánh bông lan vani phủ trái cây tươi theo mùa chua ngọt mát lành.",
            "description": (
                "Trang trí đầy màu sắc từ xoài chín, kiwi, việt quất và dâu tây tươi, "
                "mang lại cảm giác thanh mát, không bị ngán."
            ),
        },

        # --- Nhóm Bánh Cupcake ---
        {
            "name": "Cupcake Kem Dâu Pastel",
            "slug": "cupcake-kem-dau-pastel",
            "category_slug": "banh-cupcake",
            "price": 38_000,
            "stock": 24,
            "is_featured": True,
            "image": "images/featured/banh-cupcake.avif",
            "short_desc": "Cupcake vani cốt mềm cùng chóp kem dâu hồng ngọt dịu, rắc cốm xinh xắn.",
            "description": (
                "Món bánh nhỏ xinh được yêu thích nhất tại các buổi tiệc trà và sinh nhật văn phòng, "
                "vừa tay cầm và hài hoà độ ngọt."
            ),
        },
        {
            "name": "Cupcake Sô-cô-la Kem Bơ",
            "slug": "cupcake-socola-kem-bo",
            "category_slug": "banh-cupcake",
            "price": 42_000,
            "stock": 16,
            "is_featured": True,
            "image": "images/products/cupcake-1.png",
            "short_desc": "Cốt ca cao ẩm mịn, chóp kem bơ sô-cô-la phủ cốm sắc màu bắt mắt.",
            "description": (
                "Nhân sốt sô-cô-la chảy ẩn bên trong cốt bánh mềm ẩm, mang đến bất ngờ thú vị "
                "ở từng miếng thưởng thức."
            ),
        },
        {
            "name": "Cupcake Red Velvet Kem Phô Mai",
            "slug": "cupcake-red-velvet-kem-pho-mai",
            "category_slug": "banh-cupcake",
            "price": 45_000,
            "stock": 14,
            "is_featured": False,
            "image": "images/products/cupcake-2.png",
            "short_desc": "Sắc đỏ nhung quyến rũ kết hợp kem cream cheese béo nhẹ chua thanh.",
            "description": (
                "Lớp kem phô mai đánh mịn không quá ngọt nâng tầm hương vị ca cao dịu nhẹ "
                "của cốt bánh Red Velvet chuẩn vị."
            ),
        },
        {
            "name": "Cupcake Vani Mật Ong Hoa Cúc",
            "slug": "cupcake-vani-mat-ong-hoa-cuc",
            "category_slug": "banh-cupcake",
            "price": 40_000,
            "stock": 19,
            "is_featured": False,
            "image": "images/products/cupcake-3.png",
            "short_desc": "Thơm dịu mật ong rừng và vani nguyên chất, nhẹ nhàng cho tiệc trà.",
            "description": (
                "Cốt bánh nướng vàng thơm mềm mại, dùng mật ong tự nhiên giảm đường tinh luyện "
                "cho vị ngọt thanh tao."
            ),
        },
    ]

    for p in products_data:
        cat = cat_map[p.pop("category_slug")]
        db.session.add(Product(category=cat, **p))

    # 3. Tạo 3 bài viết Blog khớp hoàn toàn với video giao diện Yuu Cake
    blogs_data = [
        {
            "title": "Giáng sinh ngập tràn - Nhận ưu đãi giảm giá",
            "slug": "giang-sinh-ngap-tran-nhan-uu-dai-giam-gia",
            "category_label": "Tin tức",
            "excerpt": (
                "Không khí Giáng sinh đang đến gần, không khí se lạnh hoà cùng niềm hân hoan "
                "của mọi nhà. Tiệm bánh YuuCake gửi tặng ưu đãi đặc biệt cho tất cả đơn bánh đặt sớm..."
            ),
            "content": """Mùa lễ hội cuối năm luôn là dịp tuyệt vời nhất để quây quần bên người thân và bạn bè bên những chiếc bánh ngọt ấm áp.

Nhân dịp Giáng sinh và chào năm mới, YuuCake áp dụng chương trình ưu đãi đặc biệt:
- Miễn phí giao hàng cho mọi đơn từ 200.000 đ trong nội thành.
- Tặng kèm bộ phụ kiện nến ánh kim và thiệp chúc mừng thủ công cho mọi bánh sinh nhật.
- Giảm trực tiếp cho nhóm đặt hộp Donut và Cupcake từ 10 chiếc trở lên.

Hãy ghé ngay mục Sản phẩm để chọn chiếc bánh ưng ý nhất cho bữa tiệc mùa đông của bạn!""",
            "image": "images/blog/blog-1.avif",
            "published_at": datetime(2024, 12, 23, 9, 0),
        },
        {
            "title": 'Fondant - Vị "phù thủy" của các loại bánh ngọt',
            "slug": "fondant-vi-phu-thuy-cua-cac-loai-banh-ngot",
            "category_label": "Hướng dẫn làm bánh",
            "excerpt": (
                "Có thể nói, fondant là một nghệ thuật trang trí bánh ngọt lên một nấc thang mới, "
                "biến những chiếc bánh thành một tác phẩm ẩm thực muôn màu..."
            ),
            "content": """Fondant (đường dẻo) được ví như chất liệu điêu khắc của thế giới bánh ngọt hiện đại. Nhờ độ mịn mượt và khả năng tạo hình linh hoạt, thợ làm bánh có thể biến hóa bề mặt bánh thành những bông hoa tinh xảo, nhân vật hoạt hình hay họa tiết sang trọng.

Mẹo nhỏ để cán fondant mịn đẹp không bị nứt:
1. Nhào đường dẻo ấm tay với một lớp mỏng shortening trước khi cán.
2. Phủ một lớp kem bơ mỏng (crumb coat) làm lạnh trước khi bọc fondant để bánh sắc nét.
3. Bảo quản bánh ở nơi khô ráo, thoáng mát, tránh ẩm cao khiến bề mặt đường bị chảy.""",
            "image": "images/blog/blog-2.avif",
            "published_at": datetime(2024, 12, 27, 14, 30),
        },
        {
            "title": "Cách làm Bánh chuối yến mạch sữa chua healthy",
            "slug": "cach-lam-banh-chuoi-yen-mach-sua-chua-healthy",
            "category_label": "Hướng dẫn làm bánh",
            "excerpt": (
                'Một chiếc bánh "thuần healthy", gluten-free, dùng 100% bột yến mạch, '
                "nhưng vẫn cực mềm, ẩm và thơm nức mùi chuối tươi..."
            ),
            "content": """Nếu bạn đang tìm kiếm một món bánh ăn sáng lành mạnh, không đường tinh luyện nhưng vẫn giữ độ mềm ẩm hấp dẫn, bánh chuối yến mạch sữa chua chính là công thức lý tưởng.

Nguyên liệu cơ bản:
- 2 quả chuối chín mùi nghiền nhuyễn (tạo độ ngọt tự nhiên).
- 150g yến mạch cán dẹt xay mịn thành bột.
- 1 hộp sữa chua không đường, 2 quả trứng gà, 1 thìa cà phê bột nở và chút bột quế.

Cách làm: Trộn đều nguyên liệu ướt rồi rây bột yến mạch vào đảo nhẹ tay. Đổ khuôn lót giấy nến, xếp lát chuối lên mặt và nướng ở 170°C trong 30–35 phút.""",
            "image": "images/blog/blog-3.avif",
            "published_at": datetime(2024, 12, 24, 10, 15),
        },
    ]

    for b in blogs_data:
        db.session.add(BlogPost(**b))

    db.session.commit()
    return {
        "seeded": True,
        "categories": len(categories_data),
        "products": len(products_data),
        "blogs": len(blogs_data),
    }

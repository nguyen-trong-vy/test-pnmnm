/*
 * main.js - Tương tác giao diện nhẹ (Vanilla JS, không phụ thuộc thư viện nặng):
 * 1. Tự động chuyển slide Hero Banner trên trang chủ & bấm chấm chọn slide.
 * 2. Bật/tắt ô tìm kiếm nhanh trên thanh menu.
 * 3. Nút tăng (+) / giảm (-) số lượng ở trang chi tiết bánh (chỉ hỗ trợ UX, server vẫn kiểm tra lại).
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Hero Slider tự động chuyển sau mỗi 5 giây (hoặc sau khi video kết thúc)
  const slides = document.querySelectorAll(".yuu-hero-slide");
  const dots = document.querySelectorAll(".yuu-hero-dot");
  const prevBtn = document.querySelector(".yuu-hero-prev");
  const nextBtn = document.querySelector(".yuu-hero-next");

  if (slides.length > 1) {
    let current = 0;
    let timer = null;

    const startTimer = () => {
      if (timer) clearTimeout(timer);
      const activeSlide = slides[current];
      const video = activeSlide ? activeSlide.querySelector("video") : null;

      if (video) {
        // Nếu là slide video: phát lại từ đầu và chờ video kết thúc để chuyển slide
        video.currentTime = 0;
        const playPromise = video.play();
        if (playPromise !== undefined) {
          playPromise.catch(() => {});
        }

        const handleEnded = () => {
          video.removeEventListener("ended", handleEnded);
          goToSlide(current + 1);
        };
        video.addEventListener("ended", handleEnded, { once: true });

        // Thời gian chờ dự phòng trong trường hợp trình duyệt không bắn sự kiện ended
        timer = setTimeout(() => {
          video.removeEventListener("ended", handleEnded);
          goToSlide(current + 1);
        }, 8500);
      } else {
        // Slide ảnh tĩnh: chuyển sau 5 giây
        timer = setTimeout(() => goToSlide(current + 1), 5000);
      }
    };

    const goToSlide = (idx) => {
      if (timer) clearTimeout(timer);

      // Tạm dừng video của slide cũ nếu có
      const prevVideo = slides[current] ? slides[current].querySelector("video") : null;
      if (prevVideo) {
        prevVideo.pause();
      }

      slides[current].classList.remove("active");
      if (dots[current]) dots[current].classList.remove("active");

      current = (idx + slides.length) % slides.length;

      slides[current].classList.add("active");
      if (dots[current]) dots[current].classList.add("active");

      startTimer();
    };

    // Bắt đầu hẹn giờ cho slide đầu tiên
    startTimer();

    dots.forEach((dot, i) => {
      dot.addEventListener("click", () => {
        goToSlide(i);
      });
    });

    if (prevBtn) {
      prevBtn.addEventListener("click", () => goToSlide(current - 1));
    }
    if (nextBtn) {
      nextBtn.addEventListener("click", () => goToSlide(current + 1));
    }
  }

  // 2. Bật/tắt thanh tìm kiếm nhanh trên Navbar
  const searchToggle = document.getElementById("yuuSearchToggle");
  const searchBar = document.getElementById("yuuQuickSearch");
  const searchInput = document.getElementById("yuuQuickSearchInput");
  if (searchToggle && searchBar) {
    searchToggle.addEventListener("click", () => {
      searchBar.classList.toggle("d-none");
      if (!searchBar.classList.contains("d-none") && searchInput) {
        searchInput.focus();
      }
    });
  }

  // 3. Nút - / + điều chỉnh số lượng ở màn hình chi tiết bánh
  const qtyInput = document.getElementById("detailQtyInput");
  const decBtn = document.getElementById("detailQtyDec");
  const incBtn = document.getElementById("detailQtyInc");
  if (qtyInput && decBtn && incBtn) {
    const minVal = parseInt(qtyInput.getAttribute("min") || "1", 10);
    const maxVal = parseInt(qtyInput.getAttribute("max") || "99", 10);
    decBtn.addEventListener("click", () => {
      const val = parseInt(qtyInput.value || "1", 10);
      if (val > minVal) qtyInput.value = val - 1;
    });
    incBtn.addEventListener("click", () => {
      const val = parseInt(qtyInput.value || "1", 10);
      if (val < maxVal) qtyInput.value = val + 1;
    });
  }
});

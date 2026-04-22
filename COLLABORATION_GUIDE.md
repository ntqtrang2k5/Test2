# Hướng dẫn Hợp tác Nhóm - Dự án Thuê Xe (Car Rent)

Tài liệu này hướng dẫn cách nhóm của chúng ta (A, B và C) cùng làm việc trên một kho lưu trữ Git, quản lý các tính năng khác nhau và sử dụng các công cụ tự động hóa khác nhau (Playwright & Selenium).

---

## 1. Chiến lược Phân nhánh (Git Flow)

Để tránh làm hỏng code của nhau, **TUYỆT ĐỐI KHÔNG** push trực tiếp lên nhánh `main`. Hãy sử dụng các Nhánh Tính năng (Feature Branches).

- **Người A (Tạo Hợp đồng):** nhánh `feature/create-contract`
- **Người B (Sửa Hợp đồng):** nhánh `feature/edit-contract`
- **Người C (Quản lý Xe):** nhánh `feature/car-management`

### Quy trình làm việc cho mỗi tính năng:
1.  **Cập nhật code mới nhất:**
    ```bash
    git checkout main
    git pull origin main
    ```
2.  **Tạo nhánh của riêng bạn:**
    ```bash
    git checkout -b feature/ten-tinh-nang-cua-ban
    ```
3.  **Làm việc và Commit:**
    ```bash
    git add .
    git commit -m "Mô tả ngắn gọn những gì bạn đã làm"
    ```
4.  **Đẩy code lên Cloud:**
    ```bash
    git push origin feature/ten-tinh-nang-cua-ban
    ```
5.  **Gộp code qua Pull Request (PR):** Mở GitHub/GitLab và tạo một PR để gộp vào `main`.

---

## 2. Tài nguyên & Thành phần UI dùng chung

Antigravity đã triển khai một số tính năng toàn cục. Hãy sử dụng chúng thay vì xây dựng lại từ đầu!

- **Popup Modal Tùy chỉnh**: Thay vì dùng `confirm()`, hãy dùng `window.showConfirm(message, callback)`.
    - *Định nghĩa tại:* `templates/base.html` và `static/js/common.js`.
- **Lưu trữ Form (Persistence)**: Sử dụng `localStorage` để lưu bản nháp. Nếu bạn xây dựng một form mới, hãy xem `templates/rentals/create.html` để biết cách triển khai `saveFormState`.
- **Hỗ trợ tiền tệ**: Sử dụng `formatCurrency(val)` và `parseCurrency(str)` đã được định nghĩa trong `common.js`.

---

## 3. Cấu trúc Thư mục Kiểm thử tự động (Playwright)

Cả nhóm sẽ sử dụng **Playwright** và tổ chức thư mục theo chuẩn **Page Object Model (POM)** để dễ quản lý:

```text
tests/
├── conftest.py                # Fixtures dùng chung (Login, DB, Base URL)
├── pages/                    # Nơi chứa các Selector và Action (Dùng chung)
│   ├── contract_page.py
│   └── car_page.py
└── playwright/
    ├── contracts/             # Module Hợp đồng (Người A & B)
    │   ├── test_list.py       # Xem & Tìm kiếm HĐ
    │   ├── test_create.py     # Thêm mới (Người A)
    │   ├── test_edit.py       # Sửa HĐ đặt trước (Người B)
    │   ├── test_extension.py  # Gia hạn HĐ đang thuê (Người B)
    │   └── test_delete.py     # Quy tắc xóa HĐ
    └── cars/                  # Module Xe (Người C & Tương lai)
        ├── test_list.py       # Xem & Tìm kiếm (Người C)
        ├── test_add.py        # Thêm xe mới (Người C)
        ├── test_edit.py       # Sửa thông tin xe
        └── test_delete.py     # Xóa xe
```

### Cấu hình Fixture (trong conftest.py):
```python
@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:8000"

@pytest.fixture(scope="function")
def logged_in_page(browser_instance, base_url):
    context = browser_instance.new_context()
    page = context.new_page()
    
    # Login logic
    page.goto(f"{base_url}/login/")
    page.fill("input[name='username']", "n2tester")
    page.fill("input[name='password']", "@n2tester")
    page.click("button[type='submit']")
    
    # Wait for login to complete
    page.wait_for_url(f"{base_url}/")
    
    yield page
    context.close()
```

### Quy tắc khi viết Test:
1.  **Sử dụng Page Object**: Không viết trực tiếp Selector (`#btn-save`) vào file test. Hãy khai báo trong `tests/pages/` và gọi hàm từ đó.
2.  **Sử dụng Fixture**: Luôn dùng `@pytest.mark.django_db` và fixture `logged_in_page` để bắt đầu từ trạng thái đã đăng nhập.
3.  **Hạn chế xung đột**: Người nào làm file người đó. Nếu cần sửa file chung (`conftest.py` hoặc `pages/`), hãy báo cho cả nhóm.

### Quản lý Thư viện (Dependencies)
Cập nhật file `requirements.txt` để bao gồm cả hai:
```text
pytest-playwright
selenium
webdriver-manager
```

---

## 4. Cách xử lý Xung đột (Conflicts)

Có khả năng các bạn sẽ cùng chạm vào các file chung: `carrent/urls.py`, `templates/base.html`, và `static/js/common.js`.

1.  **Trao đổi**: Nếu bạn chuẩn bị thay đổi một file cốt lõi, hãy báo cho cả nhóm.
2.  **Gộp code thường xuyên**: Gộp nhánh `main` vào nhánh tính năng của bạn hàng ngày:
    ```bash
    git checkout feature/nhanh-cua-ban
    git merge main
    ```
3.  **Xử lý xung đột thủ công**: Nếu Git báo có xung đột, hãy tìm ký hiệu `<<<< HEAD`. Giữ lại code của CẢ HAI tính năng nếu chúng đang thêm các URL hoặc Style khác nhau.

---

## 5. Triển khai & Cơ sở dữ liệu

- **Cơ sở dữ liệu**: Chúng ta đang dùng `db.sqlite3`. **Không commit file database cá nhân nếu nó chứa dữ liệu test.** Đảm bảo file `*.sqlite3` đã có trong `.gitignore`.
- **Migration**: Nếu bạn thay đổi Django Models, hãy nhớ chạy `python manage.py makemigrations` và commit các file migration đó.

---
*Chúc các bạn làm dự án thành công!*

import pytest
from tests.pages.car_page import CarPage

@pytest.fixture
def car_page(logged_in_page):
    page_obj = CarPage(logged_in_page)
    page_obj.navigate_to_list("http://127.0.0.1:8000")
    page_obj.reset_filters()
    return page_obj


# TC-XE-R01: Hiển thị danh sách xe
def test_TC_XE_R01(car_page):
    """TC-XE-R01: Hiển thị danh sách xe khi truy cập"""
    assert car_page.page.locator(".car-card").count() > 0


# TC-XE-R02: Không có dữ liệu
def test_TC_XE_R02(car_page):
    """TC-XE-R02: Hiển thị danh sách rỗng khi không có kết quả"""
    car_page.page.fill(car_page.SEARCH_INPUT, "KHONG_TON_TAI_9999")
    car_page.page.click(car_page.FILTER_SUBMIT)
    car_page.page.wait_for_timeout(500)
    assert car_page.page.locator(car_page.EMPTY_MSG).is_visible()


# TC-XE-R03: Tìm theo tên xe
def test_TC_XE_R03(car_page):
    """TC-XE-R03: Tìm kiếm theo tên xe (Hãng/Dòng)"""
    # Lấy tên xe đầu tiên để test tìm kiếm chính xác
    first_card = car_page.page.locator(".car-card").first
    full_name = first_card.get_attribute("data-ten")
    # Lấy phần đầu (thường là Hãng)
    ten_xe = full_name.split()[0]

    car_page.page.fill(car_page.SEARCH_INPUT, ten_xe)
    car_page.page.click(car_page.FILTER_SUBMIT)
    car_page.page.wait_for_timeout(500)
    cards = car_page.page.locator(".car-card:visible")
    assert cards.count() > 0
    for i in range(cards.count()):
        ten = cards.nth(i).get_attribute("data-ten")
        assert ten_xe.lower() in ten.lower()


# TC-XE-R04: Tìm theo biển số
def test_TC_XE_R04(car_page):
    """TC-XE-R04: Tìm kiếm theo biển số xe"""
    first_card = car_page.page.locator(".car-card").first
    bien_so = first_card.get_attribute("data-bien-so")

    car_page.page.fill(car_page.SEARCH_INPUT, bien_so)
    car_page.page.click(car_page.FILTER_SUBMIT)
    car_page.page.wait_for_timeout(500)
    assert car_page.page.locator(f"div.car-card[data-bien-so='{bien_so}']:visible").count() >= 1


# TC-XE-R05: Không tìm thấy
def test_TC_XE_R05(car_page):
    """TC-XE-R05: Tìm kiếm với từ khóa không tồn tại"""
    car_page.page.fill(car_page.SEARCH_INPUT, "ABCXYZ123_NOT_FOUND")
    car_page.page.click(car_page.FILTER_SUBMIT)
    car_page.page.wait_for_timeout(500)
    assert car_page.page.locator(car_page.EMPTY_MSG).is_visible()


# TC-XE-R06: Tìm kiếm không phân biệt hoa thường
def test_TC_XE_R06(car_page):
    """TC-XE-R06: Tìm kiếm không phân biệt hoa thường"""
    first_card = car_page.page.locator(".car-card").first
    ten_original = first_card.get_attribute("data-ten")
    ten_lower = ten_original.lower()

    car_page.page.fill(car_page.SEARCH_INPUT, ten_lower)
    car_page.page.click(car_page.FILTER_SUBMIT)
    car_page.page.wait_for_timeout(500)
    assert car_page.page.locator(".car-card:visible").count() > 0


# TC-XE-R07: Tìm kiếm khoảng trắng
def test_TC_XE_R07(car_page):
    """TC-XE-R07: Tìm kiếm với khoảng trắng (không lọc)"""
    count_before = car_page.page.locator(".car-card").count()
    car_page.page.fill(car_page.SEARCH_INPUT, " ")
    car_page.page.click(car_page.FILTER_SUBMIT)
    car_page.page.wait_for_timeout(500)
    count_after = car_page.page.locator(".car-card:visible").count()
    assert count_before == count_after


# TC-XE-R08: Lọc theo trạng thái
def test_TC_XE_R08(car_page):
    """TC-XE-R08: Lọc theo trạng thái (Sẵn sàng)"""
    trang_thai = "Sẵn sàng"
    car_page.apply_filters(status=trang_thai)
    cards = car_page.page.locator(".car-card:visible")
    assert cards.count() > 0
    for i in range(cards.count()):
        assert cards.nth(i).get_attribute("data-trang-thai") == trang_thai


# TC-XE-R09: Lọc theo số chỗ
def test_TC_XE_R09(car_page):
    """TC-XE-R09: Lọc theo số chỗ (7)"""
    car_page.apply_filters(seats="7")
    cards = car_page.page.locator(".car-card:visible")
    if cards.count() > 0:
        for i in range(cards.count()):
            assert cards.nth(i).get_attribute("data-cho-ngoi") == "7"
    else:
        pytest.skip("Không có xe 7 chỗ trong danh sách")


# TC-XE-R10: Lọc theo loại xe
def test_TC_XE_R10(car_page):
    """TC-XE-R10: Lọc theo loại xe (Vios)"""
    # Lấy loại xe đầu tiên có sẵn trong dropdown
    model_options = car_page.page.locator("select#filter-model option")
    if model_options.count() > 1:
        dong_xe = model_options.nth(1).get_attribute("value")
        car_page.apply_filters(model=dong_xe)
        cards = car_page.page.locator(".car-card:visible")
        for i in range(cards.count()):
            assert cards.nth(i).get_attribute("data-dong-xe") == dong_xe
    else:
        pytest.skip("Không có tùy chọn loại xe trong dropdown")


# TC-XE-R11: Lọc nhiều điều kiện
def test_TC_XE_R11(car_page):
    """TC-XE-R11: Kết hợp nhiều điều kiện lọc"""
    # Lấy thông tin từ xe đầu tiên để đảm bảo kết quả không rỗng
    first_card = car_page.page.locator(".car-card").first
    hang = first_card.get_attribute("data-hang-xe")
    cho = first_card.get_attribute("data-cho-ngoi")

    car_page.apply_filters(brand=hang, seats=cho)
    cards = car_page.page.locator(".car-card:visible")
    assert cards.count() > 0
    for i in range(cards.count()):
        assert cards.nth(i).get_attribute("data-hang-xe") == hang
        assert cards.nth(i).get_attribute("data-cho-ngoi") == cho


# TC-XE-R12: Lọc không có kết quả
def test_TC_XE_R12(car_page):
    """TC-XE-R12: Lọc với các điều kiện không có kết quả"""
    # Lọc Mercedes-Benz + 7 chỗ (Giả định không có xe này trong DB)
    car_page.apply_filters(brand="Mercedes-Benz", seats="7")
    car_page.page.wait_for_timeout(500)

    # Nếu vẫn có kết quả thì dùng từ khóa tìm kiếm đi kèm
    if car_page.page.locator(".car-card:visible").count() > 0:
        car_page.page.fill(car_page.SEARCH_INPUT, "KHONG_THE_CO_XE_NAY_TRONG_KHO_123")
        car_page.page.click(car_page.FILTER_SUBMIT)
        car_page.page.wait_for_timeout(500)

    assert car_page.page.locator(car_page.EMPTY_MSG).is_visible()


# --- GUI TEST CASES ---

# TC-XE-G01: Hiển thị giao diện tìm kiếm
def test_TC_XE_G01(car_page):
    """TC-XE-G01: Kiểm tra hiển thị đầy đủ textbox, button tìm kiếm, filter"""
    assert car_page.page.locator(car_page.SEARCH_INPUT).is_visible()
    assert car_page.page.locator(car_page.FILTER_BRAND).is_visible()
    assert car_page.page.locator(car_page.FILTER_MODEL).is_visible()
    assert car_page.page.locator(car_page.FILTER_SEATS).is_visible()
    assert car_page.page.locator(car_page.FILTER_STATUS).is_visible()
    assert car_page.page.locator(car_page.FILTER_SUBMIT).is_visible()
    assert car_page.page.locator(car_page.FILTER_RESET).is_visible()


# TC-XE-G02: Kiểm tra placeholder
def test_TC_XE_G02(car_page):
    """TC-XE-G02: Kiểm tra nội dung placeholder của ô tìm kiếm"""
    placeholder = car_page.page.locator(car_page.SEARCH_INPUT).get_attribute("placeholder")
    assert "Tìm kiếm theo Tên xe, Biển số..." in placeholder


# TC-XE-G03: Kiểm tra button tìm kiếm
def test_TC_XE_G03(car_page):
    """TC-XE-G03: Kiểm tra button tìm kiếm hiển thị rõ và có thể click"""
    btn = car_page.page.locator(car_page.FILTER_SUBMIT)
    assert btn.is_visible()
    assert btn.is_enabled()


# TC-XE-G04: Click button tìm kiếm
def test_TC_XE_G04(car_page):
    """TC-XE-G04: Thực hiện tìm kiếm khi click button"""
    car_page.page.fill(car_page.SEARCH_INPUT, "Toyota")
    car_page.page.click(car_page.FILTER_SUBMIT)
    car_page.page.wait_for_timeout(500)
    # Xác minh có kết quả và kết quả khớp
    cards = car_page.page.locator(".car-card:visible")
    if cards.count() > 0:
        for i in range(cards.count()):
            assert "toyota" in cards.nth(i).get_attribute("data-ten").lower()
    else:
        assert car_page.page.locator(car_page.EMPTY_MSG).is_visible()


# TC-XE-G05: Kiểm tra UI filter
def test_TC_XE_G05(car_page):
    """TC-XE-G05: Kiểm tra các tùy chọn trong dropdown filter"""
    # Kiểm tra dropdown Số chỗ
    options = car_page.page.locator(f"{car_page.FILTER_SEATS} option")
    values = [options.nth(i).get_attribute("value") for i in range(options.count())]
    assert "4" in values
    assert "7" in values

    # Kiểm tra dropdown Trạng thái
    status_options = car_page.page.locator(f"{car_page.FILTER_STATUS} option")
    status_texts = [status_options.nth(i).inner_text() for i in range(status_options.count())]
    assert "Sẵn sàng" in status_texts
    assert "Đang thuê" in status_texts


# TC-XE-G06: Kiểm tra responsive
def test_TC_XE_G06(car_page):
    """TC-XE-G06: Kiểm tra giao diện khi thay đổi kích thước màn hình (Responsive)"""
    # Resize về kích thước mobile
    car_page.page.set_viewport_size({"width": 375, "height": 667})
    car_page.page.wait_for_timeout(500)
    assert car_page.page.locator(".car-grid").is_visible()
    # Kiểm tra card xe có hiển thị không (thường stack dọc)
    assert car_page.page.locator(".car-card").first.is_visible()

    # Trả lại kích thước cũ
    car_page.page.set_viewport_size({"width": 1280, "height": 720})


# TC-XE-G07: Kiểm tra thông báo không có kết quả
def test_TC_XE_G07(car_page):
    """TC-XE-G07: Kiểm tra hiển thị message khi không tìm thấy kết quả"""
    car_page.page.fill(car_page.SEARCH_INPUT, "KHONG_TON_TAI_TRONG_HE_THONG_123")
    car_page.page.click(car_page.FILTER_SUBMIT)
    car_page.page.wait_for_timeout(500)

    empty_msg = car_page.page.locator(car_page.EMPTY_MSG)
    assert empty_msg.is_visible()
    assert "Không tìm thấy xe nào phù hợp" in empty_msg.inner_text()


# TC-XE-G08: Kiểm tra clear input
def test_TC_XE_G08(car_page):
    """TC-XE-G08: Kiểm tra nút Đặt lại xóa sạch ô tìm kiếm"""
    car_page.page.fill(car_page.SEARCH_INPUT, "Dữ liệu rác")
    car_page.page.click(car_page.FILTER_RESET)
    car_page.page.wait_for_timeout(500)

    input_val = car_page.page.locator(car_page.SEARCH_INPUT).input_value()
    assert input_val == ""
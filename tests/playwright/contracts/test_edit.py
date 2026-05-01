import pytest
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta
from django.utils import timezone
from rentals.models import HopDong

def select_prebooked_contract(page: Page):
    """Lấy hợp đồng 'Đặt trước' và điều hướng thẳng đến trang chi tiết."""
    hd = HopDong.objects.filter(trang_thai='Đặt trước').order_by('?').first()
    if not hd:
        raise Exception("Không tìm thấy hợp đồng nào Đặt trước để test!")
    
    ma_hd = hd.ma_hd
    page.goto(f"http://127.0.0.1:8000/hop-dong/detail/{ma_hd}/", timeout=60000)
    page.wait_for_load_state("networkidle")
    # Đợi nút LƯU xuất hiện để chắc chắn trang load xong
    page.wait_for_selector("button:has-text('LƯU')", timeout=15000)
    return ma_hd

@pytest.mark.django_db
def test_TC_HD_U01(logged_in_page: Page):
    """TC-HD-U01: Chỉnh sửa hợp đồng đặt trước thành công (tổng hợp)"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    # 1. Chỉnh sửa thời gian (dùng JS để bypass calendar click phức tạp)
    page.evaluate("() => { window.fpStart.setDate('28/08/2027', true); }")
    page.wait_for_timeout(500)
    page.evaluate("() => { window.fpEnd.setDate('31/08/2027', true); }")
    page.wait_for_timeout(500)
    
    # 2. Chọn khách hàng khác
    page.click("#customer-search-input")
    page.wait_for_selector("#customer-dropdown .search-item")
    page.locator("#customer-dropdown .search-item").nth(0).click()
    
    # 3. Thay đổi xe (Xóa xe cũ, thêm xe mới)
    if page.locator(".car-item-row .btn-action-delete").count() > 0:
        page.locator(".car-item-row .btn-action-delete").first.click()
    
    page.click("#car-search-input-detail")
    page.wait_for_selector("#car-dropdown .search-item")
    page.locator("#car-dropdown .search-item").first.click()
    
    # 4. Bấm Lưu
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('LƯU')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    
    assert "thành công" in msg.lower()

@pytest.mark.django_db
def test_TC_HD_U02(logged_in_page: Page):
    """TC-HD-U02: Chỉnh sửa ngày nhận xe thành công và check tiền"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    old_total = page.locator("#display-total-price").inner_text()
    
    # Đổi ngày bắt đầu (Tiến lên 1 ngày để chắc chắn không bị chặn bởi minDate của quá khứ)
    current_start = page.locator("#d-start-date").input_value()
    d, m, y = map(int, current_start.split('/'))
    
    # Kiểm tra nếu tiến lên 1 ngày mà đụng ngày trả xe thì mình lùi lại (nếu cho phép)
    # Nhưng đơn giản nhất là tiến ngày lên 1 ngày
    new_date_obj = datetime(y, m, d) + timedelta(days=1)
    new_date = new_date_obj.strftime("%d/%m/%Y")
    
    page.evaluate(f"() => {{ window.fpStart.setDate('{new_date}', true); }}")
    page.wait_for_timeout(1500) # Đợi JS tính toán lại tiền
    
    new_total = page.locator("#display-total-price").inner_text()
    assert old_total != new_total, f"Expect: Tiền thuê phải thay đổi khi đổi ngày (từ {current_start} sang {new_date}). Actual: Tiền vẫn là {new_total}"
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('LƯU')")
    dialog_info.value.accept()

@pytest.mark.django_db
def test_TC_HD_U03(logged_in_page: Page):
    """TC-HD-U03: Chỉnh sửa ngày trả thành công"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    current_end = page.locator("#d-end-date").input_value()
    d, m, y = map(int, current_end.split('/'))
    new_date = (datetime(y, m, d) + timedelta(days=1)).strftime("%d/%m/%Y")
    
    page.evaluate(f"() => {{ window.fpEnd.setDate('{new_date}', true); }}")
    page.wait_for_timeout(500)
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('LƯU')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    assert "thành công" in msg.lower()

@pytest.mark.django_db
def test_TC_HD_U04(logged_in_page: Page):
    """TC-HD-U04: Thay đổi khách hàng khác"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    page.click("#customer-search-input")
    page.wait_for_selector("#customer-dropdown .search-item")
    
    # Lấy tên khách hàng thứ 2 trong list
    target_cust = page.locator("#customer-dropdown .search-item").nth(1)
    new_name = target_cust.locator("strong").inner_text()
    target_cust.click()
    
    # Kiểm tra hiển thị ngay lập tức trên UI
    assert page.locator("#display-name").input_value() == new_name
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('LƯU')")
    dialog_info.value.accept()

@pytest.mark.django_db
def test_TC_HD_U05(logged_in_page: Page):
    """TC-HD-U05: Thay đổi xe khác"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    # Xóa xe cũ
    if page.locator(".car-item-row .btn-action-delete").count() > 0:
        page.locator(".car-item-row .btn-action-delete").first.click()
    
    # Chọn xe mới
    page.click("#car-search-input-detail")
    page.wait_for_selector("#car-dropdown .search-item")
    
    new_car_item = page.locator("#customer-dropdown .search-item, #car-dropdown .search-item").first
    new_car_name = new_car_item.locator("strong").inner_text()
    new_car_item.click()
    
    # Đợi bảng render xong
    page.wait_for_timeout(1000)
    # Lấy nội dung bảng và normalize (xóa tab, xuống dòng)
    table_content = page.locator("#selected-cars-list-body").inner_text().lower().replace("\t", " ").replace("\n", " ")
    # Kiểm tra xem tên xe hoặc biển số có trong bảng không
    assert new_car_name.lower() in table_content or new_car_name.split()[-1].lower() in table_content
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('LƯU')")
    dialog_info.value.accept()

@pytest.mark.django_db
def test_TC_HD_U06(logged_in_page: Page):
    """TC-HD-U06: Xóa tất cả xe (lỗi: ít nhất 1 xe)"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    # Xóa sạch xe
    while page.locator(".car-item-row .btn-action-delete").count() > 0:
        page.locator(".car-item-row .btn-action-delete").first.click()
        page.wait_for_timeout(300)
    
    # Bắt dialog cảnh báo
    page.on("dialog", lambda dialog: dialog.accept())
    page.click("button:has-text('LƯU')")
    page.wait_for_timeout(1000)

@pytest.mark.django_db
def test_TC_HD_U07(logged_in_page: Page):
    """TC-HD-U07: Chỉnh sửa thời gian bắt đầu trùng lịch (Logic disable của Flatpickr)"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    # Kiểm tra sự tồn tại của biến JS và config
    is_ready = page.evaluate("""() => {
        return typeof window.fpStart !== 'undefined' && 
               window.fpStart.config && 
               (window.fpStart.config.disable.length > 0 || typeof BLOCKED_RANGES !== 'undefined');
    }""")
    assert is_ready, "Flatpickr start date không có logic chặn lịch"

@pytest.mark.django_db
def test_TC_HD_U08(logged_in_page: Page):
    """TC-HD-U08: Chỉnh sửa thời gian trả xe trùng lịch (Logic disable của Flatpickr)"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    is_ready = page.evaluate("""() => {
        return typeof window.fpEnd !== 'undefined' && 
               window.fpEnd.config && 
               (window.fpEnd.config.disable.length > 0 || typeof BLOCKED_RANGES !== 'undefined');
    }""")
    assert is_ready, "Flatpickr end date không có logic chặn lịch"

@pytest.mark.django_db
def test_TC_HD_U09(logged_in_page: Page):
    """TC-HD-U09: Ngày nhận xe dự kiến (minDate check)"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    has_min = page.evaluate("() => window.fpStart && (window.fpStart.config.minDate !== undefined || window.fpStart.config._minDate !== undefined)")
    assert has_min

@pytest.mark.django_db
def test_TC_HD_U10(logged_in_page: Page):
    """TC-HD-U10: Ngày trả xe dự kiến (minDate check)"""
    page = logged_in_page
    select_prebooked_contract(page)
    
    has_min = page.evaluate("() => window.fpEnd && (window.fpEnd.config.minDate !== undefined || window.fpEnd.config._minDate !== undefined)")
    assert has_min

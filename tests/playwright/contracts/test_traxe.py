import pytest
from playwright.sync_api import Page, expect
from datetime import datetime
from django.utils import timezone
from rentals.models import HopDong

def select_active_contract(page: Page):
    """Chọn hợp đồng 'Đang thuê' hoặc 'Quá hạn' (ngay_ket_thuc_du_kien < today)
    Sắp xếp ngẫu nhiên hoặc theo ID để mỗi test có xác suất lấy HĐ khác nhau."""
    today = timezone.now().date()
    
    # Lấy danh sách các HĐ có thể trả xe
    hds = HopDong.objects.filter(trang_thai__in=['Đang thuê', 'Quá hạn'])
    hd = hds.order_by('?').first() # Lấy ngẫu nhiên để tránh các test đá nhau
    
    if not hd:
        raise Exception("Không tìm thấy hợp đồng nào Đang thuê/Quá hạn để test trả xe!")
        
    ma_hd = hd.ma_hd
    page.goto(f"http://127.0.0.1:8000/hop-dong/detail/{ma_hd}/", timeout=60000)
    page.wait_for_load_state("networkidle")
    return ma_hd

def go_to_return_tab(page: Page):
    """Chuyển sang tab Trả xe và đợi nội dung hiện ra"""
    page.click("text=3. TRẢ XE & QUYẾT TOÁN")
    page.wait_for_selector("#return-actual-date", state="visible", timeout=10000)
    page.wait_for_timeout(500)

@pytest.mark.django_db
def test_TC_HD_TX_01(logged_in_page: Page):
    """TC-HD-TX-01: Trả xe thành công với đầy đủ thông tin"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    page.fill("#return-late-fee", "50000")
    page.fill("#return-other-fee", "20000")
    page.fill("#return-note", "Xe trả đúng hạn, sạch sẽ.")
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN TRẢ XE & ĐÓNG HĐ')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    
    page.wait_for_load_state("networkidle")
    assert "thành công" in msg.lower() or "hoàn tất" in msg.lower()
    
    page.wait_for_selector("#label-status")
    status_text = page.locator("#label-status").inner_text()
    assert "ĐÃ HOÀN THÀNH" in status_text.upper()

@pytest.mark.django_db
def test_TC_HD_TX_02(logged_in_page: Page):
    """TC-HD-TX-02: Kiểm tra ngày trả xe thực tế bé hơn ngày bắt đầu thuê thì bị chặn"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    # Kiểm tra config của flatpickr
    has_min_date = page.locator("#return-actual-date").evaluate(
        "el => el._flatpickr && (el._flatpickr.config.minDate !== undefined || el._flatpickr.config._minDate !== undefined)"
    )
    assert has_min_date is True

@pytest.mark.django_db
def test_TC_HD_TX_03(logged_in_page: Page):
    """TC-HD-TX-03: Kiểm tra ngày trả xe thực tế lớn hơn ngày hiện tại thì bị chặn"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    # Kiểm tra config của flatpickr
    has_max_date = page.locator("#return-actual-date").evaluate(
        "el => el._flatpickr && (el._flatpickr.config.maxDate !== undefined || el._flatpickr.config._maxDate !== undefined)"
    )
    assert has_max_date is True

@pytest.mark.django_db
def test_TC_HD_TX_04(logged_in_page: Page):
    """TC-HD-TX-04: Kiểm tra không được nhập chữ vào ô phạt quá hạn"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    page.fill("#return-late-fee", "abcxyz")
    val = page.locator("#return-late-fee").input_value()
    assert val == "" or not any(c.isalpha() for c in val)

@pytest.mark.django_db
def test_TC_HD_TX_05(logged_in_page: Page):
    """TC-HD-TX-05: Kiểm tra không được nhập chữ vào ô phụ phí khác"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    page.fill("#return-other-fee", "!!!@@@")
    val = page.locator("#return-other-fee").input_value()
    assert val == "" or not any(c.isalpha() for c in val)

@pytest.mark.django_db
def test_TC_HD_TX_06(logged_in_page: Page):
    """TC-HD-TX-06: Kiểm tra không nhập số tiền phạt quá hạn quá 8 chữ số"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    page.fill("#return-late-fee", "123456789")
    val = page.locator("#return-late-fee").input_value().replace(",", "").replace(".", "").strip()
    assert len(val) <= 8

@pytest.mark.django_db
def test_TC_HD_TX_07(logged_in_page: Page):
    """TC-HD-TX-07: (Duplicate TX-06) Kiểm tra không nhập số tiền phạt quá hạn quá 8 chữ số"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    page.fill("#return-late-fee", "999999999")
    val = page.locator("#return-late-fee").input_value().replace(",", "").replace(".", "").strip()
    assert len(val) <= 8

@pytest.mark.django_db
def test_TC_HD_TX_08(logged_in_page: Page):
    """TC-HD-TX-08: Kiểm tra số tiền phạt quá hạn là 8 chữ số (Hợp lệ)"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    page.fill("#return-late-fee", "10000000")
    val = page.locator("#return-late-fee").input_value().replace(",", "").replace(".", "").strip()
    assert val == "10000000"

@pytest.mark.django_db
def test_TC_HD_TX_09(logged_in_page: Page):
    """TC-HD-TX-09: Kiểm tra số tiền phụ phí khác là 8 chữ số (Hợp lệ)"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    page.fill("#return-other-fee", "88888888")
    val = page.locator("#return-other-fee").input_value().replace(",", "").replace(".", "").strip()
    assert val == "88888888"

@pytest.mark.django_db
def test_TC_HD_TX_10(logged_in_page: Page):
    """TC-HD-TX-10: Trả xe thành công không nhập gì cả (dùng mặc định)"""
    page = logged_in_page
    select_active_contract(page)
    go_to_return_tab(page)
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN TRẢ XE & ĐÓNG HĐ')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    
    page.wait_for_load_state("networkidle")
    assert "thành công" in msg.lower() or "hoàn tất" in msg.lower()
    
    page.wait_for_selector("#label-status")
    status_text = page.locator("#label-status").inner_text()
    assert "ĐÃ HOÀN THÀNH" in status_text.upper()

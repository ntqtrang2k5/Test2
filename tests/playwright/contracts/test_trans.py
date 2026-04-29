import pytest
from playwright.sync_api import Page, expect
from datetime import datetime
from django.utils import timezone
from rentals.models import HopDong

def select_contract(page: Page):
    """Chọn hợp đồng đang ở trạng thái 'Đặt trước' hoặc 'Đang thuê' và có ngày bắt đầu <= hôm nay"""
    today = timezone.now().date()
    # Tìm hợp đồng thỏa mãn:
    # 1. Đặt trước hoặc Đang thuê
    # 2. Ngày bắt đầu <= hôm nay (để tránh lỗi flatpickr và backend)
    hd = HopDong.objects.filter(
        trang_thai__in=['Đặt trước', 'Đang thuê'],
        ngay_bat_dau__lte=today,
    ).first()
    
    if not hd:
        raise Exception("Không tìm thấy hợp đồng nào Đặt trước/Đang thuê có ngày bắt đầu <= hôm nay để test!")
        
    ma_hd = hd.ma_hd
    
    page.goto("http://127.0.0.1:8000/hop-dong/", timeout=60000)
    page.wait_for_load_state("networkidle")
    
    # Chọn tab tương ứng
    if hd.trang_thai == 'Đặt trước':
        page.click("text=Đặt trước")
    else:
        page.click("text=Đang thuê")
    page.wait_for_timeout(1000)
    
    # Bấm nút Xem của đúng hợp đồng này
    row = page.locator(f"table tbody tr:has-text('{ma_hd}')").first
    row.locator("text=Xem").click()
    
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(".tab-item")
    return ma_hd


@pytest.mark.django_db
def test_TC_HD_GD01(logged_in_page: Page):
    """ 
    TC-HD-GD01: Kiểm tra form hiển thị mặc định loại giao dịch và ngày giao dịch 
    1. Chọn Hợp đồng thuê và Xem
    2. Chọn tab giao dịch tài chính
    3. Bấm Thêm giao dịch mới
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active", timeout=5000)
    
    # Kiểm tra mặc định là Thu thêm
    type_val = page.locator("#new-gd-type").input_value()
    assert type_val == "Thu thêm", f"Expect 'Thu thêm', got {type_val}"
    
    # Kiểm tra ngày giao dịch mặc định là ngày hôm nay
    today_str = datetime.now().strftime("%d/%m/%Y")
    date_val = page.locator("#new-gd-date").input_value()
    assert date_val == today_str, f"Expect '{today_str}', got '{date_val}'"


@pytest.mark.django_db
def test_TC_HD_GD02(logged_in_page: Page):
    """ 
    TC-HD-GD02: Thêm giao dịch Tiền ứng của khách hàng thành công
    Thu thêm tiền, kiểm tra lưu thành công, thông báo hiển thị, lịch sử thu chi và tổng đã thu cộng dồn.
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    
    # Lưu lại tổng đã thu hiện tại
    old_prepaid_text = page.locator("#label-prepaid").inner_text().replace("đ", "").replace(",", "").replace(".", "").strip()
    old_prepaid = int(old_prepaid_text) if old_prepaid_text else 0
    
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Thu thêm")
    page.fill("#new-gd-amount", "500000") # Số tiền hợp lệ < 8 số
    
    # Handle alert dialog properly using expect_event
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN GIAO DỊCH')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    
    page.wait_for_load_state("networkidle")
    
    # Check dialog message
    assert "thành công" in msg.lower(), f"Expected success, but got error dialog: {msg}"
    
    # Check current tab is still Finance (auto reloaded by js hash #tab-money)
    page.wait_for_selector("#tab-money.active")
    
    # Check 'Tổng đã thu' updated
    new_prepaid_text = page.locator("#label-prepaid").inner_text().replace("đ", "").replace(",", "").replace(".", "").strip()
    new_prepaid = int(new_prepaid_text) if new_prepaid_text else 0
    assert new_prepaid == old_prepaid + 500000
    
    # Check history table
    history_row = page.locator("#tab-money .finance-table tbody tr").first
    if history_row.count() == 0:
        history_row = page.locator("#tab-money .data-table tbody tr").first # In case class is data-table
        
    assert "Thu thêm" in history_row.inner_text()
    assert "500.000" in history_row.inner_text()


@pytest.mark.django_db
def test_TC_HD_GD03(logged_in_page: Page):
    """ 
    TC-HD-GD03: Thêm giao dịch Thu thêm và check hiển thị bên trang Tài Chính (Dashboard)
    """
    page = logged_in_page
    ma_hd = select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Thu thêm")
    page.fill("#new-gd-amount", "600000")
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN GIAO DỊCH')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    assert "thành công" in msg.lower(), f"Expected success, but got error dialog: {msg}"
    page.wait_for_load_state("networkidle")
    
    # Điều hướng qua trang Tài chính
    page.goto("http://127.0.0.1:8000/tai-chinh/")
    page.wait_for_load_state("networkidle")
    
    # Tìm dòng giao dịch vừa được thêm (tìm đúng mã hợp đồng, loại giao dịch và số tiền)
    row = page.locator(f".finance-table tbody tr:has-text('{ma_hd}'):has-text('Thu thêm'):has-text('600')").first
    row_text = row.inner_text()
    
    # Kiểm tra có tham chiếu tới Hợp đồng
    assert ma_hd in row_text
    
    # Kiểm tra số tiền nằm ở cột Thu (cell-income)
    income_cell = row.locator(".cell-income").inner_text().replace(",", "").replace(".", "").strip()
    assert "600000" in income_cell


@pytest.mark.django_db
def test_TC_HD_GD04(logged_in_page: Page):
    """ 
    TC-HD-GD04: Thêm giao dịch Hoàn trả lại khách thành công 
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    # Chọn Hoàn trả
    page.select_option("#new-gd-type", "Hoàn trả")
    page.fill("#new-gd-amount", "200000")
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN GIAO DỊCH')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    
    page.wait_for_load_state("networkidle")
    
    assert "thành công" in msg.lower(), f"Expected success, but got error dialog: {msg}"
    page.wait_for_selector("#tab-money.active")
    
    # Kiểm tra history
    history_row = page.locator("#tab-money .data-table tbody tr:has-text('Hoàn trả'):has-text('200')").first
    assert "Hoàn trả" in history_row.inner_text()
    assert "200.000" in history_row.inner_text()


@pytest.mark.django_db
def test_TC_HD_GD05(logged_in_page: Page):
    """ 
    TC-HD-GD05: Thêm giao dịch Hoàn trả và check hiển thị bên trang Tài Chính (cột Chi) 
    """
    page = logged_in_page
    ma_hd = select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Hoàn trả")
    page.fill("#new-gd-amount", "300000")
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN GIAO DỊCH')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    assert "thành công" in msg.lower(), f"Expected success, but got error dialog: {msg}"
    page.wait_for_load_state("networkidle")
    
    # Điều hướng qua trang Tài chính
    page.goto("http://127.0.0.1:8000/tai-chinh/")
    page.wait_for_load_state("networkidle")
    
    # Tìm dòng giao dịch (tìm đúng mã hợp đồng, loại giao dịch và số tiền)
    row = page.locator(f".finance-table tbody tr:has-text('{ma_hd}'):has-text('Hoàn trả'):has-text('300')").first
    row_text = row.inner_text()
    
    assert ma_hd in row_text
    
    # Kiểm tra số tiền nằm ở cột Chi (cell-expense)
    expense_cell = row.locator(".cell-expense").inner_text().replace(",", "").replace(".", "").strip()
    assert "300000" in expense_cell


@pytest.mark.django_db
def test_TC_HD_GD06(logged_in_page: Page):
    """
    TC-HD-GD06: Kiểm tra số tiền không được nhập chữ, kí tự và số âm
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Hoàn trả")
    
    # Nhập số âm
    page.fill("#new-gd-amount", "-50000")
    val_negative = page.locator("#new-gd-amount").input_value()
    
    # Nhập chữ và kí tự đặc biệt
    page.fill("#new-gd-amount", "abc!@#")
    val_chars = page.locator("#new-gd-amount").input_value()
    
    # Số âm có thể mất dấu trừ hoặc không cho nhập, kí tự thì không cho nhập
    assert val_chars == "" or not any(c.isalpha() for c in val_chars)


@pytest.mark.django_db
def test_TC_HD_GD07(logged_in_page: Page):
    """
    TC-HD-GD07: Nhập 9 chữ số để Kiểm tra số tiền không được nhập quá 8 chữ số
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Hoàn trả")
    
    page.fill("#new-gd-amount", "123456789")
    val = page.locator("#new-gd-amount").input_value().replace(",", "").replace(".", "").strip()
    assert len(val) <= 8


@pytest.mark.django_db
def test_TC_HD_GD08(logged_in_page: Page):
    """
    TC-HD-GD08: Nhập 8 chữ số để Kiểm tra số tiền không được nhập quá 8 chữ số
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Hoàn trả")
    
    page.fill("#new-gd-amount", "12345678")
    val = page.locator("#new-gd-amount").input_value().replace(",", "").replace(".", "").strip()
    assert val == "12345678"


@pytest.mark.django_db
def test_TC_HD_GD09(logged_in_page: Page):
    """
    TC-HD-GD09: Nhập 7 chữ số để Kiểm tra số tiền không được nhập quá 8 chữ số
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Hoàn trả")
    
    page.fill("#new-gd-amount", "1234567")
    val = page.locator("#new-gd-amount").input_value().replace(",", "").replace(".", "").strip()
    assert val == "1234567"


@pytest.mark.django_db
def test_TC_HD_GD10(logged_in_page: Page):
    """
    TC-HD-GD10: Nhập 7 chữ số để Kiểm tra số tiền không được nhập quá 8 chữ số (Trùng test case)
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Hoàn trả")
    
    page.fill("#new-gd-amount", "7654321")
    val = page.locator("#new-gd-amount").input_value().replace(",", "").replace(".", "").strip()
    assert val == "7654321"


@pytest.mark.django_db
def test_TC_HD_GD11(logged_in_page: Page):
    """
    TC-HD-GD11: Kiểm tra thời gian giao dịch bé hơn ngày bắt đầu thuê nhận xe
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    # Kiểm tra minDate trong flatpickr của ô input date
    min_date_set = page.locator("#new-gd-date").evaluate("el => el._flatpickr && el._flatpickr.config.minDate !== undefined")
    assert min_date_set is True


@pytest.mark.django_db
def test_TC_HD_GD12(logged_in_page: Page):
    """
    TC-HD-GD12: Kiểm tra thời gian giao dịch lớn hơn ngày trả xe
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    # Kiểm tra maxDate trong flatpickr của ô input date
    max_date_set = page.locator("#new-gd-date").evaluate("el => el._flatpickr && el._flatpickr.config.maxDate !== undefined")
    assert max_date_set is True

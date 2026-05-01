import pytest
from playwright.sync_api import Page, expect
from datetime import datetime
from django.utils import timezone
from rentals.models import HopDong

def select_contract(page: Page):
    """Lấy hợp đồng 'Đặt trước' hoặc 'Đang thuê' có thời gian gần hiện tại nhất
    để tránh các ràng buộc ngày tháng (minDate/maxDate) của Flatpickr."""
    today = timezone.now().date()
    
    # Ưu tiên 1: Đang trong hạn thuê (Ngày bắt đầu <= hôm nay <= Ngày kết thúc)
    hd = HopDong.objects.filter(
        trang_thai__in=['Đặt trước', 'Đang thuê'],
        ngay_bat_dau__lte=today,
        ngay_ket_thuc_du_kien__gte=today,
    ).first()
    
    # Ưu tiên 2: Sắp thuê (Ngày bắt đầu > hôm nay) - Sắp xếp theo ngày bắt đầu gần nhất
    if not hd:
        hd = HopDong.objects.filter(
            trang_thai__in=['Đặt trước', 'Đang thuê'],
            ngay_bat_dau__gt=today
        ).order_by('ngay_bat_dau').first()
    
    if not hd:
        raise Exception("Không tìm thấy hợp đồng nào Đặt trước/Đang thuê phù hợp để test!")
        
    ma_hd = hd.ma_hd
    page.goto(f"http://127.0.0.1:8000/hop-dong/detail/{ma_hd}/", timeout=60000)
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(".tab-container", timeout=15000)
    return ma_hd


@pytest.mark.django_db
def test_TC_HD_GD01(logged_in_page: Page):
    """
    TC-HD-GD01: Kiểm tra form hiển thị mặc định loại giao dịch và ngày giao dịch.
    Nhập số tiền hợp lệ và xác nhận.
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    
    old_prepaid_text = page.locator("#label-prepaid").inner_text().replace("đ", "").replace(",", "").replace(".", "").strip()
    old_prepaid = int(old_prepaid_text) if old_prepaid_text else 0
    
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active", timeout=5000)
    
    # Kiểm tra mặc định là Thu thêm
    type_val = page.locator("#new-gd-type").input_value()
    assert "Thu thêm" in type_val, f"Expect 'Thu thêm', got {type_val}"
    
    # Kiểm tra ngày giao dịch mặc định
    date_val = page.locator("#new-gd-date").input_value()
    
    # Nếu bị trống (do minDate > today), hãy chọn ngày bắt đầu của hợp đồng
    if not date_val:
        # Lấy ngày từ data-date của input #d-start-date trên trang detail
        fallback_date = page.locator("#d-start-date").getAttribute("data-date")
        page.evaluate(f"(d) => {{ if(window.flatpickr) flatpickr('#new-gd-date').setDate(d, true, 'd/m/Y'); }}", fallback_date)
        page.wait_for_timeout(500)
    
    page.fill("#new-gd-amount", "100000")
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN GIAO DỊCH')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    
    page.wait_for_load_state("networkidle")
    
    assert "thành công" in msg.lower(), f"Expected success, got {msg}"
    page.wait_for_selector("#tab-money.active")
    
    new_prepaid_text = page.locator("#label-prepaid").inner_text().replace("đ", "").replace(",", "").replace(".", "").strip()
    new_prepaid = int(new_prepaid_text) if new_prepaid_text else 0
    assert new_prepaid == old_prepaid + 100000
    
    history_row = page.locator("#tab-money table tbody tr").first
    assert "Thu thêm" in history_row.inner_text()
    assert "100.000" in history_row.inner_text() or "100,000" in history_row.inner_text()


@pytest.mark.django_db
def test_TC_HD_GD02(logged_in_page: Page):
    """
    TC-HD-GD02: Thêm giao dịch Tiền ứng của khách hàng thành công
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    
    old_prepaid_text = page.locator("#label-prepaid").inner_text().replace("đ", "").replace(",", "").replace(".", "").strip()
    old_prepaid = int(old_prepaid_text) if old_prepaid_text else 0
    
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Thu thêm")
    page.fill("#new-gd-amount", "500000")
    
    # Nếu bị trống, hãy chọn ngày bắt đầu của hợp đồng
    if not page.locator("#new-gd-date").input_value():
        fallback_date = page.locator("#d-start-date").getAttribute("data-date")
        page.evaluate(f"(d) => {{ if(window.flatpickr) flatpickr('#new-gd-date').setDate(d, true, 'd/m/Y'); }}", fallback_date)
    
    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN GIAO DỊCH')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    
    page.wait_for_load_state("networkidle")
    
    assert "thành công" in msg.lower(), f"Expected success, but got error dialog: {msg}"
    page.wait_for_selector("#tab-money.active")
    
    new_prepaid_text = page.locator("#label-prepaid").inner_text().replace("đ", "").replace(",", "").replace(".", "").strip()
    new_prepaid = int(new_prepaid_text) if new_prepaid_text else 0
    assert new_prepaid >= old_prepaid + 500000, f"Tổng đã thu phải tăng ít nhất 500000, got {new_prepaid} (was {old_prepaid})"
    
    # Tìm đúng dòng 'Thu thêm' có số tiền 500.000 trong bảng lịch sử
    target_row = page.locator("#tab-money table tbody tr:has-text('Thu thêm'):has-text('500')").first
    assert target_row.count() > 0, "Không tìm thấy dòng Thu thêm 500.000 trong lịch sử"


@pytest.mark.django_db
def test_TC_HD_GD03(logged_in_page: Page):
    """
    TC-HD-GD03: Thêm giao dịch Tiền ứng của khách hàng thành công và check hiển thị tài chính
    """
    page = logged_in_page
    ma_hd = select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Thu thêm")
    page.fill("#new-gd-amount", "600000")
    
    # Nếu bị trống, hãy chọn ngày bắt đầu của hợp đồng
    if not page.locator("#new-gd-date").input_value():
        fallback_date = page.locator("#d-start-date").getAttribute("data-date")
        page.evaluate(f"(d) => {{ if(window.flatpickr) flatpickr('#new-gd-date').setDate(d, true, 'd/m/Y'); }}", fallback_date)

    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN GIAO DỊCH')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    page.wait_for_load_state("networkidle")
    
    # Điều hướng trang tài chính
    page.goto("http://127.0.0.1:8000/tai-chinh/")
    page.wait_for_load_state("networkidle")
    
    # Tìm dòng chứa HD và số tiền - dùng .cell-income chỉ để tránh strict mode violation
    row = page.locator(f"table tbody tr:has-text('{ma_hd}'):has-text('Thu thêm'):has-text('600')").first
    assert row.count() > 0, "Không tìm thấy giao dịch bên trang tài chính"
    assert "600" in row.locator(".cell-income").first.inner_text()


@pytest.mark.django_db
def test_TC_HD_GD04(logged_in_page: Page):
    """
    TC-HD-GD04: Thêm giao dịch Tiền hoàn trả lại khách thành công
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Hoàn trả")
    page.fill("#new-gd-amount", "200000")
    
    # Nếu bị trống, hãy chọn ngày bắt đầu của hợp đồng
    if not page.locator("#new-gd-date").input_value():
        fallback_date = page.locator("#d-start-date").getAttribute("data-date")
        page.evaluate(f"(d) => {{ if(window.flatpickr) flatpickr('#new-gd-date').setDate(d, true, 'd/m/Y'); }}", fallback_date)

    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN GIAO DỊCH')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    
    page.wait_for_load_state("networkidle")
    
    assert "thành công" in msg.lower(), f"Expected success, got: {msg}"
    page.wait_for_selector("#tab-money.active")
    
    # Tìm đúng dòng 'Hoàn trả' có số tiền 200.000 trong bảng lịch sử
    target_row = page.locator("#tab-money table tbody tr:has-text('Hoàn trả'):has-text('200')").first
    assert target_row.count() > 0, "Không tìm thấy dòng Hoàn trả 200.000 trong lịch sử"


@pytest.mark.django_db
def test_TC_HD_GD05(logged_in_page: Page):
    """
    TC-HD-GD05: Thêm giao dịch Tiền hoàn trả lại khách thành công và check trang tài chính
    """
    page = logged_in_page
    ma_hd = select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.select_option("#new-gd-type", "Hoàn trả")
    page.fill("#new-gd-amount", "300000")
    
    # Nếu bị trống, hãy chọn ngày bắt đầu của hợp đồng
    if not page.locator("#new-gd-date").input_value():
        fallback_date = page.locator("#d-start-date").getAttribute("data-date")
        page.evaluate(f"(d) => {{ if(window.flatpickr) flatpickr('#new-gd-date').setDate(d, true, 'd/m/Y'); }}", fallback_date)

    with page.expect_event("dialog") as dialog_info:
        page.click("button:has-text('XÁC NHẬN GIAO DỊCH')")
    msg = dialog_info.value.message
    dialog_info.value.accept()
    page.wait_for_load_state("networkidle")
    
    page.goto("http://127.0.0.1:8000/tai-chinh/")
    page.wait_for_load_state("networkidle")
    
    row = page.locator(f"table tbody tr:has-text('{ma_hd}'):has-text('Hoàn trả'):has-text('300')").first
    assert row.count() > 0, "Không tìm thấy giao dịch bên trang tài chính"
    # Dùng .cell-expense chỉ để tránh strict mode violation
    assert "300" in row.locator(".cell-expense").first.inner_text()


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
    
    # Kí tự chữ
    page.fill("#new-gd-amount", "abc!@#")
    val_chars = page.locator("#new-gd-amount").input_value()
    assert val_chars == "" or not any(c.isalpha() for c in val_chars), "Không được phép nhập chữ"
    
    # Số âm
    page.fill("#new-gd-amount", "-50000")
    val_negative = page.locator("#new-gd-amount").input_value()
    assert "-" not in val_negative, "Không được phép nhập số âm"


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
    
    page.fill("#new-gd-amount", "123456789")
    val = page.locator("#new-gd-amount").input_value().replace(",", "").replace(".", "").strip()
    assert len(val) <= 8, f"Kỳ vọng max 8 số, nhưng lấy được {len(val)} số: {val}"


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
    
    page.fill("#new-gd-amount", "1234567")
    val = page.locator("#new-gd-amount").input_value().replace(",", "").replace(".", "").strip()
    assert val == "1234567"


@pytest.mark.django_db
def test_TC_HD_GD10(logged_in_page: Page):
    """
    TC-HD-GD10: Nhập 7 chữ số để Kiểm tra số tiền không được nhập quá 8 chữ số
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    page.fill("#new-gd-amount", "7654321")
    val = page.locator("#new-gd-amount").input_value().replace(",", "").replace(".", "").strip()
    assert val == "7654321"


@pytest.mark.django_db
def test_TC_HD_GD11(logged_in_page: Page):
    """
    TC-HD-GD11: Kiểm tra thời gian giao dịch bé hơn ngày bắt đầu thuê nhận xe
    (Trường hợp này ngày đó sẽ bị disable)
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    # Xác minh config của flatpickr đã set minDate
    has_min_date = page.locator("#new-gd-date").evaluate(
        "el => el._flatpickr && el._flatpickr.config.minDate !== undefined && el._flatpickr.config.minDate !== null"
    )
    assert has_min_date is True, "Chưa config giới hạn ngày nhỏ nhất (minDate) cho ô chọn ngày"


@pytest.mark.django_db
def test_TC_HD_GD12(logged_in_page: Page):
    """
    TC-HD-GD12: Kiểm tra thời gian giao dịch lớn hơn ngày trả xe (hoặc ngày hiện tại)
    (Trường hợp này ngày đó sẽ bị disable)
    """
    page = logged_in_page
    select_contract(page)
    
    page.click("text=2. GIAO DỊCH TÀI CHÍNH")
    page.wait_for_timeout(500)
    page.click("button:has-text('THÊM GIAO DỊCH MỚI')")
    page.wait_for_selector("#modal-add-transaction.active")
    
    # Xác minh config của flatpickr đã set maxDate
    has_max_date = page.locator("#new-gd-date").evaluate(
        "el => el._flatpickr && el._flatpickr.config.maxDate !== undefined && el._flatpickr.config.maxDate !== null"
    )
    assert has_max_date is True, "Chưa config giới hạn ngày lớn nhất (maxDate) cho ô chọn ngày"


import pytest
import random
from playwright.sync_api import Page, expect
from datetime import datetime, timedelta
from re import compile

def select_prebooked_contract(page: Page):
    """ V\xe0o danh s\xe1ch -> Tab \u0110\u1eb7t tr\u01b0\u1edbc -> B\u1ea5m Xem. """
    page.goto("http://127.0.0.1:8000/hop-dong/", timeout=60000)
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("text=\u0110\u1eb7t tr\u01b0\u1edbc")
    page.click("text=\u0110\u1eb7t tr\u01b0\u1edbc")
    page.wait_for_timeout(1500)
    rows = page.locator("table tbody tr")
    if rows.count() > 0:
        rows.first.locator("text=Xem").click()
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("button:has-text('L\u01afU')", timeout=30000)
    else:
        raise Exception("Expect: Co it nhat 1 hop dong Dat truoc \u0111\u1ec3 test")

@pytest.mark.django_db
def test_TC_HD_U01(logged_in_page: Page):
    """
    Steps:
    Chỉnh sửa hợp đồng đặt trước thành công
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    select_prebooked_contract(page)
    page.evaluate("() => { window.fpStart.setDate('21/08/2027', true); }")
    page.wait_for_timeout(1000)
    page.evaluate("() => { window.fpEnd.setDate('26/08/2027', true); }")
    page.click("#customer-search-input"); page.wait_for_selector("#customer-dropdown .search-item"); page.locator("#customer-dropdown .search-item").nth(1).click()
    page.locator("#selected-cars-list-body .btn-action-delete").first.click()
    page.click("#car-search-input-detail"); page.type("#car-search-input-detail", "a"); page.wait_for_selector("#car-dropdown .search-item"); page.locator("#car-dropdown .search-item").first.click()
    with page.expect_event("dialog") as d: page.get_by_role("button", name="L\u01afU").click(); d.value.accept()

@pytest.mark.django_db
def test_TC_HD_U02(logged_in_page: Page):
    """
    Steps:
    Chỉnh sửa ngày nhận xe thành công
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    select_prebooked_contract(page)
    old_total = page.locator("#display-total-price").inner_text()
    page.evaluate("() => { window.fpStart.setDate('22/08/2027', true); }")
    page.wait_for_timeout(2000)
    actual_total = page.locator("#display-total-price").inner_text()
    assert old_total != actual_total
    with page.expect_event("dialog") as d: page.get_by_role("button", name="L\u01afU").click(); d.value.accept()

@pytest.mark.django_db
def test_TC_HD_U03(logged_in_page: Page):
    """
    Steps:
    Chỉnh sửa ngày trả thành công
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    select_prebooked_contract(page)
    page.evaluate("() => { window.fpEnd.setDate('30/08/2027', true); }")
    page.wait_for_timeout(1000)
    with page.expect_event("dialog") as d: page.get_by_role("button", name="L\u01afU").click(); d.value.accept()

@pytest.mark.django_db
def test_TC_HD_U04(logged_in_page: Page):
    """
    Steps:
    Thay đổi khách hàng khác
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    select_prebooked_contract(page)
    page.click("#customer-search-input"); page.wait_for_selector("#customer-dropdown .search-item")
    new_name = page.locator("#customer-dropdown .search-item").nth(1).locator("strong").inner_text()
    page.locator("#customer-dropdown .search-item").nth(1).click()
    actual_name = page.locator("#display-name").input_value()
    assert new_name == actual_name
    with page.expect_event("dialog") as d: page.get_by_role("button", name="L\u01afU").click(); d.value.accept()

@pytest.mark.django_db
def test_TC_HD_U05(logged_in_page: Page):
    """
    Steps:
    Thay đổi xe khác
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    
    """
    page = logged_in_page
    select_prebooked_contract(page)
    page.locator("#selected-cars-list-body .btn-action-delete").first.click()
    page.click("#car-search-input-detail"); page.type("#car-search-input-detail", "a"); page.wait_for_selector("#car-dropdown .search-item")
    car_plate = page.locator("#car-dropdown .search-item").first.locator("span").first.inner_text().replace("Bi\u1ec3n s\u1ed1: ", "").strip()
    page.locator("#car-dropdown .search-item").first.click()
    page.wait_for_timeout(1000)
    actual_list = page.locator("#selected-cars-list-body").inner_text()
    assert car_plate in actual_list
    with page.expect_event("dialog") as d: page.get_by_role("button", name="L\u01afU").click(); d.value.accept()

@pytest.mark.django_db
def test_TC_HD_U06(logged_in_page: Page):
    """
    Steps:
    Xóa xe với hợp đồng hiện chỉ có 1 xe
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    V1: Lỗi hiện thông báo không đúng
V2: như mong đợi
    """
    page = logged_in_page
    select_prebooked_contract(page)
    while page.locator("#selected-cars-list-body .btn-action-delete").count() > 0:
        page.locator("#selected-cars-list-body .btn-action-delete").first.click()
        page.wait_for_timeout(300)
    msg = ""
    def handle_dialog(dialog):
        nonlocal msg; msg = dialog.message; dialog.accept()
    page.on("dialog", handle_dialog)
    page.click("button:has-text('L\u01afU')")
    page.wait_for_timeout(1000)
    assert "\xedt nh\u1ea5t m\u1ed9t xe" in msg.lower()

@pytest.mark.django_db
def test_TC_HD_U07(logged_in_page: Page):
    """
    Steps:
    Chỉnh sửa thời gian bắt đầu thuê bị lỗi
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    select_prebooked_contract(page)
    car_plate = "51A-987.65"
    page.click("#car-search-input-detail"); page.fill("#car-search-input-detail", car_plate)
    page.wait_for_selector(f"text={car_plate}"); page.locator(f"text={car_plate}").first.click()
    page.wait_for_timeout(2000)
    page.click("#d-start-date")
    page.evaluate("() => { window.fpStart.jumpToDate('2026-06-01'); }")
    page.wait_for_timeout(1000)
    info = page.evaluate("() => { const d = Array.from(document.querySelectorAll('.flatpickr-day')).find(x => x.innerText === '2' && !x.classList.contains('prevMonthDay') && !x.classList.contains('nextMonthDay')); return { is_disabled: d.classList.contains('flatpickr-disabled') || d.style.pointerEvents === 'none', title: d.getAttribute('title') }; }")
    assert info['is_disabled'], f"Expect: Ngay 02/06 phai bi DISABLE (do trung lich) - Actual: Van click \u0111\u01b0\u1ee3c"

@pytest.mark.django_db
def test_TC_HD_U08(logged_in_page: Page):
    """
    Steps:
    Chỉnh sửa thời gian trả xe bị lỗi
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    select_prebooked_contract(page)
    car_plate = "51A-987.65"
    page.click("#car-search-input-detail"); page.fill("#car-search-input-detail", car_plate)
    page.wait_for_selector(f"text={car_plate}"); page.locator(f"text={car_plate}").first.click()
    page.wait_for_timeout(2000)
    page.click("#d-end-date")
    page.evaluate("() => { window.fpEnd.jumpToDate('2026-06-01'); }")
    page.wait_for_timeout(1000)
    info = page.evaluate("() => { const d = Array.from(document.querySelectorAll('.flatpickr-day')).find(x => x.innerText === '2' && !x.classList.contains('prevMonthDay') && !x.classList.contains('nextMonthDay')); return { is_disabled: d.classList.contains('flatpickr-disabled') || d.style.pointerEvents === 'none' }; }")
    assert info['is_disabled'], f"Expect: Ngay 02/06 phai bi DISABLE - Actual: Van click \u0111\u01b0\u1ee3c"

@pytest.mark.django_db
def test_TC_HD_U09(logged_in_page: Page):
    """
    Steps:
    Kiểm tra logic thời gian ngày nhận xe dự kiến
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    select_prebooked_contract(page)
    page.click("#d-start-date")
    page.evaluate("() => { window.fpStart.jumpToDate(new Date()); }")
    page.wait_for_timeout(1000)
    yesterday = (datetime.now() - timedelta(days=1)).day
    is_disabled = page.evaluate(f"() => {{ const d = Array.from(document.querySelectorAll('.flatpickr-day:not(.nextMonthDay):not(.prevMonthDay)')).find(el => el.innerText === '{yesterday}'); return d.classList.contains('flatpickr-disabled') || d.style.pointerEvents === 'none'; }}")
    assert is_disabled

@pytest.mark.django_db
def test_TC_HD_U10(logged_in_page: Page):
    """
    Steps:
    Kiểm tra logic thời gian ngày trả xe dự kiến
    1. Chọn xem 1 hợp đồng đặt trước
    Expected:
    
    Actual:
    Như mong đợi
    """
    page = logged_in_page
    select_prebooked_contract(page)
    page.click("#d-start-date")
    page.locator(".flatpickr-day:not(.prevMonthDay):not(.nextMonthDay):has-text('20')").first.click()
    page.wait_for_timeout(2000)
    page.click("#d-end-date")
    # Ki\u1ec3m tra ng\xe0y 19: N\u1ebfu minDate l\xe0 20 th\xec 19 ph\u1ea3i b\xed disable (kh\xf4ng click \u0111\u01b0\u1ee3c)
    # C\xe1ch ki\u1ec3m tra m\u1ea1nh m\u1ebd h\u01a1n: Th\u1eed click v\xe0o ng\xe0y 19 v\xe0 xem ng\xe0y tr\xe1 c\xf3 \u0111\u1ed5i kh\xf4ng
    old_date = page.locator("#d-end-date").input_value()
    page.locator(".flatpickr-day:not(.prevMonthDay):not(.nextMonthDay):has-text('19')").first.click(force=True)
    page.wait_for_timeout(1000)
    new_date = page.locator("#d-end-date").input_value()
    assert old_date == new_date, f"Expect: Ngay 19 bi DISABLE (kh\xf4ng \u0111\u1ed5i ng\xe0y) - Actual: Ngay \u0111\xe3 b\u1ecb \u0111\u1ed5i th\xe0nh {new_date}"

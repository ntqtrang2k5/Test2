import pytest
import random
from tests.pages.car_page import CarPage
from cars.models import Xe, HangXe, LoaiXe, KieuXe, MauSac
from rentals.models import ChiTietHopDong
from django.db.models import Q

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture
def car_page(logged_in_page):
    logged_in_page.set_default_timeout(10000)
    return CarPage(logged_in_page)

def get_car_for_edit(can_change_plate=False):
    """
    Lấy một xe để edit. 
    Nếu can_change_plate=True, tìm xe chưa có hợp đồng để trường Biển số không bị readonly.
    """
    if can_change_plate:
        # Tìm xe không có trong ChiTietHopDong
        xe_bien_so_co_hd = ChiTietHopDong.objects.values_list('xe_id', flat=True)
        xe = Xe.objects.exclude(bien_so__in=xe_bien_so_co_hd).first()
        if not xe:
            # Nếu không có, lấy đại một cái (test có thể failed hoặc phải dùng force_fill)
            xe = Xe.objects.first()
    else:
        xe = Xe.objects.first()
    return xe.bien_so if xe else "15D-555.55"

def check_error_visibility(car_page, possible_texts):
    dialog_msg = getattr(car_page, "last_dialog_message", None)
    for text in possible_texts:
        if dialog_msg and text.lower() in dialog_msg.lower():
            return True
        # Kiểm tra alert browser hoặc error message div
        if car_page.page.locator(".error-message").filter(has_text=text).count() > 0:
            return True
        if car_page.page.get_by_text(text, exact=False).count() > 0:
            return True
    return False

def force_fill_plate(car_page, value):
    selector = car_page.EDIT_PLATE_INPUT
    car_page.page.evaluate(f"document.querySelector('{selector}').value = '{value}'")
    car_page.page.evaluate(f"document.querySelector('{selector}').dispatchEvent(new Event('input', {{ bubbles: true }}))")

def open_edit_form(car_page, plate=None):
    if not plate:
        plate = get_car_for_edit()
    car_page.navigate_to_list(BASE_URL)
    car_page.page.fill(car_page.SEARCH_INPUT, plate)
    car_page.page.wait_for_selector(f"div.car-card[data-bien-so='{plate}']", timeout=5000)
    car_page.page.click(f"div.car-card[data-bien-so='{plate}'] .btn-outline-view")
    car_page.page.wait_for_selector(car_page.SAVE_BTN_EDIT, timeout=5000)

# --- EDIT CAR TEST CASES (TC-XE-U01 -> U14) ---

@pytest.mark.django_db
def test_TC_XE_U01(car_page):
    """TC-XE-U01: Chỉnh sửa thành công"""
    bien_so = get_car_for_edit(can_change_plate=True)
    open_edit_form(car_page, bien_so)
    
    # Đổi hãng xe (Yêu cầu: Loại xe, Số chỗ reset)
    other_brand = HangXe.objects.exclude(ten_hang=car_page.get_dropdown_value(car_page.BRAND_TRIGGER)).first()
    if other_brand:
        car_page.select_custom_dropdown(car_page.BRAND_TRIGGER, other_brand.ten_hang)
        car_page.page.wait_for_timeout(500)
        
        model_val = car_page.get_dropdown_value(car_page.MODEL_TRIGGER)
        assert model_val == "-- Chọn Loại Xe --", f"Expect: Loại xe reset. Actual: {model_val}"
        
        # Chọn loại xe mới
        new_model = LoaiXe.objects.filter(hang_xe=other_brand).first()
        if new_model:
            car_page.select_custom_dropdown(car_page.MODEL_TRIGGER, new_model.ten_loai)
            assert str(new_model.so_cho_ngoi) in car_page.get_seats_value(), "Expect: Số chỗ tự động cập nhật"
    
    new_price = "550000"
    car_page.page.fill(car_page.EDIT_RENT_INPUT, new_price)
    car_page.save()
    
    # Đợi thông báo thành công hoặc redirect
    car_page.page.wait_for_timeout(1000)
    success = "/xe/" in car_page.page.url or check_error_visibility(car_page, ["thành công", "Cập nhật"])
    assert success, "Expect: Cập nhật thành công. Actual: Không thấy thông báo hoặc redirect."

@pytest.mark.django_db
def test_TC_XE_U02(car_page):
    """TC-XE-U02: Chỉnh sửa biển số trùng"""
    xe_a = Xe.objects.first()
    xe_b = Xe.objects.exclude(bien_so=xe_a.bien_so).first()
    if not xe_b: pytest.skip("Cần ít nhất 2 xe")
    
    # Edit xe A thành biển số của xe B
    open_edit_form(car_page, xe_a.bien_so)
    force_fill_plate(car_page, xe_b.bien_so)
    car_page.save()
    
    assert check_error_visibility(car_page, ["tồn tại", "đã có"]), "Expect: Báo lỗi biển số đã tồn tại. Actual: Không thấy báo lỗi."

@pytest.mark.django_db
def test_TC_XE_U03(car_page):
    """TC-XE-U03: Giá thuê quá nhỏ (< 300k)"""
    open_edit_form(car_page)
    car_page.page.fill(car_page.EDIT_RENT_INPUT, "200000")
    car_page.save()
    assert check_error_visibility(car_page, ["300", "3 triệu"]), "Expect: Báo lỗi giá thuê 300k-3tr. Actual: Không thấy báo lỗi."

@pytest.mark.django_db
def test_TC_XE_U04(car_page):
    """TC-XE-U04: Bỏ trống biển số"""
    open_edit_form(car_page)
    force_fill_plate(car_page, "")
    car_page.save()
    assert check_error_visibility(car_page, ["không được để trống", "Biển số"]), "Expect: Báo lỗi để trống biển số. Actual: Không thấy báo lỗi."

@pytest.mark.django_db
def test_TC_XE_U05(car_page):
    """TC-XE-U05: Bỏ trống giá thuê"""
    open_edit_form(car_page)
    car_page.page.fill(car_page.EDIT_RENT_INPUT, "")
    car_page.save()
    assert check_error_visibility(car_page, ["không được để trống", "Giá thuê"]), "Expect: Báo lỗi để trống giá thuê. Actual: Không thấy báo lỗi."

@pytest.mark.django_db
def test_TC_XE_U06(car_page):
    """TC-XE-U06: Click hủy chỉnh sửa"""
    open_edit_form(car_page)
    car_page.page.fill(car_page.EDIT_RENT_INPUT, "999999")
    
    # Lắng nghe dialog xác nhận của browser (nếu có)
    car_page.page.once("dialog", lambda d: d.accept())
    
    car_page.page.click("button.btn-secondary:has-text('Hủy')")
    car_page.page.wait_for_timeout(1000)
    assert "/xe/" in car_page.page.url, "Expect: Quay về trang danh sách. Actual: Vẫn ở trang edit."

@pytest.mark.django_db
def test_TC_XE_U07(car_page):
    """TC-XE-U07: Chỉnh sửa hãng xe (Kiểm tra reset)"""
    xe = Xe.objects.first()
    open_edit_form(car_page, xe.bien_so)
    
    current_brand = car_page.get_dropdown_value(car_page.BRAND_TRIGGER)
    other_brand = HangXe.objects.exclude(ten_hang=current_brand).first()
    if not other_brand: pytest.skip("Cần ít nhất 2 hãng xe")
    
    car_page.select_custom_dropdown(car_page.BRAND_TRIGGER, other_brand.ten_hang)
    car_page.page.wait_for_timeout(500)
    
    assert car_page.get_dropdown_value(car_page.MODEL_TRIGGER) == "-- Chọn Loại Xe --", "Expect: Loại xe reset khi đổi hãng."
    assert car_page.get_seats_value() == "", "Expect: Số chỗ reset khi đổi hãng."
    assert other_brand.quoc_gia.ten_quoc_gia in car_page.get_origin_value(), "Expect: Xuất xứ tự động cập nhật."

@pytest.mark.django_db
def test_TC_XE_U08(car_page):
    """TC-XE-U08: Nhập giá thuê bằng chữ"""
    open_edit_form(car_page)
    car_page.page.fill(car_page.EDIT_RENT_INPUT, "abc!@#")
    val = car_page.get_field_value(car_page.EDIT_RENT_INPUT)
    # Nếu UI chặn nhập chữ ngay từ đầu
    assert not any(c.isalpha() for c in val), f"Expect: Không cho nhập chữ. Actual: '{val}'"

@pytest.mark.django_db
def test_TC_XE_U09(car_page):
    """TC-XE-U09: Giá thuê quá lớn (> 3 triệu)"""
    open_edit_form(car_page)
    car_page.page.fill(car_page.EDIT_RENT_INPUT, "4000000")
    car_page.save()
    assert check_error_visibility(car_page, ["300", "3 triệu"]), "Expect: Báo lỗi giá thuê 300k-3tr. Actual: Không thấy báo lỗi."

@pytest.mark.django_db
def test_TC_XE_U10(car_page):
    """TC-XE-U10: Sai định dạng biển số"""
    open_edit_form(car_page)
    force_fill_plate(car_page, "INVALID-PLATE")
    car_page.save()
    assert check_error_visibility(car_page, ["định dạng", "VD:"]), "Expect: Báo lỗi định dạng biển số. Actual: Không thấy báo lỗi."

@pytest.mark.django_db
def test_TC_XE_U11(car_page):
    """TC-XE-U11: Nhập khoảng trắng biển số"""
    open_edit_form(car_page)
    force_fill_plate(car_page, "   ")
    car_page.save()
    assert check_error_visibility(car_page, ["không được để trống"]), "Expect: Báo lỗi khoảng trắng biển số. Actual: Không thấy báo lỗi."

@pytest.mark.django_db
def test_TC_XE_U12(car_page):
    """TC-XE-U12: Nhập khoảng trắng giá thuê"""
    open_edit_form(car_page)
    car_page.page.fill(car_page.EDIT_RENT_INPUT, "   ")
    car_page.save()
    assert check_error_visibility(car_page, ["không được để trống"]), "Expect: Báo lỗi khoảng trắng giá thuê. Actual: Không thấy báo lỗi."

@pytest.mark.django_db
def test_TC_XE_U13(car_page):
    """TC-XE-U13: Chỉnh sửa biển số chỉ khác chữ hoa thường"""
    xe = Xe.objects.first()
    open_edit_form(car_page, xe.bien_so)
    
    # Thử đổi biển số hiện tại sang chữ thường (nếu hệ thống tự in hoa thì sẽ quay lại chính nó)
    force_fill_plate(car_page, xe.bien_so.lower())
    car_page.save()
    
    # Nếu hệ thống cho phép "sửa thành chính mình" thì sẽ PASSED hoặc báo trùng
    car_page.page.wait_for_timeout(1000)
    success = "/xe/" in car_page.page.url or check_error_visibility(car_page, ["thành công", "tồn tại", "trùng"])
    assert success, "Expect: Xử lý được trường hợp hoa thường. Actual: Lỗi không xác định."

@pytest.mark.django_db
def test_TC_XE_U14(car_page):
    """TC-XE-U14: Chỉnh sửa trạng thái xe"""
    open_edit_form(car_page)
    
    current_status = car_page.get_dropdown_value(car_page.STATUS_TRIGGER)
    other_status = "Bảo trì" if current_status != "Bảo trì" else "Sẵn sàng"
    
    car_page.select_custom_dropdown(car_page.STATUS_TRIGGER, other_status)
    car_page.save()
    
    car_page.page.wait_for_timeout(1000)
    assert "/xe/" in car_page.page.url or check_error_visibility(car_page, ["thành công"]), "Expect: Cập nhật trạng thái thành công."

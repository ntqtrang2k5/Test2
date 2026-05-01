import pytest
import random
from tests.pages.car_page import CarPage
from cars.models import Xe
from rentals.models import ChiTietHopDong, HopDong
from django.db.models import Q

@pytest.fixture
def car_page(logged_in_page):
    page_obj = CarPage(logged_in_page)
    # Setup global dialog handler to capture alert messages
    page_obj.last_dialog_message = None

    def handle_dialog(dialog):
        page_obj.last_dialog_message = dialog.message
        dialog.accept() # Chấp nhận để đóng alert

    page_obj.page.on("dialog", handle_dialog)
    page_obj.navigate_to_list("http://127.0.0.1:8000")
    return page_obj

def get_car_by_condition(condition):
    """Tìm xe phù hợp với điều kiện test từ database"""
    if condition == 'available_no_contract':
        # Xe Sẵn sàng và KHÔNG có bất kỳ hợp đồng nào
        xe = Xe.objects.filter(trang_thai='Sẵn sàng').exclude(chitiethopdong__isnull=False).first()
        if not xe:
            # Tạo mới nếu không có
            xe = Xe.objects.create(
                bien_so=f"TEST-{random.randint(1000, 9999)}",
                loai_xe_id='LX_CAM', mau_sac_id='MS_TRANG', kieu_xe_id='KX_SEDAN',
                nam_san_xuat=2023, gia_thue_ngay=1000000, trang_thai='Sẵn sàng'
            )
        return xe.bien_so

    elif condition == 'active_contract':
        # Xe đang có hợp đồng hiệu lực (Đặt trước hoặc Đang thuê)
        ct = ChiTietHopDong.objects.filter(hop_dong__trang_thai__in=['Đặt trước', 'Đang thuê']).first()
        return ct.xe.bien_so if ct else None

    elif condition == 'maintenance_no_contract':
        # Xe trạng thái Bảo trì
        xe = Xe.objects.filter(trang_thai='Bảo trì').first()
        if not xe:
            xe = Xe.objects.create(
                bien_so=f"BT-{random.randint(1000, 9999)}",
                loai_xe_id='LX_CAM', mau_sac_id='MS_TRANG', kieu_xe_id='KX_SEDAN',
                nam_san_xuat=2023, gia_thue_ngay=1000000, trang_thai='Bảo trì'
            )
        return xe.bien_so

    elif condition == 'renting_status':
        # Xe có trạng thái Đang thuê
        xe = Xe.objects.filter(trang_thai='Đang thuê').first()
        return xe.bien_so if xe else None

    elif condition == 'finished_contract_only':
        # Xe chỉ có hợp đồng đã hoàn thành, không có HĐ hiệu lực
        xe_with_finished = ChiTietHopDong.objects.filter(hop_dong__trang_thai='Đã hoàn thành').values_list('xe_id', flat=True)
        xe_with_active = ChiTietHopDong.objects.filter(hop_dong__trang_thai__in=['Đặt trước', 'Đang thuê']).values_list('xe_id', flat=True)
        xe_id = Xe.objects.filter(bien_so__in=xe_with_finished).exclude(bien_so__in=xe_with_active).first()
        return xe_id.bien_so if xe_id else None

    return None

# ==============================================================================
# FUNCTIONAL TESTS (TC-XE-D01 -> D07)
# ==============================================================================

@pytest.mark.django_db
def test_TC_XE_D01(car_page):
    """TC-XE-D01: Xóa xe thành công (Sẵn sàng, không hợp đồng)"""
    bien_so = get_car_by_condition('available_no_contract')
    
    car_page.page.reload()
    car_page.page.fill(car_page.SEARCH_INPUT, bien_so)
    car_page.page.wait_for_timeout(1000)
    
    car_page.click_delete_on_car(bien_so)
    car_page.confirm_delete()
    car_page.page.wait_for_timeout(2000)
    
    # Kiểm tra không còn trong danh sách
    car_page.page.fill(car_page.SEARCH_INPUT, bien_so)
    car_page.page.wait_for_timeout(1000)
    count = car_page.page.locator(f"div.car-card[data-bien-so='{bien_so}']").count()
    assert count == 0, f"Expect: Xe {bien_so} bị xóa khỏi danh sách. Actual: Xe vẫn còn tồn tại (count={count})"

@pytest.mark.django_db
def test_TC_XE_D02(car_page):
    """TC-XE-D02: Xe có hợp đồng đang hiệu lực -> Không cho xóa"""
    bien_so = get_car_by_condition('active_contract')
    if not bien_so: pytest.skip("Không có xe nào đang có hợp đồng hiệu lực")
    
    car_page.page.fill(car_page.SEARCH_INPUT, bien_so)
    car_page.page.wait_for_timeout(1000)
    
    car_page.click_delete_on_car(bien_so)
    car_page.confirm_delete()
    car_page.page.wait_for_timeout(1500)
    
    # Kiểm tra xe vẫn tồn tại
    is_visible = car_page.page.locator(f"div.car-card[data-bien-so='{bien_so}']").is_visible()
    assert is_visible, f"Expect: Hệ thống KHÔNG cho xóa xe {bien_so} đang có hợp đồng. Actual: Xe đã bị biến mất khỏi UI."
    
    if car_page.last_dialog_message:
        assert "th" in car_page.last_dialog_message.lower(), f"Expect: Thông báo lỗi 'Không thể xóa'. Actual: '{car_page.last_dialog_message}'"

@pytest.mark.django_db
def test_TC_XE_D03(car_page):
    """TC-XE-D03: Click hủy xóa -> Dữ liệu giữ nguyên"""
    card = car_page.page.locator(".car-card").first
    bien_so = card.get_attribute("data-bien-so")
    
    car_page.click_delete_on_car(bien_so)
    car_page.cancel_delete()
    
    is_visible = car_page.page.locator(f"div.car-card[data-bien-so='{bien_so}']").is_visible()
    assert is_visible, f"Expect: Xe {bien_so} vẫn còn sau khi nhấn Hủy. Actual: Xe đã bị xóa."

@pytest.mark.django_db
def test_TC_XE_D04(car_page):
    """TC-XE-D04: Xe đang trạng thái bảo trì -> Xóa thành công (Yêu cầu USER)"""
    bien_so = get_car_by_condition('maintenance_no_contract')
    
    car_page.page.reload()
    car_page.page.fill(car_page.SEARCH_INPUT, bien_so)
    car_page.page.wait_for_selector(f"div.car-card[data-bien-so='{bien_so}']", timeout=10000)
    
    car_page.click_delete_on_car(bien_so)
    car_page.confirm_delete()
    car_page.page.wait_for_timeout(2000)
    
    count = car_page.page.locator(f"div.car-card[data-bien-so='{bien_so}']").count()
    assert count == 0, f"Expect: Xe bảo trì {bien_so} bị xóa thành công. Actual: Hệ thống chặn xóa (xe vẫn còn)."

@pytest.mark.django_db
def test_TC_XE_D05(car_page):
    """TC-XE-D05: Xe đang trạng thái đang thuê -> Không cho xóa"""
    bien_so = get_car_by_condition('renting_status')
    if not bien_so: pytest.skip("Không có xe nào ở trạng thái Đang thuê")
    
    car_page.page.fill(car_page.SEARCH_INPUT, bien_so)
    car_page.page.wait_for_timeout(1000)
    
    car_page.click_delete_on_car(bien_so)
    car_page.confirm_delete()
    car_page.page.wait_for_timeout(1500)
    
    is_visible = car_page.page.locator(f"div.car-card[data-bien-so='{bien_so}']").is_visible()
    assert is_visible, f"Expect: Xe đang thuê {bien_so} không bị xóa. Actual: Xe đã bị xóa."

@pytest.mark.django_db
def test_TC_XE_D06(car_page):
    """TC-XE-D06: Xóa xe sau khi hợp đồng kết thúc -> Xóa thành công"""
    bien_so = get_car_by_condition('finished_contract_only')
    if not bien_so: pytest.skip("Không có xe nào chỉ có hợp đồng đã hoàn thành")
    
    car_page.page.fill(car_page.SEARCH_INPUT, bien_so)
    car_page.page.wait_for_timeout(1000)
    
    car_page.click_delete_on_car(bien_so)
    car_page.confirm_delete()
    car_page.page.wait_for_timeout(2000)
    
    count = car_page.page.locator(f"div.car-card[data-bien-so='{bien_so}']").count()
    assert count == 0, f"Expect: Xe {bien_so} (HĐ đã hết) bị xóa thành công. Actual: Hệ thống chặn xóa (xe vẫn còn)."

@pytest.mark.django_db
def test_TC_XE_D07(car_page):
    """TC-XE-D07: Confirm popup hiển thị khi click xóa"""
    car_page.page.locator(".btn-action-delete").first.click()
    is_modal = car_page.is_modal_visible()
    assert is_modal, "Expect: Popup xác nhận xuất hiện. Actual: Không thấy Popup nào hiện ra."
    car_page.cancel_delete()

import pytest
import time
import random
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect
from customers.models import KhachHang
from cars.models import Xe
from rentals.models import HopDong

# Địa chỉ web của bạn
BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.django_db
class TestRentalContract:

    def setup_method(self):
        self.now = datetime.now()
        self.tomorrow = self.now + timedelta(days=1)
        self.next_week = self.now + timedelta(days=7)

    def format_dt(self, dt):
        return dt.strftime("%d/%m/%Y %H:%M")

    def test_HD_C01_form_defaults(self, logged_in_page: Page):
        """TC-HD-C01: Kiểm tra giá trị mặc định của form tạo hợp đồng"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/hop-dong/tao-moi/", wait_until="networkidle")
        input_ngay_lap = page.locator(".form-card.card-red input[disabled]")
        expect(input_ngay_lap).to_be_disabled()
        val = input_ngay_lap.get_attribute("value")
        assert str(self.now.year) in val
        expect(page.locator("#customer-search-input")).to_have_value("")
        expect(page.locator("#car-search-input-create")).to_have_value("")
        time.sleep(3)

    def test_HD_C03_create_rent_now(self, logged_in_page: Page):
        """TC-HD-C03: Thêm mới hợp đồng Thuê ngay (Ngày bắt đầu mặc định)"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/hop-dong/tao-moi/")
        
        # 1. Kiểm tra ngày bắt đầu bị khóa (Readonly)
        expect(page.locator("#new-contract-start")).to_have_attribute("readonly", "readonly")
        
        # 2. Chọn ngày kết thúc (Click lịch chọn ngày 28)
        page.click("#new-contract-end")
        page.wait_for_selector(".flatpickr-calendar.open", state="visible")
        page.locator(".flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)").filter(has_text="28").first.click()
        time.sleep(1)
        
        # 3. Chọn khách hàng
        cust = random.choice(KhachHang.objects.all())
        page.fill("#customer-search-input", cust.ho_ten)
        page.wait_for_selector("#customer-dropdown .search-item")
        page.click(f"#customer-dropdown .search-item:has-text('{cust.ho_ten}')")
        time.sleep(1)
        
        # 4. Tìm xe thực sự rảnh
        from rentals.models import ChiTietHopDong
        from django.db.models import Q
        busy_car_ids = ChiTietHopDong.objects.filter(
            Q(hop_dong__ngay_bat_dau__lt=self.next_week) & 
            Q(hop_dong__ngay_ket_thuc_du_kien__gt=self.now)
        ).values_list('xe_id', flat=True)
        car = Xe.objects.filter(trang_thai="Sẵn sàng").exclude(bien_so__in=busy_car_ids).first()
        if not car: pytest.skip("Không có xe rảnh để test Thuê ngay")
        
        page.fill("#car-search-input-create", car.bien_so)
        page.wait_for_selector("#car-dropdown .search-item")
        page.click(f"#car-dropdown .search-item:has-text('{car.bien_so}')")
        time.sleep(1)
        
        # 5. Bấm "THUÊ NGAY"
        def handle_dialog(dialog):
            print(f"Demo: {dialog.message}")
            time.sleep(2)
            dialog.accept()
        page.on("dialog", handle_dialog)
        
        page.click("button:has-text('THUÊ NGAY')")
        page.wait_for_url("**/hop-dong/")
        expect(page.locator("body")).to_contain_text("Đang thuê")
        time.sleep(3)

    def test_HD_C04_search_customer(self, logged_in_page: Page):
        """TC-HD-C04: Tìm kiếm khách hàng theo từ khóa"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/hop-dong/tao-moi/")
        
        cust = random.choice(KhachHang.objects.all())
        keyword = cust.ho_ten[:3] # Lấy 3 chữ đầu
        
        page.fill("#customer-search-input", keyword)
        page.wait_for_selector("#customer-dropdown .search-item")
        time.sleep(1)
        
        # Kiểm tra gợi ý hiện đúng tên
        expect(page.locator("#customer-dropdown")).to_contain_text(cust.ho_ten)
        page.click(f"#customer-dropdown .search-item:has-text('{cust.ho_ten}')")
        
        # Kiểm tra tự điền thông tin
        expect(page.locator("#new-contract-name")).to_have_value(cust.ho_ten)
        expect(page.locator("#new-contract-phone")).to_have_value(cust.so_dien_thoai)
        time.sleep(2)

    def test_HD_C05_C06_C19_date_logic(self, logged_in_page: Page):
        """TC-HD-C05, C06, C19: Kiểm tra logic thời gian thuê"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/hop-dong/tao-moi/")
        # C19: Chặn chọn xe khi chưa chọn ngày
        expect(page.locator("#car-search-input-create")).to_be_disabled # Note: if handled via JS alert, we check that
        
        # 1. Chọn thời gian
        val_start = self.format_dt(self.tomorrow)
        page.locator("#new-contract-start").evaluate(f"el => el.value = '{val_start}'")
        page.keyboard.press("Enter")
        
        val_end = self.format_dt(self.next_week)
        page.locator("#new-contract-end").evaluate(f"el => el.value = '{val_end}'")
        page.keyboard.press("Enter")
        expect(page.locator("#contract-duration-text")).not_to_have_text("0 ngày")

    def get_available_car(self, start, end):
        """Tìm một xe thực sự rảnh trong khoảng thời gian [start, end]"""
        from rentals.models import ChiTietHopDong
        from django.db.models import Q
        busy_car_ids = ChiTietHopDong.objects.filter(
            Q(hop_dong__ngay_bat_dau__lt=end) & 
            Q(hop_dong__ngay_ket_thuc_du_kien__gt=start)
        ).values_list('xe_id', flat=True)
        return Xe.objects.filter(trang_thai="Sẵn sàng").exclude(bien_so__in=busy_car_ids).first()

    def test_HD_C03_create_rent_now(self, logged_in_page: Page):
        """TC-HD-C03: Thêm mới hợp đồng Thuê ngay (Chọn ngày thực tế)"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/hop-dong/tao-moi/")
        
        # 1. Chọn ngày bắt đầu (Click chọn ngày 21 - Giả sử là hôm nay)
        page.click("#new-contract-start")
        page.wait_for_selector(".flatpickr-calendar.open", state="visible")
        page.locator(".flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)").filter(has_text="21").first.click()
        time.sleep(1)
        
        # 2. Chọn ngày kết thúc (Click chọn ngày 24)
        page.click("#new-contract-end")
        page.wait_for_selector(".flatpickr-calendar.open", state="visible")
        page.locator(".flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)").filter(has_text="24").first.click()
        time.sleep(1)
        
        # 3. Chọn khách hàng
        cust = random.choice(KhachHang.objects.all())
        page.fill("#customer-search-input", cust.ho_ten)
        page.wait_for_selector("#customer-dropdown .search-item")
        page.click(f"#customer-dropdown .search-item:has-text('{cust.ho_ten}')")
        
        # 4. Tìm xe rảnh (Sử dụng helper)
        car = self.get_available_car(datetime(2026, 4, 21), datetime(2026, 4, 24))
        if not car: pytest.skip("Không có xe rảnh trong khung giờ này")
        
        page.fill("#car-search-input-create", car.bien_so)
        page.wait_for_selector("#car-dropdown .search-item")
        page.click(f"#car-dropdown .search-item:has-text('{car.bien_so}')")
        time.sleep(1)
        
        # 5. Bấm "THUÊ NGAY"
        page.on("dialog", lambda d: d.accept())
        page.click("button:has-text('THUÊ NGAY')")
        page.wait_for_url("**/hop-dong/")
        expect(page.locator("body")).to_contain_text("Đang thuê")
        time.sleep(3)

    def test_HD_C02_create_preorder(self, logged_in_page: Page):
        """TC-HD-C02: Thêm mới hợp đồng đặt trước (Visual Demo)"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/hop-dong/tao-moi/")
        
        # 1. Chọn ngày bắt đầu (25)
        page.click("#new-contract-start")
        page.wait_for_selector(".flatpickr-calendar.open", state="visible")
        page.locator(".flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)").filter(has_text="25").first.click()
        time.sleep(1)
        
        # 2. Chọn ngày kết thúc (28)
        page.click("#new-contract-end")
        page.wait_for_selector(".flatpickr-calendar.open", state="visible")
        page.locator(".flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)").filter(has_text="28").first.click()
        time.sleep(1)
        
        # 3. Chọn khách hàng
        cust = random.choice(KhachHang.objects.all())
        page.fill("#customer-search-input", cust.ho_ten)
        page.wait_for_selector("#customer-dropdown .search-item")
        page.click(f"#customer-dropdown .search-item:has-text('{cust.ho_ten}')")
        
        # 4. Tìm xe rảnh
        car = self.get_available_car(datetime(2026, 4, 25), datetime(2026, 4, 28))
        if not car: pytest.skip("Không có xe rảnh")
        
        page.fill("#car-search-input-create", car.bien_so)
        page.wait_for_selector("#car-dropdown .search-item")
        page.click(f"#car-dropdown .search-item:has-text('{car.bien_so}')")
        time.sleep(1)
        
        # 5. Bấm "ĐẶT TRƯỚC"
        page.on("dialog", lambda d: [print(f"Alert: {d.message}"), time.sleep(2), d.accept()])
        page.click("button:has-text('ĐẶT TRƯỚC')")
        
        page.wait_for_url("**/hop-dong/")
        expect(page.locator("body")).to_contain_text("Đặt trước")
        time.sleep(3)

    def test_HD_C09_C10_multi_car(self, logged_in_page: Page):
        """TC-HD-C09 & C10: Chọn nhiều xe và Xóa xe khỏi danh sách"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/hop-dong/tao-moi/")
        
        # 1. Chọn ngày
        page.click("#new-contract-start")
        page.locator(".flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)").filter(has_text="25").first.click()
        time.sleep(0.5)
        page.click("#new-contract-end")
        page.locator(".flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)").filter(has_text="28").first.click()
        time.sleep(1)
        
        # Tìm 2 xe rảnh
        from rentals.models import ChiTietHopDong
        from django.db.models import Q
        busy_car_ids = ChiTietHopDong.objects.filter(
            Q(hop_dong__ngay_bat_dau__lt=datetime(2026, 4, 28)) & 
            Q(hop_dong__ngay_ket_thuc_du_kien__gt=datetime(2026, 4, 25))
        ).values_list('xe_id', flat=True)
        cars = list(Xe.objects.filter(trang_thai="Sẵn sàng").exclude(bien_so__in=busy_car_ids)[:2])
        if len(cars) < 2: pytest.skip("Không đủ xe rảnh để test chọn nhiều xe")
        
        # 2. Chọn xe 1
        page.fill("#car-search-input-create", cars[0].bien_so)
        page.wait_for_selector("#car-dropdown .search-item")
        page.click(f"#car-dropdown .search-item:has-text('{cars[0].bien_so}')")
        time.sleep(1)
        
        # 3. Chọn xe 2
        page.fill("#car-search-input-create", cars[1].bien_so)
        page.wait_for_selector("#car-dropdown .search-item")
        page.click(f"#car-dropdown .search-item:has-text('{cars[1].bien_so}')")
        time.sleep(1)
        
        # Kiểm tra bảng có 2 xe
        expect(page.locator("#selected-cars-list-body tr:not(#empty-car-row)")).to_have_count(2)
        
        # 4. Xóa bớt 1 xe (Click vào icon rác)
        page.locator("#selected-cars-list-body tr:not(#empty-car-row)").first.locator(".fa-trash").click()
        time.sleep(2)
        
        # Kiểm tra lại bảng còn 1 xe
        expect(page.locator("#selected-cars-list-body tr:not(#empty-car-row)")).to_have_count(1)
        time.sleep(2)

    def test_HD_C13_C14_C15_calculations(self, logged_in_page: Page):
        """TC-HD-C13, C14, C15: Kiểm tra logic tính tiền (Trả thêm/Trả lại/Đã đủ)"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/hop-dong/tao-moi/")
        
        # Chọn 1 ngày (ví dụ 25 đến 26)
        page.click("#new-contract-start")
        page.locator(".flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)").filter(has_text="25").first.click()
        page.click("#new-contract-end")
        page.locator(".flatpickr-calendar.open .flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)").filter(has_text="26").first.click()
        
        # Chọn 1 xe rảnh
        car = Xe.objects.filter(trang_thai="Sẵn sàng").first()
        page.fill("#car-search-input-create", car.bien_so)
        page.wait_for_selector("#car-dropdown .search-item")
        page.click(f"#car-dropdown .search-item:has-text('{car.bien_so}')")
        
        price = int(car.gia_thue_ngay)
        
        # C13: Trả đủ (Tạm ứng = Giá thuê 1 ngày)
        page.fill("#new-contract-prepaid", str(price))
        time.sleep(1)
        expect(page.locator("#row-du-tien")).to_be_visible()
        
        # C14: Trả thiếu (Tạm ứng < Giá thuê)
        page.fill("#new-contract-prepaid", str(price - 100000))
        time.sleep(1)
        expect(page.locator("#row-tra-them")).to_be_visible()
        
        # C15: Trả dư (Tạm ứng > Giá thuê)
        page.fill("#new-contract-prepaid", str(price + 100000))
        time.sleep(1)
        expect(page.locator("#row-tra-lai")).to_be_visible()
        time.sleep(2)

    def test_HD_C20_C21_mandatory_fields(self, logged_in_page: Page):
        """TC-HD-C20, C21: Bỏ trống thông tin bắt buộc"""
        page = logged_in_page
        page.goto(f"{BASE_URL}/hop-dong/tao-moi/")
        
        # C21: Thiếu xe
        page.fill("#new-contract-start", self.format_dt(self.tomorrow))
        page.fill("#new-contract-end", self.format_dt(self.next_week))
        page.fill("#new-contract-name", "Test No Car")
        
        page.on("dialog", lambda d: d.accept())
        page.click("button:has-text('LƯU HỢP ĐỒNG')")
        # Should stay on page due to validation alert
        expect(page).to_have_url("**/hop-dong/tao-moi/")

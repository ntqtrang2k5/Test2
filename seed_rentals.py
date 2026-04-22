import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carrent.settings')
django.setup()

from rentals.models import HopDong, ChiTietHopDong, GiaoDich, PhieuTraXe
from customers.models import KhachHang
from cars.models import Xe, LichSuBaoTri

def seed_data():
    customers = list(KhachHang.objects.all())
    cars = list(Xe.objects.all())
    
    if not customers or not cars:
        print("Error: Need at least one customer and one car to seed.")
        return

    # 1. WIPE ALL EXISTING RENTAL DATA
    print("Clearing existing rentals, transactions, and maintenance logs...")
    GiaoDich.objects.all().delete()
    PhieuTraXe.objects.all().delete()
    ChiTietHopDong.objects.all().delete()
    LichSuBaoTri.objects.all().delete()
    HopDong.objects.all().delete()
    
    today = timezone.now().date()
    
    # Track occupied dates per car to avoid overlaps
    car_occupations = {car.bien_so: [] for car in cars}

    def check_availability(car_plate, start, end):
        # Allow 0-day buffer or same-day return/pickup? 
        # Usually end > start is enough. 
        # We need start < existing_end and end > existing_start to overlap.
        for s, e in car_occupations[car_plate]:
            if start < e and end > s:
                return False
        return True

    def block_range(car_plate, start, end):
        car_occupations[car_plate].append((start, end))

    # 2. Seed Maintenance Logs (to show expenses)
    print("Seeding smart maintenance logs...")
    for car in random.sample(cars, 4):
        # Maintenance usually takes 1-2 days
        for _ in range(5): # try 5 times to find a slot
            m_start = today - timedelta(days=random.randint(5, 45))
            m_end = m_start + timedelta(days=1)
            if check_availability(car.bien_so, m_start, m_end):
                LichSuBaoTri.objects.create(
                    xe=car,
                    ngay_bao_tri=m_start,
                    ngay_ket_thuc=m_end,
                    loai_bao_tri=random.choice(['Bảo dưỡng định kỳ', 'Thay dầu', 'Kiểm tra lốp']),
                    noi_dung_chi_tiet="Bảo trì định kỳ hệ thống.",
                    chi_phi=random.randint(5, 10) * 100000
                )
                block_range(car.bien_so, m_start, m_end)
                break

    # 3. Generating Contracts
    print("Generating SMART synchronized contracts (No Overlaps)...")
    
    current_id_num = 1
    contracts_created = 0
    target_contracts = 28 # Reached for high variety

    # Shuffle cars to distribute load
    random.shuffle(cars)

    attempts = 0
    while contracts_created < target_contracts and attempts < 200:
        attempts += 1
        ma_hd = f"HD{current_id_num:03d}"
        customer = random.choice(customers)
        
        # Decide status and corresponding dates
        status_choice = random.choices(['Đã hoàn thành', 'Đang thuê', 'Đặt trước'], weights=[50, 30, 20])[0]
        
        if status_choice == 'Đã hoàn thành':
            days_offset = random.randint(-45, -8)
        elif status_choice == 'Đang thuê':
            days_offset = random.randint(-5, 0)
        else:
            days_offset = random.randint(1, 10)

        start_date = today + timedelta(days=days_offset)
        duration = random.randint(2, 6)
        end_date = start_date + timedelta(days=duration)
        
        # Pick 1-2 cars that are FREE in this range
        available_cars = [c for c in cars if check_availability(c.bien_so, start_date, end_date)]
        
        if not available_cars:
            continue # Try again with different dates
            
        num_cars = 1 if (random.random() > 0.15 or len(available_cars) < 2) else 2
        selected_cars = random.sample(available_cars, num_cars)

        # Calculate Price
        daily_rate_total = sum(c.gia_thue_ngay for c in selected_cars)
        total_price = daily_rate_total * duration
        
        # Financial logic
        if status_choice == 'Đã hoàn thành':
            prepaid = total_price // 2
        else:
            prepaid = int(total_price * random.choice([0.3, 0.5, 1.0]))
        
        prepaid = (prepaid // 10000) * 10000 # round to 10k

        contract = HopDong.objects.create(
            ma_hd=ma_hd,
            khach_hang=customer,
            ngay_lap=start_date - timedelta(days=1),
            ngay_bat_dau=start_date,
            ngay_ket_thuc_du_kien=end_date,
            tien_tra_truoc=prepaid,
            tong_tien_thue=total_price,
            trang_thai=status_choice
        )
        
        for car in selected_cars:
            ChiTietHopDong.objects.create(hop_dong=contract, xe=car)
            block_range(car.bien_so, start_date, end_date)
            
            # Sync car status to current DB state
            if status_choice == 'Đang thuê':
                car.trang_thai = 'Đang thuê'
                car.save()

        # Create GiaoDich
        if prepaid > 0:
            GiaoDich.objects.create(
                hop_dong=contract,
                so_tien=prepaid,
                loai_gd='Tạm ứng',
                ngay_gd=start_date
            )

        if status_choice == 'Đã hoàn thành':
            remainder = total_price - prepaid
            if remainder > 0:
                GiaoDich.objects.create(
                    hop_dong=contract,
                    so_tien=remainder,
                    loai_gd='Quyết toán',
                    ngay_gd=end_date
                )
            
            # Create PhieuTraXe
            last_tx = PhieuTraXe.objects.order_by('-ma_tra_xe').first()
            ma_tx = f"TX{int(last_tx.ma_tra_xe[2:]) + 1:03d}" if last_tx else "TX001"
            
            PhieuTraXe.objects.create(
                ma_tra_xe=ma_tx,
                hop_dong=contract,
                ngay_tra_thuc_te=end_date,
                phat_qua_han=0,
                phu_phi_khac=0,
                tien_tra_lai_khach=0,
                khach_tra_them=remainder,
            )
            contract.ngay_ket_thuc_thuc_te = end_date
            contract.save()

        current_id_num += 1
        contracts_created += 1

    print(f"Successfully created {contracts_created} SMART contracts.")
    print("NO OVERLAPS between rentals or maintenance logs.")

if __name__ == '__main__':
    seed_data()

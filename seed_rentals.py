import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carrent.settings')
django.setup()

from rentals.models import HopDong, ChiTietHopDong
from customers.models import KhachHang
from cars.models import Xe

def seed_data():
    customers = list(KhachHang.objects.all())
    cars = list(Xe.objects.all())
    
    if not customers or not cars:
        print("Error: Need at least one customer and one car to seed.")
        return

    # WIPE ALL EXISTING CONTRACTS FIRST AS REQUESTED
    print("Clearing existing contracts...")
    ChiTietHopDong.objects.all().delete()
    HopDong.objects.all().delete()
    
    statuses = ['Đã hoàn thành', 'Đang thuê', 'Chờ nhận xe', 'Quá hạn']
    
    # Start fresh from HD001
    current_id_num = 1

    contracts_created = 0
    
    # 1. Ensure every customer has at least 1 contract
    for customer in customers:
        ma_hd = f"HD{current_id_num:03d}"
        
        # Random dates
        days_ago = random.randint(1, 30)
        start_date = timezone.now() - timedelta(days=days_ago)
        duration = random.randint(1, 5)
        end_date = start_date + timedelta(days=duration)
        
        # Decide status based on dates
        if end_date < timezone.now():
            status = random.choice(['Đã hoàn thành', 'Quá hạn'])
        else:
            status = random.choice(['Đang thuê', 'Chờ nhận xe'])
            
        contract = HopDong.objects.create(
            ma_hd=ma_hd,
            khach_hang=customer,
            ngay_lap=start_date - timedelta(hours=2),
            ngay_bat_dau=start_date,
            ngay_ket_thuc_du_kien=end_date,
            tien_coc=random.randint(5, 20) * 100000,
            tien_tra_truoc=random.randint(0, 5) * 100000,
            tong_tien_thue=random.randint(10, 50) * 100000,
            trang_thai=status
        )
        
        # Add 1-2 random cars
        num_cars = random.randint(1, 2)
        selected_cars = random.sample(cars, num_cars)
        for car in selected_cars:
            ChiTietHopDong.objects.create(hop_dong=contract, xe=car)
            
        current_id_num += 1
        contracts_created += 1

    # 2. Add more to reach 20+
    target = 22
    while contracts_created < target:
        customer = random.choice(customers)
        ma_hd = f"HD{current_id_num:03d}"
        
        days_ago = random.randint(1, 45)
        start_date = timezone.now() - timedelta(days=days_ago)
        duration = random.randint(1, 7)
        end_date = start_date + timedelta(days=duration)
        
        if end_date < timezone.now():
            status = 'Đã hoàn thành'
        else:
            status = 'Đang thuê'

        contract = HopDong.objects.create(
            ma_hd=ma_hd,
            khach_hang=customer,
            ngay_lap=start_date - timedelta(hours=1),
            ngay_bat_dau=start_date,
            ngay_ket_thuc_du_kien=end_date,
            tien_coc=random.randint(10, 30) * 100000,
            tien_tra_truoc=random.randint(5, 10) * 100000,
            tong_tien_thue=random.randint(20, 80) * 100000,
            trang_thai=status
        )
        
        selected_car = random.choice(cars)
        ChiTietHopDong.objects.create(hop_dong=contract, xe=selected_car)
        
        current_id_num += 1
        contracts_created += 1

    print(f"Successfully created {contracts_created} contracts starting from HD{current_id_num - contracts_created:03d}")

if __name__ == '__main__':
    seed_data()

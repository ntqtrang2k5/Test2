import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carrent.settings')
django.setup()

from customers.models import KhachHang

def seed():
    # Xoá data cũ nếu có để tránh lỗi trùng lặp khi chạy lại
    KhachHang.objects.all().delete()
    
    customers_data = [
        ("KH001", "Nguyễn Văn An", "0901234567", "079090123451"),
        ("KH002", "Trần Thị Bích", "0912345678", "079090123452"),
        ("KH003", "Lena Lalina", "0923456789", "079090123453"), # Lena Lalina ở đây
        ("KH004", "Lê Văn Cường", "0934567890", "079090123454"),
        ("KH005", "Phạm Thị Dung", "0945678901", "079090123455"),
        ("KH006", "Hoàng Văn E", "0956789012", "079090123456"),
        ("KH007", "Phan Thị F", "0967890123", "079090123457"),
        ("KH008", "Vũ Văn G", "0978901234", "079090123458"),
        ("KH009", "Đặng Thị H", "0989012345", "079090123459"),
        ("KH010", "Bùi Văn Khang", "0990123456", "079090123460"),
    ]

    for data in customers_data:
        KhachHang.objects.create(
            ma_kh=data[0],
            ho_ten=data[1],
            so_dien_thoai=data[2],
            cccd=data[3]
        )
    print("Seeded 10 customers successfully!")

if __name__ == "__main__":
    seed()

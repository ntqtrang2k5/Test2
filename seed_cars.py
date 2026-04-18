import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carrent.settings')
django.setup()

from cars.models import QuocGia, KieuXe, MauSac, HangXe, LoaiXe, Xe

def seed_cars():
    print("Xóa dữ liệu danh mục xe cũ...")
    Xe.objects.all().delete()
    LoaiXe.objects.all().delete()
    HangXe.objects.all().delete()
    MauSac.objects.all().delete()
    KieuXe.objects.all().delete()
    QuocGia.objects.all().delete()

    print("Bơm danh sách Quốc Gia...")
    qg1 = QuocGia.objects.create(ma_quoc_gia="QG_VN", ten_quoc_gia="Việt Nam")
    qg2 = QuocGia.objects.create(ma_quoc_gia="QG_JP", ten_quoc_gia="Nhật Bản")
    qg3 = QuocGia.objects.create(ma_quoc_gia="QG_KR", ten_quoc_gia="Hàn Quốc")
    qg4 = QuocGia.objects.create(ma_quoc_gia="QG_US", ten_quoc_gia="Mỹ")
    qg5 = QuocGia.objects.create(ma_quoc_gia="QG_DE", ten_quoc_gia="Đức")

    print("Bơm danh sách Kiểu Xe...")
    kx1 = KieuXe.objects.create(ma_kieu="KX_SEDAN", ten_kieu="Sedan")
    kx2 = KieuXe.objects.create(ma_kieu="KX_SUV", ten_kieu="SUV")
    kx3 = KieuXe.objects.create(ma_kieu="KX_MPV", ten_kieu="MPV")
    kx4 = KieuXe.objects.create(ma_kieu="KX_HATCH", ten_kieu="Hatchback")
    kx5 = KieuXe.objects.create(ma_kieu="KX_PICK", ten_kieu="Bán tải")

    print("Bơm danh sách Màu Sắc...")
    ms1 = MauSac.objects.create(ma_mau="MS_TRANG", ten_mau="Trắng")
    ms2 = MauSac.objects.create(ma_mau="MS_DEN", ten_mau="Đen")
    ms3 = MauSac.objects.create(ma_mau="MS_DO", ten_mau="Đỏ")
    ms4 = MauSac.objects.create(ma_mau="MS_XANH", ten_mau="Xanh Dương")
    ms5 = MauSac.objects.create(ma_mau="MS_XAM", ten_mau="Xám")
    ms6 = MauSac.objects.create(ma_mau="MS_BAC", ten_mau="Bạc")

    print("Bơm danh sách Hãng Xe...")
    hx1 = HangXe.objects.create(ma_hang="HX_TOY", ten_hang="Toyota", quoc_gia=qg2)
    hx2 = HangXe.objects.create(ma_hang="HX_HON", ten_hang="Honda", quoc_gia=qg2)
    hx3 = HangXe.objects.create(ma_hang="HX_MAZ", ten_hang="Mazda", quoc_gia=qg2)
    hx4 = HangXe.objects.create(ma_hang="HX_HYU", ten_hang="Hyundai", quoc_gia=qg3)
    hx5 = HangXe.objects.create(ma_hang="HX_FOR", ten_hang="Ford", quoc_gia=qg4)
    hx6 = HangXe.objects.create(ma_hang="HX_KIA", ten_hang="Kia", quoc_gia=qg3)
    hx7 = HangXe.objects.create(ma_hang="HX_VIN", ten_hang="VinFast", quoc_gia=qg1)
    hx8 = HangXe.objects.create(ma_hang="HX_MER", ten_hang="Mercedes-Benz", quoc_gia=qg5)
    hx9 = HangXe.objects.create(ma_hang="HX_AUD", ten_hang="Audi", quoc_gia=qg5)

    print("Bơm danh sách Loại Xe...")
    lx1 = LoaiXe.objects.create(ma_loai="LX_CAM", ten_loai="Camry", hang_xe=hx1, kieu_xe=kx1, so_cho_ngoi=5)
    lx2 = LoaiXe.objects.create(ma_loai="LX_VIO", ten_loai="Vios", hang_xe=hx1, kieu_xe=kx1, so_cho_ngoi=5)
    lx3 = LoaiXe.objects.create(ma_loai="LX_CRV", ten_loai="CR-V", hang_xe=hx2, kieu_xe=kx2, so_cho_ngoi=7)
    lx4 = LoaiXe.objects.create(ma_loai="LX_MZ3", ten_loai="Mazda 3", hang_xe=hx3, kieu_xe=kx1, so_cho_ngoi=5)
    lx5 = LoaiXe.objects.create(ma_loai="LX_INN", ten_loai="Innova", hang_xe=hx1, kieu_xe=kx3, so_cho_ngoi=7)
    lx6 = LoaiXe.objects.create(ma_loai="LX_SAN", ten_loai="SantaFe", hang_xe=hx4, kieu_xe=kx2, so_cho_ngoi=7)
    lx7 = LoaiXe.objects.create(ma_loai="LX_FOR", ten_loai="Fortuner", hang_xe=hx1, kieu_xe=kx2, so_cho_ngoi=7)
    lx8 = LoaiXe.objects.create(ma_loai="LX_RAN", ten_loai="Ranger", hang_xe=hx5, kieu_xe=kx5, so_cho_ngoi=5)
    lx9 = LoaiXe.objects.create(ma_loai="LX_VF8", ten_loai="VF8", hang_xe=hx7, kieu_xe=kx2, so_cho_ngoi=5)
    lx10 = LoaiXe.objects.create(ma_loai="LX_C30", ten_loai="C300 AMG", hang_xe=hx8, kieu_xe=kx1, so_cho_ngoi=5)
    lx11 = LoaiXe.objects.create(ma_loai="LX_Q50", ten_loai="Q5", hang_xe=hx9, kieu_xe=kx2, so_cho_ngoi=5)

    print("Bơm danh sách Xe...")
    Xe.objects.create(bien_so="51H-123.45", loai_xe=lx1, mau_sac=ms1, kieu_xe=kx1, nam_san_xuat=2023, gia_thue_ngay=800000, trang_thai="Sẵn sàng")
    Xe.objects.create(bien_so="51K-678.90", loai_xe=lx3, mau_sac=ms2, kieu_xe=kx2, nam_san_xuat=2022, gia_thue_ngay=1200000, trang_thai="Sẵn sàng")
    Xe.objects.create(bien_so="51G-555.22", loai_xe=lx4, mau_sac=ms3, kieu_xe=kx1, nam_san_xuat=2021, gia_thue_ngay=1500000, trang_thai="Đang thuê")
    Xe.objects.create(bien_so="53H-678.36", loai_xe=lx2, mau_sac=ms6, kieu_xe=kx1, nam_san_xuat=2023, gia_thue_ngay=700000, trang_thai="Sẵn sàng")
    Xe.objects.create(bien_so="51A-987.65", loai_xe=lx7, mau_sac=ms5, kieu_xe=kx2, nam_san_xuat=2020, gia_thue_ngay=1300000, trang_thai="Bảo trì")
    Xe.objects.create(bien_so="30A-111.11", loai_xe=lx10, mau_sac=ms2, kieu_xe=kx1, nam_san_xuat=2023, gia_thue_ngay=3500000, trang_thai="Sẵn sàng")
    Xe.objects.create(bien_so="29C-222.22", loai_xe=lx11, mau_sac=ms1, kieu_xe=kx2, nam_san_xuat=2022, gia_thue_ngay=3200000, trang_thai="Đang thuê")
    Xe.objects.create(bien_so="60B-333.33", loai_xe=lx8, mau_sac=ms4, kieu_xe=kx5, nam_san_xuat=2021, gia_thue_ngay=1000000, trang_thai="Sẵn sàng")
    Xe.objects.create(bien_so="61C-444.44", loai_xe=lx9, mau_sac=ms3, kieu_xe=kx2, nam_san_xuat=2023, gia_thue_ngay=2000000, trang_thai="Sẵn sàng")
    Xe.objects.create(bien_so="15D-555.55", loai_xe=lx5, mau_sac=ms6, kieu_xe=kx3, nam_san_xuat=2019, gia_thue_ngay=900000, trang_thai="Sẵn sàng")

    print("- HOÀN TẤT BƠM DỮ LIỆU APP CARS! [10 XE + ĐỦ DANH MỤC]")

if __name__ == "__main__":
    seed_cars()

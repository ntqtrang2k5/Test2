from django.db import models
from django.utils import timezone
from customers.models import KhachHang
from cars.models import Xe

class HopDong(models.Model):
    ma_hd = models.CharField(max_length=10, primary_key=True, verbose_name="Mã hợp đồng")
    khach_hang = models.ForeignKey(KhachHang, on_delete=models.RESTRICT, verbose_name="Khách hàng")
    ngay_lap = models.DateTimeField(default=timezone.now, verbose_name="Ngày lập hợp đồng")
    ngay_bat_dau = models.DateField(verbose_name="Ngày bắt đầu")
    ngay_ket_thuc_du_kien = models.DateField(verbose_name="Ngày kết thúc dự kiến")
    ngay_ket_thuc_thuc_te = models.DateField(null=True, blank=True, verbose_name="Ngày kết thúc thực tế")
    tong_tien_thue = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="Tổng tiền thuê")
    tien_coc = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="Tiền cọc")
    tien_tra_truoc = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="Tiền trả trước")
    trang_thai = models.CharField(max_length=50, default="Chờ nhận xe", verbose_name="Trạng thái")

    class Meta:
        db_table = 'HOPDONGTHUE'
        verbose_name = "Hợp đồng thuê"

    def __str__(self):
        return f"{self.ma_hd} - {self.khach_hang.ho_ten}"


class ChiTietHopDong(models.Model):
    hop_dong = models.ForeignKey(HopDong, on_delete=models.CASCADE, verbose_name="Hợp đồng")
    xe = models.ForeignKey(Xe, on_delete=models.RESTRICT, verbose_name="Xe")
    
    class Meta:
        db_table = 'HOPDONGTHUE_CHITIET'
        unique_together = ('hop_dong', 'xe')
        verbose_name = "Chi tiết hợp đồng"


class PhieuTraXe(models.Model):
    ma_tra_xe = models.CharField(max_length=10, primary_key=True, verbose_name="Mã trả xe")
    hop_dong = models.ForeignKey(HopDong, on_delete=models.RESTRICT, verbose_name="Hợp đồng")
    ngay_tra_thuc_te = models.DateField(auto_now_add=True, verbose_name="Ngày trả thực tế")
    phat_qua_han = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="Phạt quá hạn")
    phu_phi_khac = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="Phụ phí khác")
    tien_tra_lai_khach = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="Tiền trả lại khách")
    khach_tra_them = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="Khách trả thêm")
    ghi_chu = models.TextField(null=True, blank=True, verbose_name="Ghi chú")

    class Meta:
        db_table = 'PHIEUTRAXE'
        verbose_name = "Phiếu trả xe"


class LichSuThayDoi(models.Model):
    hop_dong = models.ForeignKey(HopDong, on_delete=models.CASCADE, verbose_name="Hợp đồng")
    ngay_thay_doi = models.DateTimeField(default=timezone.now, verbose_name="Ngày thay đổi")
    noi_dung = models.TextField(verbose_name="Nội dung thay đổi")
    tien_chenh_lech = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="Tiền chênh lệch")

    class Meta:
        db_table = 'HOPDONGTHUE_LICHSU'
        verbose_name = "Lịch sử thay đổi hợp đồng"


class GiaoDich(models.Model):
    LOAI_GIAO_DICH = (
        ('Tạm ứng', 'Tạm ứng'),
        ('Thu thêm', 'Thu thêm'),
        ('Hoàn trả', 'Hoàn trả'),
        ('Quyết toán', 'Quyết toán'),
    )
    hop_dong = models.ForeignKey(HopDong, on_delete=models.CASCADE, related_name='giao_dich_set', verbose_name="Hợp đồng")
    ngay_gd = models.DateField(default=timezone.now, verbose_name="Ngày giao dịch")
    so_tien = models.DecimalField(max_digits=18, decimal_places=0, verbose_name="Số tiền")
    loai_gd = models.CharField(max_length=50, choices=LOAI_GIAO_DICH, verbose_name="Loại giao dịch")

    class Meta:
        db_table = 'HOPDONGTHUE_GIAODICH'
        verbose_name = "Giao dịch tài chính"
        ordering = ['-ngay_gd']

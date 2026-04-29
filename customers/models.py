from django.db import models

class KhachHang(models.Model):
    ma_kh = models.CharField(max_length=10, primary_key=True, verbose_name="Mã khách hàng")
    ho_ten = models.CharField(max_length=100, verbose_name="Họ và tên")
    so_dien_thoai = models.CharField(max_length=15, verbose_name="Số điện thoại")
    cccd = models.CharField(max_length=20, unique=True, verbose_name="CCCD/CMND")

    def __str__(self):
        return f"{self.ma_kh} - {self.ho_ten}"

    class Meta:
        db_table = 'KHACHHANG'
        verbose_name = "Khách hàng"
        verbose_name_plural = "Danh sách khách hàng"

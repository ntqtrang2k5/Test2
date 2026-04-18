from django.db import models

class QuocGia(models.Model):
    ma_quoc_gia = models.CharField(max_length=10, primary_key=True, verbose_name="Mã quốc gia")
    ten_quoc_gia = models.CharField(max_length=100, unique=True, verbose_name="Tên quốc gia")

    class Meta:
        db_table = 'QUOCGIA'
        verbose_name = "Quốc gia"

    def __str__(self):
        return self.ten_quoc_gia


class KieuXe(models.Model):
    ma_kieu = models.CharField(max_length=10, primary_key=True, verbose_name="Mã kiểu xe")
    ten_kieu = models.CharField(max_length=100, unique=True, verbose_name="Tên kiểu xe")

    class Meta:
        db_table = 'KIEUXE'

    def __str__(self):
        return self.ten_kieu


class MauSac(models.Model):
    ma_mau = models.CharField(max_length=10, primary_key=True, verbose_name="Mã màu")
    ten_mau = models.CharField(max_length=50, unique=True, verbose_name="Tên màu")

    class Meta:
        db_table = 'MAUSAC'

    def __str__(self):
        return self.ten_mau


class HangXe(models.Model):
    ma_hang = models.CharField(max_length=10, primary_key=True, verbose_name="Mã hãng xe")
    ten_hang = models.CharField(max_length=100, unique=True, verbose_name="Tên hãng xe")
    # Rule: Không được xóa nếu đang có xe thuộc hãng này (Dùng RESTRICT)
    quoc_gia = models.ForeignKey(QuocGia, on_delete=models.RESTRICT, verbose_name="Quốc gia")

    class Meta:
        db_table = 'HANGXE'

    def __str__(self):
        return self.ten_hang


class LoaiXe(models.Model):
    ma_loai = models.CharField(max_length=10, primary_key=True, verbose_name="Mã loại xe")
    ten_loai = models.CharField(max_length=100, unique=True, verbose_name="Tên loại xe")
    hang_xe = models.ForeignKey(HangXe, on_delete=models.RESTRICT, verbose_name="Hãng xe")
    kieu_xe = models.ForeignKey(KieuXe, on_delete=models.RESTRICT, verbose_name="Kiểu xe", null=True, blank=True)
    so_cho_ngoi = models.IntegerField(verbose_name="Số chỗ ngồi")

    class Meta:
        db_table = 'LOAIXE'
        verbose_name = "Loại xe"

    def __str__(self):
        return self.ten_loai


class Xe(models.Model):
    bien_so = models.CharField(max_length=20, primary_key=True, verbose_name="Biển số xe")
    loai_xe = models.ForeignKey(LoaiXe, on_delete=models.RESTRICT, verbose_name="Loại xe")
    mau_sac = models.ForeignKey(MauSac, on_delete=models.RESTRICT, verbose_name="Màu sơn")
    kieu_xe = models.ForeignKey(KieuXe, on_delete=models.RESTRICT, verbose_name="Kiểu xe", null=True)
    nam_san_xuat = models.IntegerField(verbose_name="Năm sản xuất", default=2022)
    gia_thue_ngay = models.IntegerField(verbose_name="Giá thuê ngày")
    trang_thai = models.CharField(max_length=50, default="Sẵn sàng", verbose_name="Trạng thái hoạt động")

    class Meta:
        db_table = 'XE'

    def __str__(self):
        return f"{self.bien_so} - {self.loai_xe.ten_loai}"


class LichSuBaoTri(models.Model):
    ma_bao_tri = models.AutoField(primary_key=True, verbose_name="Mã bảo trì")
    xe = models.ForeignKey(Xe, on_delete=models.CASCADE, verbose_name="Xe")
    loai_bao_tri = models.CharField(max_length=100, verbose_name="Loại bảo trì")
    ngay_bao_tri = models.DateField(verbose_name="Ngày bắt đầu bảo trì")
    ngay_ket_thuc = models.DateField(verbose_name="Ngày kết thúc dự kiến", null=True, blank=True)
    noi_dung_chi_tiet = models.CharField(max_length=255, verbose_name="Nội dung chi tiết", null=True, blank=True)
    chi_phi = models.IntegerField(verbose_name="Chi phí")

    class Meta:
        db_table = 'LICHSUBAOTRI'

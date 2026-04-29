from django.contrib import admin
from .models import KhachHang

@admin.register(KhachHang)
class KhachHangAdmin(admin.ModelAdmin):
    list_display = ('ma_kh', 'ho_ten', 'so_dien_thoai', 'cccd')
    search_fields = ('ma_kh', 'ho_ten', 'cccd')

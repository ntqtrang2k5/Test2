import json
import time
import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import ProtectedError
from django.utils import timezone
from rentals.models import HopDong, ChiTietHopDong
from .models import QuocGia, KieuXe, MauSac, HangXe, LoaiXe, Xe, LichSuBaoTri

def car_list(request):
    quoc_gia_list = QuocGia.objects.all()
    kieu_xe_list = KieuXe.objects.all()
    mau_sac_list = MauSac.objects.all()
    hang_xe_list = HangXe.objects.select_related('quoc_gia').all()
    loai_xe_list = LoaiXe.objects.select_related('hang_xe').all()
    
    now = timezone.now()
    today = now.date()
    xe_list = Xe.objects.select_related('loai_xe__hang_xe', 'mau_sac', 'kieu_xe').all()

    # Dynamic status calculation for the list view
    for xe in xe_list:
        # 1. Maintenance check
        in_maintenance = LichSuBaoTri.objects.filter(
            xe=xe,
            ngay_bao_tri__lte=today,
            ngay_ket_thuc__gte=today
        ).exists()
        if in_maintenance:
            xe.trang_thai = "Bảo trì"
            xe.status_class = "badge-status-yellow"
            continue

        # 2. Active contract check
        active_contract = HopDong.objects.filter(
            chitiethopdong__xe=xe,
            ngay_bat_dau__lte=now,
            ngay_ket_thuc_du_kien__gte=now,
            trang_thai__in=['Đang thuê', 'Mới']
        ).first()

        if active_contract:
            remaining = (active_contract.ngay_ket_thuc_du_kien - now).total_seconds()
            if 0 < remaining < 86400:
                xe.trang_thai = "Sắp trả"
                xe.status_class = "badge-status-orange"
            else:
                xe.trang_thai = "Đang thuê"
                xe.status_class = "badge-status-blue"
            continue

        # 3. Overdue check
        overdue_contract = HopDong.objects.filter(
            chitiethopdong__xe=xe,
            trang_thai='Quá hạn'
        ).exists()
        if overdue_contract:
            xe.trang_thai = "Quá hạn"
            xe.status_class = "badge-status-red"
            continue

        # 4. Booking check (Future)
        has_booking = HopDong.objects.filter(
            chitiethopdong__xe=xe,
            ngay_bat_dau__gt=now,
            trang_thai__in=['Mới', 'Đang thuê']
        ).exists()
        if has_booking:
            xe.trang_thai = "Đặt trước"
            xe.status_class = "badge-status-purple"
        else:
            xe.trang_thai = "Sẵn sàng"
            xe.status_class = "badge-status-green"

    context = {
        'active_page': 'quan-ly-xe',
        'quoc_gia_list': quoc_gia_list,
        'kieu_xe_list': kieu_xe_list,
        'mau_sac_list': mau_sac_list,
        'hang_xe_list': hang_xe_list,
        'loai_xe_list': loai_xe_list,
        'xe_list': xe_list,
    }
    return render(request, 'cars/list.html', context)


def config_save(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            config_type = data.get('type')
            item_id = data.get('id', '').strip()
            name = data.get('name', '').strip()

            if not name:
                return JsonResponse({'success': False, 'error': "Vui lòng nhập tên!"})

            if config_type == 'country':
                if not item_id:
                    item_id = f"QG_{int(time.time())}"
                if QuocGia.objects.exclude(ma_quoc_gia=item_id).filter(ten_quoc_gia__iexact=name).exists():
                    return JsonResponse({'success': False, 'error': 'Quốc gia đã tồn tại'})
                QuocGia.objects.update_or_create(ma_quoc_gia=item_id, defaults={'ten_quoc_gia': name})

            elif config_type == 'brand':
                country_id = data.get('countryId')
                if not country_id:
                    return JsonResponse({'success': False, 'error': 'Vui lòng chọn quốc gia sản xuất'})
                if not item_id:
                    item_id = f"HX_{int(time.time())}"
                if HangXe.objects.exclude(ma_hang=item_id).filter(ten_hang__iexact=name).exists():
                    return JsonResponse({'success': False, 'error': 'Hãng xe đã tồn tại'})
                quoc_gia = QuocGia.objects.get(ma_quoc_gia=country_id)
                HangXe.objects.update_or_create(ma_hang=item_id, defaults={'ten_hang': name, 'quoc_gia': quoc_gia})

            elif config_type == 'style':
                if not item_id:
                    item_id = f"KX_{int(time.time())}"
                if KieuXe.objects.exclude(ma_kieu=item_id).filter(ten_kieu__iexact=name).exists():
                    return JsonResponse({'success': False, 'error': 'Kiểu xe đã tồn tại'})
                KieuXe.objects.update_or_create(ma_kieu=item_id, defaults={'ten_kieu': name})

            elif config_type == 'color':
                if not item_id:
                    item_id = f"MS_{int(time.time())}"
                if MauSac.objects.exclude(ma_mau=item_id).filter(ten_mau__iexact=name).exists():
                    return JsonResponse({'success': False, 'error': 'Màu sơn đã tồn tại'})
                MauSac.objects.update_or_create(ma_mau=item_id, defaults={'ten_mau': name})

            elif config_type == 'model':
                brand_id = data.get('brandId')
                style_id = data.get('styleId')
                seats = data.get('seats')
                if not brand_id: return JsonResponse({'success': False, 'error': 'Vui lòng chọn hãng xe'})
                if not style_id: return JsonResponse({'success': False, 'error': 'Vui lòng chọn kiểu xe'})
                if not seats or int(seats) < 0: return JsonResponse({'success': False, 'error': 'Vui lòng nhập số chỗ hợp lệ'})
                
                if not item_id:
                    item_id = f"LX_{int(time.time())}"
                if LoaiXe.objects.exclude(ma_loai=item_id).filter(ten_loai__iexact=name).exists():
                    return JsonResponse({'success': False, 'error': 'Tên loại xe đã tồn tại'})
                
                LoaiXe.objects.update_or_create(
                    ma_loai=item_id, 
                    defaults={
                        'ten_loai': name,
                        'hang_xe_id': brand_id,
                        'kieu_xe_id': style_id,
                        'so_cho_ngoi': int(seats)
                    }
                )

            return JsonResponse({'success': True, 'message': 'Đã cập nhật thành công.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def config_delete(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            config_type = data.get('type')
            item_id = data.get('id')

            model_map = {
                'country': QuocGia,
                'brand': HangXe,
                'style': KieuXe,
                'color': MauSac,
                'model': LoaiXe,
            }
            
            ModelClass = model_map.get(config_type)
            if ModelClass:
                try:
                    obj = ModelClass.objects.get(pk=item_id)
                    obj.delete()
                    return JsonResponse({'success': True, 'message': 'Đã xóa thành công'})
                except ProtectedError:
                    return JsonResponse({'success': False, 'error': 'Không thể xóa dữ liệu đang được sử dụng ở nơi khác'})
                except ModelClass.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Không tìm thấy dữ liệu'})
            
            return JsonResponse({'success': False, 'error': 'Loại danh mục không hợp lệ'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def car_form(request, bien_so=None):
    hang_xe_list = HangXe.objects.all()
    loai_xe_list = LoaiXe.objects.select_related('hang_xe').all()
    mau_sac_list = MauSac.objects.all()
    kieu_xe_list = KieuXe.objects.all()

    current_year = datetime.datetime.now().year
    year_range = range(current_year, 1999, -1)
    
    context = {
        'active_page': 'quan-ly-xe',
        'hang_xe_list': hang_xe_list,
        'loai_xe_list': loai_xe_list,
        'mau_sac_list': mau_sac_list,
        'kieu_xe_list': kieu_xe_list,
        'year_range': year_range,
        'is_edit': False,
    }

    if bien_so:
        try:
            car = Xe.objects.select_related('loai_xe__hang_xe', 'mau_sac', 'kieu_xe').get(bien_so=bien_so)
            context['car'] = car
            context['is_edit'] = True
            
            # Check if car has any contracts to decide if Plate number is editable
            has_contracts = ChiTietHopDong.objects.filter(xe_id=car.bien_so).exists()
            context['has_contracts'] = has_contracts
            
            from .models import LichSuBaoTri
            expenses = LichSuBaoTri.objects.filter(xe=car).order_by('-ngay_bao_tri')
            context['expenses'] = expenses
            context['total_expense'] = sum(e.chi_phi for e in expenses)
            
            return render(request, 'cars/edit.html', context)
        except Xe.DoesNotExist:
            pass
            
    return render(request, 'cars/add.html', context)


def car_save(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bien_so = data.get('bien_so', '').strip().upper()
            original_bien_so = data.get('original_bien_so', '').strip()
            is_edit = data.get('is_edit') == 'true'
            
            loai_xe_id = data.get('loai_xe')
            mau_sac_id = data.get('mau_sac')
            kieu_xe_id = data.get('kieu_xe')
            nam_san_xuat = data.get('nam_san_xuat')
            
            gia_thue_ngay = data.get('gia_thue_ngay')
            if isinstance(gia_thue_ngay, str):
                gia_thue_ngay = gia_thue_ngay.replace(',', '').replace('.', '')
                
            trang_thai = data.get('trang_thai', 'Sẵn sàng')

            if not bien_so or not loai_xe_id or not mau_sac_id or not gia_thue_ngay or not nam_san_xuat or not kieu_xe_id:
                return JsonResponse({'success': False, 'error': 'Vui lòng nhập đầy đủ thông tin bắt buộc'})

            try:
                year_str = str(nam_san_xuat).strip()
                year_int = int(year_str)
                if len(year_str) != 4 or year_int < 0:
                    return JsonResponse({'success': False, 'error': 'Năm sản xuất không hợp lệ'})
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'Năm sản xuất không hợp lệ'})

            try:
                price_int = int(gia_thue_ngay)
                if price_int < 0:
                    return JsonResponse({'success': False, 'error': 'Giá thuê ngày không hợp lệ'})
            except (ValueError, TypeError):
                return JsonResponse({'success': False, 'error': 'Giá thuê ngày không hợp lệ'})

            from django.db import transaction
            try:
                if is_edit:
                    xe = Xe.objects.get(bien_so=original_bien_so)
                    
                    if original_bien_so != bien_so:
                        # 1. Check if vehicle has any contracts
                        if ChiTietHopDong.objects.filter(xe_id=original_bien_so).exists():
                            return JsonResponse({'success': False, 'error': 'Không thể đổi biển số cho xe đã có hợp đồng thuê.'})
                        
                        # 2. Check if new plate already exists
                        if Xe.objects.filter(bien_so=bien_so).exists():
                            return JsonResponse({'success': False, 'error': 'Biển số xe đã tồn tại.'})
                        
                        # 3. Atomic transition
                        with transaction.atomic():
                            # Create new record with same fields but new PK
                            new_xe = Xe.objects.create(
                                bien_so=bien_so,
                                loai_xe_id=loai_xe_id,
                                kieu_xe_id=kieu_xe_id,
                                mau_sac_id=mau_sac_id,
                                nam_san_xuat=year_int,
                                gia_thue_ngay=price_int,
                                trang_thai=trang_thai
                            )
                            
                            # Re-bind Maintenance History
                            LichSuBaoTri.objects.filter(xe_id=original_bien_so).update(xe=new_xe)
                            
                            # Remove old record
                            xe.delete()
                    else:
                        # Normal Update
                        xe.loai_xe_id = loai_xe_id
                        xe.kieu_xe_id = kieu_xe_id
                        xe.mau_sac_id = mau_sac_id
                        xe.nam_san_xuat = year_int
                        xe.gia_thue_ngay = price_int
                        xe.trang_thai = trang_thai
                        xe.save()
                else:
                    # New car
                    if Xe.objects.filter(bien_so=bien_so).exists():
                        return JsonResponse({'success': False, 'error': 'Biển số xe đã tồn tại.'})
                    
                    Xe.objects.create(
                        bien_so=bien_so,
                        loai_xe_id=loai_xe_id,
                        kieu_xe_id=kieu_xe_id,
                        mau_sac_id=mau_sac_id,
                        nam_san_xuat=year_int,
                        gia_thue_ngay=price_int,
                        trang_thai=trang_thai
                    )
            except Xe.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Không tìm thấy xe để cập nhật!'})

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Không thể lưu thông tin xe'})
    return JsonResponse({'success': False, 'error': 'Invalid method'})


def check_plate(request):
    bien_so = request.GET.get('bien_so', '').strip()
    if not bien_so:
        return JsonResponse({'exists': False})
    
    exists = Xe.objects.filter(bien_so__iexact=bien_so).exists()
    return JsonResponse({'exists': exists})


def car_delete(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bien_so = data.get('bien_so')
            
            xe = Xe.objects.get(bien_so=bien_so)
            xe.delete()
            return JsonResponse({'success': True})
        except ProtectedError:
            return JsonResponse({'success': False, 'error': 'Không thể xóa xe đã có lịch sử hoặc hợp đồng (dữ liệu ràng buộc)!'})
        except Xe.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Xe không tồn tại!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})


def expense_save(request):
    if request.method == 'POST':
        try:
            from .models import LichSuBaoTri
            data = json.loads(request.body)
            bien_so = data.get('bien_so')
            if not bien_so: return JsonResponse({'success': False, 'error': 'Mã xe không hợp lệ'})
            
            car = Xe.objects.get(bien_so=bien_so)
            
            date_str = data.get('date', '')
            import re
            dates = re.findall(r'\d{4}-\d{2}-\d{2}', date_str)
            
            if len(dates) >= 2:
                start_date, end_date = dates[0], dates[1]
            elif len(dates) == 1:
                start_date = end_date = dates[0]
            else:
                # Fallback for unexpected formats
                start_date = end_date = timezone.now().date()

            LichSuBaoTri.objects.create(
                xe=car,
                ngay_bao_tri=start_date,
                ngay_ket_thuc=end_date,
                loai_bao_tri=data.get('type'),
                noi_dung_chi_tiet=data.get('note'),
                chi_phi=int(data.get('amount'))
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})



def expense_delete(request):
    if request.method == 'POST':
        try:
            from .models import LichSuBaoTri
            data = json.loads(request.body)
            LichSuBaoTri.objects.filter(pk=data.get('id')).delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

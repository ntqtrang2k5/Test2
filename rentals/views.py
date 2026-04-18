import json
import time
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction, models
from django.utils import timezone
from datetime import datetime
from .models import HopDong, ChiTietHopDong, PhieuTraXe, LichSuThayDoi
from customers.models import KhachHang
from cars.models import Xe

def rental_list(request):
    """View to display the list of all rental contracts."""
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    
    contracts = HopDong.objects.all().select_related('khach_hang').order_by('-ngay_lap')
    
    if query:
        contracts = contracts.filter(
            models.Q(ma_hd__icontains=query) |
            models.Q(khach_hang__ho_ten__icontains=query) |
            models.Q(khach_hang__so_dien_thoai__icontains=query)
        )
        
    if status:
        contracts = contracts.filter(trang_thai=status)
        
    # Calculate counts for summary cards
    count_all = HopDong.objects.count()
    count_active = HopDong.objects.filter(trang_thai='Đang thuê').count()
    count_overdue = HopDong.objects.filter(trang_thai='Quá hạn').count()
    count_returned = HopDong.objects.filter(trang_thai='Đã hoàn thành').count()
    
    # Enrich contracts with display labels and badge classes for the premium UI
    today = timezone.now().date()
    
    for hd in contracts:
        if hd.trang_thai == 'Quá hạn':
            actual_diff = today - hd.ngay_ket_thuc_du_kien.date()
            if actual_diff.days <= 0:
                hd.display_status = "Vừa quá hạn"
            else:
                hd.display_status = f"Quá hạn {actual_diff.days} ngày"
            hd.badge_class = "badge-red"
        elif hd.trang_thai == 'Đang thuê':
            if hd.ngay_ket_thuc_du_kien.date() == today:
                hd.display_status = "Sắp đến hạn"
                hd.badge_class = "badge-orange"
            elif hd.ngay_ket_thuc_du_kien.date() < today:
                hd.display_status = "Đã quá hạn"
                hd.badge_class = "badge-red"
            else:
                hd.display_status = "Đang thuê"
                hd.badge_class = "badge-blue"
        elif hd.trang_thai == 'Đã hoàn thành':
            hd.display_status = "Đã trả xe"
            hd.badge_class = "badge-green"
        elif hd.trang_thai in ['Chờ nhận xe', 'Đặt trước']:
            hd.display_status = "Đặt trước"
            hd.badge_class = "badge-yellow"
        else:
            hd.display_status = hd.trang_thai
            hd.badge_class = "badge-gray"

    context = {
        'contracts': contracts,
        'active_page': 'hop-dong',
        'query': query,
        'status': status,
        'counts': {
            'all': count_all,
            'active': count_active,
            'overdue': count_overdue,
            'returned': count_returned
        },
        'today': today
    }
    return render(request, 'rentals/list.html', context)


def rental_create(request):
    # This view will render the "Tạo hợp đồng" page
    context = {
        'active_page': 'tao-hop-dong',
    }
    return render(request, 'rentals/create.html', context)


def api_search_customers(request):
    query = request.GET.get('q', '').strip()
    # Filter by name or phone
    customers = KhachHang.objects.filter(
        models.Q(ho_ten__icontains=query) | models.Q(so_dien_thoai__icontains=query)
    )[:10]
    
    results = [
        {
            'id': c.ma_kh,
            'name': c.ho_ten,
            'phone': c.so_dien_thoai,
            'cccd': c.cccd
        } for c in customers
    ]
    return JsonResponse({'success': True, 'results': results})


def api_search_cars(request):
    query = request.GET.get('q', '').strip()
    start_str = request.GET.get('start', '')
    end_str = request.GET.get('end', '')
    
    # Base queryset
    cars = Xe.objects.all()
    
    # 1. Availability Filter (Overlap check)
    if start_str and end_str:
        try:
            # Expected format from JS: Y-m-d H:i:s
            start_date = timezone.make_aware(datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S'))
            end_date = timezone.make_aware(datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S'))
            
            # Find cars that are already in overlapping contracts
            # Overlap: (existing_start < new_end) AND (existing_end > new_start)
            overlapping_car_plates = ChiTietHopDong.objects.filter(
                hop_dong__ngay_bat_dau__lt=end_date,
                hop_dong__ngay_ket_thuc_du_kien__gt=start_date,
                hop_dong__trang_thai__in=['Đang thuê', 'Chờ nhận xe']
            ).values_list('xe_id', flat=True)
            
            cars = cars.exclude(bien_so__in=overlapping_car_plates)
        except Exception as e:
            print(f"Error parsing date or filtering: {e}")
            pass # Fallback to status only if dates are invalid
    else:
        # If no dates, only show "Sẵn sàng" as a basic safety
        cars = cars.filter(trang_thai='Sẵn sàng')

    # 2. Text Search Filter
    cars = cars.filter(
        models.Q(bien_so__icontains=query) | 
        models.Q(loai_xe__ten_loai__icontains=query) |
        models.Q(loai_xe__hang_xe__ten_hang__icontains=query)
    ).select_related('loai_xe__hang_xe')[:10]
    
    results = [
        {
            'id': c.bien_so,
            'name': f"{c.loai_xe.hang_xe.ten_hang} {c.loai_xe.ten_loai}",
            'plate': c.bien_so,
            'price': c.gia_thue_ngay,
            'seats': c.loai_xe.so_cho_ngoi
        } for c in cars
    ]
    return JsonResponse({'success': True, 'results': results})


@transaction.atomic
def save_new_contract(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    
    try:
        data = json.loads(request.body)
        
        # 1. Customer Handling
        customer_id = data.get('customer_id')
        if not customer_id:
            # Try to find by CCCD/Phone or create new
            cccd = data.get('customer_cccd')
            phone = data.get('customer_phone')
            name = data.get('customer_name')
            
            customer = KhachHang.objects.filter(models.Q(cccd=cccd) | models.Q(so_dien_thoai=phone)).first()
            if not customer:
                if not name or not phone or not cccd:
                    return JsonResponse({'success': False, 'error': 'Vui lòng điền đủ thông tin khách hàng!'})
                
                # Generate new ID if needed (or let model handle)
                last_kh = KhachHang.objects.order_by('-ma_kh').first()
                if last_kh:
                    next_id = f"KH{int(last_kh.ma_kh[2:]) + 1:03d}"
                else:
                    next_id = "KH001"
                
                customer = KhachHang.objects.create(
                    ma_kh=next_id,
                    ho_ten=name,
                    so_dien_thoai=phone,
                    cccd=cccd
                )
        else:
            customer = KhachHang.objects.get(ma_kh=customer_id)

        # 2. Contract Main Data - Sequential ID Logic
        last_hd = HopDong.objects.order_by('-ma_hd').first()
        if last_hd:
            try:
                # Extract number from HDxxx
                last_num = int(last_hd.ma_hd[2:])
                ma_hd = f"HD{last_num + 1:03d}"
            except:
                ma_hd = f"HD{int(time.time()) % 1000:03d}"
        else:
            ma_hd = "HD001"
        
        now = timezone.now()
        ngay_lap_server = now # Always use current time for creation
        
        try:
            start_date_raw = data.get('start_date')
            end_date_raw = data.get('end_date')
            
            # Use make_aware for strings coming from JS (if they aren't already formatted and handled)
            # Actually data.get('start_date') is already a formatted string. 
            # Let's ensure they are converted to datetime objects for comparison
            start_date = timezone.make_aware(datetime.strptime(start_date_raw, '%Y-%m-%d %H:%M:%S'))
            end_date = timezone.make_aware(datetime.strptime(end_date_raw, '%Y-%m-%d %H:%M:%S'))
            
            if start_date < now - timezone.timedelta(minutes=5): # Allow 5 min buffer for slow forms
                return JsonResponse({'success': False, 'error': 'Ngày giờ bắt đầu không được ở quá khứ!'})
            
            if end_date <= start_date:
                return JsonResponse({'success': False, 'error': 'Ngày trả xe phải sau ngày nhận xe!'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Định dạng ngày tháng không hợp lệ: {str(e)}'})

        tien_coc = int(data.get('tien_coc', 0))
        tien_tra_truoc = int(data.get('tien_tra_truoc', 0))
        tong_tien_thue = int(data.get('tong_tien', 0))
        trang_thai = data.get('trang_thai', 'Chờ nhận xe')
        
        hop_dong = HopDong.objects.create(
            ma_hd=ma_hd,
            khach_hang=customer,
            ngay_lap=ngay_lap_server,
            ngay_bat_dau=start_date,
            ngay_ket_thuc_du_kien=end_date,
            tien_coc=tien_coc,
            tien_tra_truoc=tien_tra_truoc,
            tong_tien_thue=tong_tien_thue,
            trang_thai=trang_thai
        )

        # 3. Contract Details (Cars)
        selected_car_plates = data.get('cars', [])
        if not selected_car_plates:
            raise Exception("Chưa chọn xe thuê!")

        for plate in selected_car_plates:
            xe = Xe.objects.get(bien_so=plate)
            
            # Final availability check against overlap
            # (Just in case someone booked it while the user was filling the form)
            is_busy = ChiTietHopDong.objects.filter(
                xe=xe,
                hop_dong__ngay_bat_dau__lt=end_date,
                hop_dong__ngay_ket_thuc_du_kien__gt=start_date,
                hop_dong__trang_thai__in=['Đang thuê', 'Chờ nhận xe']
            ).exclude(hop_dong=hop_dong).exists()
            
            if is_busy:
                raise Exception(f"Xe {plate} vừa được đặt bởi người khác trong khoảng thời gian này!")
            
            ChiTietHopDong.objects.create(
                hop_dong=hop_dong,
                xe=xe
            )
            
            # Update Car Status
            xe.trang_thai = 'Đang thuê'
            xe.save()

        return JsonResponse({'success': True, 'ma_hd': ma_hd})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@transaction.atomic
def save_customer(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        cccd = data.get('cccd', '').strip()

        if not name or not phone or not cccd:
            return JsonResponse({'success': False, 'error': 'Vui lòng nhập đầy đủ Họ tên, SĐT và CCCD!'})

        import re
        # Validate Name: No numbers, no special chars
        name_regex = r'^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸửữựỳỵỷỹýỹ\s]+$'
        if not re.match(name_regex, name):
            return JsonResponse({'success': False, 'error': 'Họ tên không được chứa số hoặc ký tự đặc biệt!'})

        # Validate Phone: 10 digits, starts with 0
        if not re.match(r'^0\d{9}$', phone):
            return JsonResponse({'success': False, 'error': 'Số điện thoại phải có đúng 10 chữ số và bắt đầu bằng số 0!'})
            
        # Validate CCCD: 12 digits
        if not re.match(r'^\d{12}$', cccd):
            return JsonResponse({'success': False, 'error': 'Số CCCD phải có đúng 12 chữ số!'})

        # Check duplicates
        if KhachHang.objects.filter(so_dien_thoai=phone).exists():
            return JsonResponse({'success': False, 'error': f'Số điện thoại {phone} đã tồn tại trong hệ thống!'})
        
        if KhachHang.objects.filter(cccd=cccd).exists():
            return JsonResponse({'success': False, 'error': f'Số CCCD {cccd} đã tồn tại trong hệ thống!'})

        # Generate ID
        last_kh = KhachHang.objects.order_by('-ma_kh').first()
        if last_kh:
            next_id = f"KH{int(last_kh.ma_kh[2:]) + 1:03d}"
        else:
            next_id = "KH001"

        new_kh = KhachHang.objects.create(
            ma_kh=next_id,
            ho_ten=name,
            so_dien_thoai=phone,
            cccd=cccd
        )

        return JsonResponse({
            'success': True, 
            'message': 'Thêm khách hàng mới thành công!',
            'customer': {
                'id': new_kh.ma_kh,
                'name': new_kh.ho_ten,
                'phone': new_kh.so_dien_thoai,
                'cccd': new_kh.cccd
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def contract_detail(request, ma_hd):
    """View to display and manage a single rental contract."""
    hd = get_object_or_404(HopDong.objects.select_related('khach_hang').prefetch_related('chitiethopdong_set__xe'), ma_hd=ma_hd)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            with transaction.atomic():
                if action == 'save':
                    # 1. Detection of changes
                    old_end = hd.ngay_ket_thuc_du_kien
                    new_end_str = request.POST.get('ngay_ket_thuc_du_kien')
                    new_end = timezone.make_aware(datetime.strptime(new_end_str, '%Y-%m-%d %H:%M:%S'))
                    
                    price_diff = 0
                    change_log = []

                    # 2. Handle Date Change Logic
                    if new_end != old_end:
                        if hd.trang_thai == 'Đã hoàn thành':
                            return JsonResponse({'success': False, 'error': 'Không thể đổi ngày cho hợp đồng đã hoàn thành!'})

                        # Check Availability if extending
                        if new_end > old_end:
                            for detail in hd.chitiethopdong_set.all():
                                xe = detail.xe
                                is_busy = ChiTietHopDong.objects.filter(
                                    xe=xe,
                                    hop_dong__ngay_bat_dau__lt=new_end,
                                    hop_dong__ngay_ket_thuc_du_kien__gt=old_end,
                                    hop_dong__trang_thai__in=['Đang thuê', 'Chờ nhận xe']
                                ).exclude(hop_dong=hd).exists()
                                
                                if is_busy:
                                    return JsonResponse({'success': False, 'error': f'Xe {xe.bien_so} đã có lịch bận trong khoảng thời gian gia hạn thêm!'})

                        # Calculate Price Difference
                        total_daily_price = int(hd.chitiethopdong_set.aggregate(total=models.Sum('xe__gia_thue_ngay'))['total'] or 0)
                        old_days = (old_end - hd.ngay_bat_dau).days or 1
                        new_days = (new_end - hd.ngay_bat_dau).days or 1
                        
                        day_diff = new_days - old_days
                        price_diff = day_diff * total_daily_price
                        
                        change_log.append(f"Đổi ngày trả: {old_end.strftime('%d/%m/%Y %H:%M')} -> {new_end.strftime('%d/%m/%Y %H:%M')} ({day_diff} ngày).")
                        hd.ngay_ket_thuc_du_kien = new_end
                        hd.tong_tien_thue += price_diff

                    # 3. Update Other Fields
                    new_tien_coc = int(request.POST.get('tien_coc', 0).replace('.', '').replace(',', ''))
                    new_tien_tra_truoc = int(request.POST.get('tien_tra_truoc', 0).replace('.', '').replace(',', ''))
                    
                    if new_tien_coc != hd.tien_coc:
                        change_log.append(f"Cập nhật tiền cọc: {int(hd.tien_coc):,} -> {new_tien_coc:,}")
                        hd.tien_coc = new_tien_coc
                    
                    if new_tien_tra_truoc != hd.tien_tra_truoc:
                        change_log.append(f"Cập nhật trả trước: {int(hd.tien_tra_truoc):,} -> {new_tien_tra_truoc:,}")
                        hd.tien_tra_truoc = new_tien_tra_truoc

                    # 4. Save and Log History
                    if change_log:
                        LichSuThayDoi.objects.create(
                            hop_dong=hd,
                            noi_dung="; ".join(change_log),
                            tien_chenh_lech=price_diff
                        )
                        hd.save()
                        return JsonResponse({'success': True, 'message': 'Cập nhật hợp đồng thành công!'})
                    else:
                        return JsonResponse({'success': True, 'message': 'Không có thay đổi nào được thực hiện.'})

                elif action == 'return':
                    # Create Return Record
                    last_tx = PhieuTraXe.objects.order_by('-ma_tra_xe').first()
                    ma_tx = f"TX{int(last_tx.ma_tra_xe[2:]) + 1:03d}" if last_tx else "TX001"
                    
                    late_fee = int(request.POST.get('late_fee', 0).replace('.', '').replace(',', ''))
                    other_fee = int(request.POST.get('other_fee', 0).replace('.', '').replace(',', ''))
                    return_back = int(request.POST.get('return_back', 0).replace('.', '').replace(',', ''))
                    pay_more = int(request.POST.get('pay_more', 0).replace('.', '').replace(',', ''))
                    note = request.POST.get('note', '')

                    PhieuTraXe.objects.create(
                        ma_tra_xe=ma_tx,
                        hop_dong=hd,
                        phat_qua_han=late_fee,
                        phu_phi_khac=other_fee,
                        tien_tra_lai_khach=return_back,
                        khach_tra_them=pay_more,
                        ghi_chu=note
                    )
                    
                    hd.trang_thai = 'Đã hoàn thành'
                    hd.ngay_ket_thuc_thuc_te = timezone.now()
                    hd.save()
                    
                    # Release Cars
                    for detail in hd.chitiethopdong_set.all():
                        xe = detail.xe
                        xe.trang_thai = 'Sẵn sàng'
                        xe.save()
                        
                    return JsonResponse({'success': True, 'message': 'Đã trả xe và hoàn tất hợp đồng!'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # Fetch Change History for UI
    history = LichSuThayDoi.objects.filter(hop_dong=hd).order_by('-ngay_thay_doi')
    
    # Calculate current duration for UI
    duration = (hd.ngay_ket_thuc_du_kien - hd.ngay_bat_dau).days
    if duration == 0: duration = 1
    
    # Calculate total daily price for auto-extension calculation
    total_daily_price = hd.chitiethopdong_set.aggregate(total=models.Sum('xe__gia_thue_ngay'))['total'] or 0

    context = {
        'hd': hd,
        'duration': duration,
        'total_daily_price': total_daily_price,
        'history': history,
        'active_page': 'hop-dong',
    }
    return render(request, 'rentals/detail.html', context)

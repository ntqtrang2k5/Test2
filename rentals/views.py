import json
import time
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction, models
from django.utils import timezone
from datetime import datetime
from .models import HopDong, ChiTietHopDong, PhieuTraXe, LichSuThayDoi, GiaoDich
from customers.models import KhachHang
from cars.models import Xe
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def rental_list(request):
    """View to display the list of all rental contracts."""
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    
    contracts = HopDong.objects.all().select_related('khach_hang').order_by('-ma_hd')
    
    if query:
        contracts = contracts.filter(
            models.Q(ma_hd__icontains=query) |
            models.Q(khach_hang__ho_ten__icontains=query) |
            models.Q(khach_hang__so_dien_thoai__icontains=query)
        )
        
    if status:
        contracts = contracts.filter(trang_thai=status)
        
    # Calculate counts for summary cards
    today = timezone.now().date()
    count_all = HopDong.objects.count()
    count_active = HopDong.objects.filter(trang_thai='Đang thuê', ngay_ket_thuc_du_kien__gte=today).count()
    count_overdue = HopDong.objects.filter(
        models.Q(trang_thai='Quá hạn') | 
        models.Q(trang_thai='Đang thuê', ngay_ket_thuc_du_kien__lt=today)
    ).count()
    count_returned = HopDong.objects.filter(trang_thai='Đã hoàn thành').count()
    count_reservation = HopDong.objects.filter(trang_thai='Đặt trước').count()
    count_cancelled = HopDong.objects.filter(trang_thai='Đã hủy').count()
    
    # Enrich contracts with display labels and badge classes for the premium UI
    
    for hd in contracts:
        # Dynamically treat 'Đang thuê' as 'Quá hạn' if date passed
        if hd.trang_thai == 'Đang thuê' and hd.ngay_ket_thuc_du_kien and hd.ngay_ket_thuc_du_kien < today:
            hd.trang_thai = 'Quá hạn'

        if hd.trang_thai == 'Quá hạn' and hd.ngay_ket_thuc_du_kien:
            actual_diff = today - hd.ngay_ket_thuc_du_kien
            if actual_diff.days <= 0:
                hd.display_status = "Vừa quá hạn"
            else:
                hd.display_status = f"Quá hạn {actual_diff.days} ngày"
            hd.badge_class = "badge-red"
        elif hd.trang_thai == 'Đang thuê':
            if hd.ngay_ket_thuc_du_kien and hd.ngay_ket_thuc_du_kien == today:
                hd.display_status = "Sắp đến hạn"
                hd.badge_class = "badge-orange"
            elif hd.ngay_ket_thuc_du_kien and hd.ngay_ket_thuc_du_kien < today:
                hd.display_status = "Đã quá hạn"
                hd.badge_class = "badge-red"
            else:
                hd.display_status = "Đang thuê"
                hd.badge_class = "badge-blue"
        elif hd.trang_thai == 'Đã hoàn thành':
            hd.display_status = "Đã trả xe"
            hd.badge_class = "badge-green"
        elif hd.trang_thai == 'Đặt trước':
            hd.display_status = "Đặt trước"
            hd.badge_class = "badge-yellow"
        elif hd.trang_thai == 'Đã hủy':
            hd.display_status = "Đã hủy"
            hd.badge_class = "badge-gray"
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
            'returned': count_returned,
            'reservation': count_reservation,
            'cancelled': count_cancelled
        },
        'today': today
    }
    return render(request, 'rentals/list.html', context)


@login_required(login_url='/login/')
def rental_create(request):
    # This view will render the "Tạo hợp đồng" page
    context = {
        'active_page': 'tao-hop-dong',
    }
    return render(request, 'rentals/create.html', context)


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def api_search_cars(request):
    query = request.GET.get('q', '').strip()
    start_str = request.GET.get('start', '')
    end_str = request.GET.get('end', '')
    
    # Base queryset
    # Always exclude cars that are out of service
    cars = Xe.objects.exclude(trang_thai='Ngưng hoạt động')
    
    # 1. Availability Filter (Overlap check)
    if start_str and end_str:
        try:
            # Expected format from JS: Y-m-d
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            
            # A. Overlap with Existing Contracts
            # Overlap: (existing_start < new_end) AND (existing_end > new_start)
            # Conditions for active contracts: Đang thuê, Đặt trước, Chờ nhận xe
            busy_contract_car_plates = ChiTietHopDong.objects.filter(
                hop_dong__ngay_bat_dau__lt=end_date,
                hop_dong__ngay_ket_thuc_du_kien__gt=start_date,
                hop_dong__trang_thai__in=['Đang thuê', 'Đặt trước', 'Chờ nhận xe', 'Đã quá hạn']
            ).values_list('xe_id', flat=True)
            
            cars = cars.exclude(bien_so__in=busy_contract_car_plates)

            # B. Overlap with Maintenance History
            # Comparison uses dates since maintenance is tracked by day
            s_date = start_date
            e_date = end_date
            
            from cars.models import LichSuBaoTri
            maintenance_car_plates = LichSuBaoTri.objects.filter(
                ngay_bao_tri__lte=e_date,
                ngay_ket_thuc__gte=s_date
            ).values_list('xe_id', flat=True)

            cars = cars.exclude(bien_so__in=maintenance_car_plates)
            
        except Exception as e:
            print(f"Error parsing date or filtering: {e}")
            # Fallback: if maintenance or contracts error, stay safe
            pass 
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
            'price': int(c.gia_thue_ngay) if c.gia_thue_ngay else 0,
            'seats': c.loai_xe.so_cho_ngoi
        } for c in cars
    ]
    return JsonResponse({'success': True, 'results': results})


@login_required(login_url='/login/')
def api_validate_cars(request):
    """Checks if a list of car plates are available for a given period."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
        
    try:
        data = json.loads(request.body)
        plates = data.get('plates', [])
        start_str = data.get('start', '')
        end_str = data.get('end', '')
        
        if not plates or not start_str or not end_str:
            return JsonResponse({'success': True, 'unavailable': []})
            
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        
        # Check Contracts
        busy_contracts = ChiTietHopDong.objects.filter(
            xe_id__in=plates,
            hop_dong__ngay_bat_dau__lt=end_date,
            hop_dong__ngay_ket_thuc_du_kien__gt=start_date,
            hop_dong__trang_thai__in=['Đang thuê', 'Đặt trước', 'Chờ nhận xe', 'Đã quá hạn']
        ).values_list('xe_id', flat=True)
        
        # Check Maintenance
        s_date = start_date.date()
        e_date = end_date.date()
        from cars.models import LichSuBaoTri
        busy_maintenance = LichSuBaoTri.objects.filter(
            xe_id__in=plates,
            ngay_bao_tri__lte=e_date,
            ngay_ket_thuc__gte=s_date
        ).values_list('xe_id', flat=True)
        
        unavailable = list(set(list(busy_contracts) + list(busy_maintenance)))
        
        return JsonResponse({'success': True, 'unavailable': unavailable})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required(login_url='/login/')
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
            
            start_date = datetime.strptime(start_date_raw, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_raw, '%Y-%m-%d').date()
            
            if start_date < now.date(): # No more 5 min buffer needed for pure dates
                return JsonResponse({'success': False, 'error': 'Ngày giờ bắt đầu không được ở quá khứ!'})
            
            if end_date <= start_date:
                return JsonResponse({'success': False, 'error': 'Ngày trả xe phải sau ngày nhận xe!'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Định dạng ngày tháng không hợp lệ: {str(e)}'})

        tien_coc = 0  # Deposit removed as per user request
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
            raise Exception("Vui lòng chọn ít nhất một xe!")

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
        
        # 4. Create Initial Transaction
        if tien_tra_truoc > 0:
            GiaoDich.objects.create(
                hop_dong=hop_dong,
                so_tien=tien_tra_truoc,
                loai_gd='Tạm ứng'
            )

        return JsonResponse({'success': True, 'ma_hd': ma_hd})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def contract_detail(request, ma_hd):
    """View to display and manage a single rental contract."""
    hd = get_object_or_404(HopDong.objects.select_related('khach_hang').prefetch_related('chitiethopdong_set__xe'), ma_hd=ma_hd)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            with transaction.atomic():
                if action == 'save':
                    # Chặn hoàn toàn nếu đã hoàn thành
                    if hd.trang_thai == 'Đã hoàn thành':
                        return JsonResponse({'success': False, 'error': 'Hợp đồng đã hoàn thành, không thể chỉnh sửa!'})

                    # 1. Detection of changes
                    old_end = hd.ngay_ket_thuc_du_kien
                    new_end_str = request.POST.get('ngay_ket_thuc_du_kien')
                    new_end = datetime.strptime(new_end_str, '%Y-%m-%d').date()
                    
                    price_diff = 0
                    change_log = []

                    # 2. Handle Date Change Logic
                    if hd.trang_thai == 'Đang thuê':
                        # Đang thuê: chỉ cho sửa ngày kết thúc (gia hạn)
                        new_start = hd.ngay_bat_dau  # Giữ nguyên ngày bắt đầu
                        new_start_str = request.POST.get('ngay_bat_dau', '')
                        if new_start_str:
                            try:
                                submitted_start = datetime.strptime(new_start_str, '%Y-%m-%d').date()
                                if submitted_start != hd.ngay_bat_dau:
                                    return JsonResponse({'success': False, 'error': 'Đang thuê: không được phép thay đổi ngày nhận xe!'})
                            except Exception:
                                pass

                        if new_end != old_end:
                            if new_end < old_end:
                                return JsonResponse({'success': False, 'error': 'Gia hạn: Ngày kết thúc mới phải lớn hơn ngày kết thúc hiện tại!'})

                            # Chỉ kiểm tra xung đột trong khoảng GIA HẠN [old_end → new_end]
                            for detail in hd.chitiethopdong_set.all():
                                xe = detail.xe
                                is_busy = ChiTietHopDong.objects.filter(
                                    xe=xe,
                                    hop_dong__ngay_bat_dau__lt=new_end,
                                    hop_dong__ngay_ket_thuc_du_kien__gt=old_end,
                                    hop_dong__trang_thai__in=['Đang thuê', 'Chờ nhận xe', 'Đặt trước']
                                ).exclude(hop_dong=hd).exists()
                                if is_busy:
                                    return JsonResponse({'success': False, 'error': f'Xe {xe.bien_so} đã có lịch bận trong khoảng gia hạn ({old_end.strftime("%d/%m/%Y")} → {new_end.strftime("%d/%m/%Y")})!'})

                            total_daily_price = int(hd.chitiethopdong_set.aggregate(total=models.Sum('xe__gia_thue_ngay'))['total'] or 0)
                            old_days = (old_end - hd.ngay_bat_dau).days or 1
                            new_days = (new_end - hd.ngay_bat_dau).days or 1
                            day_diff = new_days - old_days
                            price_diff = day_diff * total_daily_price

                            change_log.append(f"Gia hạn thuê: {old_end.strftime('%d/%m/%Y')} → {new_end.strftime('%d/%m/%Y')} (+{day_diff} ngày, +{price_diff:,}đ)")
                            hd.ngay_ket_thuc_du_kien = new_end
                            hd.tong_tien_thue += price_diff
                    else:
                        # Đặt trước / Chờ nhận xe: cho sửa cả 2 ngày
                        new_start_str = request.POST.get('ngay_bat_dau')
                        new_start = datetime.strptime(new_start_str, '%Y-%m-%d').date()

                        if new_start != hd.ngay_bat_dau or new_end != old_end:
                            for detail in hd.chitiethopdong_set.all():
                                xe = detail.xe
                                is_busy = ChiTietHopDong.objects.filter(
                                    xe=xe,
                                    hop_dong__ngay_bat_dau__lt=new_end,
                                    hop_dong__ngay_ket_thuc_du_kien__gt=new_start,
                                    hop_dong__trang_thai__in=['Đang thuê', 'Chờ nhận xe', 'Đặt trước']
                                ).exclude(hop_dong=hd).exists()
                                if is_busy:
                                    return JsonResponse({'success': False, 'error': f'Xe {xe.bien_so} đã có lịch bận trong khoảng thời gian điều chỉnh!'})

                            total_daily_price = int(hd.chitiethopdong_set.aggregate(total=models.Sum('xe__gia_thue_ngay'))['total'] or 0)
                            old_days = (old_end - hd.ngay_bat_dau).days or 1
                            new_days = (new_end - new_start).days or 1
                            day_diff = new_days - old_days
                            price_diff = day_diff * total_daily_price

                            msg = f"Đổi ngày: [{hd.ngay_bat_dau.strftime('%d/%m/%Y')} - {old_end.strftime('%d/%m/%Y')}] → [{new_start.strftime('%d/%m/%Y')} - {new_end.strftime('%d/%m/%Y')}] ({day_diff:+d} ngày)."
                            change_log.append(msg)
                            hd.ngay_bat_dau = new_start
                            hd.ngay_ket_thuc_du_kien = new_end
                            hd.tong_tien_thue += price_diff

                    # 3. Update Customer
                    new_customer_id = request.POST.get('customer_id')
                    if new_customer_id and new_customer_id != hd.khach_hang.ma_kh:
                        if hd.trang_thai in ['Đặt trước', 'Chờ nhận xe']:
                            new_customer = KhachHang.objects.get(ma_kh=new_customer_id)
                            change_log.append(f"Đổi khách hàng: {hd.khach_hang.ho_ten} -> {new_customer.ho_ten}")
                            hd.khach_hang = new_customer
                        else:
                            return JsonResponse({'success': False, 'error': 'Không thể đổi khách hàng khi đã bắt đầu thuê!'})

                    # 4. Update Vehicles (Only if reservation)
                    new_car_plates = request.POST.getlist('cars')
                    if hd.trang_thai in ['Đặt trước', 'Chờ nhận xe'] and not new_car_plates:
                        return JsonResponse({'success': False, 'error': 'Vui lòng chọn ít nhất một xe!'})

                    if new_car_plates:
                        if hd.trang_thai not in ['Đặt trước', 'Chờ nhận xe']:
                            # If already renting, we don't allow changing the car list here for simplicity/safety
                            pass 
                        else:
                            current_car_plates = list(hd.chitiethopdong_set.values_list('xe__bien_so', flat=True))
                            if set(new_car_plates) != set(current_car_plates):
                                # Release old cars
                                for detail in hd.chitiethopdong_set.all():
                                    xe = detail.xe
                                    xe.trang_thai = 'Sẵn sàng'
                                    xe.save()
                                
                                # Remove old details
                                hd.chitiethopdong_set.all().delete()
                                
                                # Add new cars
                                total_daily_price = 0
                                car_names = []
                                for plate in new_car_plates:
                                    xe = Xe.objects.get(bien_so=plate)
                                    # Check availability (exclude THIS contract)
                                    is_busy = ChiTietHopDong.objects.filter(
                                        xe=xe,
                                        hop_dong__ngay_bat_dau__lt=hd.ngay_ket_thuc_du_kien,
                                        hop_dong__ngay_ket_thuc_du_kien__gt=hd.ngay_bat_dau,
                                        hop_dong__trang_thai__in=['Đang thuê', 'Chờ nhận xe']
                                    ).exists()
                                    if is_busy:
                                        return JsonResponse({'success': False, 'error': f'Xe {plate} đã có lịch bận trong thời gian này!'})
                                    
                                    ChiTietHopDong.objects.create(hop_dong=hd, xe=xe)
                                    xe.trang_thai = 'Đang thuê'
                                    xe.save()
                                    total_daily_price += xe.gia_thue_ngay
                                    car_names.append(plate)
                                
                                change_log.append(f"Cập nhật danh sách xe: {', '.join(car_names)}")
                                
                                # Recalculate total price
                                duration = (hd.ngay_ket_thuc_du_kien - hd.ngay_bat_dau).days or 1
                                hd.tong_tien_thue = duration * total_daily_price

                    # 5. Update Payment Fields
                    new_tien_tra_truoc = int(request.POST.get('tien_tra_truoc', '0').replace('.', '').replace(',', ''))
                    
                    if new_tien_tra_truoc != hd.tien_tra_truoc:
                        diff = new_tien_tra_truoc - hd.tien_tra_truoc
                        loai = 'Thu thêm' if diff > 0 else 'Hoàn trả'
                        change_log.append(f"Cập nhật tạm ứng: {int(hd.tien_tra_truoc):,} -> {new_tien_tra_truoc:,}")
                        
                        # Record Transaction
                        GiaoDich.objects.create(
                            hop_dong=hd,
                            so_tien=abs(diff),
                            loai_gd=loai
                        )
                        
                        hd.tien_tra_truoc = new_tien_tra_truoc

                    # 6. Save and Log History
                    if change_log:
                        LichSuThayDoi.objects.create(
                            hop_dong=hd,
                            noi_dung="; ".join(change_log),
                            tien_chenh_lech=price_diff # date change diff
                        )
                        # Ensure tien_coc is 0 (standardization)
                        hd.tien_coc = 0
                        hd.save()
                        return JsonResponse({'success': True, 'message': 'Cập nhật hợp đồng thành công!'})
                    else:
                        return JsonResponse({'success': True, 'message': 'Không có thay đổi nào được thực hiện.'})

                elif action == 'add_transaction':
                    loai_gd = request.POST.get('loai_gd')
                    so_tien = int(request.POST.get('so_tien', 0).replace('.', '').replace(',', ''))
                    ngay_gd_str = request.POST.get('ngay_gd')
                    if not so_tien or not loai_gd:
                        return JsonResponse({'success': False, 'error': 'Vui lòng nhập đủ thông tin giao dịch!'})
                        
                    ngay_gd = datetime.strptime(ngay_gd_str, '%Y-%m-%d').date()
                    
                    # Validation: ngay_gd must be between hd.ngay_bat_dau and hd.ngay_ket_thuc_du_kien
                    if ngay_gd < hd.ngay_bat_dau or ngay_gd > hd.ngay_ket_thuc_du_kien:
                        return JsonResponse({'success': False, 'error': f'Ngày giao dịch phải từ ngày bắt đầu thuê ({hd.ngay_bat_dau.strftime("%d/%m/%Y")}) đến ngày trả xe dự kiến ({hd.ngay_ket_thuc_du_kien.strftime("%d/%m/%Y")})!'})

                    # Record the transaction
                    GiaoDich.objects.create(
                        hop_dong=hd,
                        so_tien=so_tien,
                        loai_gd=loai_gd,
                        ngay_gd=ngay_gd
                    )
                    
                    # Update contract prepaid total
                    # Rule: Tạm ứng, Thu thêm -> +, Hoàn trả -> -
                    if loai_gd in ['Tạm ứng', 'Thu thêm']:
                        hd.tien_tra_truoc += so_tien
                    elif loai_gd == 'Hoàn trả':
                        hd.tien_tra_truoc -= so_tien
                    
                    hd.save()
                    return JsonResponse({'success': True, 'message': 'Đã ghi nhận giao dịch thành công!'})

                elif action == 'delete_transaction':
                    gd_id = request.POST.get('gd_id')
                    try:
                        gd = GiaoDich.objects.get(id=gd_id, hop_dong=hd)
                        
                        # Reverse the payment effect before deleting
                        if gd.loai_gd in ['Tạm ứng', 'Thu thêm']:
                            hd.tien_tra_truoc -= gd.so_tien
                        elif gd.loai_gd == 'Hoàn trả':
                            hd.tien_tra_truoc += gd.so_tien
                        elif gd.loai_gd == 'Quyết toán':
                            # Quyết toán usually happens at the end, but if deleted, reverse it
                            hd.tien_tra_truoc -= gd.so_tien

                        hd.save()
                        gd.delete()
                        return JsonResponse({'success': True, 'message': 'Đã xóa giao dịch và cập nhật lại dòng tiền!'})
                    except GiaoDich.DoesNotExist:
                        return JsonResponse({'success': False, 'error': 'Không tìm thấy giao dịch!'})

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
                    
                    # Use actual return date from request
                    actual_return_str = request.POST.get('ngay_tra_thuc_te')
                    if actual_return_str:
                        hd.ngay_ket_thuc_thuc_te = datetime.strptime(actual_return_str, '%Y-%m-%d').date()
                    else:
                        hd.ngay_ket_thuc_thuc_te = timezone.now().date()
                        
                    hd.save()
                    
                    # Release Cars
                    for detail in hd.chitiethopdong_set.all():
                        xe = detail.xe
                        xe.trang_thai = 'Sẵn sàng'
                        xe.save()
                    
                    # Record Settlement Transaction
                    final_diff = pay_more - return_back
                    if final_diff != 0:
                        loai_set = 'Quyết toán' if final_diff > 0 else 'Hoàn trả'
                        ghi_chu_set = f"Quyết toán khi trả xe. {'Khách trả thêm' if final_diff > 0 else 'Hoàn trả khách'}: {abs(final_diff):,}đ"
                        GiaoDich.objects.create(
                            hop_dong=hd,
                            so_tien=abs(final_diff),
                            loai_gd=loai_set
                        )
                        
                    return JsonResponse({'success': True, 'message': 'Đã trả xe và hoàn tất hợp đồng!'})

                elif action == 'cancel':
                    if hd.trang_thai != 'Đặt trước':
                        return JsonResponse({'success': False, 'error': 'Chỉ có thể xóa hợp đồng đang ở trạng thái Đặt trước!'})
                    
                    # Release Cars
                    for detail in hd.chitiethopdong_set.all():
                        xe = detail.xe
                        xe.trang_thai = 'Sẵn sàng'
                        xe.save()
                    
                    # Delete the contract (this will cascade delete transactions, details, and logs)
                    hd.delete()
                    
                    return JsonResponse({'success': True, 'message': 'Đã xóa hợp đồng và cập nhật lại dòng tiền!'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    # Fetch histories and transactions
    history = LichSuThayDoi.objects.filter(hop_dong=hd).order_by('-ngay_thay_doi')
    transactions = GiaoDich.objects.filter(hop_dong=hd).order_by('-ngay_gd')
    phieu_tra = PhieuTraXe.objects.filter(hop_dong=hd).first()

    # Calculate duration for display
    if hd.ngay_ket_thuc_du_kien and hd.ngay_bat_dau:
        duration = (hd.ngay_ket_thuc_du_kien - hd.ngay_bat_dau).days
        if duration <= 0: duration = 1
    else:
        duration = 1

    # Tính khoảng ngày bị chặn (xe đang dung cho HĐ khác) để flatpickr disable
    import json as _json
    seen_hd = set()
    blocked = []
    for detail in hd.chitiethopdong_set.all():
        busy_qs = ChiTietHopDong.objects.filter(
            xe=detail.xe,
            hop_dong__trang_thai__in=['Đang thuê', 'Đặt trước']
        ).exclude(hop_dong=hd).select_related('hop_dong')
        for bc in busy_qs:
            key = bc.hop_dong.ma_hd
            if key not in seen_hd:
                seen_hd.add(key)
                blocked.append({
                    'from': bc.hop_dong.ngay_bat_dau.strftime('%Y-%m-%d'),
                    'to': bc.hop_dong.ngay_ket_thuc_du_kien.strftime('%Y-%m-%d'),
                    'label': f"{bc.hop_dong.ma_hd} ({bc.hop_dong.khach_hang.ho_ten})"
                })
    blocked_ranges_json = _json.dumps(blocked)

    # Dynamically treat 'Đang thuê' as 'Quá hạn' if end date has passed (mirrors rental_list logic)
    today = timezone.now().date()
    if hd.trang_thai == 'Đang thuê' and hd.ngay_ket_thuc_du_kien and hd.ngay_ket_thuc_du_kien < today:
        hd.trang_thai = 'Quá hạn'

    context = {
        'hd': hd,
        'history': history,
        'transactions': transactions,
        'phieu_tra': phieu_tra,
        'active_page': 'hop-dong',
        'duration': duration,
        'blocked_ranges_json': blocked_ranges_json,
        'today': today,
    }
    return render(request, 'rentals/detail.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from rentals.models import HopDong, ChiTietHopDong, PhieuTraXe
from cars.models import Xe, LichSuBaoTri
from django.db.models import Sum, Count, Q
from django.utils import timezone
import json
from datetime import datetime

@login_required(login_url='/login/')
def dashboard(request):
    """
    View for the main dashboard (Tong Quan) using real data.
    """
    now = timezone.now()
    today = now.date()
    
    # --- STATS CARDS ---
    count_all = HopDong.objects.count()
    total_revenue = HopDong.objects.aggregate(total=Sum('tong_tien_thue'))['total'] or 0
    
    # Contracts needing attention (Urgent list)
    attention_contracts_qs = HopDong.objects.select_related('khach_hang').filter(
        Q(trang_thai='Quá hạn') | 
        Q(trang_thai='Đang thuê', ngay_ket_thuc_du_kien__lte=now + timezone.timedelta(days=1))
    ).order_by('ngay_ket_thuc_du_kien')[:10]
    
    for hd in attention_contracts_qs:
        if hd.trang_thai == 'Quá hạn':
            hd.badge_class = 'badge-red'
            hd.display_status = 'Quá hạn'
        else:
            hd.badge_class = 'badge-orange'
            hd.display_status = 'Sắp đến hạn'

    # Top Cars (Performance)
    top_cars = Xe.objects.annotate(
        rental_count=Count('chitiethopdong')
    ).select_related('loai_xe__hang_xe').order_by('-rental_count')[:5]

    # --- FINANCIAL DATA AGGREGATION ---
    transactions = []
    total_income = 0
    total_expense = 0

    # 1. Income from Contracts
    contracts_qs = HopDong.objects.select_related('khach_hang').prefetch_related('chitiethopdong_set__xe')
    for hd in contracts_qs:
        # Deposit
        if hd.tien_coc > 0:
            total_income += int(hd.tien_coc)
            transactions.append({
                'date': hd.ngay_lap.date(),
                'title': f"Khách cọc giữ xe {hd.ma_hd} - {hd.khach_hang.ho_ten}",
                'category': 'TIỀN CỌC',
                'income': int(hd.tien_coc),
                'expense': 0,
                'ref': hd.ma_hd,
                'type': 'income'
            })
        
        # Prepayment (Tam ung)
        if hd.tien_tra_truoc > 0:
            total_income += int(hd.tien_tra_truoc)
            transactions.append({
                'date': hd.ngay_lap.date(),
                'title': f"Tạm ứng HĐ {hd.ma_hd} - {hd.khach_hang.ho_ten}",
                'category': 'TẠM ỨNG',
                'income': int(hd.tien_tra_truoc),
                'expense': 0,
                'ref': hd.ma_hd,
                'type': 'income'
            })
            
        # Final Payment (if completed)
        if hd.trang_thai == 'Đã hoàn thành':
            remaining = int(hd.tong_tien_thue) - int(hd.tien_tra_truoc)
            if remaining > 0:
                dt_final = hd.ngay_ket_thuc_thuc_te or hd.ngay_ket_thuc_du_kien
                total_income += remaining
                transactions.append({
                    'date': dt_final.date(),
                    'title': f"Thanh toán nốt HĐ {hd.ma_hd} - {hd.khach_hang.ho_ten}",
                    'category': 'HỢP ĐỒNG',
                    'income': int(remaining),
                    'expense': 0,
                    'ref': hd.ma_hd,
                    'type': 'income'
                })

    # 2. Income/Expense from Return Slips (PhieuTraXe)
    returns_qs = PhieuTraXe.objects.select_related('hop_dong__khach_hang')
    for tx in returns_qs:
        # Extra fees (Income)
        extra = int(tx.phat_qua_han) + int(tx.phu_phi_khac)
        if extra > 0:
            total_income += extra
            transactions.append({
                'date': tx.ngay_tra_thuc_te.date(),
                'title': f"Phụ thu HĐ {tx.hop_dong.ma_hd} ({tx.ghi_chu or 'Khác'})",
                'category': 'PHỤ THU',
                'income': int(extra),
                'expense': 0,
                'ref': tx.hop_dong.ma_hd,
                'type': 'income'
            })
        
        # Refunds to customer (Expense)
        if tx.tien_tra_lai_khach > 0:
            total_expense += int(tx.tien_tra_lai_khach)
            transactions.append({
                'date': tx.ngay_tra_thuc_te.date(),
                'title': f"Hoàn tiền HĐ {tx.hop_dong.ma_hd} cho khách",
                'category': 'HOÀN TRẢ',
                'income': 0,
                'expense': int(tx.tien_tra_lai_khach),
                'ref': tx.hop_dong.ma_hd,
                'type': 'expense'
            })

    # 3. Expenses from Maintenance (LichSuBaoTri)
    maintenance_qs = LichSuBaoTri.objects.select_related('xe')
    for mt in maintenance_qs:
        if mt.chi_phi > 0:
            total_expense += int(mt.chi_phi)
            transactions.append({
                'date': mt.ngay_bao_tri,
                'title': f"{mt.loai_bao_tri} - Xe {mt.xe.bien_so}",
                'category': 'SỬA CHỮA',
                'income': 0,
                'expense': int(mt.chi_phi),
                'ref': mt.xe.bien_so,
                'type': 'expense'
            })

    # Sort all transactions by date descending
    transactions.sort(key=lambda x: x['date'], reverse=True)
    net_profit = total_income - total_expense

    # --- SCHEDULER DATA ---
    # Fetch all cars and their rental periods
    cars_qs = Xe.objects.select_related('loai_xe__hang_xe').all()
    cars_data = [{
        'id': xe.bien_so,
        'name': f"{xe.loai_xe.hang_xe.ten_hang} {xe.loai_xe.ten_loai}",
        'plate': xe.bien_so,
        'trang_thai': xe.trang_thai
    } for xe in cars_qs]

    # Fetch all active/upcoming contracts to plot on schedule
    all_contracts = HopDong.objects.prefetch_related('chitiethopdong_set__xe').select_related('khach_hang').all()
    
    scheduler_events = []
    
    # 1. Add Maintenance Events
    maintenance_logs = LichSuBaoTri.objects.select_related('xe').filter(ngay_ket_thuc__isnull=False)
    for mt in maintenance_logs:
        s_date = mt.ngay_bao_tri.strftime('%Y-%m-%dT%H:%M:%S')
        e_date = mt.ngay_ket_thuc.strftime('%Y-%m-%dT23:59:59')
        scheduler_events.append({
            'carId': mt.xe.bien_so,
            'start': s_date,
            'end': e_date,
            'status': 'maintenance',
            'title': f"Bảo trì: {mt.loai_bao_tri}"
        })

    # 2. Add Contract Events
    for hd in all_contracts:
        for detail in hd.chitiethopdong_set.all():
            status_class = 'renting'
            
            if hd.trang_thai == 'Quá hạn': 
                status_class = 'overdue'
            elif hd.trang_thai in ['Đang thuê', 'Mới', 'Chờ nhận xe', 'Đặt trước']:
                # Deterministic check for status
                if hd.ngay_bat_dau > now:
                    status_class = 'booked'
                else:
                    # Check for "Sắp đến hạn trả" (< 1 day)
                    remaining_seconds = (hd.ngay_ket_thuc_du_kien - now).total_seconds()
                    if 0 < remaining_seconds < 86400:
                        status_class = 'upcoming'
                    else:
                        status_class = 'renting'

            scheduler_events.append({
                'carId': detail.xe.bien_so,
                'start': hd.ngay_bat_dau.isoformat(),
                'end': hd.ngay_ket_thuc_du_kien.isoformat(),
                'status': status_class,
                'title': f"{hd.ma_hd}: {hd.khach_hang.ho_ten}"
            })

    context = {
        'active_page': 'tong-quan',
        'count_all': count_all,
        'total_revenue': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'attention_contracts': attention_contracts_qs,
        'top_cars': top_cars,
        'transactions': transactions,
        'cars_json': json.dumps(cars_data),
        'scheduler_events_json': json.dumps(scheduler_events),
        'today': today,
    }
    return render(request, 'dashboard.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Auto-create the tester user if it doesn't exist
    if not User.objects.filter(username='n2tester').exists():
        User.objects.create_user(username='n2tester', password='@n2tester', is_staff=True, is_superuser=True)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

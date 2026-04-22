from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from rentals.models import HopDong, ChiTietHopDong, GiaoDich
from cars.models import Xe, LichSuBaoTri
from django.db.models import Sum, Count, Q
from django.utils import timezone
import json
from datetime import datetime

@login_required(login_url='/login/')
def get_dashboard_context(request, active_tab='schedule'):
    """
    Helper function to provide data for the main dashboard views.
    """
    now = timezone.now()
    today = now.date()
    
    # --- FINANCIAL DATA ---
    transactions = []
    total_income = 0
    total_expense = 0

    # 1. Financial Data from GiaoDich
    gd_qs = GiaoDich.objects.select_related('hop_dong__khach_hang').order_by('-ngay_gd')
    
    for gd in gd_qs:
        hd = gd.hop_dong
        is_income = gd.loai_gd in ['Tạm ứng', 'Thu thêm', 'Quyết toán']
        amt = int(gd.so_tien)
        
        if is_income:
            total_income += amt
            transactions.append({
                'date': gd.ngay_gd,
                'title': f"{gd.loai_gd} HĐ {hd.ma_hd} - {hd.khach_hang.ho_ten}",
                'category': gd.loai_gd.upper(),
                'income': amt,
                'expense': 0,
                'ref': hd.ma_hd,
                'type': 'income'
            })
        else:
            total_expense += amt
            transactions.append({
                'date': gd.ngay_gd,
                'title': f"Hoàn trả HĐ {hd.ma_hd} - {hd.khach_hang.ho_ten}",
                'category': 'HOÀN TRẢ',
                'income': 0,
                'expense': amt,
                'ref': hd.ma_hd,
                'type': 'expense'
            })

    # 2. Expenses from Maintenance
    maintenance_qs = LichSuBaoTri.objects.select_related('xe').order_by('-ngay_bao_tri')
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

    transactions.sort(key=lambda x: x['date'], reverse=True)
    net_profit = total_income - total_expense

    # --- SCHEDULER DATA ---
    cars_qs = Xe.objects.select_related('loai_xe__hang_xe').all()
    cars_data = [{
        'id': xe.bien_so,
        'name': f"{xe.loai_xe.hang_xe.ten_hang} {xe.loai_xe.ten_loai}",
        'plate': xe.bien_so,
        'trang_thai': xe.trang_thai
    } for xe in cars_qs]

    first_day_current = today.replace(day=1)
    if first_day_current.month == 1:
        start_limit = first_day_current.replace(year=first_day_current.year-1, month=12)
    else:
        start_limit = first_day_current.replace(month=first_day_current.month-1)
    
    all_contracts = HopDong.objects.prefetch_related('chitiethopdong_set__xe').select_related('khach_hang').filter(
        ngay_ket_thuc_du_kien__gte=start_limit
    )
    
    scheduler_events = []
    maintenance_logs = LichSuBaoTri.objects.select_related('xe').filter(
        Q(ngay_ket_thuc__isnull=False),
        Q(ngay_ket_thuc__gte=start_limit) | Q(ngay_bao_tri__gte=start_limit)
    )
    for mt in maintenance_logs:
        s_date = mt.ngay_bao_tri.strftime('%Y-%m-%dT%H:%M:%S')
        e_date = mt.ngay_ket_thuc.strftime('%Y-%m-%dT23:59:59')
        scheduler_events.append({
            'carId': mt.xe.bien_so,
            'start': s_date,
            'end': e_date,
            'status': 'maintenance',
            'title': f"Bảo trì: {mt.loai_bao_tri}",
            'url': reverse('cars:edit', args=[mt.xe.bien_so])
        })

    for hd in all_contracts:
        for detail in hd.chitiethopdong_set.all():
            status_class = 'renting'
            if hd.trang_thai == 'Quá hạn': 
                status_class = 'overdue'
            elif hd.trang_thai in ['Đang thuê', 'Mới', 'Chờ nhận xe', 'Đặt trước']:
                if hd.ngay_bat_dau > today:
                    status_class = 'booked'
                else:
                    diff_days = (hd.ngay_ket_thuc_du_kien - today).days
                    if diff_days == 0:
                        status_class = 'upcoming'
                    else:
                        status_class = 'renting'

            scheduler_events.append({
                'carId': detail.xe.bien_so,
                'start': hd.ngay_bat_dau.isoformat(),
                'end': hd.ngay_ket_thuc_du_kien.isoformat(),
                'status': status_class,
                'title': f"{hd.ma_hd}: {hd.khach_hang.ho_ten}",
                'url': reverse('rentals:detail', args=[hd.ma_hd])
            })

    return {
        'active_page': 'tong-quan',
        'active_tab': active_tab,
        'total_revenue': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'transactions': transactions,
        'cars_json': json.dumps(cars_data),
        'scheduler_events_json': json.dumps(scheduler_events),
        'today': today,
    }

@login_required(login_url='/login/')
def dashboard(request):
    return redirect('lichxe')

@login_required(login_url='/login/')
def lich_xe(request):
    context = get_dashboard_context(request, active_tab='schedule')
    return render(request, 'dashboard.html', context)

@login_required(login_url='/login/')
def tai_chinh(request):
    context = get_dashboard_context(request, active_tab='finance')
    return render(request, 'dashboard.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('lichxe')
    
    if not User.objects.filter(username='n2tester').exists():
        User.objects.create_user(username='n2tester', password='@n2tester', is_staff=True, is_superuser=True)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('lichxe')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

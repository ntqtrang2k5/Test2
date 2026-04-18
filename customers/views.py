import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import KhachHang

def customer_list(request):
    customers = KhachHang.objects.all().order_by('ma_kh')
    
    last_customer = KhachHang.objects.order_by('-ma_kh').first()
    if last_customer:
        try:
            last_num = int(last_customer.ma_kh[2:])
            next_id = f"KH{last_num + 1:03d}"
        except ValueError:
            next_id = "KH001"
    else:
        next_id = "KH001"

    context = {
        'customers': customers,
        'active_page': 'khach-hang',
        'next_kh_id': next_id
    }
    return render(request, 'customers/list.html', context)

import re

@require_POST
def save_customer(request):
    try:
        data = json.loads(request.body)
        ma_kh = data.get('id', '').strip()
        ho_ten = data.get('name', '').strip()
        so_dien_thoai = data.get('phone', '').strip()
        cccd = data.get('cccd', '').strip()

        # 2a. Tên không được chứa số/ký tự đặc biệt và không được để trống
        name_regex = r'^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴÝỶỸửữựỳỵỷỹýỹ\s]+$'
        if not ho_ten or not re.match(name_regex, ho_ten):
            return JsonResponse({'success': False, 'message': 'Họ tên không hợp lệ (không được chứa số hoặc ký tự đặc biệt)'})

        # 3a. Số điện thoại phải 10 số, bắt đầu bằng 0
        if not re.match(r'^0\d{9}$', so_dien_thoai):
            return JsonResponse({'success': False, 'message': 'SĐT không hợp lệ (phải có 10 số và bắt đầu bằng số 0)'})

        # 4a. CCCD phải đủ 12 số
        if not re.match(r'^\d{12}$', cccd):
            return JsonResponse({'success': False, 'message': 'CCCD không hợp lệ (phải có đúng 12 số)'})

        # Số điện thoại và CCCD phải là duy nhất (không trùng lặp với KH khác)
        if KhachHang.objects.filter(so_dien_thoai=so_dien_thoai).exclude(ma_kh=ma_kh).exists():
            return JsonResponse({'success': False, 'message': 'Số điện thoại đã bị trùng với khách hàng khác. Vui lòng nhập lại.'})
            
        if KhachHang.objects.filter(cccd=cccd).exclude(ma_kh=ma_kh).exists():
            return JsonResponse({'success': False, 'message': 'CCCD này đã tồn tại trong hệ thống. Vui lòng kiểm tra lại.'})

        # Lưu dữ liệu
        KhachHang.objects.update_or_create(
            ma_kh=ma_kh,
            defaults={
                'ho_ten': ho_ten,
                'so_dien_thoai': so_dien_thoai,
                'cccd': cccd
            }
        )
        return JsonResponse({'success': True, 'message': 'Lưu thông tin khách hàng thành công'})

    except Exception as e:
        # 6a. Lưu không thành công do lỗi code/server
        return JsonResponse({'success': False, 'message': 'Không thể lưu thông tin khách hàng'})

@require_POST
def delete_customer(request):
    try:
        data = json.loads(request.body)
        ma_kh = data.get('id')
        KhachHang.objects.filter(ma_kh=ma_kh).delete()
        return JsonResponse({'success': True, 'message': 'Đã xóa khách hàng thành công!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

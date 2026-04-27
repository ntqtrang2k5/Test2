# Test Cases: Xóa Thông Tin Xe

# Sheet: Xóa thông tin xe

## TC-XE-D01: Xóa xe thành công
**Steps:**
1.Chọn xe
2.Click xóa
3.Xác nhận xóa

**Expected:**
Xóa thành công

---

## TC-XE-D02: Xe có hợp đồng đang hiệu lực
**Steps:**
1.Chọn xe
2.Click xóa
3.Xác nhận xóa

**Expected:**
Không cho xóa

---

## TC-XE-D03: Click hủy xóa
**Steps:**
1.Chọn xe
2.Click xóa
3.Click cancel

**Expected:**
Không xóa

---

## TC-XE-D04: Xe đang trạng thái bảo trì
**Steps:**
1.Chọn xe
2.Click xóa

**Expected:**
Xóa thành công

---

## TC-XE-D05: Xe đang trạng thái đang thuê
**Steps:**
1.Chọn xe
2.Click xóa

**Expected:**
Hiển thị thông báo lỗi và không xóa

---

## TC-XE-D06: Xóa xe sau khi hợp đồng kết thúc
**Steps:**
1.Chọn xe
2.Click xóa

**Expected:**
Xóa thành công

---

## TC-XE-D07: Confirm popup hiển thị
**Steps:**
1.Click xóa

**Expected:**
Popup xác nhận

---

## TC-XE-G01: Hiển thị nút Xóa
**Steps:**
1. Quan sát danh sách xe

**Expected:**
Nút "Xóa" hiển thị rõ ràng trên mỗi dòng xe

---

## TC-XE-G02: Enable nút Xóa khi chọn xe
**Steps:**
1. Chọn 1 xe

**Expected:**
Nút "Xóa" được enable

---

## TC-XE-G03: Disable khi chưa chọn xe
**Steps:**
1. Không chọn xe

**Expected:**
Nút "Xóa" bị disable

---

## TC-XE-G04: Hiển thị popup xác nhận
**Steps:**
1. Click "Xóa"

**Expected:**
Hiển thị popup xác nhận "Bạn có chắc chắn muốn xóa?"

---

## TC-XE-G05: Nội dung popup
**Steps:**
1. Quan sát popup

**Expected:**
Popup hiển thị đầy đủ: tiêu đề, nội dung, nút Xác nhận/Hủy

---

## TC-XE-G06: Nút Xác nhận trong popup
**Steps:**
1. Click "Xóa" 

**Expected:**
Nút hoạt động bình thường, click được

---

## TC-XE-G07: 
**Steps:**
2. Click "Xác nhận"

**Expected:**


---

## TC-XE-G08: Nút Hủy trong popup
**Steps:**
1. Click "Xóa" 

**Expected:**
Đóng popup, không thực hiện xóa

---

## TC-XE-G09: 
**Steps:**
2. Click "Hủy"

**Expected:**


---

## TC-XE-G10: Đóng popup bằng nút X
**Steps:**
1. Click "X" trên popup

**Expected:**
Popup đóng, không xóa dữ liệu

---

## TC-XE-G11: Hiển thị thông báo sau xóa
**Steps:**
1. Xóa thành công

**Expected:**
Hiển thị message "Xóa xe thành công"

---

## TC-XE-G12: Hiển thị lỗi khi không cho xóa
**Steps:**
1. Xóa xe đang thuê

**Expected:**
Hiển thị thông báo lỗi rõ ràng

---

## TC-XE-G13: Cập nhật danh sách sau xóa
**Steps:**
1. Xóa xe thành công

**Expected:**
Xe bị xóa khỏi danh sách ngay lập tức

---

## TC-XE-G14: Highlight dòng được chọn
**Steps:**
1. Chọn xe

**Expected:**
Dòng được chọn được highlight rõ ràng

---

## TC-XE-G15: Loading khi xóa
**Steps:**
1. Click xác nhận xóa

**Expected:**
Hiển thị loading (nếu có) tránh click nhiều lần

---

## TC-XE-G16: Không bị double click
**Steps:**
1. Click Xóa nhiều lần nhanh

**Expected:**
Chỉ thực hiện 1 lần xóa

---

## TC-XE-G17: Font & màu popup
**Steps:**
1. Quan sát popup

**Expected:**
Giao diện rõ ràng, dễ đọc, đúng chuẩn UI

---


# Car Edit Test Cases

## TC-XE-U01: Chỉnh sửa thành công
**Steps:**
- 1. Chọn xe cần sửa
- 2. Nhấn nút "Chỉnh sửa"
- 3.Cập nhật thông tin Hãng xe
- 4. Cập nhật Loại xe
- 5. Chỉnh sửa biển số xe, Năm sản xuất, Màu xe, Kiểu dáng, Giá thuê ngày, Trạng thái
- 6. Nhấn "Lưu"

**Expected:**
- Loại xe, Số chỗ reset lại 
Xuất xứ tự động cập nhật
- Số chỗ tự động cập nhật
- Cập nhật thành công và hiển thị thông báo "Cập nhật thông tin xe thành công"

**Test Data:** Hãng xe = Toyota
Loại xe = Vios
Biển số = 43A-11111
Năm SX = 2022
Màu = Trắng
Số chỗ = 5
Kiểu dáng = Sedan
Xuất xứ = Nhật
Giá = 500000
Trạng thái = Sẵn sàng

---

## TC-XE-U02: Chỉnh sửa biển số trùng
**Steps:**
- 1. Chọn xe cần sửa
- 2. Nhấn chỉnh sửa
- 3. Nhập biển số đã tồn tại
- 4. Nhấn lưu

**Expected:**
- Không cho lưu và hiển thị "Biển số xe đã tồn tại"

**Test Data:** Biển số = 43A-12345 (đã tồn tại)

---

## TC-XE-U03: Giá thuê quá nhỏ
**Steps:**
- 1. Chọn xe cần chỉnh sửa
- 2. Nhấn "Chỉnh sửa"
- 3. Sửa giá thuê
- 4. Click "Lưu"

**Expected:**
- Không cập nhật và hiển thị "Giá thuê từ 300k - 3 triệu"

**Test Data:** Giá thuê ngày = -100000

---

## F0004: Bỏ trống tên xe
**Steps:**
- 
3.Xóa tên
4.Click lưu

**Expected:**
- 

**Test Data:** None

---

## TC-XE-U04: Bỏ trống biển số
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 3. Xóa biển số
- 4. Nhấn lưu

**Expected:**
- Không lưu và hiển thị "Biển số xe không được để trống"

**Test Data:** Biển số xe = ""

---

## F0006: Năm SX lớn hơn hiện tại
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 2. Sửa năm sản xuất > năm hiện tại
- 3. Lưu

**Expected:**
- Không cập nhật và hiển thị "Năm sản xuất không hợp lệ"

**Test Data:** Năm sản xuất = 2030

---

## F0007: Số chỗ âm
**Steps:**
- 
3.Sửa số chỗ
4.Click lưu

**Expected:**
- 

**Test Data:** None

---

## F0008: Không thay đổi dữ liệu
**Steps:**
- 
3.Click lưu

**Expected:**
- Hiển thị thông báo "Không có thay đổi"

**Test Data:** None

---

## TC-XE-U05: Bỏ trống giá thuê
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 3. Xóa giá thuê
- 4. Lưu

**Expected:**
- Không cập nhật và hiển thị "Giá thuê không được để trống"

**Test Data:** Giá thuê ngày = ""

---

## F0010: Sửa trạng thái
**Steps:**
- 1.Chọn xe
2.Click sửa
3.Sửa trạng thái
4.Click lưu

**Expected:**
- 

**Test Data:** None

---

## TC-XE-U06: Click hủy chỉnh sửa
**Steps:**
- 1. Chọn xe cần chỉnh sửa
- 2. Nhấn nút "Chỉnh sửa"
- 3. Thay đổi thông tin bất kỳ
- 4. Nhấn "Hủy thay đổi"

**Expected:**
- Hiển thị thông báo xác nhận "Bạn chưa lưu thông tin, có muốn hủy?"

**Test Data:** -

---

## TC-XE-U07: Chỉnh sửa hãng xe
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 3. CHỌN Hãng xe khác
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 2. Xóa hãng xe
- 3. Lưu

**Expected:**
- Loại xe reset
Số chỗ reset
Xuất xứ auto-fill lại
- "Loại xe reset
Kiểu dáng reset
Số chỗ auto-fill lại
Xuất xứ auto-fill lại"
- Không lưu và hiển thị "Vui lòng nhập đầy đủ thông tin bắt buộc"

**Test Data:** Hãng xe = "Toyota"

---

## F0014: Bỏ trống loại xe
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 2. Xóa loại xe
- 3. Lưu

**Expected:**
- Số chỗ cập nhật lại
Không cho nhập tay nếu bị disable
- Không lưu và hiển thị "Vui lòng nhập đầy đủ thông tin bắt buộc"

**Test Data:** Loại xe = ""

---

## F0015: Bỏ trống kiểu dáng
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 2. Xóa kiểu dáng
- 3. Lưu

**Expected:**
- Không lưu và hiển thị "Vui lòng nhập đầy đủ thông tin bắt buộc"

**Test Data:** Kiểu dáng = ""

---

## F0017: Nhập ký tự đặc biệt biển số
**Steps:**
- 
3.Sửa biển số
4.Click lưu

**Expected:**
- Không cập nhật và hiển thị "Biển số không hợp lệ"

**Test Data:** Biển số = 43A@12345

---

## F0018: Nhập số chỗ bằng chữ
**Steps:**
- 1.Chọn xe
2.Click sửa
3.Sửa số chỗ
4.Click lưu

**Expected:**
- 

**Test Data:** None

---

## TC-XE-U08: Nhập giá thuê bằng chữ
**Steps:**
- 1. Chọn xe cần chỉnh sửa
- 2. Nhấn "Chỉnh sửa"
- 3. Sửa giá
- 4. Click lưu

**Expected:**
- Không cho nhập giá thuê bằng chữ và ký tự đặc biệt
- Không cập nhật và hiển thị "Giá thuê ngày không được để trống"

**Test Data:** Giá thuê = abc

---

## F0021: Nhập số chỗ = 0
**Steps:**
- 1.Chọn xe
2.Click sửa
3.Sửa số chỗ
4.Click lưu

**Expected:**
- 

**Test Data:** None

---

## F0022: Nhập giá thuê = 0
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 3. Nhập giá thuê = 0
- 4. Nhấn lưu

**Expected:**
- Không lưu và hiển thị "Giá thuê phải lớn hơn 0"

**Test Data:** Giá thuê ngày = 0

---

## F0020: Sửa nhiều trường cùng lúc
**Steps:**
- 1.Chọn xe
2.Click sửa
3.Sửa nhiều field
4.Click lưu

**Expected:**
- Cập nhật thành công

**Test Data:** Tên xe = Mazda CX5
Năm sản xuất = 2022
Màu xe = Trắng
Dòng xe = SUV
Biển số xe = 43A-66666
Số chỗ xe = 5
Giá ngày thuê = 850000
Trạng thái = Sẵn sàng

---

## TC-XE-U09: Giá thuê quá lớn
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 3. Nhập giá > 3 triệu
- 4. Lưu

**Expected:**
- Không lưu và hiển thị "Giá thuê từ 300k - 3 triệu"

**Test Data:** Giá thuê = 10000000

---

## TC-XE-U10: Sai định dạng biển số
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 3. Nhập biển số sai định dạng
- 4. Lưu

**Expected:**
- Không lưu và hiển thị "Biển số xe không đúng định dạng (VD: 43A-123.45)."

**Test Data:** Biển số xe = ABC123

---

## TC-XE-U11: Nhập khoảng trắng biển số
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 3. Nhập biển số có khoảng trắng
- 4. Lưu

**Expected:**
- Không lưu và hiển thị "Biển số xe không được để trống."

**Test Data:** Biển số xe = " "

---

## TC-XE-U12: Nhập khoảng trắng giá thuê
**Steps:**
- 1. Chọn xe
- 2. Nhấn chỉnh sửa
- 3. Nhập giá thuê có khoảng trắng
- 4. Lưu

**Expected:**
- Không lưu và hiển thị "Giá thuê ngày không được để trống"

**Test Data:** Giá thuê = " "

---

## TC-XE-U13: Chỉnh sửa biển số nhưng chỉ khác chữ hoa thường
**Steps:**
- 1. Chọn xe cần chỉnh sửa
- 2. Nhấn nút "Chỉnh sửa"
- 3. Nhập biển số chỉ khác chữ hoa thường
- 4. Nhấn "Lưu"

**Expected:**
- Tự động in hoa
- Lưu thông tin xe và hiển thị: "Biển số xe không được trùng"

**Test Data:** DB: 43A-12345
Edit: 43a-12345

---

## TC-XE-U14: Chỉnh sửa trạng thái xe
**Steps:**
- 1. Chọn xe cần chỉnh sửa
- 2. Nhấn nút "Chỉnh sửa"
- 3. CHỌN trạng thái khác
- 4. Nhấn "Lưu"

**Expected:**
- Cập nhật thành công và hiển thị: "Cập nhật thông tin xe thành công!"

**Test Data:** 
Trạng thái = Bảo trì

---

## TC-XE-G01: Hiển thị form chỉnh sửa
**Steps:**
- 1. Chọn xe 2. Click "Chỉnh sửa"

**Expected:**
- Hiển thị form chỉnh sửa với dữ liệu cũ được fill sẵn

**Test Data:** None

---

## TC-XE-G02: Hiển thị dữ liệu ban đầu
**Steps:**
- 1. Mở form chỉnh sửa

**Expected:**
- Tất cả field hiển thị đúng dữ liệu của xe đã chọn

**Test Data:** None

---

## TC-XE-G03: Disable Số chỗ
**Steps:**
- 1. Quan sát field Số chỗ

**Expected:**
- Số chỗ không cho nhập tay (disable)

**Test Data:** None

---

## TC-XE-G04: Disable Xuất xứ
**Steps:**
- 1. Quan sát field Xuất xứ

**Expected:**
- Xuất xứ auto-fill và không cho sửa

**Test Data:** None

---

## TC-XE-G05: Dropdown hoạt động đúng
**Steps:**
- 1. Click dropdown Hãng, Loại, Kiểu dáng

**Expected:**
- Hiển thị danh sách đúng

**Test Data:** None

---

## TC-XE-G06: Reset khi đổi hãng xe
**Steps:**
- 1. Đổi hãng xe

**Expected:**
- Loại xe reset, Số chỗ reset, Xuất xứ cập nhật lại

**Test Data:** None

---

## TC-XE-G07: Auto-fill khi đổi loại xe
**Steps:**
- 1. Đổi loại xe

**Expected:**
- Số chỗ tự động cập nhật

**Test Data:** None

---

## TC-XE-G08: Input biển số
**Steps:**
- 1. Nhập biển số

**Expected:**
- Hiển thị đúng format, canh trái

**Test Data:** None

---

## TC-XE-G09: Input giá thuê
**Steps:**
- 1. Nhập giá

**Expected:**
- Chỉ cho nhập số

**Test Data:** None

---

## TC-XE-G10: Button Lưu
**Steps:**
- 1. Quan sát nút

**Expected:**
- Nút “Lưu” hiển thị rõ, click được

**Test Data:** None

---

## TC-XE-G11: Button Hủy
**Steps:**
- 1. Quan sát nút

**Expected:**
- Có nút “Hủy thay đổi”

**Test Data:** None

---

## TC-XE-G12: Căn chỉnh layout
**Steps:**
- 1. Quan sát form

**Expected:**
- Các field thẳng hàng, không lệch

**Test Data:** None

---

## TC-XE-G13: Tab order
**Steps:**
- 1. Nhấn Tab

**Expected:**
- Di chuyển đúng thứ tự field

**Test Data:** None

---

## TC-XE-G14: Hiển thị thông báo lỗi
**Steps:**
- 1. Nhập sai dữ liệu
- 2. Click Lưu

**Expected:**
- Thông báo lỗi hiển thị rõ ràng

**Test Data:** None

---

## TC-XE-G15: Highlight field lỗi
**Steps:**
- 1. Nhập sai

**Expected:**
- Field lỗi được highlight (viền đỏ hoặc thông báo dưới field)

**Test Data:** None

---

## TC-XE-G16: Responsive form
**Steps:**
- 1. Resize màn hình

**Expected:**
- Không vỡ giao diện

**Test Data:** None

---

## TC-XE-G17: Font & màu sắc
**Steps:**
- 1. Quan sát UI

**Expected:**
- Đồng bộ, dễ nhìn

**Test Data:** None

---


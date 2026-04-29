# THIẾT KẾ CƠ SỞ DỮ LIỆU - DỰ ÁN CARRENT

## PHẦN 1: THIẾT KẾ 3 MỨC (CONCEPTUAL, LOGICAL, PHYSICAL)

### 1. Mức khái niệm (Conceptual Design)
Thiết kế mức khái niệm là quá trình xác định các thực thể (Entities), thuộc tính của chúng (Attributes) và mối quan hệ (Relationships) mà không quan tâm đến hệ quản trị cơ sở dữ liệu (DBMS) cụ thể.
*   **Thực thể chính:** Xe, Khách Hàng, Hợp Đồng Thuê.
*   **Thực thể danh mục (từ điển):** Quốc Gia, Hãng Xe, Kiểu Xe, Màu Sắc, Loại Xe.
*   **Thực thể phụ thuộc/Quá trình:** Lịch Sử Bảo Trì, Phiếu Trả Xe, Chi Tiết Hợp Đồng, Lịch Sử Thay Đổi Hợp Đồng, Giao Dịch.
*   **Mối quan hệ:**
    *   *Quốc Gia - Hãng Xe (1-N)*: Một quốc gia có nhiều hãng xe.
    *   *Hãng Xe - Loại Xe (1-N)*: Một hãng xe sản xuất nhiều loại xe.
    *   *Loại Xe, Màu Sắc, Kiểu Xe - Xe (1-N)*: Một chiếc xe thuộc một loại, màu sắc và kiểu cụ thể.
    *   *Khách Hàng - Hợp Đồng (1-N)*: Một khách hàng có thể thuê nhiều lần (có nhiều hợp đồng).
    *   *Hợp Đồng - Xe (N-N)*: Một hợp đồng có thể thuê nhiều xe, một xe có thể được thuê trong nhiều hợp đồng (tại các thời điểm khác nhau). Mối quan hệ này được giải quyết bằng thực thể trung gian là *Chi Tiết Hợp Đồng*.
    *   *Hợp Đồng - Phiếu Trả Xe, Giao Dịch, Lịch Sử Thay Đổi (1-N)*: Mỗi hợp đồng có thể sinh ra các giao dịch, lịch sử và phiếu trả xe tương ứng.

### 2. Mức logic (Logical Design)
Thiết kế mức logic chuyển đổi mô hình khái niệm thành cấu trúc dữ liệu quan hệ (Relational Model), xác định các bảng (Tables), Khóa chính (Primary Keys - PK), Khóa ngoại (Foreign Keys - FK) để chuẩn hóa dữ liệu.
*   Giải quyết triệt để quan hệ N-N giữa `Hợp Đồng` và `Xe` thông qua bảng `Chi Tiết Hợp Đồng` (chứa `ma_hd` và `bien_so_xe`).
*   Xác định các quy tắc toàn vẹn tham chiếu (Referential Integrity): Ví dụ, không thể xóa `Hãng Xe` nếu đã có `Loại Xe` liên kết tới nó (Ràng buộc RESTRICT). Xóa `Hợp Đồng` sẽ tự động xóa `Chi Tiết Hợp Đồng` (Ràng buộc CASCADE).

### 3. Mức vật lý (Physical Design)
Thiết kế mức vật lý ánh xạ trực tiếp mô hình logic xuống DBMS thực tế. Dưới đây là chi tiết các bảng vật lý.

---

## PHẦN 2: CHI TIẾT CÁC BẢNG (PHYSICAL SCHEMA)

### 1. Bảng QUOCGIA (Danh mục Quốc Gia)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `ma_quoc_gia` | VARCHAR(10) | **Khóa chính (PK)**, NOT NULL | Mã quốc gia |
| `ten_quoc_gia` | VARCHAR(100) | UNIQUE, NOT NULL | Tên quốc gia |

### 2. Bảng KIEUXE (Danh mục Kiểu Xe)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `ma_kieu` | VARCHAR(10) | **Khóa chính (PK)**, NOT NULL | Mã kiểu xe |
| `ten_kieu` | VARCHAR(100) | UNIQUE, NOT NULL | Tên kiểu xe |

### 3. Bảng MAUSAC (Danh mục Màu Sắc)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `ma_mau` | VARCHAR(10) | **Khóa chính (PK)**, NOT NULL | Mã màu |
| `ten_mau` | VARCHAR(50) | UNIQUE, NOT NULL | Tên màu sơn |

### 4. Bảng HANGXE (Danh mục Hãng Xe)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `ma_hang` | VARCHAR(10) | **Khóa chính (PK)**, NOT NULL | Mã hãng xe |
| `ten_hang` | VARCHAR(100) | UNIQUE, NOT NULL | Tên hãng xe |
| `quoc_gia_id` | VARCHAR(10) | **Khóa ngoại (FK)**, NOT NULL, RESTRICT | Tới QUOCGIA |

### 5. Bảng LOAIXE (Danh mục Loại Xe)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `ma_loai` | VARCHAR(10) | **Khóa chính (PK)**, NOT NULL | Mã loại xe |
| `ten_loai` | VARCHAR(100) | UNIQUE, NOT NULL | Tên loại xe |
| `hang_xe_id` | VARCHAR(10) | **Khóa ngoại (FK)**, NOT NULL, RESTRICT | Tới HANGXE |
| `kieu_xe_id` | VARCHAR(10) | **Khóa ngoại (FK)**, NULL, RESTRICT | Tới KIEUXE |
| `so_cho_ngoi` | INTEGER | NOT NULL | Số lượng chỗ ngồi |

### 6. Bảng XE (Thông tin Xe)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `bien_so` | VARCHAR(20) | **Khóa chính (PK)**, NOT NULL | Biển số xe |
| `loai_xe_id` | VARCHAR(10) | **Khóa ngoại (FK)**, NOT NULL, RESTRICT | Tới LOAIXE |
| `mau_sac_id` | VARCHAR(10) | **Khóa ngoại (FK)**, NOT NULL, RESTRICT | Tới MAUSAC |
| `kieu_xe_id` | VARCHAR(10) | **Khóa ngoại (FK)**, NULL, RESTRICT | Tới KIEUXE |
| `nam_san_xuat` | INTEGER | DEFAULT 2022, NOT NULL | Năm sản xuất |
| `gia_thue_ngay` | INTEGER | NOT NULL | Giá thuê ngày |
| `trang_thai` | VARCHAR(50) | DEFAULT 'Sẵn sàng', NOT NULL | Trạng thái hoạt động |

### 7. Bảng LICHSUBAOTRI (Lịch Sử Bảo Trì)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `ma_bao_tri` | INTEGER | **Khóa chính (PK)**, AUTO INCREMENT | Mã bảo trì |
| `xe_id` | VARCHAR(20) | **Khóa ngoại (FK)**, NOT NULL, CASCADE | Tới XE |
| `loai_bao_tri` | VARCHAR(100) | NOT NULL | Loại bảo trì |
| `ngay_bao_tri` | DATE | NOT NULL | Ngày bắt đầu bảo trì |
| `ngay_ket_thuc` | DATE | NULL | Ngày kết thúc |
| `noi_dung_chi_tiet`| VARCHAR(255) | NULL | Nội dung chi tiết |
| `chi_phi` | INTEGER | NOT NULL | Chi phí |

### 8. Bảng KHACHHANG (Khách Hàng)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `ma_kh` | VARCHAR(10) | **Khóa chính (PK)**, NOT NULL | Mã khách hàng |
| `ho_ten` | VARCHAR(100) | NOT NULL | Họ và tên |
| `so_dien_thoai` | VARCHAR(15) | NOT NULL | Số điện thoại |
| `cccd` | VARCHAR(20) | UNIQUE, NOT NULL | Căn cước công dân |

### 9. Bảng HOPDONGTHUE (Hợp Đồng Thuê)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `ma_hd` | VARCHAR(10) | **Khóa chính (PK)**, NOT NULL | Mã hợp đồng |
| `khach_hang_id` | VARCHAR(10) | **Khóa ngoại (FK)**, NOT NULL, RESTRICT | Tới KHACHHANG |
| `ngay_lap` | DATETIME | DEFAULT Current Time, NOT NULL | Ngày lập |
| `ngay_bat_dau` | DATE | NOT NULL | Ngày bắt đầu thuê |
| `ngay_ket_thuc...` | DATE | NOT NULL | Ngày kết thúc dự kiến |
| `ngay_ket_thuc...` | DATE | NULL | Ngày kết thúc thực tế |
| `tong_tien_thue` | DECIMAL(18,0)| DEFAULT 0, NOT NULL | Tổng tiền thuê |
| `tien_coc` | DECIMAL(18,0)| DEFAULT 0, NOT NULL | Tiền cọc |
| `tien_tra_truoc` | DECIMAL(18,0)| DEFAULT 0, NOT NULL | Tiền trả trước |
| `trang_thai` | VARCHAR(50) | DEFAULT 'Chờ nhận xe', NOT NULL | Trạng thái |

### 10. Bảng HOPDONGTHUE_CHITIET (Chi Tiết Hợp Đồng)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | **Khóa chính (PK)** | ID tự sinh |
| `hop_dong_id` | VARCHAR(10) | **Khóa ngoại (FK)**, CASCADE | Tới HOPDONGTHUE |
| `xe_id` | VARCHAR(20) | **Khóa ngoại (FK)**, RESTRICT | Tới XE |
| `(Ràng buộc)` | | UNIQUE(hop_dong_id, xe_id) | Unique Together |

### 11. Bảng PHIEUTRAXE (Phiếu Trả Xe)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `ma_tra_xe` | VARCHAR(10) | **Khóa chính (PK)**, NOT NULL | Mã phiếu trả xe |
| `hop_dong_id` | VARCHAR(10) | **Khóa ngoại (FK)**, RESTRICT | Tới HOPDONGTHUE |
| `ngay_tra_thuc_te`| DATE | Auto Add, NOT NULL | Ngày trả thực tế |
| `phat_qua_han` | DECIMAL(18,0)| DEFAULT 0, NOT NULL | Tiền phạt |
| `phu_phi_khac` | DECIMAL(18,0)| DEFAULT 0, NOT NULL | Phụ phí |
| `tien_tra_lai_...`| DECIMAL(18,0)| DEFAULT 0, NOT NULL | Tiền trả lại khách |
| `khach_tra_them` | DECIMAL(18,0)| DEFAULT 0, NOT NULL | Khách trả thêm |
| `ghi_chu` | TEXT | NULL | Ghi chú |

### 12. Bảng HOPDONGTHUE_LICHSU (Lịch Sử Thay Đổi HĐ)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | **Khóa chính (PK)** | ID tự sinh |
| `hop_dong_id` | VARCHAR(10) | **Khóa ngoại (FK)**, CASCADE | Tới HOPDONGTHUE |
| `ngay_thay_doi` | DATETIME | DEFAULT Current Time | Ngày thay đổi |
| `noi_dung` | TEXT | NOT NULL | Nội dung thay đổi |
| `tien_chenh_lech` | DECIMAL(18,0)| DEFAULT 0 | Tiền chênh lệch |

### 13. Bảng HOPDONGTHUE_GIAODICH (Giao Dịch)
| Tên cột | Kiểu dữ liệu | Ràng buộc | Ghi chú |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | **Khóa chính (PK)** | ID tự sinh |
| `hop_dong_id` | VARCHAR(10) | **Khóa ngoại (FK)**, CASCADE | Tới HOPDONGTHUE |
| `ngay_gd` | DATE | DEFAULT Current Date | Ngày giao dịch |
| `so_tien` | DECIMAL(18,0)| NOT NULL | Số tiền |
| `loai_gd` | VARCHAR(50) | NOT NULL | Loại giao dịch |

# Hướng dẫn sử dụng chức năng Xuất Word mới (Phiên bản 3.2)

## Tổng quan

Chức năng "Xuất Word" đã được cải tiến để sử dụng template `TO_KHAI.docx` với thư viện `docxtpl`, cho phép người dùng nhập thông tin kỳ, năm và cơ quan tiếp nhận trước khi xuất tờ khai.

## Các cải tiến mới trong phiên bản 3.2

### 1. **Danh sách nguồn thải được tối ưu**
- Biến `{{danh_sach_nguon_thai}}` giờ chỉ hiển thị tên các nguồn thải, cách nhau bởi dấu phẩy
- Ví dụ: "Nguồn thải 1, Nguồn thải 2, Nguồn thải 3"

### 2. **Thêm trường Cơ quan tiếp nhận**
- Popup xuất tờ khai có thêm trường "Cơ quan tiếp nhận"
- Placeholder mặc định: "Sở Nông nghiệp và Môi trường Thành phố Hồ Chí Minh"
- Trường này bắt buộc phải nhập

### 3. **Cải tiến tên file xuất**
- **Xuất Word**: `{ten_profile}_{ky}_{nam}_{timestamp}.docx`
- **Xuất Excel**: `{ten_profile}_{timestamp}.xlsx`
- Ví dụ: `Plant_1_I_2025_20250907_143022.docx`

### 4. **Tính toán phí môi trường**
- **Phí cố định**: 750,000 VNĐ
- **Phí phát sinh**: Tổng Ci của tất cả nguồn thải
- **Tổng phí**: Phí cố định + Phí phát sinh
- **Chuyển đổi số thành chữ**: Tự động chuyển đổi tổng phí thành chữ

## Các thay đổi chính

### 1. Giao diện người dùng
- Button "Xuất Word" hiện tại sẽ mở một popup modal
- Modal cho phép người dùng chọn:
  - **Kỳ**: I, II, III, IV (dropdown)
  - **Năm**: Từ 2025 đến năm hiện tại (dropdown tự động tạo)
  - **Cơ quan tiếp nhận**: Trường text input (bắt buộc)

### 2. Công nghệ sử dụng
- **docxtpl**: Thư viện template cho Word documents
- **Template**: `TO_KHAI.docx` - file template chính thức
- **Context data**: Dữ liệu được render theo cấu trúc trong `context.txt`

### 3. Cấu trúc dữ liệu xuất

#### Thông tin thời gian
```python
{
    'ky': 'I',           # Kỳ được chọn
    'nam': '2025',       # Năm được chọn
    'quy': 'I',          # Alias cho kỳ
    'co_quan_tiep_nhan': 'Sở Nông nghiệp và Môi trường Thành phố Hồ Chí Minh'
}
```

#### Thông tin công ty
```python
{
    'ten_cong_ty': '...',
    'dia_chi': '...',
    'mst': '...',
    'dien_thoai': '...',
    'fax': '...',
    'email': '...',
    'tai_khoan_ngan_hang': '...',
    'tai_ngan_hang': '...',
    'loai_hinh_san_xuat': '...'
}
```

#### Danh sách nguồn thải
```python
{
    'profile_records': [
        {
            'stt': '1',
            'ten_nguon_thai': '...',
            'luu_luong': 100.0,
            'tong_thoi_gian': 8760.0,
            'thong_tin_don_vi': '...',
            'bui': 50.0,
            'nox': 200.0,
            'sox': 150.0,
            'co': 100.0,
            'ci_bui': 1000000.0,
            'ci_nox': 2000000.0,
            'ci_sox': 1500000.0,
            'ci_co': 500000.0
        }
    ]
}
```

#### Thông tin tổng phí
```python
{
    'phi_co_dinh': 750000,           # Phí cố định 750,000 VNĐ
    'phi_do_dinh': 750000,           # Alias cho phí cố định
    'phi_phat_sinh': 5000000.0,      # Tổng Ci của tất cả nguồn thải
    'tong_phi': 5750000.0,           # Phí cố định + Phí phát sinh
    'result_data': {'Ci': 5000000.0}, # Template sử dụng result_data['Ci']
    'so_tien_bang_chu': 'Năm triệu bảy trăm năm mươi nghìn đồng'
}
```

## Hướng dẫn sử dụng

### Bước 1: Truy cập trang chính
1. Đăng nhập vào hệ thống
2. Chọn profile có dữ liệu nguồn thải

### Bước 2: Xuất Word
1. Click button **"Xuất Word"**
2. Popup modal sẽ hiện ra với 3 trường:
   - **Kỳ**: Chọn I, II, III, hoặc IV
   - **Năm**: Chọn từ danh sách năm (2025 đến năm hiện tại)
   - **Cơ quan tiếp nhận**: Nhập tên cơ quan (bắt buộc)
3. Click **"Xuất Tờ Khai"**

### Bước 3: Tải file
- File Word sẽ được tự động tải về với tên: `{ten_profile}_{ky}_{nam}_{timestamp}.docx`
- Ví dụ: `Plant_1_I_2025_20250907_143022.docx`

## Cấu hình template

### File template: `TO_KHAI.docx`
Template sử dụng cú pháp Jinja2 với các biến:

#### Biến đơn giản:
- `{{ten_cong_ty}}` - Tên công ty
- `{{ky}}` - Kỳ báo cáo
- `{{nam}}` - Năm báo cáo
- `{{mst}}` - Mã số thuế

#### Vòng lặp:
```jinja2
{% for record in profile_records %}
    {{record.stt}} - {{record.ten_nguon_thai}}
    Bụi: {{record.bui}} mg/Nm³
    Ci: {{record.ci_bui}} VNĐ
{% endfor %}
```

#### Danh sách nguồn thải:
```jinja2
{{danh_sach_nguon_thai}}
<!-- Hiển thị: "Nguồn thải 1, Nguồn thải 2, Nguồn thải 3" -->
```

#### Tính toán phí:
```jinja2
Phí cố định: {{phi_co_dinh}} VNĐ
Phí phát sinh: {{result_data['Ci']}} VNĐ
Tổng phí: {{phi_co_dinh + result_data['Ci']}} VNĐ
Hoặc: {{tong_phi}} VNĐ
Bằng chữ: {{so_tien_bang_chu}}
```

## Xử lý lỗi

### Lỗi thường gặp:
1. **Template không tồn tại**: Kiểm tra file `TO_KHAI.docx` trong thư mục gốc
2. **Biến undefined**: Kiểm tra cấu trúc context trong `export_utils.py`
3. **Không có dữ liệu**: Đảm bảo profile có ít nhất 1 nguồn thải

### Debug:
- Kiểm tra log trong terminal khi chạy Flask
- File test có thể tạo để kiểm tra: `test_word_export.py`

## Cài đặt dependencies

```bash
pip install docxtpl==0.16.7
```

## Files liên quan

- `templates/index.html` - Giao diện popup modal
- `flask_app.py` - Route `/export_word_with_time/<int:profile_id>`
- `export_utils.py` - Class `WordExporter.export_with_template()`
- `TO_KHAI.docx` - Template Word chính thức
- `context.txt` - Cấu trúc dữ liệu context

---

## Changelog

### Phiên bản 3.2 (2025-09-07)
- ✅ Cải tiến `{{danh_sach_nguon_thai}}` chỉ hiển thị tên nguồn thải
- ✅ Thêm trường "Cơ quan tiếp nhận" vào popup
- ✅ Cải tiến tên file xuất: `{ten_profile}_{ky}_{nam}_{timestamp}.docx`
- ✅ Cải tiến tên file Excel: `{ten_profile}_{timestamp}.xlsx`
- ✅ Thêm tính toán phí cố định 750,000 VNĐ
- ✅ Tự động tính tổng phí và chuyển đổi thành chữ

### Phiên bản 3.1 (2025-09-07)
- ✅ Sử dụng docxtpl với template TO_KHAI.docx
- ✅ Popup modal cho việc chọn kỳ và năm
- ✅ Context data theo cấu trúc yêu cầu

**Phiên bản hiện tại**: 3.2 với Template Word và cải tiến tên file
**Ngày cập nhật**: 2025-09-07

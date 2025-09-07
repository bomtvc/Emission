# Hệ thống Tính toán Phát thải và Phí Bảo vệ Môi trường

Webapp Flask để nhập dữ liệu phát thải, tính toán phí bảo vệ môi trường và xuất báo cáo Excel/Word.

## Tính năng chính

- 🔐 **Xác thực người dùng**: Đăng ký, đăng nhập, quản lý tài khoản
- 🏭 **Quản lý Profile**: Thông tin cơ sở công nghiệp, công ty
- 📊 **Quản lý nguồn thải**: Thêm, sửa, xóa bản ghi phát thải
- 📤 **Import/Export Excel**: Nhập và xuất dữ liệu Excel
- 📄 **Xuất Word với template**: Tờ khai theo mẫu chính thức
- 💰 **Tính phí tự động**: Phí cố định 750,000 VNĐ + phí phát sinh
- 🔢 **Chuyển số thành chữ**: Tiếng Việt chuẩn
- ⏰ **Chọn kỳ báo cáo**: I, II, III, IV và năm
- 🏢 **Cơ quan tiếp nhận**: Tùy chỉnh theo địa phương

## Cài đặt

1. **Clone hoặc tải về dự án**
2. **Tạo môi trường ảo Python (khuyến nghị)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # hoặc
   source venv/bin/activate  # Linux/Mac
   ```

3. **Cài đặt dependencies**
   ```bash
   # Cách 1: Sử dụng script tự động
   python install_requirements.py

   # Cách 2: Cài đặt thủ công
   pip install -r requirements.txt
   ```

## Chạy ứng dụng

```bash
python flask_app.py
```

Mở trình duyệt và truy cập: `http://127.0.0.1:5000`

## Hướng dẫn sử dụng

### 1. Thêm dữ liệu mới
- Click "Thêm dữ liệu" trên thanh menu
- Nhập đầy đủ thông tin nguồn thải:
  - STT, Tên nguồn thải
  - Lưu lượng (Nm³/h)
  - Tổng thời gian xả thải (Giờ)
  - Thông tin đơn vị phân tích
  - Nồng độ các chất: Bụi, NOx, SOx, CO (mg/Nm³)
  - Tiêu chuẩn tương ứng cho từng chất
- Click "Xem trước tính toán" để kiểm tra kết quả
- Click "Lưu dữ liệu" để hoàn tất

### 2. Xem danh sách và chi tiết
- Trang chủ hiển thị tất cả nguồn thải đã nhập
- Click biểu tượng mắt để xem chi tiết bản ghi
- Click biểu tượng thùng rác để xóa bản ghi

### 3. Xuất báo cáo
- **Excel**: Click "Xuất Excel" để tải file .xlsx với đầy đủ dữ liệu
  - Format: `{ten_profile}_{timestamp}.xlsx`
- **Word**: Click "Xuất Word" để mở popup chọn thông tin
  - Chọn Kỳ: I, II, III, IV
  - Chọn Năm: 2025 đến năm hiện tại
  - Nhập Cơ quan tiếp nhận
  - Format: `{ten_profile}_{ky}_{nam}_{timestamp}.docx`

## Công thức tính toán

### Tính phí môi trường
```
Tổng phí = Phí cố định + Phí phát sinh
         = 750,000 VNĐ + Σ(Ci của tất cả nguồn thải)
```

### Ví dụ tính toán
- **Phí cố định**: 750,000 VNĐ
- **Phí phát sinh**: 1,549 VNĐ (tổng Ci)
- **Tổng phí**: 751,549 VNĐ
- **Bằng chữ**: "Bảy trăm năm mươi một nghìn năm trăm bốn mươi chín đồng"

### Mức thu phí biến đổi
```
Nếu (Tiêu chuẩn - Thực tế)/Tiêu chuẩn × 100 ≥ 0.3 → Hệ số = 0.5
Ngược lại < 0.3 → Hệ số = 0.75
```

### Hệ số phí cố định
- Fee_Bụi = 800 VNĐ
- Fee_NOx = 700 VNĐ
- Fee_SOx = 800 VNĐ
- Fee_CO = 500 VNĐ

### Công thức Ci
```
Ci = Lưu lượng × Thời gian × Nồng độ × Mức thu phí × Fee
Tổng Ci = Ci(Bụi) + Ci(NOx) + Ci(SOx) + Ci(CO)
```

## Cấu trúc dự án

```
Emission/
├── flask_app.py           # Ứng dụng chính Flask
├── database.py            # Models cơ sở dữ liệu
├── auth.py               # Xác thực người dùng
├── export_utils.py       # Xuất Excel/Word
├── emission.db           # Database SQLite
├── TO_KHAI.docx         # Template Word
├── requirements.txt      # Dependencies
├── install_requirements.py # Script cài đặt
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── add_record.html
│   └── view_record.html
├── static/             # CSS, JS, images
└── venv/              # Virtual environment
```

## Công nghệ sử dụng

- **Backend**: Flask 3.1.2, SQLAlchemy 2.0.43
- **Database**: SQLite (emission.db)
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **Excel**: OpenPyXL 3.1.5
- **Word**: python-docx 1.2.0, docxtpl 0.16.7
- **Data**: Pandas 2.3.2, NumPy 2.3.2

## Phiên bản

**v3.2** - Cập nhật 2025-09-07
- ✅ Template Word với docxtpl
- ✅ Popup chọn kỳ, năm, cơ quan tiếp nhận
- ✅ Tính phí cố định 750,000 VNĐ
- ✅ Chuyển đổi số thành chữ chính xác
- ✅ Tên file xuất theo format: `{profile}_{ky}_{nam}_{timestamp}`

## Lưu ý

- Dữ liệu được lưu trong SQLite database (emission.db)
- File template TO_KHAI.docx cần có trong thư mục gốc
- Ứng dụng chạy ở chế độ debug, không sử dụng trong production
- Hỗ trợ đầy đủ tiếng Việt

## Hỗ trợ

Nếu gặp vấn đề:
1. Chạy `python install_requirements.py` để kiểm tra dependencies
2. Kiểm tra Python version >= 3.8
3. Đảm bảo file TO_KHAI.docx tồn tại
4. Port 5000 không bị chiếm dụng
5. Quyền ghi file trong thư mục dự án

---
**Phát triển**: Emission Management System v3.2
**Ngôn ngữ**: Tiếng Việt
**License**: MIT

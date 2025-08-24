# Hệ thống Tính toán Phát thải và Phí Bảo vệ Môi trường

Webapp Flask để nhập dữ liệu phát thải, tính toán phí bảo vệ môi trường và xuất báo cáo Excel/Word.

## Tính năng chính

- ✅ Nhập dữ liệu nguồn thải khí
- ✅ Tự động tính toán mức thu phí biến đổi
- ✅ Tính toán giá trị Ci theo công thức quy định
- ✅ Xuất báo cáo Excel với định dạng đẹp
- ✅ Xuất báo cáo Word với template chuyên nghiệp
- ✅ Xem trước kết quả tính toán
- ✅ Quản lý danh sách nguồn thải

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
   pip install -r requirements.txt
   ```

## Chạy ứng dụng

```bash
python app.py
```

Mở trình duyệt và truy cập: `http://localhost:5000`

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
- **Word**: Click "Xuất Word" để tải file .docx với báo cáo chuyên nghiệp

## Công thức tính toán

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
emission/
├── app.py              # File chính Flask
├── models.py           # Model dữ liệu
├── export_utils.py     # Utilities xuất file
├── requirements.txt    # Dependencies
├── templates/          # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── add_record.html
│   └── view_record.html
├── static/            # CSS, JS, images
├── uploads/           # Thư mục chứa file xuất
└── venv/             # Môi trường ảo Python
```

## Lưu ý

- Dữ liệu được lưu trong bộ nhớ, sẽ mất khi restart ứng dụng
- Để lưu trữ lâu dài, có thể tích hợp database (SQLite, PostgreSQL, etc.)
- File xuất được lưu trong thư mục `uploads/`
- Ứng dụng chạy ở chế độ debug, không sử dụng trong production

## Hỗ trợ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. Python version >= 3.8
2. Tất cả dependencies đã được cài đặt
3. Port 5000 không bị chiếm dụng
4. Quyền ghi file trong thư mục dự án

# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG TÍNH TOÁN PHÍ PHÁT THẢI

## 1. CÀI ĐẶT VÀ KHỞI CHẠY

### Yêu cầu hệ thống:
- Python 3.8 trở lên
- Các thư viện trong requirements.txt

### Cài đặt:
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Khởi tạo database (chỉ chạy lần đầu)
python -c "from flask_app import app, db; app.app_context().push(); db.create_all(); from database import User; admin = User(username='admin', email='admin@emission.local', is_admin=True, is_active=True); admin.set_password('admin123'); db.session.add(admin); db.session.commit(); print('✅ Database và admin user đã được tạo!')"

# Chạy ứng dụng
python flask_app.py
```

### Truy cập:
- Mở trình duyệt và truy cập: http://127.0.0.1:5000
- Đăng nhập với tài khoản admin mặc định:
  - Username: `admin`
  - Password: `admin123`
  - **⚠️ Quan trọng: Đổi password ngay sau khi đăng nhập lần đầu!**

## 2. PHÂN QUYỀN HỆ THỐNG

### Admin:
- Có quyền cao nhất trong hệ thống
- Quản lý tất cả user: tạo, kích hoạt/khóa, reset password, xóa user
- Xem và quản lý tất cả profile của mọi user
- Đổi password của chính mình

### User thường:
- Chỉ đăng nhập được sau khi Admin kích hoạt tài khoản
- Chỉ xem và quản lý profile do chính mình tạo
- Không thể xem profile của user khác
- Đổi password của chính mình

## 3. HƯỚNG DẪN SỬ DỤNG CHO ADMIN

### Quản lý User:
1. Đăng nhập với tài khoản admin
2. Click "Quản lý User" trên thanh navigation
3. Xem danh sách tất cả user trong hệ thống
4. Thực hiện các thao tác:
   - **Kích hoạt/Khóa user**: Click nút "Mở khóa"/"Khóa"
   - **Reset password**: Click "Reset PW", nhập password mới
   - **Xóa user**: Click "Xóa" (chỉ với user thường)

### Quản lý Profile:
- Admin có thể xem và chỉnh sửa tất cả profile của mọi user
- Có thể tạo profile mới cho chính mình

## 4. HƯỚNG DẪN SỬ DỤNG CHO USER

### Đăng ký tài khoản:
1. Click "Đăng ký" trên trang đăng nhập
2. Điền đầy đủ thông tin: username, email, password
3. Sau khi đăng ký, chờ Admin kích hoạt tài khoản

### Quản lý Profile:
1. Sau khi đăng nhập, tạo profile đầu tiên
2. Điền đầy đủ thông tin công ty
3. Chọn profile để làm việc

### Quản lý Nguồn thải:
1. Chọn profile cần làm việc
2. Click "Thêm nguồn thải"
3. Điền đầy đủ thông tin:
   - Tên nguồn thải
   - Lưu lượng (Nm³/h)
   - Thời gian xả thải (giờ)
   - Các hệ số Kp, Kv
   - Nồng độ các chất: Bụi, NOx, SOx, CO
   - Tiêu chuẩn tương ứng
4. Hệ thống tự động tính toán phí Ci

### Xuất báo cáo:
- **Excel**: Xuất dữ liệu dạng bảng tính
- **Word**: Xuất báo cáo định dạng văn bản
- **JSON**: Xuất để backup/import

## 5. TÍNH NĂNG CHÍNH

### Tính toán tự động:
- Hệ thống tự động tính mức thu phí biến đổi
- Tính toán Ci cho từng chất thải
- Tổng hợp tổng Ci

### Quản lý dữ liệu:
- Tạo, sửa, xóa, nhân bản nguồn thải
- Quản lý nhiều profile
- Import/Export dữ liệu

### Bảo mật:
- Đăng nhập bắt buộc
- Phân quyền rõ ràng
- Mã hóa password

## 6. LƯU Ý QUAN TRỌNG

1. **Đổi password admin**: Ngay sau khi cài đặt, đổi password admin mặc định
2. **Backup dữ liệu**: Thường xuyên xuất JSON để backup
3. **Kích hoạt user**: Admin cần kích hoạt user mới đăng ký
4. **Phân quyền**: User chỉ thấy profile của mình, Admin thấy tất cả

## 7. KHẮC PHỤC SỰ CỐ

### Quên password admin:
```python
# Chạy script này để reset password admin
from flask_app import app, db
from database import User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    admin.set_password('admin123')
    db.session.commit()
    print("Password admin đã được reset về 'admin123'")
```

### Xóa tất cả dữ liệu:
```bash
# Xóa file database để reset hoàn toàn
rm emission.db
# Sau đó chạy lại script khởi tạo database
```

## 8. HỖ TRỢ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. Python version >= 3.8
2. Tất cả dependencies đã được cài đặt
3. Database đã được khởi tạo
4. Port 5000 không bị chiếm dụng

---
**Phiên bản**: 3.0 với Database và Authentication
**Ngày cập nhật**: 2025-01-04

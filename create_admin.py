#!/usr/bin/env python3
"""
Script tạo tài khoản admin đầu tiên
"""

from flask_app import app, db
from database import User

def create_admin():
    """Tạo tài khoản admin đầu tiên"""
    
    with app.app_context():
        # Kiểm tra xem đã có admin chưa
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print(f"⚠️  Đã có tài khoản admin: {existing_admin.username}")
            print("Nếu muốn tạo admin mới, hãy xóa admin cũ trước.")
            return
        
        print("🔧 TẠO TÀI KHOẢN ADMIN ĐẦU TIÊN")
        print("=" * 40)
        
        # Nhập thông tin admin
        username = input("Nhập username admin: ").strip()
        if not username:
            print("❌ Username không được để trống!")
            return
        
        # Kiểm tra username đã tồn tại
        if User.query.filter_by(username=username).first():
            print("❌ Username đã tồn tại!")
            return
        
        email = input("Nhập email admin: ").strip()
        if not email:
            print("❌ Email không được để trống!")
            return
        
        # Kiểm tra email đã tồn tại
        if User.query.filter_by(email=email).first():
            print("❌ Email đã được sử dụng!")
            return
        
        password = input("Nhập password (tối thiểu 6 ký tự): ").strip()
        if len(password) < 6:
            print("❌ Password phải có ít nhất 6 ký tự!")
            return
        
        confirm_password = input("Xác nhận password: ").strip()
        if password != confirm_password:
            print("❌ Password xác nhận không khớp!")
            return
        
        try:
            # Tạo admin user
            admin = User(
                username=username,
                email=email,
                is_admin=True,
                is_active=True  # Admin tự động được kích hoạt
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Tạo tài khoản admin thành công!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Quyền: Admin")
            print(f"   Trạng thái: Đã kích hoạt")
            print("\n🚀 Bây giờ bạn có thể đăng nhập vào hệ thống!")
            
        except Exception as e:
            print(f"❌ Lỗi khi tạo admin: {str(e)}")
            db.session.rollback()

def show_existing_users():
    """Hiển thị danh sách user hiện có"""
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("📭 Chưa có user nào trong hệ thống")
            return
        
        print("\n👥 DANH SÁCH USER HIỆN CÓ:")
        print("=" * 50)
        print(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Admin':<8} {'Active':<8}")
        print("-" * 50)
        
        for user in users:
            admin_status = "✅" if user.is_admin else "❌"
            active_status = "✅" if user.is_active else "❌"
            print(f"{user.id:<5} {user.username:<15} {user.email:<25} {admin_status:<8} {active_status:<8}")

def main():
    """Hàm chính"""
    print("🔐 QUẢN LÝ TÀI KHOẢN ADMIN")
    print("=" * 30)
    
    while True:
        print("\nChọn hành động:")
        print("1. Tạo tài khoản admin mới")
        print("2. Xem danh sách user hiện có")
        print("3. Thoát")
        
        choice = input("\nNhập lựa chọn (1-3): ").strip()
        
        if choice == "1":
            create_admin()
        elif choice == "2":
            show_existing_users()
        elif choice == "3":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()

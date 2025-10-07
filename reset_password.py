#!/usr/bin/env python3
"""
Script reset mật khẩu cho user
"""

from flask_app import app, db
from database import User

def list_users():
    """Hiển thị danh sách tất cả user"""
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("📭 Không có user nào trong hệ thống")
            return []
        
        print("\n👥 DANH SÁCH USER:")
        print("=" * 70)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Admin':<8} {'Active':<8}")
        print("-" * 70)
        
        for user in users:
            admin_status = "✅ Yes" if user.is_admin else "❌ No"
            active_status = "✅ Yes" if user.is_active else "❌ No"
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {admin_status:<8} {active_status:<8}")
        
        return users

def reset_user_password():
    """Reset mật khẩu cho user"""
    
    with app.app_context():
        users = list_users()
        
        if not users:
            return
        
        print("\n🔄 RESET MẬT KHẨU")
        print("=" * 30)
        
        # Chọn user
        try:
            user_input = input("\nNhập ID hoặc Username của user cần reset: ").strip()
            
            # Tìm user theo ID hoặc username
            user = None
            if user_input.isdigit():
                user = User.query.get(int(user_input))
            else:
                user = User.query.filter_by(username=user_input).first()
            
            if not user:
                print("❌ Không tìm thấy user!")
                return
            
            print(f"\n📋 Thông tin user được chọn:")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Admin: {'Yes' if user.is_admin else 'No'}")
            print(f"   Active: {'Yes' if user.is_active else 'No'}")
            
            # Xác nhận
            confirm = input(f"\n❓ Bạn có chắc muốn reset password cho user '{user.username}'? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes', 'có']:
                print("⏭️  Hủy bỏ reset password")
                return
            
            # Nhập password mới
            new_password = input("\n🔑 Nhập password mới (tối thiểu 6 ký tự): ").strip()
            if len(new_password) < 6:
                print("❌ Password phải có ít nhất 6 ký tự!")
                return
            
            confirm_password = input("🔑 Xác nhận password mới: ").strip()
            if new_password != confirm_password:
                print("❌ Password xác nhận không khớp!")
                return
            
            # Reset password
            user.set_password(new_password)
            
            # Đảm bảo user được kích hoạt (nếu chưa)
            if not user.is_active:
                activate = input(f"\n⚠️  User '{user.username}' chưa được kích hoạt. Kích hoạt luôn? (y/n): ").strip().lower()
                if activate in ['y', 'yes', 'có']:
                    user.is_active = True
                    print("✅ Đã kích hoạt user")
            
            db.session.commit()
            
            print(f"\n🎉 Reset password thành công cho user '{user.username}'!")
            print(f"   Username: {user.username}")
            print(f"   Password mới: {new_password}")
            print(f"   Trạng thái: {'Đã kích hoạt' if user.is_active else 'Chưa kích hoạt'}")
            print("\n🚀 Bây giờ bạn có thể đăng nhập với password mới!")
            
        except ValueError:
            print("❌ ID không hợp lệ!")
        except Exception as e:
            print(f"❌ Lỗi khi reset password: {str(e)}")
            db.session.rollback()

def create_emergency_admin():
    """Tạo tài khoản admin khẩn cấp"""
    
    with app.app_context():
        print("\n🚨 TẠO ADMIN KHẨN CẤP")
        print("=" * 30)
        print("⚠️  Chỉ sử dụng khi không thể truy cập tài khoản admin nào!")
        
        confirm = input("\nBạn có chắc muốn tạo admin khẩn cấp? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', 'có']:
            print("⏭️  Hủy bỏ tạo admin khẩn cấp")
            return
        
        # Tạo username tự động
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        emergency_username = f"emergency_admin_{timestamp}"
        emergency_email = f"emergency_{timestamp}@admin.local"
        emergency_password = f"admin123_{timestamp[-6:]}"
        
        try:
            # Tạo admin khẩn cấp
            admin = User(
                username=emergency_username,
                email=emergency_email,
                is_admin=True,
                is_active=True
            )
            admin.set_password(emergency_password)
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Tạo admin khẩn cấp thành công!")
            print(f"   Username: {emergency_username}")
            print(f"   Email: {emergency_email}")
            print(f"   Password: {emergency_password}")
            print(f"   Quyền: Admin")
            print(f"   Trạng thái: Đã kích hoạt")
            print("\n🚀 Hãy đăng nhập ngay và đổi password!")
            print("💡 Nhớ xóa tài khoản này sau khi đã khôi phục tài khoản chính!")
            
        except Exception as e:
            print(f"❌ Lỗi khi tạo admin khẩn cấp: {str(e)}")
            db.session.rollback()

def main():
    """Hàm chính"""
    print("🔐 RESET MẬT KHẨU USER")
    print("=" * 25)
    
    while True:
        print("\nChọn hành động:")
        print("1. Xem danh sách user")
        print("2. Reset password cho user")
        print("3. Tạo admin khẩn cấp")
        print("4. Thoát")
        
        choice = input("\nNhập lựa chọn (1-4): ").strip()
        
        if choice == "1":
            list_users()
        elif choice == "2":
            reset_user_password()
        elif choice == "3":
            create_emergency_admin()
        elif choice == "4":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script reset password admin đơn giản
"""

from flask_app import app, db
from database import User

def reset_admin_password():
    """Reset password admin thành admin123"""
    
    with app.app_context():
        print("🔐 RESET PASSWORD ADMIN")
        print("=" * 30)
        
        # Tìm tất cả admin
        admins = User.query.filter_by(is_admin=True).all()
        
        if not admins:
            print("❌ Không tìm thấy tài khoản admin nào!")
            print("💡 Hãy chạy: python create_admin.py để tạo admin mới")
            return
        
        print("👥 Danh sách admin hiện có:")
        print("-" * 50)
        for i, admin in enumerate(admins, 1):
            status = "✅ Active" if admin.is_active else "❌ Inactive"
            print(f"{i}. {admin.username} ({admin.email}) - {status}")
        
        if len(admins) == 1:
            # Chỉ có 1 admin, reset luôn
            admin = admins[0]
            print(f"\n🎯 Sẽ reset password cho admin: {admin.username}")
        else:
            # Có nhiều admin, cho chọn
            try:
                choice = int(input(f"\nChọn admin cần reset (1-{len(admins)}): "))
                if choice < 1 or choice > len(admins):
                    print("❌ Lựa chọn không hợp lệ!")
                    return
                admin = admins[choice - 1]
            except ValueError:
                print("❌ Vui lòng nhập số!")
                return
        
        print(f"\n📋 Thông tin admin:")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Trạng thái: {'Active' if admin.is_active else 'Inactive'}")
        
        # Xác nhận reset
        confirm = input(f"\n❓ Reset password cho '{admin.username}' thành 'admin123'? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', 'có']:
            print("⏭️  Hủy bỏ reset password")
            return
        
        try:
            # Reset password thành admin123
            admin.set_password("admin123")
            
            # Đảm bảo admin được kích hoạt
            if not admin.is_active:
                admin.is_active = True
                print("✅ Đã kích hoạt tài khoản admin")
            
            db.session.commit()
            
            print(f"\n🎉 Reset password thành công!")
            print(f"   Username: {admin.username}")
            print(f"   Password: admin123")
            print(f"   Trạng thái: Active")
            print("\n🚀 Bây giờ bạn có thể đăng nhập với:")
            print(f"   - Username: {admin.username}")
            print(f"   - Password: admin123")
            print("\n💡 Khuyến nghị: Đăng nhập và đổi password ngay!")
            
        except Exception as e:
            print(f"❌ Lỗi khi reset password: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    reset_admin_password()

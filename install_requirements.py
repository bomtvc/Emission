#!/usr/bin/env python3
"""
Script để kiểm tra và cài đặt dependencies từ requirements.txt
"""

import subprocess
import sys
import os

def check_and_install_requirements():
    """Kiểm tra và cài đặt các package từ requirements.txt"""
    
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ File {requirements_file} không tồn tại!")
        return False
    
    print("🔍 Kiểm tra dependencies...")
    
    try:
        # Đọc requirements.txt
        with open(requirements_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Lọc các dòng package (bỏ comment và dòng trống)
        packages = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '==' in line:
                packages.append(line)
        
        print(f"📦 Tìm thấy {len(packages)} packages cần kiểm tra")
        
        # Kiểm tra từng package
        missing_packages = []
        for package in packages:
            package_name = package.split('==')[0]
            try:
                __import__(package_name.replace('-', '_'))
                print(f"✅ {package_name} - Đã cài đặt")
            except ImportError:
                try:
                    # Thử import với tên khác
                    if package_name == 'python-docx':
                        __import__('docx')
                        print(f"✅ {package_name} - Đã cài đặt")
                    elif package_name == 'Flask-SQLAlchemy':
                        __import__('flask_sqlalchemy')
                        print(f"✅ {package_name} - Đã cài đặt")
                    elif package_name == 'Flask-Login':
                        __import__('flask_login')
                        print(f"✅ {package_name} - Đã cài đặt")
                    else:
                        missing_packages.append(package)
                        print(f"❌ {package_name} - Chưa cài đặt")
                except ImportError:
                    missing_packages.append(package)
                    print(f"❌ {package_name} - Chưa cài đặt")
        
        if missing_packages:
            print(f"\n⚠️  Có {len(missing_packages)} packages chưa được cài đặt:")
            for pkg in missing_packages:
                print(f"   - {pkg}")
            
            response = input("\n🤔 Bạn có muốn cài đặt các packages này không? (y/n): ")
            if response.lower() in ['y', 'yes', 'có']:
                install_packages(missing_packages)
            else:
                print("⏭️  Bỏ qua cài đặt")
        else:
            print("\n🎉 Tất cả dependencies đã được cài đặt!")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra requirements: {str(e)}")
        return False

def install_packages(packages):
    """Cài đặt các packages"""
    print("\n📥 Bắt đầu cài đặt packages...")
    
    for package in packages:
        try:
            print(f"🔄 Đang cài đặt {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Cài đặt thành công {package}")
            else:
                print(f"❌ Lỗi cài đặt {package}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Lỗi khi cài đặt {package}: {str(e)}")
    
    print("\n🏁 Hoàn thành cài đặt!")

def check_python_version():
    """Kiểm tra phiên bản Python"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  Khuyến nghị sử dụng Python 3.8 trở lên")
        return False
    else:
        print("✅ Phiên bản Python phù hợp")
        return True

def main():
    """Hàm chính"""
    print("=" * 50)
    print("🔧 KIỂM TRA VÀ CÀI ĐẶT DEPENDENCIES")
    print("=" * 50)
    
    # Kiểm tra phiên bản Python
    if not check_python_version():
        print("❌ Vui lòng cập nhật Python!")
        return
    
    # Kiểm tra và cài đặt requirements
    if check_and_install_requirements():
        print("\n🎯 Hệ thống sẵn sàng để chạy!")
        print("💡 Chạy: python flask_app.py để khởi động ứng dụng")
    else:
        print("\n❌ Có lỗi xảy ra trong quá trình kiểm tra")

if __name__ == "__main__":
    main()

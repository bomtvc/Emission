from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator yêu cầu quyền admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập trang này!', 'error')
            return redirect(url_for('login'))
        
        if not current_user.is_admin:
            flash('Bạn không có quyền truy cập trang này!', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def login_required_custom(f):
    """Decorator yêu cầu đăng nhập và tài khoản được kích hoạt"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập trang này!', 'error')
            return redirect(url_for('login'))
        
        if not current_user.is_active:
            flash('Tài khoản của bạn chưa được kích hoạt. Vui lòng liên hệ Admin!', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def check_profile_ownership(profile_id):
    """Kiểm tra quyền sở hữu profile"""
    from database import Profile
    
    if current_user.is_admin:
        return True  # Admin có thể truy cập tất cả profile
    
    profile = Profile.query.get(profile_id)
    if not profile:
        return False
    
    return profile.user_id == current_user.id

def get_user_profiles():
    """Lấy danh sách profile mà user hiện tại có quyền truy cập"""
    from database import Profile
    
    if current_user.is_admin:
        return Profile.query.all()  # Admin xem tất cả
    else:
        return Profile.query.filter_by(user_id=current_user.id).all()  # User chỉ xem của mình

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import json
import tempfile
from datetime import datetime
from database import db, User, Profile, EmissionRecord
from auth import admin_required, login_required_custom, check_profile_ownership, get_user_profiles
from export_utils import ExcelExporter, WordExporter

app = Flask(__name__)

# Cấu hình
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "emission.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Khởi tạo extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes Authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Đăng nhập"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Tài khoản của bạn chưa được kích hoạt. Vui lòng liên hệ Admin!', 'error')
                return render_template('login.html')
            
            login_user(user)
            flash(f'Chào mừng {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Đăng ký"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'error')
            return render_template('register.html')
        
        # Kiểm tra username đã tồn tại
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'error')
            return render_template('register.html')
        
        # Kiểm tra email đã tồn tại
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'error')
            return render_template('register.html')
        
        # Tạo user mới
        user = User(username=username, email=email, is_active=False)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Đăng ký thành công! Vui lòng chờ Admin kích hoạt tài khoản.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Đăng xuất"""
    logout_user()
    flash('Đã đăng xuất thành công!', 'success')
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required_custom
def change_password():
    """Đổi mật khẩu"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Kiểm tra mật khẩu hiện tại
        if not current_user.check_password(current_password):
            flash('Mật khẩu hiện tại không đúng!', 'error')
            return render_template('change_password.html')
        
        # Validation mật khẩu mới
        if len(new_password) < 6:
            flash('Mật khẩu mới phải có ít nhất 6 ký tự!', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'error')
            return render_template('change_password.html')
        
        # Cập nhật mật khẩu
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('change_password.html')

# Routes quản lý user (Admin only)
@app.route('/manage_users')
@admin_required
def manage_users():
    """Quản lý người dùng (Admin only)"""
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/toggle_user_status/<int:user_id>')
@admin_required
def toggle_user_status(user_id):
    """Bật/tắt trạng thái user"""
    user = User.query.get_or_404(user_id)
    
    # Không cho phép admin tự khóa chính mình
    if user.id == current_user.id:
        flash('Bạn không thể khóa chính mình!', 'error')
        return redirect(url_for('manage_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "kích hoạt" if user.is_active else "khóa"
    flash(f'Đã {status} tài khoản {user.username}!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/reset_user_password/<int:user_id>', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """Reset mật khẩu user"""
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if len(new_password) < 6:
        flash('Mật khẩu phải có ít nhất 6 ký tự!', 'error')
        return redirect(url_for('manage_users'))
    
    if new_password != confirm_password:
        flash('Mật khẩu xác nhận không khớp!', 'error')
        return redirect(url_for('manage_users'))
    
    user.set_password(new_password)
    db.session.commit()
    
    flash(f'Đã reset mật khẩu cho {user.username}!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    """Xóa user"""
    user = User.query.get_or_404(user_id)
    
    # Không cho phép xóa admin
    if user.is_admin:
        flash('Không thể xóa tài khoản Admin!', 'error')
        return redirect(url_for('manage_users'))
    
    # Không cho phép admin tự xóa chính mình
    if user.id == current_user.id:
        flash('Bạn không thể xóa chính mình!', 'error')
        return redirect(url_for('manage_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Đã xóa tài khoản {username}!', 'success')
    return redirect(url_for('manage_users'))

# Route chính
@app.route('/')
@login_required_custom
def index():
    """Trang chủ hiển thị danh sách profiles"""
    profiles = get_user_profiles()
    
    # Lấy profile hiện tại từ session hoặc profile đầu tiên
    current_profile_id = request.args.get('profile_id', type=int)
    current_profile = None
    
    if current_profile_id:
        current_profile = Profile.query.get(current_profile_id)
        if current_profile and not check_profile_ownership(current_profile.id):
            flash('Bạn không có quyền truy cập profile này!', 'error')
            current_profile = None
    
    if not current_profile and profiles:
        current_profile = profiles[0]
    
    # Nếu có profile hiện tại, hiển thị dữ liệu của nó
    if current_profile:
        records_data = []
        for record in current_profile.records:
            record_dict = record.to_dict()
            record_dict['id'] = record.id  # Thêm ID để sử dụng trong template
            records_data.append(record_dict)
        total_ci = sum(record['Ci'] for record in records_data)
    else:
        records_data = []
        total_ci = 0
    
    return render_template('index.html',
                         profiles=profiles,
                         current_profile=current_profile,
                         records=records_data,
                         total_ci=total_ci)

@app.route('/create_profile', methods=['GET', 'POST'])
@login_required_custom
def create_profile():
    """Tạo profile mới"""
    if request.method == 'POST':
        try:
            # Lấy thông tin cơ bản
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()

            # Lấy thông tin công ty
            ten_cong_ty = request.form.get('ten_cong_ty', '').strip()
            dia_chi = request.form.get('dia_chi', '').strip()
            mst = request.form.get('mst', '').strip()
            dien_thoai = request.form.get('dien_thoai', '').strip()
            fax = request.form.get('fax', '').strip()
            email = request.form.get('email', '').strip()
            tai_khoan_ngan_hang = request.form.get('tai_khoan_ngan_hang', '').strip()
            tai_ngan_hang = request.form.get('tai_ngan_hang', '').strip()
            loai_hinh_san_xuat = request.form.get('loai_hinh_san_xuat', '').strip()

            # Validation các trường bắt buộc
            if not name:
                flash('Tên profile không được để trống!', 'error')
                return render_template('create_profile.html')

            if not ten_cong_ty:
                flash('Tên công ty không được để trống!', 'error')
                return render_template('create_profile.html')

            if not dia_chi:
                flash('Địa chỉ không được để trống!', 'error')
                return render_template('create_profile.html')

            if not mst:
                flash('Mã số thuế không được để trống!', 'error')
                return render_template('create_profile.html')

            # Tạo profile mới
            profile = Profile(
                name=name,
                description=description,
                ten_cong_ty=ten_cong_ty,
                dia_chi=dia_chi,
                mst=mst,
                dien_thoai=dien_thoai,
                fax=fax,
                email=email,
                tai_khoan_ngan_hang=tai_khoan_ngan_hang,
                tai_ngan_hang=tai_ngan_hang,
                loai_hinh_san_xuat=loai_hinh_san_xuat,
                user_id=current_user.id
            )

            db.session.add(profile)
            db.session.commit()

            flash(f'Đã tạo profile "{name}" thành công!', 'success')
            return redirect(url_for('index', profile_id=profile.id))

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('create_profile.html')

@app.route('/delete_profile/<int:profile_id>')
@login_required_custom
def delete_profile(profile_id):
    """Xóa profile"""
    profile = Profile.query.get_or_404(profile_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(profile.id):
        flash('Bạn không có quyền xóa profile này!', 'error')
        return redirect(url_for('index'))

    try:
        profile_name = profile.name
        db.session.delete(profile)
        db.session.commit()
        flash(f'Đã xóa profile "{profile_name}" thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra khi xóa profile: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/add_record', methods=['GET', 'POST'])
@login_required_custom
def add_record():
    """Thêm bản ghi mới"""
    # Lấy profile hiện tại
    profile_id = request.args.get('profile_id', type=int)
    if not profile_id:
        flash('Vui lòng chọn một profile trước khi thêm nguồn thải!', 'error')
        return redirect(url_for('index'))

    profile = Profile.query.get_or_404(profile_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(profile.id):
        flash('Bạn không có quyền thêm dữ liệu vào profile này!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Tạo bản ghi mới
            record = EmissionRecord()

            # Lấy dữ liệu từ form
            form_data = {
                'stt': str(len(profile.records) + 1),
                'ten_nguon_thai': request.form.get('ten_nguon_thai', ''),
                'luu_luong': request.form.get('luu_luong', 0),
                'tong_thoi_gian': request.form.get('tong_thoi_gian', 0),
                'thong_tin_don_vi': request.form.get('thong_tin_don_vi', ''),
                'kp': request.form.get('kp', 1.0),
                'kv': request.form.get('kv', 1.0),
                'bui': request.form.get('bui', 0),
                'tieu_chuan_bui': request.form.get('tieu_chuan_bui', 0),
                'nox': request.form.get('nox', 0),
                'tieu_chuan_nox': request.form.get('tieu_chuan_nox', 0),
                'sox': request.form.get('sox', 0),
                'tieu_chuan_sox': request.form.get('tieu_chuan_sox', 0),
                'co': request.form.get('co', 0),
                'tieu_chuan_co': request.form.get('tieu_chuan_co', 0)
            }

            # Nạp dữ liệu và tính toán
            record.from_dict(form_data)
            record.profile_id = profile.id

            # Thêm vào database
            db.session.add(record)
            db.session.commit()

            flash('Đã thêm nguồn thải thành công!', 'success')
            return redirect(url_for('index', profile_id=profile.id))

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('add_record.html', profile=profile)

@app.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])
@login_required_custom
def edit_record(record_id):
    """Chỉnh sửa bản ghi"""
    record = EmissionRecord.query.get_or_404(record_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(record.profile.id):
        flash('Bạn không có quyền chỉnh sửa bản ghi này!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            form_data = {
                'stt': record.stt,  # Giữ nguyên STT
                'ten_nguon_thai': request.form.get('ten_nguon_thai', ''),
                'luu_luong': request.form.get('luu_luong', 0),
                'tong_thoi_gian': request.form.get('tong_thoi_gian', 0),
                'thong_tin_don_vi': request.form.get('thong_tin_don_vi', ''),
                'kp': request.form.get('kp', 1.0),
                'kv': request.form.get('kv', 1.0),
                'bui': request.form.get('bui', 0),
                'tieu_chuan_bui': request.form.get('tieu_chuan_bui', 0),
                'nox': request.form.get('nox', 0),
                'tieu_chuan_nox': request.form.get('tieu_chuan_nox', 0),
                'sox': request.form.get('sox', 0),
                'tieu_chuan_sox': request.form.get('tieu_chuan_sox', 0),
                'co': request.form.get('co', 0),
                'tieu_chuan_co': request.form.get('tieu_chuan_co', 0)
            }

            # Cập nhật bản ghi
            record.from_dict(form_data)
            db.session.commit()

            flash('Đã cập nhật nguồn thải thành công!', 'success')
            return redirect(url_for('index', profile_id=record.profile.id))

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    # GET request - hiển thị form chỉnh sửa
    record_data = record.to_dict()
    return render_template('edit_record.html', record=record_data, record_id=record_id, profile=record.profile)

@app.route('/delete_record/<int:record_id>')
@login_required_custom
def delete_record(record_id):
    """Xóa bản ghi"""
    record = EmissionRecord.query.get_or_404(record_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(record.profile.id):
        flash('Bạn không có quyền xóa bản ghi này!', 'error')
        return redirect(url_for('index'))

    try:
        profile_id = record.profile.id
        db.session.delete(record)
        db.session.commit()

        # Tái đánh số STT cho các record còn lại
        remaining_records = EmissionRecord.query.filter_by(profile_id=profile_id).order_by(EmissionRecord.id).all()
        for i, rec in enumerate(remaining_records):
            rec.stt = str(i + 1)
        db.session.commit()

        flash('Đã xóa bản ghi thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra khi xóa: {str(e)}', 'error')

    return redirect(url_for('index', profile_id=profile_id))

@app.route('/duplicate_record/<int:record_id>')
@login_required_custom
def duplicate_record(record_id):
    """Nhân bản bản ghi"""
    record = EmissionRecord.query.get_or_404(record_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(record.profile.id):
        flash('Bạn không có quyền nhân bản bản ghi này!', 'error')
        return redirect(url_for('index'))

    try:
        # Tạo bản ghi mới
        new_record = EmissionRecord()

        # Copy dữ liệu
        new_record.ten_nguon_thai = record.ten_nguon_thai + " (Copy)"
        new_record.luu_luong = record.luu_luong
        new_record.tong_thoi_gian = record.tong_thoi_gian
        new_record.thong_tin_don_vi = record.thong_tin_don_vi
        new_record.kp = record.kp
        new_record.kv = record.kv
        new_record.bui = record.bui
        new_record.tieu_chuan_bui = record.tieu_chuan_bui
        new_record.nox = record.nox
        new_record.tieu_chuan_nox = record.tieu_chuan_nox
        new_record.sox = record.sox
        new_record.tieu_chuan_sox = record.tieu_chuan_sox
        new_record.co = record.co
        new_record.tieu_chuan_co = record.tieu_chuan_co
        new_record.profile_id = record.profile_id
        new_record.stt = str(len(record.profile.records) + 1)

        # Tính toán lại
        new_record.calculate_all()

        db.session.add(new_record)
        db.session.commit()

        flash('Đã nhân bản nguồn thải thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra khi nhân bản: {str(e)}', 'error')

    return redirect(url_for('index', profile_id=record.profile.id))

@app.route('/view_record/<int:record_id>')
@login_required_custom
def view_record(record_id):
    """Xem chi tiết bản ghi"""
    record = EmissionRecord.query.get_or_404(record_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(record.profile.id):
        flash('Bạn không có quyền xem bản ghi này!', 'error')
        return redirect(url_for('index'))

    record_data = record.to_dict()
    return render_template('view_record.html', record=record_data, record_id=record_id, profile=record.profile)

@app.route('/clear_all/<int:profile_id>')
@login_required_custom
def clear_all(profile_id):
    """Xóa tất cả dữ liệu trong profile"""
    profile = Profile.query.get_or_404(profile_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(profile.id):
        flash('Bạn không có quyền xóa dữ liệu trong profile này!', 'error')
        return redirect(url_for('index'))

    try:
        # Xóa tất cả records
        EmissionRecord.query.filter_by(profile_id=profile.id).delete()
        db.session.commit()
        flash(f'Đã xóa tất cả dữ liệu trong profile "{profile.name}"!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return redirect(url_for('index', profile_id=profile.id))

@app.route('/preview_calculation', methods=['POST'])
@login_required_custom
def preview_calculation():
    """API để xem trước kết quả tính toán"""
    try:
        # Tạo bản ghi tạm thời để tính toán
        record = EmissionRecord()

        form_data = {
            'stt': request.form.get('stt', ''),
            'ten_nguon_thai': request.form.get('ten_nguon_thai', ''),
            'luu_luong': request.form.get('luu_luong', 0),
            'tong_thoi_gian': request.form.get('tong_thoi_gian', 0),
            'thong_tin_don_vi': request.form.get('thong_tin_don_vi', ''),
            'kp': request.form.get('kp', 1.0),
            'kv': request.form.get('kv', 1.0),
            'bui': request.form.get('bui', 0),
            'tieu_chuan_bui': request.form.get('tieu_chuan_bui', 0),
            'nox': request.form.get('nox', 0),
            'tieu_chuan_nox': request.form.get('tieu_chuan_nox', 0),
            'sox': request.form.get('sox', 0),
            'tieu_chuan_sox': request.form.get('tieu_chuan_sox', 0),
            'co': request.form.get('co', 0),
            'tieu_chuan_co': request.form.get('tieu_chuan_co', 0)
        }

        record.from_dict(form_data)
        result_data = record.to_dict()

        # Tạo HTML cho modal
        html = f"""
        <div class="row">
            <div class="col-md-6">
                <h6 class="text-secondary">Mức thu phí biến đổi</h6>
                <table class="table table-sm table-striped">
                    <tr><td>Bụi:</td><td class="text-end">{result_data['Mức thu phí biến đổi của Bụi']}</td></tr>
                    <tr><td>NOx:</td><td class="text-end">{result_data['Mức thu phí biến đổi của Nox']}</td></tr>
                    <tr><td>SOx:</td><td class="text-end">{result_data['Mức thu phí biến đổi của Sox']}</td></tr>
                    <tr><td>CO:</td><td class="text-end">{result_data['Mức thu phí biến đổi của CO']}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6 class="text-secondary">Giá trị Ci (VNĐ)</h6>
                <table class="table table-sm table-striped">
                    <tr><td>Ci (Bụi):</td><td class="text-end">{result_data['Ci (Bụi)']:,.0f}</td></tr>
                    <tr><td>Ci (NOx):</td><td class="text-end">{result_data['Ci (NOx)']:,.0f}</td></tr>
                    <tr><td>Ci (SOx):</td><td class="text-end">{result_data['Ci (SOx)']:,.0f}</td></tr>
                    <tr><td>Ci (CO):</td><td class="text-end">{result_data['Ci (CO)']:,.0f}</td></tr>
                    <tr class="table-warning"><td class="fw-bold">Tổng Ci:</td><td class="text-end fw-bold">{result_data['Ci']:,.0f}</td></tr>
                </table>
            </div>
        </div>
        """

        return jsonify({'success': True, 'html': html})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export_excel/<int:profile_id>')
@login_required_custom
def export_excel(profile_id):
    """Xuất dữ liệu ra file Excel"""
    profile = Profile.query.get_or_404(profile_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(profile.id):
        flash('Bạn không có quyền xuất dữ liệu từ profile này!', 'error')
        return redirect(url_for('index'))

    try:
        records = profile.to_list_of_dicts()
        if not records:
            flash('Không có dữ liệu để xuất!', 'error')
            return redirect(url_for('index', profile_id=profile.id))

        # Chuẩn bị thông tin profile
        profile_info = {
            'ten_cong_ty': profile.ten_cong_ty,
            'dia_chi': profile.dia_chi,
            'mst': profile.mst,
            'dien_thoai': profile.dien_thoai,
            'fax': profile.fax,
            'email': profile.email
        }

        exporter = ExcelExporter()

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            filepath = exporter.export_data(records, profile_name=profile.name, profile_info=profile_info, output_path=tmp_file.name)

            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))

    except Exception as e:
        flash(f'Có lỗi xảy ra khi xuất Excel: {str(e)}', 'error')
        return redirect(url_for('index', profile_id=profile.id))

@app.route('/export_word/<int:profile_id>')
@login_required_custom
def export_word(profile_id):
    """Xuất dữ liệu ra file Word"""
    profile = Profile.query.get_or_404(profile_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(profile.id):
        flash('Bạn không có quyền xuất dữ liệu từ profile này!', 'error')
        return redirect(url_for('index'))

    try:
        records = profile.to_list_of_dicts()
        if not records:
            flash('Không có dữ liệu để xuất!', 'error')
            return redirect(url_for('index', profile_id=profile.id))

        # Chuẩn bị thông tin profile
        profile_info = {
            'ten_cong_ty': profile.ten_cong_ty,
            'dia_chi': profile.dia_chi,
            'mst': profile.mst,
            'dien_thoai': profile.dien_thoai,
            'fax': profile.fax,
            'email': profile.email
        }

        exporter = WordExporter()

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            filepath = exporter.export_data(records, profile_name=profile.name, profile_info=profile_info, output_path=tmp_file.name)

            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))

    except Exception as e:
        flash(f'Có lỗi xảy ra khi xuất Word: {str(e)}', 'error')
        return redirect(url_for('index', profile_id=profile.id))

@app.route('/export_json/<int:profile_id>')
@login_required_custom
def export_json(profile_id):
    """Xuất dữ liệu ra file JSON để backup"""
    profile = Profile.query.get_or_404(profile_id)

    # Kiểm tra quyền sở hữu
    if not check_profile_ownership(profile.id):
        flash('Bạn không có quyền xuất dữ liệu từ profile này!', 'error')
        return redirect(url_for('index'))

    try:
        # Tạo dữ liệu JSON
        json_data = profile.to_json_dict()

        # Tạo tên file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_profile_name = "".join(c for c in profile.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_profile_name = clean_profile_name.replace(' ', '_')
        filename = f"Backup_{clean_profile_name}_{timestamp}.json"

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as tmp_file:
            json.dump(json_data, tmp_file, ensure_ascii=False, indent=2)
            tmp_file.flush()

            return send_file(tmp_file.name, as_attachment=True, download_name=filename)

    except Exception as e:
        flash(f'Có lỗi xảy ra khi xuất JSON: {str(e)}', 'error')
        return redirect(url_for('index', profile_id=profile.id))

@app.route('/import_json', methods=['GET', 'POST'])
@login_required_custom
def import_json():
    """Nhập dữ liệu từ file JSON"""
    if request.method == 'POST':
        try:
            # Kiểm tra file upload
            if 'json_file' not in request.files:
                flash('Vui lòng chọn file JSON!', 'error')
                return redirect(url_for('import_json'))

            file = request.files['json_file']
            if file.filename == '':
                flash('Vui lòng chọn file JSON!', 'error')
                return redirect(url_for('import_json'))

            if not file.filename.lower().endswith('.json'):
                flash('Vui lòng chọn file có định dạng .json!', 'error')
                return redirect(url_for('import_json'))

            # Đọc và parse JSON
            json_content = file.read().decode('utf-8')
            data = json.loads(json_content)

            # Tạo profile mới từ dữ liệu JSON
            profile_info = data.get('profile_info', {})

            profile = Profile(
                name=profile_info.get('name', ''),
                description=profile_info.get('description', ''),
                ten_cong_ty=profile_info.get('ten_cong_ty', ''),
                dia_chi=profile_info.get('dia_chi', ''),
                mst=profile_info.get('mst', ''),
                dien_thoai=profile_info.get('dien_thoai', ''),
                fax=profile_info.get('fax', ''),
                email=profile_info.get('email', ''),
                tai_khoan_ngan_hang=profile_info.get('tai_khoan_ngan_hang', ''),
                tai_ngan_hang=profile_info.get('tai_ngan_hang', ''),
                loai_hinh_san_xuat=profile_info.get('loai_hinh_san_xuat', ''),
                user_id=current_user.id
            )

            db.session.add(profile)
            db.session.flush()  # Để lấy profile.id

            # Nạp các bản ghi
            records_data = data.get('records', [])
            for record_data in records_data:
                record = EmissionRecord()
                # Chuyển đổi key để phù hợp với from_dict
                converted_data = {
                    'stt': record_data.get('STT', ''),
                    'ten_nguon_thai': record_data.get('Tên Nguồn thải', ''),
                    'luu_luong': record_data.get('Lưu lượng (Nm3/h)', 0),
                    'tong_thoi_gian': record_data.get('Tổng thời gian xả thải trong kỳ (Giờ)', 0),
                    'thong_tin_don_vi': record_data.get('Thông tin đơn vị Phân tích', ''),
                    'kp': record_data.get('Kp', 1.0),
                    'kv': record_data.get('Kv', 1.0),
                    'bui': record_data.get('Bụi (mg/Nm3)', 0),
                    'tieu_chuan_bui': record_data.get('Tiêu chuẩn Bụi', 0),
                    'nox': record_data.get('NOx (gồm NO2 và NO) (mg/Nm3)', 0),
                    'tieu_chuan_nox': record_data.get('Tiêu chuẩn NOx', 0),
                    'sox': record_data.get('SOx (mg/Nm3)', 0),
                    'tieu_chuan_sox': record_data.get('Tiêu chuẩn SOx', 0),
                    'co': record_data.get('CO (mg/Nm3)', 0),
                    'tieu_chuan_co': record_data.get('Tiêu chuẩn CO', 0)
                }
                record.from_dict(converted_data)
                record.profile_id = profile.id
                db.session.add(record)

            db.session.commit()

            flash(f'Đã nhập thành công profile "{profile.name}" với {len(records_data)} nguồn thải!', 'success')
            return redirect(url_for('index', profile_id=profile.id))

        except json.JSONDecodeError:
            flash('File JSON không hợp lệ!', 'error')
        except Exception as e:
            flash(f'Có lỗi xảy ra khi nhập JSON: {str(e)}', 'error')

    return render_template('import_json.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

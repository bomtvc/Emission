from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Model cho bảng User"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)  # Admin phải bật user mới login được
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship với Profile
    profiles = db.relationship('Profile', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Mã hóa và lưu password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Kiểm tra password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'profile_count': len(self.profiles)
        }

class Profile(db.Model):
    """Model cho bảng Profile"""
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Thông tin công ty
    ten_cong_ty = db.Column(db.String(200))
    dia_chi = db.Column(db.Text)
    mst = db.Column(db.String(50))
    dien_thoai = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    email = db.Column(db.String(120))
    tai_khoan_ngan_hang = db.Column(db.String(50))
    tai_ngan_hang = db.Column(db.String(200))
    loai_hinh_san_xuat = db.Column(db.String(200))
    
    # Foreign key tới User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship với EmissionRecord
    records = db.relationship('EmissionRecord', backref='profile', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S') if self.created_date else None,
            'ten_cong_ty': self.ten_cong_ty,
            'dia_chi': self.dia_chi,
            'mst': self.mst,
            'dien_thoai': self.dien_thoai,
            'fax': self.fax,
            'email': self.email,
            'tai_khoan_ngan_hang': self.tai_khoan_ngan_hang,
            'tai_ngan_hang': self.tai_ngan_hang,
            'loai_hinh_san_xuat': self.loai_hinh_san_xuat,
            'user_id': self.user_id,
            'record_count': len(self.records),
            'total_ci': sum(record.ci_total for record in self.records)
        }
    
    def to_list_of_dicts(self):
        """Chuyển đổi tất cả records thành list of dictionaries"""
        return [record.to_dict() for record in self.records]
    
    def to_json_dict(self):
        """Chuyển đổi profile thành dictionary để xuất JSON"""
        return {
            'profile_info': {
                'name': self.name,
                'description': self.description,
                'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S') if self.created_date else None,
                'ten_cong_ty': self.ten_cong_ty,
                'dia_chi': self.dia_chi,
                'mst': self.mst,
                'dien_thoai': self.dien_thoai,
                'fax': self.fax,
                'email': self.email,
                'tai_khoan_ngan_hang': self.tai_khoan_ngan_hang,
                'tai_ngan_hang': self.tai_ngan_hang,
                'loai_hinh_san_xuat': self.loai_hinh_san_xuat,
                'version': '3.0'
            },
            'records': [record.to_dict() for record in self.records]
        }

class EmissionRecord(db.Model):
    """Model cho bảng EmissionRecord"""
    __tablename__ = 'emission_records'
    
    id = db.Column(db.Integer, primary_key=True)
    stt = db.Column(db.String(10))
    ten_nguon_thai = db.Column(db.String(200))
    luu_luong = db.Column(db.Float, default=0.0)
    tong_thoi_gian = db.Column(db.Float, default=0.0)
    thong_tin_don_vi = db.Column(db.String(200))
    kp = db.Column(db.Float, default=1.0)
    kv = db.Column(db.Float, default=1.0)
    bui = db.Column(db.Float, default=0.0)
    tieu_chuan_bui = db.Column(db.Float, default=0.0)
    nox = db.Column(db.Float, default=0.0)
    tieu_chuan_nox = db.Column(db.Float, default=0.0)
    sox = db.Column(db.Float, default=0.0)
    tieu_chuan_sox = db.Column(db.Float, default=0.0)
    co = db.Column(db.Float, default=0.0)
    tieu_chuan_co = db.Column(db.Float, default=0.0)
    
    # Các trường tính toán
    muc_thu_phi_bui = db.Column(db.Float, default=0.0)
    muc_thu_phi_nox = db.Column(db.Float, default=0.0)
    muc_thu_phi_sox = db.Column(db.Float, default=0.0)
    muc_thu_phi_co = db.Column(db.Float, default=0.0)
    ci_bui = db.Column(db.Float, default=0.0)
    ci_nox = db.Column(db.Float, default=0.0)
    ci_sox = db.Column(db.Float, default=0.0)
    ci_co = db.Column(db.Float, default=0.0)
    ci_total = db.Column(db.Float, default=0.0)
    
    # Foreign key tới Profile
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    
    # Các hệ số phí cố định
    FEE_BUI = 800
    FEE_SOX = 800
    FEE_NOX = 700
    FEE_CO = 500
    
    def calculate_muc_thu_phi_bien_doi(self, tieu_chuan, thuc_te, kp, kv):
        """Tính mức thu phí biến đổi"""
        tieu_chuan_adjusted = tieu_chuan * kp * kv
        if tieu_chuan_adjusted == 0:
            return 0.75
        
        ty_le = (tieu_chuan_adjusted - thuc_te) / tieu_chuan_adjusted * 100
        return 0.5 if ty_le >= 30 else 0.75
    
    def calculate_all(self):
        """Tính toán tất cả các giá trị"""
        # Tính mức thu phí biến đổi
        self.muc_thu_phi_bui = self.calculate_muc_thu_phi_bien_doi(self.tieu_chuan_bui, self.bui, self.kp, self.kv)
        self.muc_thu_phi_nox = self.calculate_muc_thu_phi_bien_doi(self.tieu_chuan_nox, self.nox, self.kp, self.kv)
        self.muc_thu_phi_sox = self.calculate_muc_thu_phi_bien_doi(self.tieu_chuan_sox, self.sox, self.kp, self.kv)
        self.muc_thu_phi_co = self.calculate_muc_thu_phi_bien_doi(self.tieu_chuan_co, self.co, self.kp, self.kv)
        
        # Tính Ci cho từng chất
        base_calculation = self.luu_luong * self.tong_thoi_gian
        
        self.ci_bui = base_calculation * self.bui * self.muc_thu_phi_bui * self.FEE_BUI * (10**-9)
        self.ci_sox = base_calculation * self.sox * self.muc_thu_phi_sox * self.FEE_SOX * (10**-9)
        self.ci_nox = base_calculation * self.nox * self.muc_thu_phi_nox * self.FEE_NOX * (10**-9)
        self.ci_co = base_calculation * self.co * self.muc_thu_phi_co * self.FEE_CO * (10**-9)
        
        # Tính tổng Ci
        self.ci_total = self.ci_bui + self.ci_sox + self.ci_nox + self.ci_co
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'STT': self.stt,
            'Tên Nguồn thải': self.ten_nguon_thai,
            'Lưu lượng (Nm3/h)': self.luu_luong,
            'Tổng thời gian xả thải trong kỳ (Giờ)': self.tong_thoi_gian,
            'Thông tin đơn vị Phân tích': self.thong_tin_don_vi,
            'Kp': self.kp,
            'Kv': self.kv,
            'Bụi (mg/Nm3)': self.bui,
            'Tiêu chuẩn Bụi': self.tieu_chuan_bui,
            'NOx (gồm NO2 và NO) (mg/Nm3)': self.nox,
            'Tiêu chuẩn NOx': self.tieu_chuan_nox,
            'SOx (mg/Nm3)': self.sox,
            'Tiêu chuẩn SOx': self.tieu_chuan_sox,
            'CO (mg/Nm3)': self.co,
            'Tiêu chuẩn CO': self.tieu_chuan_co,
            'Mức thu phí biến đổi của Bụi': self.muc_thu_phi_bui,
            'Mức thu phí biến đổi của Nox': self.muc_thu_phi_nox,
            'Mức thu phí biến đổi của Sox': self.muc_thu_phi_sox,
            'Mức thu phí biến đổi của CO': self.muc_thu_phi_co,
            'Ci (Bụi)': self.ci_bui,
            'Ci (NOx)': self.ci_nox,
            'Ci (SOx)': self.ci_sox,
            'Ci (CO)': self.ci_co,
            'Ci': self.ci_total
        }
    
    def from_dict(self, data):
        """Nạp dữ liệu từ dictionary"""
        self.stt = data.get('stt', '')
        self.ten_nguon_thai = data.get('ten_nguon_thai', '')
        self.luu_luong = float(data.get('luu_luong', 0))
        self.tong_thoi_gian = float(data.get('tong_thoi_gian', 0))
        self.thong_tin_don_vi = data.get('thong_tin_don_vi', '')
        self.kp = float(data.get('kp', 1.0))
        self.kv = float(data.get('kv', 1.0))
        self.bui = float(data.get('bui', 0))
        self.tieu_chuan_bui = float(data.get('tieu_chuan_bui', 0))
        self.nox = float(data.get('nox', 0))
        self.tieu_chuan_nox = float(data.get('tieu_chuan_nox', 0))
        self.sox = float(data.get('sox', 0))
        self.tieu_chuan_sox = float(data.get('tieu_chuan_sox', 0))
        self.co = float(data.get('co', 0))
        self.tieu_chuan_co = float(data.get('tieu_chuan_co', 0))
        
        # Tính toán các giá trị
        self.calculate_all()

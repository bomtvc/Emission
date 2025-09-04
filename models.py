class EmissionRecord:
    """
    Class để lưu trữ và tính toán dữ liệu phát thải
    """
    
    # Các hệ số phí cố định
    FEE_BUI = 800
    FEE_SOX = 800
    FEE_NOX = 700
    FEE_CO = 500
    
    def __init__(self):
        # Các trường dữ liệu người dùng nhập
        self.stt = ""
        self.ten_nguon_thai = ""
        self.luu_luong = 0.0  # Nm3/h
        self.tong_thoi_gian = 0.0  # Giờ
        self.thong_tin_don_vi = ""
        self.kp = 1.0  # Hệ số Kp
        self.kv = 1.0  # Hệ số Kv
        self.bui = 0.0  # mg/Nm3
        self.tieu_chuan_bui = 0.0
        self.nox = 0.0  # mg/Nm3
        self.tieu_chuan_nox = 0.0
        self.sox = 0.0  # mg/Nm3
        self.tieu_chuan_sox = 0.0
        self.co = 0.0  # mg/Nm3
        self.tieu_chuan_co = 0.0
        
        # Các trường tính toán
        self.muc_thu_phi_bui = 0.0
        self.muc_thu_phi_nox = 0.0
        self.muc_thu_phi_sox = 0.0
        self.muc_thu_phi_co = 0.0
        self.ci_bui = 0.0
        self.ci_nox = 0.0
        self.ci_sox = 0.0
        self.ci_co = 0.0
        self.ci_total = 0.0
    
    def calculate_muc_thu_phi_bien_doi(self, tieu_chuan, thuc_te, kp, kv):
        """
        Tính mức thu phí biến đổi dựa trên công thức:
        ty_le = ((tieu_chuan*Kp*Kv) - thuc_te) / (tieu_chuan*Kp*Kv) * 100
        Nếu ty_le >= 30 thì = 0.5
        Ngược lại < 30 thì = 0.75
        """
        tieu_chuan_adjusted = tieu_chuan * kp * kv
        if tieu_chuan_adjusted == 0:
            return 0.75  # Tránh chia cho 0

        ty_le = (tieu_chuan_adjusted - thuc_te) / tieu_chuan_adjusted * 100
        return 0.5 if ty_le >= 30 else 0.75
    
    def calculate_all(self):
        """
        Tính toán tất cả các giá trị dựa trên dữ liệu đã nhập
        """
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
        """
        Chuyển đổi object thành dictionary để dễ dàng xuất dữ liệu
        """
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
        """
        Nạp dữ liệu từ dictionary vào object
        """
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


class Profile:
    """
    Class đại diện cho một profile chứa nhiều nguồn thải
    """

    def __init__(self, name="", description=""):
        self.name = name
        self.description = description
        self.created_date = ""
        self.records = []

    def add_record(self, record):
        """Thêm một bản ghi mới với STT tự động"""
        # Tự động đánh số STT
        record.stt = str(len(self.records) + 1)
        self.records.append(record)

    def remove_record(self, index):
        """Xóa bản ghi theo index và tái đánh số STT"""
        if 0 <= index < len(self.records):
            del self.records[index]
            # Tái đánh số STT cho tất cả bản ghi
            self._renumber_stt()

    def get_all_records(self):
        """Lấy tất cả bản ghi"""
        return self.records

    def clear_all(self):
        """Xóa tất cả bản ghi"""
        self.records.clear()

    def to_list_of_dicts(self):
        """Chuyển đổi tất cả records thành list of dictionaries"""
        return [record.to_dict() for record in self.records]

    def duplicate_record(self, index):
        """Nhân bản một bản ghi theo index"""
        if 0 <= index < len(self.records):
            original_record = self.records[index]

            # Tạo bản ghi mới
            new_record = EmissionRecord()

            # Copy tất cả dữ liệu từ bản ghi gốc (trừ STT)
            new_record.ten_nguon_thai = original_record.ten_nguon_thai + " (Copy)"
            new_record.luu_luong = original_record.luu_luong
            new_record.tong_thoi_gian = original_record.tong_thoi_gian
            new_record.thong_tin_don_vi = original_record.thong_tin_don_vi
            new_record.kp = original_record.kp
            new_record.kv = original_record.kv
            new_record.bui = original_record.bui
            new_record.tieu_chuan_bui = original_record.tieu_chuan_bui
            new_record.nox = original_record.nox
            new_record.tieu_chuan_nox = original_record.tieu_chuan_nox
            new_record.sox = original_record.sox
            new_record.tieu_chuan_sox = original_record.tieu_chuan_sox
            new_record.co = original_record.co
            new_record.tieu_chuan_co = original_record.tieu_chuan_co

            # Tính toán lại các giá trị
            new_record.calculate_all()

            # Thêm vào danh sách (STT sẽ được tự động đánh số)
            self.add_record(new_record)

            return new_record
        return None

    def _renumber_stt(self):
        """Tái đánh số STT cho tất cả bản ghi"""
        for i, record in enumerate(self.records):
            record.stt = str(i + 1)

    def to_dict(self):
        """Chuyển đổi profile thành dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date,
            'record_count': len(self.records),
            'total_ci': sum(record.ci_total for record in self.records)
        }


class EmissionDataManager:
    """
    Class quản lý danh sách các profile
    """

    def __init__(self):
        self.profiles = []
        self.current_profile_index = None
    
    def create_profile(self, name, description=""):
        """Tạo profile mới"""
        from datetime import datetime
        profile = Profile(name, description)
        profile.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.profiles.append(profile)
        return profile

    def get_profile(self, index):
        """Lấy profile theo index"""
        if 0 <= index < len(self.profiles):
            return self.profiles[index]
        return None

    def get_current_profile(self):
        """Lấy profile hiện tại"""
        if self.current_profile_index is not None and 0 <= self.current_profile_index < len(self.profiles):
            return self.profiles[self.current_profile_index]
        return None

    def set_current_profile(self, index):
        """Đặt profile hiện tại"""
        if 0 <= index < len(self.profiles):
            self.current_profile_index = index
            return True
        return False

    def delete_profile(self, index):
        """Xóa profile"""
        if 0 <= index < len(self.profiles):
            del self.profiles[index]
            # Cập nhật current_profile_index nếu cần
            if self.current_profile_index == index:
                self.current_profile_index = None
            elif self.current_profile_index is not None and self.current_profile_index > index:
                self.current_profile_index -= 1
            return True
        return False

    def get_all_profiles(self):
        """Lấy tất cả profiles"""
        return self.profiles

    # Các phương thức tương thích với code cũ
    def add_record(self, record):
        """Thêm bản ghi vào profile hiện tại"""
        current_profile = self.get_current_profile()
        if current_profile:
            current_profile.add_record(record)
        else:
            # Nếu chưa có profile nào, tạo profile mặc định
            if not self.profiles:
                self.create_profile("Profile mặc định", "Profile được tạo tự động")
                self.set_current_profile(0)
            self.get_current_profile().add_record(record)

    def remove_record(self, index):
        """Xóa bản ghi từ profile hiện tại"""
        current_profile = self.get_current_profile()
        if current_profile:
            current_profile.remove_record(index)

    def get_all_records(self):
        """Lấy tất cả bản ghi từ profile hiện tại"""
        current_profile = self.get_current_profile()
        if current_profile:
            return current_profile.get_all_records()
        return []

    def clear_all(self):
        """Xóa tất cả bản ghi từ profile hiện tại"""
        current_profile = self.get_current_profile()
        if current_profile:
            current_profile.clear_all()

    def to_list_of_dicts(self):
        """Chuyển đổi tất cả records từ profile hiện tại thành list of dictionaries"""
        current_profile = self.get_current_profile()
        if current_profile:
            return current_profile.to_list_of_dicts()
        return []

    def duplicate_record(self, index):
        """Nhân bản bản ghi trong profile hiện tại"""
        current_profile = self.get_current_profile()
        if current_profile:
            return current_profile.duplicate_record(index)
        return None

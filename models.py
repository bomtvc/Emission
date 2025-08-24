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
    
    def calculate_muc_thu_phi_bien_doi(self, tieu_chuan, thuc_te):
        """
        Tính mức thu phí biến đổi dựa trên công thức:
        Nếu (Tiêu chuẩn - Thực tế)/Tiêu chuẩn*100 >= 30 thì = 0.5
        Ngược lại < 30 thì = 0.75
        """
        if tieu_chuan == 0:
            return 0.75  # Tránh chia cho 0

        ty_le = (tieu_chuan - thuc_te) / tieu_chuan * 100
        return 0.5 if ty_le >= 30 else 0.75
    
    def calculate_all(self):
        """
        Tính toán tất cả các giá trị dựa trên dữ liệu đã nhập
        """
        # Tính mức thu phí biến đổi
        self.muc_thu_phi_bui = self.calculate_muc_thu_phi_bien_doi(self.tieu_chuan_bui, self.bui)
        self.muc_thu_phi_nox = self.calculate_muc_thu_phi_bien_doi(self.tieu_chuan_nox, self.nox)
        self.muc_thu_phi_sox = self.calculate_muc_thu_phi_bien_doi(self.tieu_chuan_sox, self.sox)
        self.muc_thu_phi_co = self.calculate_muc_thu_phi_bien_doi(self.tieu_chuan_co, self.co)
        
        # Tính Ci cho từng chất
        base_calculation = self.luu_luong * self.tong_thoi_gian
        
        self.ci_bui = base_calculation * self.bui * self.muc_thu_phi_bui * self.FEE_BUI
        self.ci_sox = base_calculation * self.sox * self.muc_thu_phi_sox * self.FEE_SOX
        self.ci_nox = base_calculation * self.nox * self.muc_thu_phi_nox * self.FEE_NOX
        self.ci_co = base_calculation * self.co * self.muc_thu_phi_co * self.FEE_CO
        
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


class EmissionDataManager:
    """
    Class quản lý danh sách các bản ghi phát thải
    """
    
    def __init__(self):
        self.records = []
    
    def add_record(self, record):
        """Thêm một bản ghi mới"""
        self.records.append(record)
    
    def remove_record(self, index):
        """Xóa bản ghi theo index"""
        if 0 <= index < len(self.records):
            del self.records[index]
    
    def get_all_records(self):
        """Lấy tất cả bản ghi"""
        return self.records
    
    def clear_all(self):
        """Xóa tất cả bản ghi"""
        self.records.clear()
    
    def to_list_of_dicts(self):
        """Chuyển đổi tất cả records thành list of dictionaries"""
        return [record.to_dict() for record in self.records]

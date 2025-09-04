from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import os
import json
from datetime import datetime
from models import EmissionRecord, EmissionDataManager, Profile
from export_utils import ExcelExporter, WordExporter

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Thay đổi trong production

# Khởi tạo data manager
data_manager = EmissionDataManager()

@app.route('/')
def index():
    """Trang chủ hiển thị danh sách profiles"""
    profiles = data_manager.get_all_profiles()
    current_profile = data_manager.get_current_profile()

    # Nếu có profile hiện tại, hiển thị dữ liệu của nó
    if current_profile:
        records = current_profile.to_list_of_dicts()
        total_ci = sum(record['Ci'] for record in records)
    else:
        records = []
        total_ci = 0

    return render_template('index.html',
                         profiles=profiles,
                         current_profile=current_profile,
                         current_profile_index=data_manager.current_profile_index,
                         records=records,
                         total_ci=total_ci)

@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    """Thêm bản ghi mới"""
    # Kiểm tra xem có profile hiện tại không
    current_profile = data_manager.get_current_profile()
    if not current_profile:
        flash('Vui lòng tạo hoặc chọn một profile trước khi thêm nguồn thải!', 'error')
        return redirect(url_for('create_profile'))

    if request.method == 'POST':
        try:
            # Tạo bản ghi mới
            record = EmissionRecord()
            
            # Lấy dữ liệu từ form
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
            
            # Nạp dữ liệu và tính toán
            record.from_dict(form_data)
            
            # Thêm vào data manager
            data_manager.add_record(record)
            
            flash('Đã thêm nguồn thải thành công!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
    
    return render_template('add_record.html')

@app.route('/preview_calculation', methods=['POST'])
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

@app.route('/view_record/<int:index>')
def view_record(index):
    """Xem chi tiết bản ghi"""
    records = data_manager.get_all_records()
    if 0 <= index < len(records):
        record_data = records[index].to_dict()
        return render_template('view_record.html', record=record_data, index=index)
    else:
        flash('Không tìm thấy bản ghi!', 'error')
        return redirect(url_for('index'))

@app.route('/duplicate_record/<int:index>')
def duplicate_record(index):
    """Nhân bản bản ghi"""
    try:
        duplicated_record = data_manager.duplicate_record(index)
        if duplicated_record:
            flash('Đã nhân bản nguồn thải thành công!', 'success')
        else:
            flash('Không tìm thấy bản ghi để nhân bản!', 'error')
    except Exception as e:
        flash(f'Có lỗi xảy ra khi nhân bản: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/edit_record/<int:index>', methods=['GET', 'POST'])
def edit_record(index):
    """Chỉnh sửa bản ghi"""
    # Kiểm tra xem có profile hiện tại không
    current_profile = data_manager.get_current_profile()
    if not current_profile:
        flash('Không có profile nào được chọn!', 'error')
        return redirect(url_for('index'))

    records = data_manager.get_all_records()
    if not (0 <= index < len(records)):
        flash('Không tìm thấy bản ghi!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
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

            # Cập nhật bản ghi
            record = records[index]
            record.from_dict(form_data)
            # Giữ nguyên STT gốc
            record.stt = str(index + 1)

            flash('Đã cập nhật nguồn thải thành công!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    # GET request - hiển thị form chỉnh sửa
    record_data = records[index].to_dict()
    return render_template('edit_record.html', record=record_data, index=index)

@app.route('/delete_record/<int:index>')
def delete_record(index):
    """Xóa bản ghi"""
    try:
        data_manager.remove_record(index)
        flash('Đã xóa bản ghi thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra khi xóa: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/create_profile', methods=['GET', 'POST'])
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
            profile = data_manager.create_profile(name, description)

            # Gán thông tin công ty
            profile.ten_cong_ty = ten_cong_ty
            profile.dia_chi = dia_chi
            profile.mst = mst
            profile.dien_thoai = dien_thoai
            profile.fax = fax
            profile.email = email
            profile.tai_khoan_ngan_hang = tai_khoan_ngan_hang
            profile.tai_ngan_hang = tai_ngan_hang
            profile.loai_hinh_san_xuat = loai_hinh_san_xuat

            # Đặt làm profile hiện tại
            profile_index = len(data_manager.profiles) - 1
            data_manager.set_current_profile(profile_index)

            flash(f'Đã tạo profile "{name}" thành công!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')

    return render_template('create_profile.html')

@app.route('/switch_profile/<int:index>')
def switch_profile(index):
    """Chuyển đổi profile hiện tại"""
    if data_manager.set_current_profile(index):
        profile = data_manager.get_profile(index)
        flash(f'Đã chuyển sang profile "{profile.name}"', 'success')
    else:
        flash('Không tìm thấy profile!', 'error')
    return redirect(url_for('index'))

@app.route('/delete_profile/<int:index>')
def delete_profile(index):
    """Xóa profile"""
    try:
        profile = data_manager.get_profile(index)
        if profile:
            profile_name = profile.name
            if data_manager.delete_profile(index):
                flash(f'Đã xóa profile "{profile_name}" thành công!', 'success')
            else:
                flash('Không thể xóa profile!', 'error')
        else:
            flash('Không tìm thấy profile!', 'error')
    except Exception as e:
        flash(f'Có lỗi xảy ra khi xóa profile: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/clear_all')
def clear_all():
    """Xóa tất cả dữ liệu trong profile hiện tại"""
    current_profile = data_manager.get_current_profile()
    if current_profile:
        data_manager.clear_all()
        flash(f'Đã xóa tất cả dữ liệu trong profile "{current_profile.name}"!', 'success')
    else:
        flash('Không có profile nào được chọn!', 'error')
    return redirect(url_for('index'))

@app.route('/export_excel')
def export_excel():
    """Xuất dữ liệu ra file Excel"""
    try:
        current_profile = data_manager.get_current_profile()
        if not current_profile:
            flash('Không có profile nào được chọn!', 'error')
            return redirect(url_for('index'))

        records = data_manager.to_list_of_dicts()
        if not records:
            flash('Không có dữ liệu để xuất!', 'error')
            return redirect(url_for('index'))

        # Chuẩn bị thông tin profile
        profile_info = {
            'ten_cong_ty': current_profile.ten_cong_ty,
            'dia_chi': current_profile.dia_chi,
            'mst': current_profile.mst,
            'dien_thoai': current_profile.dien_thoai,
            'fax': current_profile.fax,
            'email': current_profile.email
        }

        exporter = ExcelExporter()
        filepath = exporter.export_data(records, profile_name=current_profile.name, profile_info=profile_info)

        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))

    except Exception as e:
        flash(f'Có lỗi xảy ra khi xuất Excel: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/export_word')
def export_word():
    """Xuất dữ liệu ra file Word"""
    try:
        current_profile = data_manager.get_current_profile()
        if not current_profile:
            flash('Không có profile nào được chọn!', 'error')
            return redirect(url_for('index'))

        records = data_manager.to_list_of_dicts()
        if not records:
            flash('Không có dữ liệu để xuất!', 'error')
            return redirect(url_for('index'))

        # Chuẩn bị thông tin profile
        profile_info = {
            'ten_cong_ty': current_profile.ten_cong_ty,
            'dia_chi': current_profile.dia_chi,
            'mst': current_profile.mst,
            'dien_thoai': current_profile.dien_thoai,
            'fax': current_profile.fax,
            'email': current_profile.email
        }

        exporter = WordExporter()
        filepath = exporter.export_data(records, profile_name=current_profile.name, profile_info=profile_info)

        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))

    except Exception as e:
        flash(f'Có lỗi xảy ra khi xuất Word: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/export_json')
def export_json():
    """Xuất dữ liệu ra file JSON để backup"""
    try:
        current_profile = data_manager.get_current_profile()
        if not current_profile:
            flash('Không có profile nào được chọn!', 'error')
            return redirect(url_for('index'))

        # Tạo dữ liệu JSON
        json_data = current_profile.to_json_dict()

        # Tạo tên file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_profile_name = "".join(c for c in current_profile.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_profile_name = clean_profile_name.replace(' ', '_')
        filename = f"Backup_{clean_profile_name}_{timestamp}.json"

        # Lưu file
        filepath = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        return send_file(filepath, as_attachment=True, download_name=filename)

    except Exception as e:
        flash(f'Có lỗi xảy ra khi xuất JSON: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/import_json', methods=['GET', 'POST'])
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
            profile = Profile()
            profile.from_json_dict(data)

            # Thêm vào data manager
            data_manager.profiles.append(profile)

            # Đặt làm profile hiện tại
            profile_index = len(data_manager.profiles) - 1
            data_manager.set_current_profile(profile_index)

            flash(f'Đã nhập thành công profile "{profile.name}" với {len(profile.records)} nguồn thải!', 'success')
            return redirect(url_for('index'))

        except json.JSONDecodeError:
            flash('File JSON không hợp lệ!', 'error')
        except Exception as e:
            flash(f'Có lỗi xảy ra khi nhập JSON: {str(e)}', 'error')

    return render_template('import_json.html')

if __name__ == '__main__':
    # Tạo thư mục uploads nếu chưa có
    os.makedirs('uploads', exist_ok=True)
    
    # Chạy ứng dụng
    app.run(debug=True, host='0.0.0.0', port=5000)

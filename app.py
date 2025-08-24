from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import os
from models import EmissionRecord, EmissionDataManager
from export_utils import ExcelExporter, WordExporter

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Thay đổi trong production

# Khởi tạo data manager
data_manager = EmissionDataManager()

@app.route('/')
def index():
    """Trang chủ hiển thị danh sách dữ liệu"""
    records = data_manager.to_list_of_dicts()
    total_ci = sum(record['Ci'] for record in records)
    return render_template('index.html', records=records, total_ci=total_ci)

@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    """Thêm bản ghi mới"""
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
            
            flash('Đã thêm dữ liệu thành công!', 'success')
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

@app.route('/delete_record/<int:index>')
def delete_record(index):
    """Xóa bản ghi"""
    try:
        data_manager.remove_record(index)
        flash('Đã xóa bản ghi thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra khi xóa: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/clear_all')
def clear_all():
    """Xóa tất cả dữ liệu"""
    data_manager.clear_all()
    flash('Đã xóa tất cả dữ liệu!', 'success')
    return redirect(url_for('index'))

@app.route('/export_excel')
def export_excel():
    """Xuất dữ liệu ra file Excel"""
    try:
        records = data_manager.to_list_of_dicts()
        if not records:
            flash('Không có dữ liệu để xuất!', 'error')
            return redirect(url_for('index'))
        
        exporter = ExcelExporter()
        filepath = exporter.export_data(records)
        
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
    except Exception as e:
        flash(f'Có lỗi xảy ra khi xuất Excel: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/export_word')
def export_word():
    """Xuất dữ liệu ra file Word"""
    try:
        records = data_manager.to_list_of_dicts()
        if not records:
            flash('Không có dữ liệu để xuất!', 'error')
            return redirect(url_for('index'))
        
        exporter = WordExporter()
        filepath = exporter.export_data(records)
        
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
    except Exception as e:
        flash(f'Có lỗi xảy ra khi xuất Word: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Tạo thư mục uploads nếu chưa có
    os.makedirs('uploads', exist_ok=True)
    
    # Chạy ứng dụng
    app.run(debug=True, host='0.0.0.0', port=5000)

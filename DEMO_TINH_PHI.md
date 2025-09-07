# Demo Tính Toán Phí Môi Trường

## Công thức tính phí

### Phí cố định
- **Mức phí**: 750,000 VNĐ
- **Áp dụng**: Cho mọi doanh nghiệp có hoạt động phát thải

### Phí phát sinh (biến đổi)
- **Công thức**: Tổng Ci của tất cả nguồn thải
- **Ci**: Chỉ số phát thải của từng nguồn thải (VNĐ)

### Tổng phí
```
Tổng phí = Phí cố định + Phí phát sinh
Tổng phí = 750,000 + Σ(Ci của tất cả nguồn thải)
```

## Ví dụ tính toán

### Dữ liệu mẫu (Profile: Plant 1)

| STT | Tên Nguồn thải | Ci (VNĐ) |
|-----|----------------|----------|
| 1   | Khí thải hơi dung môi | 387 |
| 2   | Khí thải lò hơi 1 | 387 |
| 3   | Khí thải lò hơi 2 | 387 |
| 4   | Đầu ra HTXL Cyclone | 388 |

### Tính toán

```
Phí cố định = 750,000 VNĐ
Phí phát sinh = 387 + 387 + 387 + 388 = 1,549 VNĐ
Tổng phí = 750,000 + 1,549 = 751,549 VNĐ
```

### Chuyển đổi thành chữ
```
751,549 VNĐ = "Bảy trăm năm mươi một nghìn năm trăm bốn mươi chín đồng"
750,000 VNĐ = "Bảy trăm năm mươi nghìn đồng"
1,549 VNĐ = "Một nghìn năm trăm bốn mươi chín đồng"
```

## Biến template sử dụng

### Trong template Word (TO_KHAI.docx):

```jinja2
<!-- Phí cố định -->
{{phi_co_dinh}} VNĐ
{{phi_do_dinh}} VNĐ

<!-- Phí phát sinh -->
{{result_data['Ci']}} VNĐ

<!-- Tổng phí -->
{{phi_co_dinh + result_data['Ci']}} VNĐ
{{tong_phi}} VNĐ

<!-- Số tiền bằng chữ -->
{{so_tien_bang_chu}}
```

### Context data được truyền:

```python
{
    'phi_co_dinh': 750000,
    'phi_do_dinh': 750000,           # Alias
    'phi_phat_sinh': 1549,
    'tong_phi': 751549,
    'result_data': {'Ci': 1549},
    'so_tien_bang_chu': 'Bảy trăm năm mươi một nghìn năm trăm bốn mươi chín đồng'
}
```

## Lưu ý

1. **Phí cố định**: Được hard-code trong code là 750,000 VNĐ
2. **Phí phát sinh**: Được tính tự động từ dữ liệu Ci trong database
3. **Chuyển đổi số thành chữ**: Sử dụng hàm `so_thanh_chu()` đơn giản
4. **Template**: Có thể sử dụng nhiều biến khác nhau để hiển thị cùng một giá trị

## Cách thay đổi phí cố định

Để thay đổi mức phí cố định, sửa trong file `export_utils.py`:

```python
# Dòng 330
phi_co_dinh = 750000  # Thay đổi số này
```

---

**Ngày tạo**: 2025-09-07  
**Phiên bản**: 3.2

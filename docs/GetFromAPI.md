# Get Data From API

Trích xuất một giá trị cụ thể (ảnh hoặc văn bản) từ từ điển `all_data` được tạo ra bởi node **APITrigger**.

## Đầu vào (Inputs)
- **all_data**: Liên kết từ điển từ APITrigger.
- **key**: Tên trường dữ liệu từ yêu cầu POST ban đầu.

## Đầu ra (Outputs)
- **text**: Giá trị dưới dạng chuỗi văn bản.
- **image**: Ảnh nếu giá trị trỏ đến một đường dẫn ảnh hợp lệ.

# Node System & Queue Status

Node này giúp bạn theo dõi "sức khỏe" của server ComfyUI một cách chi tiết, rất hữu ích khi bạn vận hành hệ thống qua API.

## Các Thông Số Theo Dõi
Node cung cấp 3 loại đầu ra chính:

### 1. all_stats (Dữ liệu chi tiết - DICT)
Trả về một từ điển chứa đầy đủ các thông số kỹ thuật, phù hợp để gửi qua Webhook hoặc phân tích logic:
- **queue**: `running` (đang chạy), `pending` (đang chờ), `total`.
- **system**: `% CPU` đang dùng, `% RAM` đang dùng, `Dung lượng RAM trống (GB)`.
- **gpu**: Tên card đồ họa, `% VRAM` đang dùng, `VRAM trống (GB)`.
- **is_idle**: Trả về `True` nếu hệ thống đang rảnh (không có task nào chạy).

### 2. summary_text (Tóm tắt nhanh - STRING)
Một dòng chữ ngắn gọn tóm tắt tình trạng máy chủ, ví dụ: 
`Q: 1 running, 0 pending | CPU: 15% | RAM: 45% | VRAM: 30%`

### 3. is_idle (Trạng thái rảnh - BOOLEAN)
Giá trị logic Đúng/Sai để bạn có thể kết nối với các node Switch, giúp workflow đưa ra quyết định dựa trên việc server có đang bận hay không.

## Ứng dụng thực tế
- Sử dụng trước khi gọi API để tránh làm nghẽn server.
- Gửi thông tin tài nguyên máy chủ về dashboard của bạn qua Webhook.
- Tự động cảnh báo nếu VRAM hoặc RAM sắp hết.

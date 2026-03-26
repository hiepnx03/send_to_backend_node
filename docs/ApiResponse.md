# Node API Response (Sync Out)

Node này chịu trách nhiệm đóng gói và gửi kết quả cuối cùng quay trở lại cho ứng dụng gọi API (ví dụ: Frontend Web). Phiên bản mới đã được nâng cấp để tùy biến cao hơn.

## Các Tùy Chọn Bật/Tắt (Toggles)
Bạn có thể điều chỉnh dữ liệu trả về để tối ưu dung lượng API:
- **include_image**: Cho phép trả về ảnh hoặc danh sách ảnh dưới dạng chuỗi Base64.
- **include_text**: Cho phép trả về kết quả văn bản.
- **include_stats**: Cho phép trả về các thông số kỹ thuật (thời gian xử lý, độ phân giải, batch size).

## Các Đầu Vào Mới
- **extra_data**: Một cổng kết nối (DICT) giúp bạn truyền bất kỳ dữ liệu phụ nào từ các node Vision hoặc Automation vào kết quả API cuối cùng.
- **image**: Hỗ trợ cả ảnh đơn lẻ và một batch (nhóm) ảnh.

## Cấu Trúc Kết Quả API
Khi gọi API ở chế độ đồng bộ (`?wait=true`), bạn sẽ nhận được:
- **execution_time_sec**: Thời gian tính từ lúc API nhận yêu cầu đến khi workflow chạy xong ở node này.
- **images_base64**: Xuất hiện thay cho `image_base64` nếu bạn gen nhiều ảnh cùng lúc.

---
*Gợi ý: Nếu bạn chỉ cần lấy text (ví dụ: dùng ComfyUI như một con AI Vision), hãy tắt `include_image` để API phản hồi nhanh hơn.*

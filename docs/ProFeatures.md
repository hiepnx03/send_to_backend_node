# Pro Utilities (Bộ Công Cụ Cao Cấp)

Bộ node này cung cấp các tính năng xử lý ảnh và video chuyên sâu, giúp workflow API của bạn trở nên chuyên nghiệp hơn.

---

## 1. Auto Background Remover (Xóa Phông Tự Động)
Sử dụng thư viện `rembg` để tách người/vật thể ra khỏi nền ngay lập tức.
- **Đầu vào**: IMAGE.
- **Đầu ra**: IMAGE (đã xóa nền) và MASK (mặt nạ độ trong suốt).
- **Ứng dụng**: Phù hợp cho API tạo sticker, ảnh sản phẩm thương mại điện tử.

## 2. Color Palette Extractor (Trích Xuất Bảng Màu)
Phân tích ảnh và trả về danh sách các màu sắc chủ đạo.
- **Đầu vào**: IMAGE, số lượng màu (mặc định 5).
- **Đầu ra**: Chuỗi HEX (ví dụ: `#ffffff, #000000`) và JSON Palette.
- **Ứng dụng**: Giúp các ứng dụng Frontend đồng bộ màu sắc giao diện với ảnh vừa tạo.

## 3. Video Preview (Frame Grid)
Trích xuất các khung hình từ video và gộp thành một tấm ảnh duy nhất (Mosaic).
- **Đầu vào**: IMAGES (chuỗi khung hình từ video).
- **Đầu ra**: IMAGE (ảnh Grid).
- **Tại sao cần?**: Thay vì trả về video nặng hàng chục MB qua API, bạn có thể trả về ảnh preview này để người dùng xem nhanh kết quả.

## 4. Prompt Router (Điều Hướng Thông Minh)
Dựa vào từ khóa trong Prompt để quyết định workflow sẽ đi theo hướng nào.
- **Đầu vào**: TEXT (Prompt từ API).
- **Cách dùng**: Nhập các từ khóa vào 3 nhóm (`keywords_1`, `keywords_2`, `keywords_3`). 
- **Đầu ra**: 4 cổng BOOLEAN (`match_1`, `match_2`, `match_3`, `no_match`).
- **Ứng dụng**: Tự động chọn Model/LoRA dựa trên yêu cầu của khách hàng (ví dụ: nếu có chữ "landscape" thì dùng Model phong cảnh).

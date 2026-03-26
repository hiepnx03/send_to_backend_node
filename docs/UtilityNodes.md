# Ultimate Utility Suite (Siêu Tiện Ích)

Bộ node này cung cấp các công cụ bổ trợ mạnh mẽ để xử lý số liệu, chèn chữ chuyên nghiệp và hậu kỳ hình ảnh ngay trong ComfyUI.

---

## 1. Ultimate Math Expression (Tính toán biểu thức)
Cho phép bạn thực hiện các phép tính phức tạp giữa các giá trị FLOAT/INT.
- **Biểu thức ví dụ**: `(a + b) * 1.5`, `sqrt(a^2 + b^2)`, `max(a, b) / 2`.
- **Ứng dụng**: Tự động tính toán kích thước ảnh, độ mờ (Blur) dựa trên các tham số khác.

## 2. Advanced Text Overlay (Chèn chữ nâng cao)
Công cụ hoàn hảo để tạo Meme, ảnh Quote, hoặc đóng dấu nhãn hiệu cho sản phẩm.
- **Căn lề**: Hỗ trợ 7 chế độ căn lề (Trái, Phải, Giữa, Trên, Dưới).
- **Shadow**: Có bóng đổ (Shadow) để chữ nổi bật trên mọi nền ảnh.
- **Margin**: Điều chỉnh khoảng cách lề theo tỷ lệ % linh hoạt.

## 3. Professional Image Sharpener (Làm nét chuyên nghiệp)
Bộ lọc làm nét ảnh cao cấp dùng để hậu kỳ sau khi gen ảnh hoặc upscale.
- **Strength**: Điều chỉnh độ sắc nét từ nhẹ nhàng đến cực mạnh.
- **Ứng dụng**: Giúp các chi tiết nhỏ trong mắt, tóc, hoặc vân vải trở nên rõ nét hơn.

## 4. Smart Auto-Crop (Cắt ảnh theo tỷ lệ)
Tự động cắt ảnh về các tỷ lệ khung hình chuẩn mà không làm méo vật thể.
- **Tỷ lệ hỗ trợ**: 1:1 (Square), 16:9 (Widescreen), 9:16 (TikTok/Reels), 4:5 (Instagram).
- **Logic**: Tự động lấy vùng trung tâm và cắt bỏ phần thừa để đảm bảo tỷ lệ chính xác.

## 5. Ultimate Random Generator (Tạo giá trị ngẫu nhiên)
- **UUID**: Tạo mã định danh duy nhất cho mỗi lần gen (tránh trùng lặp file).
- **Filename**: Tự động tạo tên file có timestamp và prefix.
- **Hex Color**: Tạo màu sắc ngẫu nhiên ở định dạng Hex (dễ dàng dùng cho node Text Overlay).
- **Int Range**: Sinh số ngẫu nhiên trong một khoảng xác định (dùng để random tham số).

---

## Mẹo kết hợp:
Bạn có thể dùng **Ultimate Math Expression** để tính toán lề (Margin) cho node **Text Overlay**, sau đó dùng **Random Generator** để tạo màu chữ ngẫu nhiên cho mỗi bức ảnh!
 Eleanor

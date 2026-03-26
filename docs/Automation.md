# Bộ Node Tự Động Hóa (Automation Suite)

Bộ node này cung cấp đầy đủ các công cụ từ cơ bản đến nâng cao để xây dựng workflow tự động hóa chuyên nghiệp trong ComfyUI.

## 1. Nhóm Node Cơ Bản (Logic & Text)
- **Text Combiner**: Gộp tối đa 4 đoạn văn bản thành một chuỗi duy nhất với dấu phân cách tùy chỉnh.
- **Text Switch / Image Switch**: Công tắc chọn dữ liệu đầu ra dựa trên điều kiện Đúng/Sai (Boolean).
- **Variable Storage**: Lưu trữ và truy xuất các giá trị văn bản vào file JSON (`v_storage.json`) để dùng lại sau này.

## 2. Nhóm Node Nâng Cao (Xử lý & Debug)
- **API Image Resizer**: Thay đổi kích thước ảnh theo chuẩn Stable Diffusion (chia hết cho 8) với các chế độ Stretch, Fit, hoặc Crop.
- **Console Logger (Debug)**: In thông tin log ra cửa sổ Terminal với màu xanh nổi bật để theo dõi dữ liệu API.
- **Global Time Stamper**: Tạo mốc thời gian hiện tại theo định dạng tùy chỉnh (phục vụ đặt tên file).
- **Text Replacer (API)**: Tìm kiếm và thay thế văn bản, hỗ trợ cả biểu thức chính quy (Regex).

## 3. Nhóm Node Chuyên Nghiệp (Hậu Kỳ & Lưu Trữ)
- **Pro Image Watermark**: Chèn Logo/Watermark lên ảnh với tùy chỉnh vị trí, tỷ lệ và độ trong suốt.
- **Image Grid (Mosaic)**: Gộp nhóm ảnh thành một tấm ảnh lưới (contact sheet) duy nhất.
- **Dynamic File Saver**: Lưu ảnh vào các thư mục được phân loại tự động theo ngày tháng hoặc tiền tố động. Trả về đường dẫn file sau khi lưu.

---
*Tất cả các node này nằm trong mục **Automation** và **API** trong menu của ComfyUI.*

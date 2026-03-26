# Các Node Phân Tích Hình Ảnh (Vision)

Bộ node này sử dụng các mô hình học sâu (Deep Learning) để giúp ComfyUI "nhìn" và hiểu hình ảnh, từ đó tự động hóa việc tạo ra các prompt sáng tạo.

## 1. AI Image to Prompt (BLIP)
Sử dụng mô hình BLIP (Bootstrapping Language-Image Pre-training) để phân tích ảnh và sinh ra câu mô tả văn bản. 
- **image**: Ảnh đầu vào cần phân tích.
- **model_name**: 
    - `blip-image-captioning-base`: Phiên bản tiêu chuẩn, tốc độ nhanh.
    - `blip-image-captioning-large`: Phiên bản lớn, mô tả chi tiết và chính xác hơn.

> [!IMPORTANT]
> Lần đầu tiên sử dụng, node sẽ tải mô hình từ internet (dung lượng khoảng 1GB). Quá trình này có thể mất vài phút tùy vào tốc độ mạng của bạn.

## 2. Creative Prompt Variation (N)
Nhận một câu mô tả gốc và tự động sinh ra `N` biến thể khác nhau bằng cách phối hợp ngẫu nhiên các phong cách nghệ thuật, góc chụp và điều kiện ánh sáng.
- **base_prompt**: Nội dung gốc (ví dụ lấy từ kết quả của node ImageToText).
- **n_variations**: Số lượng phiên bản bạn muốn tạo ra (ví dụ: tạo 5 prompt khác nhau từ 1 ảnh).
- **seed**: Dùng để cố định kết quả ngẫu nhiên.
- **use_angles / styles / lighting**: Tùy chọn bật/tắt các nhóm sáng tạo.

**Đầu ra:**
- **combined_text**: Toàn bộ các prompt được gộp lại, phân cách bằng dấu `---`.
- **first_variation**: Chỉ lấy prompt đầu tiên để đưa trực tiếp vào các node tạo ảnh (như CLIP Text Encode).
 bitumen

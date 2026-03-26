# Hướng Dẫn Cài Đặt Model Offline (Flux 2 & LTX 2.3)

Tài liệu này hướng dẫn bạn cách tải và cấu hình các model mạnh mẽ nhất hiện nay để chạy hoàn toàn Offline trên máy cá nhân, kết hợp với bộ node API.

---

## 1. FLUX 2 (Model Tạo Ảnh Bá Chủ)
Flux 2 yêu cầu cấu hình máy tính khá mạnh (Khuyên dùng VRAM từ 12GB trở lên).

### Các File Cần Tải (Từ Hugging Face):
- **Checkpoint**: Tải bản `flux2-dev-fp8.safetensors` (đã nén để nhẹ hơn).
- **VAE**: Tải `flux-vae.safetensors`.
- **CLIP**: Tải `clip_l.safetensors` và `t5xxl_fp8_e4m3fn.safetensors`.

### Vị Trí Lưu File:
- Checkpoint: `ComfyUI/models/checkpoints/`
- VAE: `ComfyUI/models/vae/`
- CLIP: `ComfyUI/models/clip/`

### Cấu Hình API:
Để chạy Flux 2 qua API nhanh nhất, hãy dùng node **APITrigger** truyền Prompt vào node **CLIP Text Encode (Flux)**. Flux 2 rất nhạy cảm với Prompt dài, hãy dùng node **Text Replacer** của bộ Automation để làm sạch prompt trước khi gen.

---

## 2. LTX 2.3 (Model Tạo Video Đỉnh Cao)
LTX 2.3 là model tạo video có âm thanh mã nguồn mở tốt nhất hiện nay.

### Cách Cài Đặt:
1. Cài đặt Custom Node: `ComfyUI-LTX-Video`.
2. Tải Model (`ltx-2.3-22b-distilled.safetensors`) từ Hugging Face của Lightricks.
3. Lưu vào: `ComfyUI/models/checkpoints/LTX-Video/`.

### Lưu Ý Khi Dùng Với API:
- Video gen ra thường rất nặng. Hãy dùng node **Image Grid** của bộ Automation để tạo "ảnh xem trước" (Preview Grid) trước khi trả về API Sync Mode.
- Sử dụng node **System Status** để kiểm tra VRAM vì LTX 2.3 ngốn rất nhiều tài nguyên (nên có 24GB VRAM để chạy mượt).

---

## 3. HUNYUAN VIDEO (Sức Mạnh Từ Tencent)
Model này đang cực hot vì khả năng hiểu prompt và chất lượng video cực cao.

### Cài Đặt:
- **Main Model**: `hunyuan_video_720p_bf16.safetensors` -> `models/diffusion_models/`
- **VAE**: `hunyuan_video_vae_bf16.safetensors` -> `models/vae/`
- **Text Encoders**: `clip_l.safetensors` và `llava_llama3_fp8_scaled.safetensors` -> `models/text_encoders/`

---

## 4. COGVIDEOX (Nhẹ Nhàng & Hiệu Quả)
Nếu máy bạn không quá mạnh, CogVideoX (bản 2B hoặc 5B) là lựa chọn tuyệt vời.

### Cài Đặt:
1. Cài Custom Node: `ComfyUI CogVideoX Wrapper`.
2. Model thường được tự động tải về khi chạy workflow lần đầu, hoặc bạn có thể tải bản `fp8` để tiết kiệm VRAM.

---

## 5. MOCHI 1 (Chuyển Động Siêu Thực)
Được đánh giá cao về độ mượt mà của chuyển động ("High-fidelity motion").

### Cài Đặt:
1. Cài Custom Node: `ComfyUI-MochiWrapper`.
2. Tải bản All-in-one: `mochi_preview_fp8_scaled.safetensors` -> `models/checkpoints/`. Đây là bản rút gọn giúp bạn khởi chạy nhanh nhất.

---

# II. Image to Video (Chuyển Ảnh thành Video)

Các model này cho phép bạn đưa 1 tấm ảnh đầu vào (từ API) và nó sẽ tự động làm cho tấm ảnh đó chuyển động.

## 1. HUNYUANVIDEO-I2V (Tencent - Mới nhất)
Vừa ra mắt đầu năm 2025, cho khả năng nhất quán nhân vật cực tốt.
- **Model**: `hunyuan_video_image_to_video_720p_bf16.safetensors`
- **Vị trí**: `models/diffusion_models/`
- **Lưu ý**: Cần dùng chung với các text encoder của bản Hunyuan Video gốc.

## 2. COGVIDEOX-1.5 5B-I2V
Hỗ trợ tạo video 10 giây với độ phân giải cao và chuyển động phức tạp.
- **Custom Node**: `ComfyUI CogVideoX Wrapper`.
- **Phần cứng**: Yêu cầu VRAM từ 12-16GB để chạy mượt bản 5B.

## 3. STABLE VIDEO DIFFUSION (SVD-XT)
Model "quốc dân" cho việc chuyển ảnh thành video, nhẹ và chạy nhanh trên nhiều dòng card.
- **Model**: `svd_img2vid_xt_1_1.safetensors`
- **Vị trí**: `models/checkpoints/`
- **Cấu hình API**: Bạn có thể gửi ảnh qua API, dùng node **APITrigger** để nhận ảnh, rồi đưa thẳng vào node **SVD_img2vid_Conditioning**.

---

## 6. Tại Sao Nên Chạy Offline?
1. **Bảo mật**: Dữ liệu ảnh và prompt của khách hàng không bao giờ rời khỏi server của bạn.
2. **Tiết kiệm**: Không mất phí gọi API theo lượt cho các bên như OpenAI hay Midjourney.
3. **Tốc độ**: Với card đồ họa RTX 3090/4090, việc gen video có thể thực hiện liên tục mà không lo bị bóp băng thông.

> [!TIP]
> Bạn nên sử dụng node **Dynamic File Saver** để lưu kết quả của các model này vào các thư mục riêng biệt theo tên model (`output/flux2/%Y-%m-%d`) để dễ quản lý.

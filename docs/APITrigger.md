# APITrigger (Dynamic)

Node này cho phép bạn kích hoạt workflow ComfyUI thông qua một yêu cầu HTTP POST từ bên ngoài. Phiên bản mới đã hỗ trợ quản lý nhiều workflow khác nhau.

## Đầu vào (Inputs)
- **workflow_name**: Tên định danh cho workflow này (mặc định là `default`). Khi bạn nhấn Queue Prompt, workflow sẽ được lưu lại với tên này.
- **api_data**: Dữ liệu JSON gửi từ API.
- **batch_size**: Số lượng ảnh cần gen.
- **first_image**: File ảnh đầu tiên tìm thấy trong yêu cầu POST.
- **first_text**: Trường văn bản đầu tiên tìm thấy trong yêu cầu POST.
- **all_data**: Một từ điển (dictionary) chứa tất cả các trường và đường dẫn file từ yêu cầu POST.
- **batch_size**: Số lượng batch được truyền từ API (mặc định là 1). Dùng để nối vào các node 'Empty Latent Image' hoặc 'Prompt Augmenter'.

## Cách hoạt động
1. Thêm node này vào workflow của bạn.
2. Nhấn **Queue Prompt** một lần trong giao diện UI để "đăng ký" workflow.
3. Gọi API `http://localhost:8188/api/v1/trigger` với dữ liệu dạng form-data.
    - **Trường ảnh**: Có thể gửi file trực tiếp HOẶC gửi link ảnh (URL). Nếu là link, server sẽ tự động tải về.
    - **Trường text**: Bất kỳ trường văn bản nào khác.
    - **Tham số `workflow`**: (Tùy chọn) Truyền tên workflow muốn chạy (ví dụ: `?workflow=remove_bg` hoặc thêm vào form-data). Nếu không truyền, mặc định sẽ là `default`.

## Quản lý nhiều Workflow
Hệ thống cho phép bạn lưu trữ không giới hạn số lượng workflow:
1. Trong node **APITrigger**, hãy đặt một tên gợi nhớ tại ô `workflow_name` (ví dụ: `generate_portrait`).
2. Nhấn **Queue Prompt**. Workflow sẽ được lưu vào thư mục `workflows/`.
3. Khi gọi API, chỉ cần thêm tham số `workflow=generate_portrait` để chạy đúng workflow đó.

### API Danh sách Workflow
- **Endpoint**: `GET /api/v1/workflows`
- **Kết quả**: Trả về danh sách tất cả các tên workflow đã được đăng ký.

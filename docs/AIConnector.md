# AI Universal Connector (Bộ não AI)

Node này cho phép bạn kết nối ComfyUI với các mô hình ngôn ngữ lớn (LLM) để tự động hóa quy trình suy nghĩ, viết prompt và phân tích dữ liệu.

---

## 1. Cách Cài Đặt LLM Cục Bộ (Khuyên dùng)

Để chạy các model "xịn" hoàn toàn offline và miễn phí, bạn nên dùng **Ollama**.

### Bước 1: Tải và cài đặt Ollama
- Truy cập [ollama.com](https://ollama.com) và tải bản cài đặt cho Windows.
- Chạy bản cài đặt.

### Bước 2: Tải các Model mạnh nhất hiện nay
Mở Terminal (CMD hoặc PowerShell) và chạy các lệnh sau:
- **Llama 3.1 (Rất đa năng)**: `ollama run llama3.1`
- **Gemma 2 (Google - Rất thông minh)**: `ollama run gemma2`
- **Phi-3 (Microsoft - Nhẹ và nhanh)**: `ollama run phi3`

---

## 2. Cách Sử Dụng Node Trong ComfyUI

### Thông số cấu hình (Ollama mặc định):
- **api_url**: `http://localhost:11434/v1/chat/completions`
- **api_key**: `ollama` (hoặc bất kỳ ký tự nào vì Ollama local không check key).
- **model**: Tên model bạn đã tải (ví dụ: `llama3.1`).

### Chế độ Prompt Refiner (Làm đẹp Prompt):
- **System Prompt**: "You are a professional Stable Diffusion prompt engineer. Expand the user's short description into a detailed, high-quality prompt with artistic keywords, lighting, and camera settings. Return ONLY the refined prompt."
- **User Prompt**: "A cat in a space suit"
- **Kết quả**: LLM sẽ tự động tạo ra một prompt dài và chuyên nghiệp hơn để bạn đưa vào KSampler.

### Chế độ Negative Gen (Tạo Negative Prompt):
- **System Prompt**: "Based on the user's prompt, generate a tailored negative prompt that avoids typical artifacts and unwanted elements for this specific style. Return ONLY the negative keywords."

---

## 3. Kết nối với các dịch vụ khác
Bạn cũng có thể dùng node này để kết nối với:
- **LM Studio**: Bật "Local Server" trong LM Studio và dùng URL mặc định (thường là `http://localhost:1234/v1/chat/completions`).
- **OpenAI**: Dùng URL `https://api.openai.com/v1/chat/completions` và dán `api_key` của bạn vào.

---

## 4. Lợi ích vượt trội
- **Tự động hóa hoàn toàn**: Bạn chỉ cần nhập ý tưởng sơ sài, AI sẽ lo phần kỹ thuật.
- **Quyết định thông minh**: Kết hợp với node `Prompt Router` để điều hướng workflow dựa trên phân tích của LLM.
- **Offline 100%**: Nếu dùng Ollama, không có dữ liệu nào của bạn bị gửi ra ngoài internet.

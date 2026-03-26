# Gemini Browser Bridge (Nâng cấp Tự Động Hóa)

Tài liệu này cung cấp mã nguồn **Extension v2** với khả năng tự động tải ảnh (Upload Image) và nhận dạng kết quả thông minh.

---

## Hướng Dẫn Nâng Cấp Extension

### 1. content.js (Bản nâng cấp)
File này chứa logic quan trọng nhất để điều khiển Gemini.

```javascript
// content.js
async function pasteImage(base64Data, targetElement) {
    const res = await fetch(`data:image/png;base64,${base64Data}`);
    const blob = await res.blob();
    const file = new File([blob], "image_comfyui.png", { type: "image/png" });
    
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    
    const pasteEvent = new ClipboardEvent("paste", {
        bubbles: true,
        cancelable: true,
        clipboardData: dataTransfer
    });
    targetElement.focus();
    targetElement.dispatchEvent(pasteEvent);
    console.log("Image pasted successfully.");
}

function waitForResponse(prompt_id) {
    return new Promise((resolve) => {
        let lastLength = 0;
        let stableCount = 0;
        
        const observer = new MutationObserver(() => {
            // 1. Tìm nút Send để biết AI đã xong chưa
            const sendButton = document.querySelector('button[aria-label="Send message"]') || 
                               document.querySelector('.send-button');
            const isProcessing = sendButton && sendButton.hasAttribute("disabled");

            // 2. Lấy nội dung phản hồi cuối cùng
            const responses = document.querySelectorAll(".model-response-text, .markdown");
            const lastResponse = responses[responses.length - 1];
            
            if (lastResponse) {
                const currentText = lastResponse.innerText;
                if (!isProcessing && currentText.length > 0 && currentText.length === lastLength) {
                    stableCount++;
                    if (stableCount > 3) { // Đảm bảo text không đổi trong 3 nhịp observer
                        observer.disconnect();
                        resolve(currentText);
                    }
                } else {
                    lastLength = currentText.length;
                    stableCount = 0;
                }
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });
    });
}

chrome.runtime.onMessage.addListener(async (request) => {
    if (request.type === "gemini_request") {
        console.log("Processing request:", request.prompt_id);
        
        const inputArea = document.querySelector('[contenteditable="true"]') || 
                          document.querySelector('textarea[placeholder*="Gemini"]');
        
        if (!inputArea) {
            console.error("Input area not found!");
            return;
        }

        // 1. Upload ảnh nếu có
        if (request.image_base64) {
             await pasteImage(request.image_base64, inputArea);
             await new Promise(r => setTimeout(r, 1000)); // Chờ ảnh load
        }

        // 2. Nhập Prompt
        inputArea.innerText = request.prompt;
        inputArea.dispatchEvent(new Event('input', { bubbles: true }));

        // 3. Ấn gửi
        setTimeout(() => {
            const sendButton = document.querySelector('button[aria-label="Send message"]') || 
                               document.querySelector('.send-button');
            if (sendButton) sendButton.click();
        }, 500);

        // 4. Đợi phản hồi thông minh
        const responseText = await waitForResponse(request.prompt_id);
        
        chrome.runtime.sendMessage({
            type: "gemini_response",
            prompt_id: request.prompt_id,
            text: responseText
        });
    }
});
```

### 2. background.js & manifest.json
(Vẫn giữ nguyên như bản v1, nhưng hãy đảm bảo bạn đã cấp quyền `host_permissions` đầy đủ).

---

## Các Cải Tiến Mới (V2)
1. **Tự động Paste Ảnh**: Nếu node **Gemini Browser Bridge** nhận vào một IMAGE, extension sẽ tự động "dán" ảnh đó vào cửa sổ chat của Gemini trước khi gửi.
2. **Theo dõi thông minh (MutationObserver)**: Node sẽ không đợi một khoảng thời gian cố định nữa. Nó sẽ theo dõi DOM của Gemini:
    - Khi nút Send mở khóa trở lại.
    - Khi đoạn văn bản phản hồi ngừng thay đổi chiều dài (đã viết xong).
3. **Độ trễ thấp**: Phản hồi sẽ được gửi ngược về ComfyUI ngay lập tức khi Gemini trả lời xong.

## Lưu ý quan trọng
- Bạn cần đảm bảo cửa sổ trình duyệt Gemini đang **mở và đăng nhập** sẵn.
- Nên chạy Gemini trong một cửa sổ riêng biệt để tránh bị gián đoạn khi bạn làm việc khác.

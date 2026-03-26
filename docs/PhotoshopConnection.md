# Photoshop Bridge (Kết nối Adobe Photoshop)

Bộ node này cho phép bạn biến Photoshop thành một phần của workflow ComfyUI. Bạn có thể gửi ảnh từ ComfyUI sang Photoshop thành layer mới, hoặc lấy canvas đang vẽ từ Photoshop về ComfyUI để xử lý AI.

---

## 1. Cách Hoạt Động
Vì Photoshop là ứng dụng Desktop, chúng ta cần một "Cầu nối" (Bridge) để kết nối ComfyUI WebSocket với Photoshop API.

## 2. Hướng Dẫn Cài Đặt "Cầu Nối" (Python Bridge)

Tôi khuyên bạn nên dùng một script Python chạy ngầm trên máy để điều khiển Photoshop.

### Bước 1: Cài đặt thư viện cần thiết
Mở Terminal/CMD và chạy:
```bash
pip install photoshop-python-api websockets Pillow
```

### Bước 2: Lưu và chạy Script sau (`ps_bridge.py`)
```python
import asyncio
import websockets
import json
import base64
import io
import os
from PIL import Image
from photoshop import Session

COMFY_WS_URL = "ws://localhost:8188/api/v1/photoshop/ws"

async def bridge():
    async with websockets.connect(COMFY_WS_URL) as ws:
        print("✅ Đã kết nối tới ComfyUI Photoshop Bridge")
        
        async for message in ws:
            data = json.loads(message)
            msg_type = data.get("type")
            
            with Session() as ps:
                if msg_type == "new_layer":
                    # Nhận ảnh từ ComfyUI và tạo layer mới
                    img_data = base64.b64decode(data["image"])
                    img = Image.open(io.BytesIO(img_data))
                    temp_path = os.path.abspath("temp_comfy_layer.png")
                    img.save(temp_path)
                    
                    desc = ps.ActionDescriptor
                    desc.putPath(ps.app.charIDToTypeID("null"), temp_path)
                    ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
                    ps.active_document.activeLayer.name = data["layer_name"]
                    print(f"📥 Đã tạo layer: {data['layer_name']}")

                elif msg_type == "get_canvas":
                    # Gửi toàn bộ canvas
                    temp_out = os.path.abspath("temp_ps_out.png")
                    ps.active_document.saveAs(temp_out, ps.PNGSaveOptions(), True)
                    with open(temp_out, "rb") as f:
                        img_b64 = base64.b64encode(f.read()).decode("utf-8")
                    await ws.send(json.dumps({
                        "type": "canvas_response",
                        "request_id": data["request_id"],
                        "image": img_b64
                    }))
                    print("📤 Đã gửi canvas")

                elif msg_type == "get_selection":
                    # Lấy vùng chọn (Selection) và Mask
                    print("📤 Đang trích xuất vùng chọn...")
                    jsx = """
                    var doc = app.activeDocument;
                    var file = new File('""" + os.path.abspath("temp_sel.png").replace("\\", "/") + """');
                    try {
                        doc.selection.copy();
                        var tempDoc = app.documents.add(doc.selection.bounds[2]-doc.selection.bounds[0], doc.selection.bounds[3]-doc.selection.bounds[1], 72, "Temp", NewDocumentMode.RGB, DocumentFill.TRANSPARENT);
                        tempDoc.paste();
                        tempDoc.saveAs(file, new PNGSaveOptions(), true);
                        tempDoc.close(SaveOptions.DONOTSAVECHANGES);
                    } catch(e) { }
                    """
                    ps.app.doJavaScript(jsx)
                    
                    if os.path.exists("temp_sel.png"):
                        with open("temp_sel.png", "rb") as f:
                            img_b64 = base64.b64encode(f.read()).decode("utf-8")
                        await ws.send(json.dumps({
                            "type": "selection_response",
                            "request_id": data["request_id"],
                            "image": img_b64,
                            "mask": img_b64
                        }))

                elif msg_type == "get_layers":
                    # Lấy danh sách layer
                    layers = [l.name for l in ps.active_document.layers]
                    await ws.send(json.dumps({
                        "type": "layers_response",
                        "request_id": data["request_id"],
                        "layers": layers
                    }))
                    print(f"📤 Đã gửi danh sách {len(layers)} layers")

                elif msg_type == "run_jsx":
                    # Chạy script tùy chỉnh
                    print(f"⚙️ Đang chạy JSX: {data['script'][:20]}...")
                    ps.app.doJavaScript(data["script"])

asyncio.run(bridge())
```

---

## 3. Các Node khả dụng
- **Send to Photoshop**: Gửi ảnh ComfyUI sang Photoshop. Bạn có thể đặt tên `layer_name` để dễ quản lý trong PS.
- **Get from Photoshop**: Chụp ảnh từ Photoshop đưa vào ComfyUI. Rất hữu ích khi bạn đang vẽ phác thảo và muốn AI hoàn thiện.

---

## 4. Lưu ý quan trọng
- Bạn phải mở Photoshop trước khi chạy script bridge.
- Đảm bảo Photoshop của bạn đã bật tùy chọn "Remote Connection" (nếu cần, tùy phiên bản).
- Nếu Photoshop yêu cầu quyền, hãy xác nhận để Python có thể điều khiển script.

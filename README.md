# Voice-Agent

Giai đoạn hiện tại chỉ tập trung vào **Speech-to-Text tiếng Việt chạy local**.

```text
Microphone -> Audio -> sherpa-onnx -> Vietnamese Zipformer -> Text -> Terminal
```

Chưa có LLM, TTS, Agent, memory, tools hay cloud API.

## STT engine

- Engine: `sherpa-onnx`
- Model: `sherpa-onnx-zipformer-vi-int8-2025-04-20`
- Ngôn ngữ: Vietnamese
- Device: CPU
- Sample rate: 16 kHz
- Audio: mono / float32
- API key: không cần
- Internet khi nhận giọng nói: không cần sau khi model đã được tải

Model được tải từ release chính thức của `k2-fsa/sherpa-onnx`.

## Cài đặt

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Tải model

Chạy một lần:

```powershell
python setup_model.py
```

Script sẽ tải và giải nén model tiếng Việt vào:

```text
models/
└── sherpa-onnx-zipformer-vi-int8-2025-04-20/
```

Thư mục `models/` không được commit lên Git.

## Chạy Speech-to-Text

```powershell
python main.py
```

Luồng sử dụng:

1. Chương trình hiển thị microphone mặc định.
2. Nhấn Enter để bắt đầu.
3. Nói vào microphone.
4. Nhấn Enter để kết thúc.
5. Audio được đưa trực tiếp vào Sherpa-ONNX.
6. Văn bản tiếng Việt được in ra terminal.

Ví dụ:

```text
Voice-Agent: Vietnamese Speech-to-Text
Engine: sherpa-onnx
Model: sherpa-onnx-zipformer-vi-int8-2025-04-20
Microphone: Microphone Array (...)
Loading model...
Ready. CPU threads: 4. Press Ctrl+C to exit.

Press Enter to start recording...
Recording... speak now, then press Enter to stop.
Transcribing...
You: xin chào đây là chương trình nhận diện giọng nói
```

## Khác với phiên bản Whisper trước

Phiên bản này không:

- dùng `faster-whisper`;
- tạo file WAV tạm;
- tải model Whisper;
- gọi API cloud.

Audio `float32` từ microphone được đưa thẳng vào `sherpa_onnx.OfflineRecognizer`.

Nếu tín hiệu microphone quá nhỏ, chương trình sẽ cảnh báo để tránh nhầm lỗi audio với lỗi model.

## Bước tiếp theo

Chưa thêm VAD ngay.

Sau khi xác nhận model này nhận tiếng Việt tốt và ổn định trên laptop, bước tiếp theo mới là:

```text
Microphone liên tục
        ↓
Silero VAD
        ↓
speech start / speech end
        ↓
Sherpa-ONNX
        ↓
Text
```

Sau đó mới tiến tới streaming STT, LLM và TTS.

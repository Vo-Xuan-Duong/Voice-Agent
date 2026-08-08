# Voice-Agent

Bắt đầu lại từ đầu với một mục tiêu duy nhất: **nhận giọng nói từ microphone và chuyển thành văn bản ngay trên terminal**.

## Luồng hiện tại

```text
Microphone -> Audio -> faster-whisper -> Text -> Terminal
```

Phiên bản này chưa có LLM, TTS, Agent, memory, tools hay cloud API.

## Yêu cầu

- Python 3.11+
- Microphone
- Windows, Linux hoặc macOS

## Cài đặt

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Chạy

```powershell
python main.py
```

Sau đó:

1. Nhấn Enter để bắt đầu ghi âm.
2. Nói vào microphone.
3. Nhấn Enter để kết thúc.
4. Chương trình dùng `faster-whisper` chạy local để chuyển âm thanh thành văn bản.
5. Văn bản được in ra terminal.

Ví dụ:

```text
Voice-Agent: Speech-to-Text
Loading local Whisper model...
Ready. Press Ctrl+C to exit.

Press Enter to start recording...
Recording... speak now, then press Enter to stop.
Transcribing...
You: xin chào đây là chương trình nhận diện giọng nói
```

## Cấu hình ban đầu

`main.py` đang dùng:

- Sample rate: `16000 Hz`
- Audio: mono
- Whisper model: `small`
- Device: CPU
- Compute type: `int8`
- Language: Vietnamese (`vi`)

Lần chạy đầu tiên có thể cần tải model Whisper về máy.

## Bước tiếp theo

Chỉ sau khi bước Speech-to-Text này chạy ổn mới thêm VAD để tự phát hiện lúc bắt đầu/kết thúc nói. Sau đó mới phát triển streaming STT, LLM và TTS.

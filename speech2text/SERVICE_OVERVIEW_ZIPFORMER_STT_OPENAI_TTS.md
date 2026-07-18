# Tổng Quan Service: Zipformer STT + OpenAI TTS

## Mục tiêu

Service này phục vụ demo giọng nói tiếng Việt theo luồng:

```text
Giọng nói người dùng -> STT local bằng Zipformer -> Văn bản
Văn bản -> TTS bằng OpenAI -> Audio phản hồi
```

Định hướng chính là dùng **Zipformer local cho Speech-to-Text (STT)** và
**OpenAI cloud cho Text-to-Speech (TTS)**. Cách này giữ phần nhận dạng giọng nói
chạy trên máy, còn phần tạo giọng nói tận dụng model cloud để giảm tải phần cứng
local.

## Chức năng tổng quát

- Thu âm từ microphone trên trình duyệt.
- Chọn đúng thiết bị microphone, có meter kiểm tra tín hiệu đầu vào.
- Gửi audio realtime dạng PCM 16 kHz tới Zipformer service local.
- Hiển thị transcript realtime/final từ Zipformer.
- Lưu bản ghi trên giao diện để nghe lại hoặc tải xuống.
- Nhập text hoặc dùng transcript làm đầu vào TTS.
- Gọi OpenAI TTS từ backend, không để lộ API key ra frontend.
- Phát audio TTS trên trình duyệt và cho phép tải file audio.
- Hiển thị trạng thái service, lỗi cấu hình, lỗi API và thời gian xử lý.

## Mô hình sử dụng

### STT local

```text
sherpa-onnx-zipformer-vi-30M-int8-2026-02-09
```

- Loại: Zipformer ASR tiếng Việt, chạy local bằng `sherpa-onnx`.
- Runtime: Python/FastAPI service, ONNX Runtime, CPU.
- Input realtime: PCM 16-bit, mono, 16 kHz từ browser qua WebSocket.
- Không cần FFmpeg cho realtime.
- Không cần internet sau khi model đã được tải xong.

### TTS cloud

```text
gpt-4o-mini-tts
```

- Loại: OpenAI Text-to-Speech.
- Runtime: gọi API từ Node/Express backend.
- Input: text tiếng Việt.
- Output: audio, thường dùng `mp3` hoặc `wav`.
- API key nằm trong `.env` backend.
- Cần internet và có chi phí API.

## Tài nguyên phần cứng ước lượng

### Zipformer STT

Ước lượng với model INT8 30M:

```text
RAM khi load service: khoảng 300 MB - 800 MB
RAM khi đang nhận dạng: khoảng 500 MB - 1.5 GB
CPU: dùng CPU rõ rệt khi decode audio
GPU: không bắt buộc
Ổ đĩa model/cache: nên chừa ít nhất vài GB
```

Nếu chạy realtime liên tục, CPU sẽ là tài nguyên quan trọng hơn GPU. Audio càng
dài hoặc decode càng thường xuyên thì CPU usage càng tăng.

### OpenAI TTS

OpenAI TTS chạy trên cloud nên máy local chỉ chịu tải nhẹ:

```text
RAM local: không đáng kể, chủ yếu giữ request/response audio
CPU local: thấp
GPU: không cần
Internet: bắt buộc
Ổ đĩa: chỉ cần chỗ lưu file audio output nếu có
```

### Tổng khi chạy demo

Ước lượng khi mở Node backend, Zipformer service và một tab browser:

```text
Node/Express backend: khoảng 100 MB - 300 MB RAM
Zipformer service: khoảng 500 MB - 1.5 GB RAM
Browser tab: khoảng 300 MB - 1 GB RAM
Tổng demo: khoảng 1.5 GB - 3 GB RAM
```

## Cấu hình phần cứng khuyến nghị

### Tối thiểu

```text
CPU: 4 nhân
RAM: 8 GB
GPU: không cần
Ổ đĩa trống: 5 GB trở lên
Internet: cần cho OpenAI TTS
```

### Khuyến nghị

```text
CPU: Intel Core i5/Ryzen 5 đời tương đối mới hoặc tốt hơn
RAM: 16 GB
GPU: không cần
Ổ đĩa trống: 10 GB trở lên
Ổ C: nên còn ít nhất 5 GB trống
Ổ D/cache project: nên còn nhiều dung lượng cho model, pip cache, Hugging Face cache
```

## Lưu ý vận hành

- Nếu port Zipformer hoặc TTS bị chiếm, cần dừng process cũ trước khi chạy lại.
- Nếu thấy lỗi `No space left on device`, nguyên nhân thường là cache/temp vẫn
  trỏ về ổ C hoặc ổ C quá đầy.
- Nên đặt cache lớn như Hugging Face, pip temp và output audio sang ổ D.
- OpenAI TTS nhẹ máy nhưng phụ thuộc mạng, API key và quota.
- Zipformer STT riêng tư hơn vì audio nhận dạng không cần gửi lên cloud.

## Kết luận

Cấu hình **Zipformer STT local + OpenAI TTS cloud** là phương án cân bằng cho
demo:

- STT không tốn phí API và chạy local.
- TTS tự nhiên hơn, nhẹ máy hơn vì chạy cloud.
- Không cần GPU.
- RAM 16 GB là mức nên có để chạy ổn định cùng browser và các service khác.

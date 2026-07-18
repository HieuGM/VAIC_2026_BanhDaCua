from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
MODEL_NAME = "sherpa-onnx-zipformer-vi-30M-int8-2026-02-09"
DEFAULT_MODEL_DIR = BASE_DIR / "models" / MODEL_NAME
MODEL_DIR = Path(os.getenv("ZIPFORMER_MODEL_DIR", str(DEFAULT_MODEL_DIR))).resolve()

MAX_AUDIO_SIZE_BYTES = int(
    os.getenv("ZIPFORMER_MAX_AUDIO_BYTES", str(25 * 1024 * 1024))
)
NUM_THREADS = max(1, int(os.getenv("ZIPFORMER_NUM_THREADS", "2")))
STREAM_SAMPLE_RATE = 16000
STREAM_PARTIAL_INTERVAL_SECONDS = float(
    os.getenv("ZIPFORMER_STREAM_PARTIAL_INTERVAL_SECONDS", "1.5")
)
STREAM_MIN_AUDIO_SECONDS = float(os.getenv("ZIPFORMER_STREAM_MIN_AUDIO_SECONDS", "1.0"))

ENCODER_PATH = MODEL_DIR / "encoder.int8.onnx"
DECODER_PATH = MODEL_DIR / "decoder.onnx"
JOINER_PATH = MODEL_DIR / "joiner.int8.onnx"
TOKENS_PATH = MODEL_DIR / "tokens.txt"


def require_file(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"Không tìm thấy file model: {path}")


def resolve_ffmpeg_path() -> str:
    configured_path = os.getenv("ZIPFORMER_FFMPEG_PATH")

    if configured_path:
      configured = Path(configured_path).resolve()
      if configured.is_file():
          return str(configured)
      raise RuntimeError(f"ZIPFORMER_FFMPEG_PATH không hợp lệ: {configured}")

    tools_dir = PROJECT_DIR / "tools" / "ffmpeg"
    executable_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"

    if tools_dir.is_dir():
        matches = sorted(tools_dir.rglob(executable_name))
        if matches:
            return str(matches[0])

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    raise RuntimeError(
        "Không tìm thấy FFmpeg. Hãy chạy npm run zipformer:setup trước."
    )


for required_path in (ENCODER_PATH, DECODER_PATH, JOINER_PATH, TOKENS_PATH):
    require_file(required_path)

FFMPEG_PATH = resolve_ffmpeg_path()

print(f"Đang tải Zipformer từ: {MODEL_DIR}")
model_load_started = time.perf_counter()

recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=str(ENCODER_PATH),
    decoder=str(DECODER_PATH),
    joiner=str(JOINER_PATH),
    tokens=str(TOKENS_PATH),
    num_threads=NUM_THREADS,
    sample_rate=16000,
    feature_dim=80,
    decoding_method="greedy_search",
    provider="cpu",
    debug=False,
)

MODEL_LOAD_MS = round((time.perf_counter() - model_load_started) * 1000, 2)
print(f"Đã tải Zipformer trong {MODEL_LOAD_MS} ms")

recognizer_lock = threading.Lock()

app = FastAPI(
    title="Vietnamese Zipformer STT Service",
    version="1.0.0",
)


def convert_to_pcm_wav(input_path: Path, output_path: Path) -> None:
    command = [
        FFMPEG_PATH,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    if completed.returncode != 0:
        detail = completed.stderr.strip() or "FFmpeg không thể chuyển đổi audio"
        raise RuntimeError(detail)


def read_pcm16_wav(wav_path: Path) -> tuple[int, np.ndarray]:
    with wave.open(str(wav_path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        pcm_bytes = wav_file.readframes(frame_count)

    if channels != 1:
        raise RuntimeError(f"Audio sau chuyển đổi không phải mono: {channels} kênh")

    if sample_width != 2:
        raise RuntimeError(
            f"Audio sau chuyển đổi không phải PCM 16-bit: {sample_width * 8}-bit"
        )

    samples = np.frombuffer(pcm_bytes, dtype=np.int16)
    samples = samples.astype(np.float32) / 32768.0

    if samples.size == 0:
        raise RuntimeError("Audio không chứa mẫu âm thanh")

    return sample_rate, samples


def decode_wav(wav_path: Path) -> dict[str, object]:
    sample_rate, samples = read_pcm16_wav(wav_path)
    return decode_samples(sample_rate, samples)


def decode_samples(sample_rate: int, samples: np.ndarray) -> dict[str, object]:
    if samples.size == 0:
        raise RuntimeError("Audio không chứa mẫu âm thanh")

    audio_duration_seconds = samples.size / sample_rate

    inference_started = time.perf_counter()

    with recognizer_lock:
        stream = recognizer.create_stream()
        stream.accept_waveform(sample_rate, samples)
        recognizer.decode_stream(stream)
        text = stream.result.text.strip()

    inference_seconds = time.perf_counter() - inference_started
    real_time_factor = (
        inference_seconds / audio_duration_seconds
        if audio_duration_seconds > 0
        else None
    )

    return {
        "text": text,
        "audioDurationSeconds": round(audio_duration_seconds, 3),
        "inferenceMs": round(inference_seconds * 1000, 2),
        "realTimeFactor": (
            round(real_time_factor, 4) if real_time_factor is not None else None
        ),
    }


def pcm16_bytes_to_float32(audio_bytes: bytes) -> np.ndarray:
    if len(audio_bytes) < 2:
        return np.empty(0, dtype=np.float32)

    usable_bytes = audio_bytes[: len(audio_bytes) - (len(audio_bytes) % 2)]
    samples = np.frombuffer(usable_bytes, dtype="<i2")
    return samples.astype(np.float32) / 32768.0


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "model": MODEL_DIR.name,
        "provider": "cpu",
        "numThreads": NUM_THREADS,
        "modelLoadMs": MODEL_LOAD_MS,
        "ffmpeg": FFMPEG_PATH,
        "streaming": {
            "mode": "simulated",
            "sampleRate": STREAM_SAMPLE_RATE,
            "partialIntervalSeconds": STREAM_PARTIAL_INTERVAL_SECONDS,
        },
    }


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)) -> dict[str, object]:
    request_started = time.perf_counter()
    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="File audio rỗng")

    if len(audio_bytes) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File audio vượt quá {MAX_AUDIO_SIZE_BYTES} byte",
        )

    original_suffix = Path(audio.filename or "recording.webm").suffix
    suffix = original_suffix if original_suffix else ".webm"

    try:
        with tempfile.TemporaryDirectory(prefix="zipformer-stt-") as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / f"input{suffix}"
            wav_path = temp_path / "audio.wav"

            input_path.write_bytes(audio_bytes)

            await run_in_threadpool(convert_to_pcm_wav, input_path, wav_path)
            result = await run_in_threadpool(decode_wav, wav_path)

        total_ms = round((time.perf_counter() - request_started) * 1000, 2)

        return {
            **result,
            "model": MODEL_DIR.name,
            "totalMs": total_ms,
            "audioSizeBytes": len(audio_bytes),
        }
    except subprocess.TimeoutExpired as error:
        raise HTTPException(
            status_code=408,
            detail="FFmpeg xử lý audio quá thời gian cho phép",
        ) from error
    except RuntimeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Zipformer service gặp lỗi không xác định",
        ) from error


@app.websocket("/ws/transcribe")
async def transcribe_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(
        {
            "type": "ready",
            "sampleRate": STREAM_SAMPLE_RATE,
            "mode": "simulated",
        }
    )

    chunks: list[np.ndarray] = []
    sample_count = 0
    last_decoded_sample_count = 0
    stream_started = time.perf_counter()
    min_samples = int(STREAM_SAMPLE_RATE * STREAM_MIN_AUDIO_SECONDS)
    partial_interval_samples = int(
        STREAM_SAMPLE_RATE * STREAM_PARTIAL_INTERVAL_SECONDS
    )

    async def decode_current_audio(message_type: str) -> None:
        nonlocal last_decoded_sample_count

        if sample_count < min_samples:
            return

        samples = np.concatenate(chunks).astype(np.float32, copy=False)
        result = await run_in_threadpool(
            decode_samples,
            STREAM_SAMPLE_RATE,
            samples.copy(),
        )
        last_decoded_sample_count = sample_count
        await websocket.send_json(
            {
                "type": message_type,
                **result,
                "totalMs": round((time.perf_counter() - stream_started) * 1000, 2),
                "model": MODEL_DIR.name,
                "audioSizeBytes": int(sample_count * 2),
            }
        )

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

            audio_bytes = message.get("bytes")
            text_message = message.get("text")

            if audio_bytes is not None:
                samples = pcm16_bytes_to_float32(audio_bytes)

                if samples.size == 0:
                    continue

                chunks.append(samples)
                sample_count += int(samples.size)

                if (
                    sample_count >= min_samples
                    and sample_count - last_decoded_sample_count
                    >= partial_interval_samples
                ):
                    await decode_current_audio("partial")
                continue

            if text_message is None:
                continue

            try:
                command = json.loads(text_message)
            except json.JSONDecodeError:
                continue

            if command.get("type") == "stop":
                await decode_current_audio("final")
                await websocket.close()
                break
    except WebSocketDisconnect:
        pass
    except RuntimeError as error:
        await websocket.send_json({"type": "error", "message": str(error)})
    except Exception:
        await websocket.send_json(
            {"type": "error", "message": "Zipformer realtime gặp lỗi không xác định"}
        )

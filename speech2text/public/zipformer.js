const startButton = document.querySelector("#startButton");
const stopButton = document.querySelector("#stopButton");
const statusText = document.querySelector("#statusText");
const statusDot = document.querySelector("#statusDot");
const timerElement = document.querySelector("#timer");
const micSelect = document.querySelector("#micSelect");
const micHintElement = document.querySelector("#micHint");
const inputLevelBar = document.querySelector("#inputLevelBar");
const inputLevelText = document.querySelector("#inputLevelText");
const transcriptElement = document.querySelector("#transcript");
const recordingInfoElement = document.querySelector("#recordingInfo");
const recordingAudioElement = document.querySelector("#recordingAudio");
const downloadRecordingLink = document.querySelector("#downloadRecordingLink");
const audioDurationElement = document.querySelector("#audioDuration");
const inferenceTimeElement = document.querySelector("#inferenceTime");
const totalTimeElement = document.querySelector("#totalTime");
const realTimeFactorElement = document.querySelector("#realTimeFactor");
const errorBox = document.querySelector("#errorBox");

let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let selectedMimeType = "";
let timerInterval = null;
let inputLevelFrame = null;
let audioContext = null;
let analyserNode = null;
let analyserData = null;
let inputLevelSource = null;
let realtimeSocket = null;
let realtimeAudioContext = null;
let realtimeSource = null;
let realtimeProcessor = null;
let startedAt = 0;
let recordingObjectUrl = "";
let selectedMicDeviceId = "";
let processing = false;
let serviceReady = false;

startButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopAndTranscribe);
micSelect.addEventListener("change", () => {
  selectedMicDeviceId = micSelect.value;
});
window.addEventListener("beforeunload", cleanupMedia);

refreshMicrophoneList();
checkZipformerService();

async function checkZipformerService() {
  resetError();
  setStatus("Đang kiểm tra Zipformer service...");
  startButton.disabled = true;
  serviceReady = false;

  try {
    const response = await fetch("/api/zipformer/health");
    const data = await readJsonResponse(response);

    if (!response.ok) {
      throw new Error(data.error || "Zipformer service chưa sẵn sàng");
    }

    serviceReady = true;
    setStatus(`Sẵn sàng - ${data.model || "Zipformer local"}`);
    statusDot.classList.remove("active");
    statusDot.classList.add("success");
    startButton.disabled = false;
  } catch (error) {
    setStatus("Zipformer service chưa chạy");
    statusDot.classList.remove("active", "success");
    showError(
      `${error.message}. Hãy chạy npm run zipformer:service rồi tải lại trang.`,
    );
  }
}

async function startRecording() {
  if (processing || !serviceReady) {
    return;
  }

  resetError();
  resetMetrics();
  clearRecordingPreview();
  recordedChunks = [];
  transcriptElement.textContent = "Đang nghe realtime...";
  transcriptElement.classList.add("muted");

  startButton.disabled = true;

  try {
    mediaStream = await openSelectedMicrophone();
    micSelect.disabled = true;
    await refreshMicrophoneList(mediaStream);
    startInputLevelMeter(mediaStream);

    setStatus("Đang mở realtime Zipformer...");
    await startZipformerRealtime(mediaStream);

    selectedMimeType = chooseRecorderMimeType();
    mediaRecorder = selectedMimeType
      ? new MediaRecorder(mediaStream, { mimeType: selectedMimeType })
      : new MediaRecorder(mediaStream);

    mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    });

    mediaRecorder.addEventListener("error", (event) => {
      showError(event.error?.message || "MediaRecorder gặp lỗi");
    });

    mediaRecorder.start(250);
    startedAt = Date.now();
    startTimer();

    setStatus("Đang ghi âm - hãy bắt đầu nói");
    statusDot.classList.remove("success");
    statusDot.classList.add("active");
    stopButton.disabled = false;
  } catch (error) {
    console.error(error);
    showError(error.message || "Không thể mở microphone");
    setStatus("Không thể bắt đầu ghi âm");
    cleanupMedia();
    startButton.disabled = false;
  }
}

async function stopAndTranscribe() {
  if (processing || !mediaRecorder) {
    return;
  }

  processing = true;
  stopButton.disabled = true;
  stopTimer();
  setStatus("Đang hoàn tất bản ghi...");

  try {
    if (mediaRecorder.state === "inactive") {
      throw new Error("MediaRecorder chưa hoạt động");
    }

    const recorderStopped = new Promise((resolve) => {
      mediaRecorder.addEventListener("stop", resolve, { once: true });
    });

    mediaRecorder.stop();
    await recorderStopped;

    const actualMimeType =
      mediaRecorder.mimeType || selectedMimeType || "audio/webm";
    const audioBlob = new Blob(recordedChunks, { type: actualMimeType });

    if (audioBlob.size === 0) {
      throw new Error("Bản ghi rỗng. Hãy thử lại.");
    }

    const durationSeconds = Math.max(
      0,
      Math.floor((Date.now() - startedAt) / 1000),
    );
    const extension = actualMimeType.includes("mp4") ? "mp4" : "webm";
    const filename = createRecordingFilename(extension);
    setRecordingPreview(audioBlob, actualMimeType, filename, durationSeconds);
    cleanupMedia();

    setStatus("Zipformer đang nhận dạng...");
    transcriptElement.textContent = "Đang xử lý local trên CPU...";
    transcriptElement.classList.add("muted");

    const formData = new FormData();
    formData.append("audio", audioBlob, filename);

    const response = await fetch("/api/transcribe/zipformer", {
      method: "POST",
      body: formData,
    });

    const data = await readJsonResponse(response);

    if (!response.ok) {
      const detail =
        typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail || data);
      throw new Error(detail || data.error || "Zipformer xử lý thất bại");
    }

    transcriptElement.textContent =
      data.text || "Model không nhận dạng được nội dung.";
    transcriptElement.classList.remove("muted");

    audioDurationElement.textContent = formatSeconds(
      data.audioDurationSeconds,
    );
    inferenceTimeElement.textContent = formatMilliseconds(data.inferenceMs);
    totalTimeElement.textContent = formatMilliseconds(data.totalMs);
    realTimeFactorElement.textContent =
      typeof data.realTimeFactor === "number"
        ? data.realTimeFactor.toFixed(4)
        : "—";

    setStatus("Đã nhận dạng xong");
    statusDot.classList.remove("active");
    statusDot.classList.add("success");
  } catch (error) {
    console.error(error);
    showError(error.message || "Không thể nhận dạng audio");
    setStatus("Nhận dạng thất bại");
    statusDot.classList.remove("active");
  } finally {
    cleanupMedia();
    processing = false;
    startButton.disabled = !serviceReady;
    stopButton.disabled = true;
  }
}

async function openSelectedMicrophone() {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error("Trình duyệt không hỗ trợ truy cập microphone");
  }

  return navigator.mediaDevices.getUserMedia({
    audio: buildAudioConstraints(selectedMicDeviceId),
  });
}

function buildAudioConstraints(deviceId) {
  const constraints = {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    channelCount: { ideal: 1 },
  };

  if (deviceId) {
    constraints.deviceId = { exact: deviceId };
  }

  return constraints;
}

async function refreshMicrophoneList(activeStream = null) {
  if (!navigator.mediaDevices?.enumerateDevices) {
    micSelect.innerHTML =
      '<option value="">Trình duyệt không hỗ trợ chọn microphone</option>';
    micSelect.disabled = true;
    return;
  }

  try {
    const activeDeviceId =
      activeStream?.getAudioTracks()[0]?.getSettings().deviceId || "";
    const preferredDeviceId =
      activeDeviceId || selectedMicDeviceId || micSelect.value || "";
    const devices = await navigator.mediaDevices.enumerateDevices();
    const microphones = devices.filter((device) => device.kind === "audioinput");

    micSelect.innerHTML = "";

    if (microphones.length === 0) {
      micSelect.append(new Option("Không tìm thấy microphone", ""));
      micSelect.disabled = true;
      micHintElement.textContent =
        "Hãy kiểm tra quyền microphone trong trình duyệt và Windows.";
      return;
    }

    microphones.forEach((device, index) => {
      const label = device.label || `Microphone ${index + 1}`;
      micSelect.append(new Option(label, device.deviceId));
    });

    const nextDeviceId =
      microphones.find((device) => device.deviceId === preferredDeviceId)
        ?.deviceId || microphones[0].deviceId;

    micSelect.value = nextDeviceId;
    selectedMicDeviceId = nextDeviceId;
    micSelect.disabled = Boolean(activeStream);
    micHintElement.textContent =
      "Nếu dùng tai nghe Bluetooth, hãy chọn thiết bị có chữ Bluetooth, Headset hoặc Hands-Free rồi ghi lại.";
  } catch (error) {
    console.error("Không liệt kê được microphone:", error);
    micHintElement.textContent =
      "Không đọc được danh sách microphone. Hãy kiểm tra quyền microphone của trình duyệt.";
  }
}

function startInputLevelMeter(stream) {
  stopInputLevelMeter();

  const AudioContextClass = window.AudioContext || window.webkitAudioContext;

  if (!AudioContextClass) {
    setInputLevel(0, "Không hỗ trợ");
    return;
  }

  audioContext = new AudioContextClass();
  inputLevelSource = audioContext.createMediaStreamSource(stream);
  analyserNode = audioContext.createAnalyser();
  analyserNode.fftSize = 2048;
  analyserData = new Uint8Array(analyserNode.fftSize);
  inputLevelSource.connect(analyserNode);

  const tick = () => {
    analyserNode.getByteTimeDomainData(analyserData);

    let sumSquares = 0;
    for (const value of analyserData) {
      const normalized = (value - 128) / 128;
      sumSquares += normalized * normalized;
    }

    const rms = Math.sqrt(sumSquares / analyserData.length);
    const level = Math.min(100, Math.round(rms * 260));
    const label =
      level >= 12
        ? "Có tín hiệu"
        : level >= 4
          ? "Tín hiệu yếu"
          : "Không thấy tín hiệu";

    setInputLevel(level, label);
    inputLevelFrame = window.requestAnimationFrame(tick);
  };

  tick();
}

function stopInputLevelMeter() {
  if (inputLevelFrame) {
    window.cancelAnimationFrame(inputLevelFrame);
    inputLevelFrame = null;
  }

  if (audioContext) {
    audioContext.close().catch(() => {});
  }

  audioContext = null;
  analyserNode = null;
  analyserData = null;
  inputLevelSource = null;
  setInputLevel(0, "Đã dừng");
}

function setInputLevel(percent, label) {
  inputLevelBar.style.width = `${percent}%`;
  inputLevelText.textContent = label;
}

async function startZipformerRealtime(stream) {
  stopZipformerRealtime();

  const socket = new WebSocket(getZipformerWebSocketUrl());
  socket.binaryType = "arraybuffer";
  realtimeSocket = socket;

  socket.addEventListener("message", handleRealtimeMessage);
  socket.addEventListener("error", () => {
    showError("Không kết nối được WebSocket Zipformer realtime");
  });

  await waitForSocketOpen(socket, 5000);

  const AudioContextClass = window.AudioContext || window.webkitAudioContext;

  if (!AudioContextClass) {
    throw new Error("Trình duyệt không hỗ trợ AudioContext");
  }

  realtimeAudioContext = new AudioContextClass();
  realtimeSource = realtimeAudioContext.createMediaStreamSource(stream);
  realtimeProcessor = realtimeAudioContext.createScriptProcessor(4096, 1, 1);

  realtimeProcessor.onaudioprocess = (event) => {
    if (socket.readyState !== WebSocket.OPEN) {
      return;
    }

    const input = event.inputBuffer.getChannelData(0);
    const output = event.outputBuffer.getChannelData(0);
    output.fill(0);

    const downsampled = downsampleTo16k(input, realtimeAudioContext.sampleRate);
    const pcm16 = float32ToPcm16(downsampled);

    if (pcm16.byteLength > 0) {
      socket.send(pcm16);
    }
  };

  realtimeSource.connect(realtimeProcessor);
  realtimeProcessor.connect(realtimeAudioContext.destination);
}

function stopZipformerRealtime() {
  if (realtimeProcessor) {
    realtimeProcessor.disconnect();
    realtimeProcessor.onaudioprocess = null;
  }

  if (realtimeSource) {
    realtimeSource.disconnect();
  }

  if (realtimeAudioContext) {
    realtimeAudioContext.close().catch(() => {});
  }

  if (realtimeSocket) {
    try {
      if (realtimeSocket.readyState === WebSocket.OPEN) {
        realtimeSocket.send(JSON.stringify({ type: "stop" }));
      }
      realtimeSocket.close();
    } catch {
      // The socket may already be closing.
    }
  }

  realtimeProcessor = null;
  realtimeSource = null;
  realtimeAudioContext = null;
  realtimeSocket = null;
}

function handleRealtimeMessage(messageEvent) {
  let event;

  try {
    event = JSON.parse(messageEvent.data);
  } catch {
    return;
  }

  if (event.type === "ready") {
    return;
  }

  if (event.type === "partial" || event.type === "final") {
    if (event.text) {
      transcriptElement.textContent = event.text;
      transcriptElement.classList.remove("muted");
    }

    audioDurationElement.textContent = formatSeconds(
      event.audioDurationSeconds,
    );
    inferenceTimeElement.textContent = formatMilliseconds(event.inferenceMs);
    totalTimeElement.textContent = formatMilliseconds(event.totalMs);
    realTimeFactorElement.textContent =
      typeof event.realTimeFactor === "number"
        ? event.realTimeFactor.toFixed(4)
        : "—";
    return;
  }

  if (event.type === "error") {
    showError(event.message || "Zipformer realtime gặp lỗi");
  }
}

function getZipformerWebSocketUrl() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host =
    window.location.hostname === "localhost"
      ? "127.0.0.1"
      : window.location.hostname || "127.0.0.1";

  return `${protocol}//${host}:8001/ws/transcribe`;
}

function waitForSocketOpen(socket, timeoutMs) {
  if (socket.readyState === WebSocket.OPEN) {
    return Promise.resolve();
  }

  return new Promise((resolve, reject) => {
    const timeoutId = window.setTimeout(() => {
      reject(new Error("WebSocket Zipformer không mở trong thời gian cho phép"));
    }, timeoutMs);

    socket.addEventListener(
      "open",
      () => {
        window.clearTimeout(timeoutId);
        resolve();
      },
      { once: true },
    );

    socket.addEventListener(
      "error",
      () => {
        window.clearTimeout(timeoutId);
        reject(new Error("Không kết nối được WebSocket Zipformer"));
      },
      { once: true },
    );
  });
}

function downsampleTo16k(input, inputSampleRate) {
  const outputSampleRate = 16000;

  if (inputSampleRate === outputSampleRate) {
    return input;
  }

  const ratio = inputSampleRate / outputSampleRate;
  const outputLength = Math.max(1, Math.floor(input.length / ratio));
  const output = new Float32Array(outputLength);

  for (let index = 0; index < outputLength; index += 1) {
    const start = Math.floor(index * ratio);
    const end = Math.min(input.length, Math.floor((index + 1) * ratio));
    let sum = 0;
    let count = 0;

    for (let inputIndex = start; inputIndex < end; inputIndex += 1) {
      sum += input[inputIndex];
      count += 1;
    }

    output[index] = count > 0 ? sum / count : input[start] || 0;
  }

  return output;
}

function float32ToPcm16(samples) {
  const buffer = new ArrayBuffer(samples.length * 2);
  const view = new DataView(buffer);

  for (let index = 0; index < samples.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, samples[index]));
    view.setInt16(
      index * 2,
      sample < 0 ? sample * 0x8000 : sample * 0x7fff,
      true,
    );
  }

  return buffer;
}

function chooseRecorderMimeType() {
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4;codecs=mp4a.40.2",
    "audio/mp4",
  ];

  return candidates.find((type) => MediaRecorder.isTypeSupported(type)) || "";
}

function startTimer() {
  stopTimer();
  updateTimer();
  timerInterval = window.setInterval(updateTimer, 250);
}

function stopTimer() {
  if (timerInterval) {
    window.clearInterval(timerInterval);
    timerInterval = null;
  }
}

function updateTimer() {
  const elapsedSeconds = Math.floor((Date.now() - startedAt) / 1000);
  const minutes = String(Math.floor(elapsedSeconds / 60)).padStart(2, "0");
  const seconds = String(elapsedSeconds % 60).padStart(2, "0");
  timerElement.textContent = `${minutes}:${seconds}`;
}

function cleanupMedia() {
  stopTimer();
  stopInputLevelMeter();
  stopZipformerRealtime();

  for (const track of mediaStream?.getTracks() || []) {
    track.stop();
  }

  mediaStream = null;
  mediaRecorder = null;
  micSelect.disabled = false;
  refreshMicrophoneList().catch(() => {});
}

function resetMetrics() {
  audioDurationElement.textContent = "—";
  inferenceTimeElement.textContent = "—";
  totalTimeElement.textContent = "—";
  realTimeFactorElement.textContent = "—";
}

function setRecordingPreview(audioBlob, mimeType, filename, durationSeconds) {
  if (recordingObjectUrl) {
    URL.revokeObjectURL(recordingObjectUrl);
  }

  recordingObjectUrl = URL.createObjectURL(audioBlob);
  recordingAudioElement.src = recordingObjectUrl;
  recordingAudioElement.hidden = false;

  downloadRecordingLink.href = recordingObjectUrl;
  downloadRecordingLink.download = filename;
  downloadRecordingLink.hidden = false;

  const micName = micSelect.selectedOptions[0]?.textContent || "micro đang chọn";
  recordingInfoElement.textContent = `Đã ghi ${formatDuration(
    durationSeconds,
  )} - ${formatBytes(audioBlob.size)} - ${
    mimeType || "audio/webm"
  } - ${micName}`;
  recordingInfoElement.classList.remove("muted");
}

function clearRecordingPreview() {
  if (recordingObjectUrl) {
    URL.revokeObjectURL(recordingObjectUrl);
    recordingObjectUrl = "";
  }

  recordingAudioElement.removeAttribute("src");
  recordingAudioElement.hidden = true;
  downloadRecordingLink.removeAttribute("href");
  downloadRecordingLink.removeAttribute("download");
  downloadRecordingLink.hidden = true;
  recordingInfoElement.textContent = "Chưa có bản ghi.";
  recordingInfoElement.classList.add("muted");
}

function createRecordingFilename(extension) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  return `zipformer-recording-${timestamp}.${extension}`;
}

function formatDuration(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function formatBytes(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function formatSeconds(value) {
  return typeof value === "number" ? `${value.toFixed(2)} s` : "—";
}

function formatMilliseconds(value) {
  return typeof value === "number" ? `${value.toFixed(0)} ms` : "—";
}

function setStatus(text) {
  statusText.textContent = text;
}

function showError(message) {
  errorBox.hidden = false;
  errorBox.textContent = message;
}

function resetError() {
  errorBox.hidden = true;
  errorBox.textContent = "";
}

async function readJsonResponse(response) {
  const text = await response.text();

  if (!text) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch {
    return { detail: text };
  }
}

const startButton = document.querySelector("#startButton");
const stopButton = document.querySelector("#stopButton");
const statusText = document.querySelector("#statusText");
const statusDot = document.querySelector("#statusDot");
const timerElement = document.querySelector("#timer");
const micSelect = document.querySelector("#micSelect");
const micHintElement = document.querySelector("#micHint");
const inputLevelBar = document.querySelector("#inputLevelBar");
const inputLevelText = document.querySelector("#inputLevelText");
const liveTranscriptElement = document.querySelector("#liveTranscript");
const finalTranscriptElement = document.querySelector("#finalTranscript");
const recordingInfoElement = document.querySelector("#recordingInfo");
const recordingAudioElement = document.querySelector("#recordingAudio");
const downloadRecordingLink = document.querySelector("#downloadRecordingLink");
const errorBox = document.querySelector("#errorBox");

let peerConnection = null;
let dataChannel = null;
let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let selectedMimeType = "";
let timerInterval = null;
let realtimeCommitInterval = null;
let inputLevelFrame = null;
let audioContext = null;
let analyserNode = null;
let analyserData = null;
let inputLevelSource = null;
let startedAt = 0;
let liveTranscript = "";
let transcriptItemOrder = [];
let transcriptByItem = new Map();
let recordingObjectUrl = "";
let selectedMicDeviceId = "";
let stopping = false;

const REALTIME_COMMIT_INTERVAL_MS = 1500;

startButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
micSelect.addEventListener("change", () => {
  selectedMicDeviceId = micSelect.value;
});

refreshMicrophoneList();

async function startRecording() {
  resetError();
  stopping = false;
  liveTranscript = "";
  transcriptItemOrder = [];
  transcriptByItem = new Map();
  recordedChunks = [];
  clearRecordingPreview();

  setLiveTranscript("Đang kết nối...", true);
  setFinalTranscript("Chưa có kết quả cuối.", true);
  setStatus("Đang xin quyền microphone...");
  startButton.disabled = true;

  try {
    mediaStream = await openSelectedMicrophone();
    micSelect.disabled = true;
    await refreshMicrophoneList(mediaStream);
    startInputLevelMeter(mediaStream);

    setStatus("Đang tạo phiên realtime...");

    const tokenResponse = await fetch("/api/realtime-token");
    const tokenData = await readJsonResponse(tokenResponse);

    if (!tokenResponse.ok) {
      throw new Error(
        tokenData.detail || tokenData.error || "Không lấy được realtime token",
      );
    }

    const ephemeralKey = tokenData.value || tokenData.client_secret?.value;

    if (!ephemeralKey) {
      throw new Error("Backend không trả về ephemeral token hợp lệ");
    }

    peerConnection = new RTCPeerConnection();
    dataChannel = peerConnection.createDataChannel("oai-events");

    dataChannel.addEventListener("message", handleRealtimeEvent);
    dataChannel.addEventListener("close", () => {
      if (!stopping) {
        setStatus("Kết nối realtime đã đóng");
      }
    });

    for (const track of mediaStream.getTracks()) {
      peerConnection.addTrack(track, mediaStream);
    }

    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    const sdpResponse = await fetch(
      "https://api.openai.com/v1/realtime/calls",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${ephemeralKey}`,
          "Content-Type": "application/sdp",
        },
        body: offer.sdp,
      },
    );

    const answerSdp = await sdpResponse.text();

    if (!sdpResponse.ok) {
      throw new Error(`Không kết nối được Realtime API: ${answerSdp}`);
    }

    await peerConnection.setRemoteDescription({
      type: "answer",
      sdp: answerSdp,
    });

    await waitForDataChannelOpen(dataChannel, 10_000);

    selectedMimeType = chooseRecorderMimeType();
    mediaRecorder = selectedMimeType
      ? new MediaRecorder(mediaStream, { mimeType: selectedMimeType })
      : new MediaRecorder(mediaStream);

    mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data.size > 0) {
        recordedChunks.push(event.data);
      }
    });

    mediaRecorder.start(250);
    startRealtimeCommitLoop();

    startedAt = Date.now();
    startTimer();

    statusDot.classList.add("active");
    statusDot.classList.remove("success");
    setStatus("Đang nghe - hãy bắt đầu nói");
    setLiveTranscript("", false);

    stopButton.disabled = false;
  } catch (error) {
    console.error(error);
    showError(error.message || "Không thể bắt đầu ghi âm");
    setStatus("Khởi tạo thất bại");
    cleanupResources();
    startButton.disabled = false;
    stopButton.disabled = true;
  }
}

async function stopRecording() {
  if (stopping) {
    return;
  }

  stopping = true;
  stopButton.disabled = true;
  stopRealtimeCommitLoop();
  stopTimer();
  setStatus("Đang hoàn tất audio...");

  try {
    if (dataChannel?.readyState === "open") {
      dataChannel.send(
        JSON.stringify({
          type: "input_audio_buffer.commit",
        }),
      );
    }

    if (!mediaRecorder || mediaRecorder.state === "inactive") {
      throw new Error("MediaRecorder chưa hoạt động");
    }

    const recorderStopped = new Promise((resolve) => {
      mediaRecorder.addEventListener("stop", resolve, { once: true });
    });

    mediaRecorder.stop();
    await recorderStopped;

    for (const track of mediaStream?.getAudioTracks() || []) {
      track.enabled = false;
    }

    const actualMimeType =
      mediaRecorder.mimeType || selectedMimeType || "audio/webm";

    const audioBlob = new Blob(recordedChunks, {
      type: actualMimeType,
    });

    if (audioBlob.size === 0) {
      throw new Error("Bản ghi âm rỗng. Hãy thử ghi âm lại.");
    }

    const durationSeconds = Math.max(
      0,
      Math.floor((Date.now() - startedAt) / 1000),
    );
    const extension = actualMimeType.includes("mp4") ? "mp4" : "webm";
    const filename = createRecordingFilename(extension);
    setRecordingPreview(audioBlob, actualMimeType, filename, durationSeconds);

    setStatus("Đang tạo transcript cuối...");
    setFinalTranscript("Đang xử lý bằng gpt-4o-transcribe...", true);

    const formData = new FormData();
    formData.append("audio", audioBlob, filename);

    const response = await fetch("/api/transcribe", {
      method: "POST",
      body: formData,
    });

    const data = await readJsonResponse(response);

    if (!response.ok) {
      throw new Error(data.detail || data.error || "Transcription thất bại");
    }

    setFinalTranscript(data.text || "Không nhận dạng được nội dung.", false);
    setStatus("Đã xử lý xong");
    statusDot.classList.remove("active");
    statusDot.classList.add("success");

    await sleep(500);
  } catch (error) {
    console.error(error);
    showError(error.message || "Không thể xử lý bản ghi âm");
    setStatus("Xử lý thất bại");
    statusDot.classList.remove("active");
  } finally {
    cleanupResources();
    startButton.disabled = false;
    stopButton.disabled = true;
    stopping = false;
  }
}

function handleRealtimeEvent(messageEvent) {
  let event;

  try {
    event = JSON.parse(messageEvent.data);
  } catch {
    return;
  }

  if (
    event.type === "conversation.item.input_audio_transcription.delta" &&
    typeof event.delta === "string"
  ) {
    appendTranscriptDelta(event.item_id, event.delta);
    return;
  }

  if (
    event.type === "conversation.item.input_audio_transcription.completed" &&
    typeof event.transcript === "string"
  ) {
    setTranscriptItem(event.item_id, event.transcript);
    return;
  }

  if (event.type === "error") {
    const message =
      event.error?.message || JSON.stringify(event.error || event, null, 2);
    if (isExpectedEmptyCommitError(message)) {
      console.debug("Ignoring empty realtime commit:", message);
      return;
    }
    showError(`Realtime API: ${message}`);
  }
}

function isExpectedEmptyCommitError(message) {
  return /buffer (is )?empty|empty buffer|buffer too small/i.test(message);
}

function startRealtimeCommitLoop() {
  stopRealtimeCommitLoop();
  realtimeCommitInterval = window.setInterval(() => {
    sendRealtimeCommit();
  }, REALTIME_COMMIT_INTERVAL_MS);
}

function stopRealtimeCommitLoop() {
  if (realtimeCommitInterval) {
    window.clearInterval(realtimeCommitInterval);
    realtimeCommitInterval = null;
  }
}

function sendRealtimeCommit() {
  if (dataChannel?.readyState !== "open") {
    return;
  }

  dataChannel.send(
    JSON.stringify({
      type: "input_audio_buffer.commit",
    }),
  );
}

function appendTranscriptDelta(itemId, delta) {
  if (!itemId) {
    liveTranscript += delta;
    setLiveTranscript(liveTranscript, false);
    return;
  }

  ensureTranscriptItem(itemId);
  transcriptByItem.set(itemId, `${transcriptByItem.get(itemId) || ""}${delta}`);
  renderLiveTranscript();
}

function setTranscriptItem(itemId, transcript) {
  if (!itemId) {
    liveTranscript = transcript;
    setLiveTranscript(liveTranscript, false);
    return;
  }

  ensureTranscriptItem(itemId);
  transcriptByItem.set(itemId, transcript);
  renderLiveTranscript();
}

function ensureTranscriptItem(itemId) {
  if (!transcriptByItem.has(itemId)) {
    transcriptItemOrder.push(itemId);
    transcriptByItem.set(itemId, "");
  }
}

function renderLiveTranscript() {
  liveTranscript = transcriptItemOrder
    .map((itemId) => transcriptByItem.get(itemId) || "")
    .join(" ")
    .replace(/\s+/g, " ")
    .trim();
  setLiveTranscript(liveTranscript, false);
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

function chooseRecorderMimeType() {
  const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"];

  return candidates.find((type) => MediaRecorder.isTypeSupported(type)) || "";
}

function waitForDataChannelOpen(channel, timeoutMs) {
  if (channel.readyState === "open") {
    return Promise.resolve();
  }

  return new Promise((resolve, reject) => {
    const timeoutId = window.setTimeout(() => {
      reject(new Error("Data channel không mở trong thời gian cho phép"));
    }, timeoutMs);

    channel.addEventListener(
      "open",
      () => {
        window.clearTimeout(timeoutId);
        resolve();
      },
      { once: true },
    );
  });
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

function cleanupResources() {
  stopTimer();
  stopRealtimeCommitLoop();
  stopInputLevelMeter();

  if (dataChannel) {
    try {
      dataChannel.close();
    } catch {
      // Nothing else to clean up.
    }
  }

  if (peerConnection) {
    try {
      peerConnection.close();
    } catch {
      // Nothing else to clean up.
    }
  }

  for (const track of mediaStream?.getTracks() || []) {
    track.stop();
  }

  peerConnection = null;
  dataChannel = null;
  mediaStream = null;
  mediaRecorder = null;
  recordedChunks = [];
  micSelect.disabled = false;
  refreshMicrophoneList().catch(() => {});
}

function setStatus(text) {
  statusText.textContent = text;
}

function setLiveTranscript(text, muted) {
  liveTranscriptElement.textContent = text;
  liveTranscriptElement.classList.toggle("muted", muted);
}

function setFinalTranscript(text, muted) {
  finalTranscriptElement.textContent = text;
  finalTranscriptElement.classList.toggle("muted", muted);
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
  return `recording-${timestamp}.${extension}`;
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

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function resetError() {
  errorBox.textContent = "";
  errorBox.hidden = true;
}

function sleep(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

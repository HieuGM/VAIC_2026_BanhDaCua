import "dotenv/config";
import express from "express";
import multer from "multer";
import path from "node:path";
import { fileURLToPath } from "node:url";

const app = express();
const port = Number(process.env.PORT || 3001);
const apiKey = process.env.OPENAI_API_KEY;
const openaiEnabled = Boolean(apiKey);

if (!openaiEnabled) {
  console.warn(
    "OPENAI_API_KEY chưa được cấu hình. Trang Zipformer vẫn sử dụng được.",
  );
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 25 * 1024 * 1024,
  },
});

const finalPrompt =
  process.env.STT_DOMAIN_PROMPT ||
  "Cuộc hội thoại bằng tiếng Việt. Hãy chép lại chính xác và thêm dấu câu phù hợp.";
const zipformerServiceUrl =
  process.env.ZIPFORMER_SERVICE_URL || "http://127.0.0.1:8001";

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.get("/api/health", (_req, res) => {
  res.json({
    ok: true,
    openaiEnabled,
    zipformerServiceUrl,
  });
});

/**
 * Mint an ephemeral token for the browser to connect directly to the
 * OpenAI Realtime API over WebRTC.
 */
app.get("/api/realtime-token", async (_req, res) => {
  if (!openaiEnabled) {
    return res.status(503).json({
      error: "OpenAI chưa được cấu hình",
    });
  }

  const sessionConfig = {
    session: {
      type: "transcription",
      audio: {
        input: {
          transcription: {
            model: "gpt-realtime-whisper",
            language: "vi",
            delay: "low",
          },
          turn_detection: null,
          noise_reduction: {
            type: "far_field",
          },
        },
      },
    },
  };

  try {
    const response = await fetch(
      "https://api.openai.com/v1/realtime/client_secrets",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
          "OpenAI-Safety-Identifier": "local-stt-demo-user",
        },
        body: JSON.stringify(sessionConfig),
      },
    );

    const responseText = await response.text();

    if (!response.ok) {
      console.error("Không tạo được realtime token:", responseText);
      return res.status(response.status).json({
        error: "Không tạo được realtime token",
        detail: responseText,
      });
    }

    const data = JSON.parse(responseText);
    const clientSecret = data.client_secret || data;
    const value = clientSecret.value || data.value;

    if (!value) {
      console.error("Realtime token response did not include a token:", data);
      return res.status(502).json({
        error: "Phản hồi realtime token không chứa token hợp lệ",
      });
    }

    return res.json({
      value,
      expiresAt: clientSecret.expires_at || data.expires_at || null,
    });
  } catch (error) {
    console.error("Lỗi realtime token:", error);
    return res.status(500).json({
      error: "Lỗi server khi tạo realtime token",
    });
  }
});

/**
 * Receive the MediaRecorder file and call gpt-4o-transcribe for the final
 * transcript.
 */
app.post("/api/transcribe", upload.single("audio"), async (req, res) => {
  if (!openaiEnabled) {
    return res.status(503).json({
      error: "OpenAI chưa được cấu hình",
    });
  }

  if (!req.file) {
    return res.status(400).json({ error: "Không nhận được file audio" });
  }

  if (req.file.size === 0) {
    return res.status(400).json({ error: "File audio rỗng" });
  }

  const mimeType = req.file.mimetype || "audio/webm";
  const filename = req.file.originalname || "recording.webm";

  const formData = new FormData();
  formData.append(
    "file",
    new Blob([req.file.buffer], { type: mimeType }),
    filename,
  );
  formData.append("model", "gpt-4o-transcribe");
  formData.append("language", "vi");
  formData.append("response_format", "json");
  formData.append("prompt", finalPrompt);

  try {
    const response = await fetch(
      "https://api.openai.com/v1/audio/transcriptions",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
        body: formData,
      },
    );

    const responseText = await response.text();

    if (!response.ok) {
      console.error("Lỗi final transcription:", responseText);
      return res.status(response.status).json({
        error: "Không thể tạo transcript cuối",
        detail: responseText,
      });
    }

    const data = JSON.parse(responseText);

    return res.json({
      text: data.text || "",
      model: "gpt-4o-transcribe",
      audioSizeBytes: req.file.size,
    });
  } catch (error) {
    console.error("Lỗi gọi transcription API:", error);
    return res.status(500).json({
      error: "Lỗi server khi xử lý audio",
    });
  }
});

app.get("/api/zipformer/health", async (_req, res) => {
  try {
    const response = await fetch(`${zipformerServiceUrl}/health`);
    const responseText = await response.text();

    res.status(response.status);
    res.type("application/json");
    return res.send(responseText);
  } catch (error) {
    console.error("Không kết nối được Zipformer service:", error);
    return res.status(503).json({
      error: "Zipformer service chưa chạy",
      serviceUrl: zipformerServiceUrl,
    });
  }
});

app.post(
  "/api/transcribe/zipformer",
  upload.single("audio"),
  async (req, res) => {
    if (!req.file || req.file.size === 0) {
      return res.status(400).json({
        error: "Không nhận được file audio hợp lệ",
      });
    }

    const mimeType = req.file.mimetype || "audio/webm";
    const filename = req.file.originalname || "recording.webm";

    const formData = new FormData();
    formData.append(
      "audio",
      new Blob([req.file.buffer], { type: mimeType }),
      filename,
    );

    try {
      const response = await fetch(`${zipformerServiceUrl}/transcribe`, {
        method: "POST",
        body: formData,
      });

      const responseText = await response.text();

      if (!response.ok) {
        console.error("Zipformer transcription lỗi:", responseText);
        return res.status(response.status).json({
          error: "Zipformer không thể nhận dạng audio",
          detail: responseText,
        });
      }

      res.type("application/json");
      return res.send(responseText);
    } catch (error) {
      console.error("Không gọi được Zipformer service:", error);
      return res.status(503).json({
        error: "Không kết nối được Zipformer service",
        serviceUrl: zipformerServiceUrl,
      });
    }
  },
);

app.use((error, _req, res, _next) => {
  if (error instanceof multer.MulterError) {
    return res.status(400).json({
      error: "File audio không hợp lệ",
      detail: error.message,
    });
  }

  console.error("Unhandled error:", error);
  return res.status(500).json({ error: "Lỗi server không xác định" });
});

app.listen(port, () => {
  console.log(`Demo STT tiếng Việt đang chạy tại http://localhost:${port}`);
});

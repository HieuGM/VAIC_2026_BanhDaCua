# 01 — Project Overview

> Tổng quan dự án. Đọc sau `00-competition-rubric-and-principles` và `00-hospital-domain-rules`.
> Cập nhật: 2026-07-17 · Trạng thái: Draft v1.

---

## 1. Tên & Codename
- **Tên dự án (demo):** TimHN Assistant — Trợ lý CSKH AI cho Bệnh viện Tim Hà Nội
- **Codename repo:** `BanhDaCua`
- **Đề bài:** *"Intelligent AI Customer Care Assistant for Hanoi Heart Hospital"* (VAIC 2026)

## 2. Tầm nhìn (Vision)
Trợ lý AI hội thoại **đáng tin cậy**, trả lời chính xác các câu hỏi CSKH của bệnh nhân/người nhà BV Tim HN dựa trên **nguồn chính thức**, giảm tải tổng đài/reception, và **bắt đúng dấu hiệu cấp cứu** để chuyển khoa Cấp cứu kịp thời.

## 3. Vấn đề (Problem)
- **2.500–3.000 BN ngoại trú/ngày** → lượng câu hỏi lặp khổng lồ (đặt khám, quy trình, BHYT, giá, giờ, lịch BS).
- Trả lời thủ công qua tổng đài/website/mạng xã hội/reception → **chậm, không đồng nhất, quá tải nhân sự CSKH**.
- Thiếu kênh tự phục vụ 24/7 đáng tin cậy cho thông tin chính thức.

## 4. Giải pháp (Solution)
Chatbot web (text + ASR/TTS tiếng Việt tuỳ chọn) trên kiến trúc **RAG grounded**:
- Ingest KB chính thức (crawl website BV + SOP `QT.25.01`) → vector store.
- Truy vấn → retrieve + rerank → LLM grounded + **citation**.
- Lớp guardrail: intent router, **emergency triage (kill switch)**, refusal/out-of-scope gate.
- Tích hợp (mock + roadmap thật): redirect đặt khám (Web/Zalo Mini App/Tổng đài), tra lịch/giá khi có API.

## 5. Phạm vi (Scope)

### In-scope (48h)
- Chat UI web responsive (text); bonus ASR/TTS tiếng Việt.
- RAG pipeline đầy đủ (ingest → retrieve → answer + citation).
- Guardrail emergency + out-of-scope + no-medical-advice.
- KB từ website công khai BV + SOP.
- Mock integration đặt khám + roadmap pilot.
- Deploy Docker trên VPS, public URL.

### Out-of-scope (xem `00-competition-rubric-and-principles` §6)
- Chẩn đoán/kê đơn/giải thích KQ CLS.
- Tích hợp thật HIS/API BV.
- Fine-tune model riêng.
- Hồ sơ bệnh án / auth BN.
- Mobile native.

## 6. Tech Stack (đề xuất — chi tiết ở `05-system-architecture`)

| Lớp | Công nghệ | Lý do |
|---|---|---|
| Frontend | Next.js 15 (App Router) + TS + Tailwind + shadcn/ui | Chat UI nhanh, responsive, dễ deploy |
| Backend API | Python 3.12 + FastAPI | Hệ sinh thái AI/RAG, async, nhẹ |
| RAG | Qdrant (vector DB) + BGE-M3/multilingual-e5 (embed VI) + rerank | Tiếng Việt tốt, chạy Docker |
| LLM | Cloud API (demo): GPT-4o-mini / Gemini / Claude · **Đường on-prem**: Qwen2.5 / Vistral-7B (pilot) | Chất lượng 48h + privacy path |
| Guardrail | Rule-based + LLM classifier (emergency/intent) | Kill switch R2, gate R7 |
| ASR/TTS (bonus) | VinAI PhoWhisper (ASR) + Viettel/FPT TTS | Tiếng Việt |
| KB ingest | Firecrawl/httpx + langchain-style chunker | Crawl site BV + SOP md |
| Deploy | Docker Compose + Caddy (TLS) trên VPS | 1 lệnh, portable sang infra BV |
| Obs/Eval | Structlog + small eval set (golden Q&A) | Grounding correctness |

## 7. Team & Luồng song song (không phụ thuộc)

| Role (số lượng) | Sở hữu | Phụ thuộc? |
|---|---|---|
| Web FE (3) | Next.js chat UI, suggested Q, citation UI, ASR/TTS UI, redirect buttons | Chỉ phụ thuộc **API contract** (`07-api-design`), không phụ thuộc AI nội bộ |
| AI (2) | RAG pipeline (ingest/retrieve/answer), guardrail, eval, KB xây | Phụ thuộc **KB content** (BA) + API contract |
| BA (1) | KB content (FAQ/giá/quyền BHYT từ site), bộ test golden Q&A, kịch bản demo, slide/pitch | Độc lập |

> **Nguyên tắc chia việc:** chốt **API contract** (`07-api-design`) NGAY trong giờ đầu → 3 luồng (FE / AI / data+BA) chạy song song không chặn nhau. Contract ổn định, impl thay đổi.

## 8. Success Metrics (định lượng — dùng cho slide + rubric 03)
- **Grounding accuracy ≥ 90%** trên golden Q&A set (có trích nguồn đúng).
- **Emergency recall = 100%** (không bỏ sót case cấp cứu test).
- **T2 là < 4s** (end-to-end chat).
- **Demo 5'** chạy thật trên deployed URL, ≥3 luồng tình huống (FAQ / BHYT / cấp cứu).
- **Reduction proxy**: giả định giảm 40–60% cuộc gọi tổng đài lặp (business case).

## 9. Rủi ro chính
| Rủi ro | Tác động | Giảm thiểu |
|---|---|---|
| Hallucinate thông tin y tế | Mất ô 05, nguy hiểm | Grounding cứng + citation + refusal gate; eval set |
| Crawler site BV chặn/đổi cấu trúc | KB mỏng | Backup: SOP + nội dung BA biên soạn |
| 48h thiếu thời gian | Demo hời hợt | Lát cắt hẹp, ưu tiên 01+02+03+05 |
| API BV không có | Pilot yếu | Mock + roadmap thật rõ ràng |
| VPS giới hạn GPU (ASR/TTS/local LLM) | Bonus bị cắt | Cloud API cho LLM; ASR/TTS làm nếu đủ thời gian |

## 10. Liên quan
- [[00-competition-rubric-and-principles]] · [[00-hospital-domain-rules]]
- [[02-business-analysis]] · [[03-functional-requirements]] · [[04-non-functional-requirements]]

# 01 — Project Overview (PDR rút gọn)

> **Mục đích:** nguồn sự thật về *tầm nhìn, scope, tech stack, team, metrics*.
> **Đọc sau:** `00-competition-rubric-and-principles`, `00-hospital-domain-rules`.
> Cập nhật: 2026-07-17 · Phiên bản: **v1.1** · Trạng thái: **Review** (owner: Lead — verify theo `00-team-working-guide` §7).

---

## 1. Tên & Codename
- **Tên dự án (demo):** *TimHN Assistant* — Trợ lý CSKH AI cho Bệnh viện Tim Hà Nội (BVT).
- **Codename repo:** `BanhDaCua`.
- **Đề bài:** *"Intelligent AI Customer Care Assistant for Hanoi Heart Hospital"* — VAIC 2026.
- **Domain:** Y tế (nghiêm ngặt — **KHÔNG hallucinate**, an toàn dữ liệu).

## 2. Tầm nhìn (Vision)
Trợ lý AI hội thoại **đáng tin cậy**, trả lời chính xác câu hỏi CSKH của BN/người nhà BVT dựa trên **nguồn chính thức**, giảm tải tổng đài/reception 24/7, và **bắt đúng dấu hiệu cấp cứu** để chuyển khoa Cấp cứu kịp thời theo `HD.25.01`.

## 3. Vấn đề (Problem)
| # | Nỗi đau | Hệ quả |
|---|---|---|
| P1 | **2.500–3.000 BN ngoại trú/ngày** tạo lượng câu hỏi lặp khổng lồ | Tổng đài/reception quá tải |
| P2 | Trả lời thủ công nhiều kênh (DT/Web/Fanpage) | Chậm, mâu thuẫn thông tin |
| P3 | Thiếu kênh tự phục vụ 24/7 đáng tin cậy | BN nản, tăng chờ, giảm trải nghiệm |
| P4 | BN/kế bên không nhận diện dấu hiệu nguy hiểm | Chậm chuyển cấp cứu → rủi ro y tế |

## 4. Giải pháp (Solution)
Chatbot web (text + ASR/TTS tiếng Việt *bonus*) trên kiến trúc **RAG grounded**:
- **Ingest** KB chính thức (crawl website BV + SOP `QT.25.01` + forms) → vector store.
- **Retrieve + rerank** → LLM grounded + **citation** (R1, R9).
- **Guardrail** theo lớp: intent router → **emergency triage kill switch (R2)** → refusal/out-of-scope gate (R7) → no-medical-advice (R4).
- **Integration** (mock + roadmap thật): redirect đặt khám (Web/Zalo Mini App/Tổng đài — R6); tra lịch/giá khi có API.

## 5. Phạm vi (Scope)
**In-scope (48h):** chat UI responsive (text) + RAG pipeline đầy đủ + guardrail (emergency/OOS/no-advice) + KB (site công khai + SOP) + mock booking + roadmap pilot + deploy Docker trên VPS (public URL). Bonus: ASR/TTS tiếng Việt nếu đủ thời gian.
**Out-of-scope:** chẩn đoán/kê đơn/giải thích KQ CLS · tích hợp thật HIS/API · fine-tune model · hồ sơ bệnh án/auth BN · mobile native (xem `00-competition-rubric-and-principles` §6).

## 6. Tech Stack

> **Quyết ownership (3 lớp backend, swappable — ô 03):** **Web FE** = 2 web dev (Next.js) · **Data Backend** = Spring Boot (PostgreSQL, business data) · **AI/Backend** = 2 AI engineer (FastAPI + RAG + Qdrant). FastAPI gọi Spring Boot qua interface `HospitalDataProvider` → demo đọc PG, prod swap HIS thật (xem `06` §6).

### 6.1 Web (Frontend) — **đề xuất CHỐT** (chi tiết setup ở `08-development-guide`)

> ⚠️ **Trạng thái thực tế (2026-07-18):** FE triển khai thực tế = **React 18.2 + Create React App (react-scripts 5.0.1), JSX (KHÔNG TypeScript)**, dev port **3000**, thư mục `frontend/` (không phải `web/`). `src/services/chatAI.js` hiện là **PURE MOCK** (`sendMessageToAI(msg) => Promise<string>`, không network call); chat lưu **localStorage** (`bvthn_chat_conversations`, `bvthn_chat_active`) — KHÔNG persist backend, KHÔNG citations, KHÔNG status field, KHÔNG SSE/streaming. Bảng Next.js / SSE / TanStack / TypeScript dưới đây = **đề xuất CHƯA implement** (giữ làm roadmap). Khi wire chat thật → swap `chatAI.js` gọi `data-api POST /data/v1/chat` (xem **Recommendation A / ADR-008** trong `05`/`07`).

| Lớp | Công nghệ | Lý do (defensible — ô 06) |
|---|---|---|
| Framework | **Next.js 15 (App Router) + React 19 + TypeScript 5** | Team 3 web fluency React; Route Handler làm **BFF proxy SSE** → ẩn URL FastAPI + inject key + 1 domain (không CORS); standalone Docker build. |
| UI primitives | **shadcn/ui** (Radix-based) + lucide-react | Copy-paste ownership, a11y sẵn (focus trap/ARIA → ô 04), aesthetic y tế sạch, không fight theme. |
| Styling | **Tailwind CSS** | Nhanh, đồng nhất, bundle nhỏ, mobile-first. |
| Data/streaming | **TanStack Query v5** (REST) + **SSE** native/ReadableStream hook | Cache + devtools cho `/citations/{id}`, `/session`, `/channels`; streaming answer token-by-token. |
| Markdown | **react-markdown + remark-gfm + rehype-sanitize** | Render câu trả lời LLM; **sanitize HTML** = security (ô 05). |
| Form/validate | React Hook Form + Zod | Form đặt khám/feedback; schema dùng chung với contract `07`. |
| i18n | next-intl | Tiếng Việt mặc định, EN fallback (R10). |
| Animation | Framer Motion *(dùng ít)* | Banner cấp cứu pulse, transition tin nhắn (ô 04). |
| Audio (bonus) | MediaRecorder + Web Audio API + native Audio | Mic ASR + playback TTS (FR-9). |
| Test | Vitest + Testing Library (+ Playwright smoke) | Unit + e2e luồng demo. |
| Lint/format | **Biome** *(1 tool, nhanh)* hoặc ESLint+Prettier | Tối thiểu config trong 48h. |
| Pkg manager | **pnpm** | Nhanh, tiết kiệm disk, monorepo-friendly. |

> **Alternative (lean):** nếu team muốn tối giản → **Vite + React SPA** (static build qua Caddy, browser gọi trực tiếp FastAPI + CORS). Mất BFF, tự wire streaming/a11y. *Khuyên Next.js cho polish ô 04.*

### 6.2 Data Backend — **Spring Boot** (sở hữu: data dev)
| Lớp | Công nghệ |
|---|---|
| Framework | **Java 21 + Spring Boot 3** (Spring Web/Data JPA) |
| DB | **PostgreSQL** (schema `hospital`) |
| Migration | Flyway (`V1__init` + `V2__seed`) |
| API | REST `/data/v1/*` (departments, doctors, schedules, services, prices, bhyt, procedures, channels, appointment-slots mock) — khớp contract `07-api-design`; kb/articles·faqs·emergency thuộc scope AI team (xem `07` §B.3) |
| Seed | `data/seed/*.json|csv` loader (`SPRING_PROFILES=seed`) |
| Deploy | Docker (cùng compose với api/qdrant/caddy) |

> Là **nguồn dữ liệu cấu trúc chính thức** cho demo. Prod → adapter gọi HIS thật.

### 6.3 AI / RAG (sở hữu AI team — *FE/data không phụ thuộc nội bộ*)
| Lớp | Công nghệ |
|---|---|
| API | Python 3.12 + **FastAPI** (SSE `POST /api/v1/chat`) |
| RAG | Qdrant (vector DB) + BGE-M3 / multilingual-e5 (embed VI) + BGE-reranker-v2-m3 |
| LLM | Cloud API (demo): GPT-4o-mini / Gemini / Claude · on-prem path: Qwen2.5 / Vistral-7B (pilot) |
| Guardrail | Rule-based + LLM classifier (emergency/intent) |
| ASR/TTS (bonus) | VinAI PhoWhisper (ASR) + Viettel/FPT TTS |
| KB ingest | Firecrawl/httpx + chunker |
| Deploy | Docker Compose + Caddy (TLS) trên VPS |
| Obs/Eval | Structlog + golden Q&A eval set |

> **Điểm giao thoa duy nhất FE↔AI = API contract `07-api-design.md`** (chốt giờ đầu → 3 luồng song song).

## 7. Team & luồng song song (không phụ thuộc)

> ⚠️ **Lưu ý thực tế (2026-07-18):** thư mục code FE thực tế là **`frontend/`** (không phải `web/` như bảng gốc). Headcount đang mâu thuẫn: bảng đây ghi **Web FE (2)**, nhưng `00-team-working-guide` §3 ghi **Web FE (3)** — cần Lead chốt (xem `00` §3). Mới thêm vai **Data Backend (1)** sở hữu luôn cả **chat BFF + persistence ở data-api** (Recommendation A / ADR-008).

| Role (SL) | Sở hữu code | Phụ thuộc |
|---|---|---|
| **Web FE (2)** | `frontend/` (React 18 + CRA, thực tế) — đề xuất Next.js roadmap | chỉ contract `07` |
| **Data Backend (1)** | `data-api/` (Spring Boot + PG `hospital`) + **chat BFF + persistence** (ADR-008) | data seed (BA) |
| **AI (2)** | `chatbot-service/` (FastAPI), `ingest/`, `retrieval/`, `guardrail/`, `eval/`, Qdrant | data REST (Spring Boot) + KB (BA) + contract `07` |
| **BA (1)** | `data/seed`, `data/content`, golden Q&A, slide, kịch bản demo | độc lập |
| **Lead** (1 trong 6) | repo + Docker compose + deploy | — |

> **Nguyên tắc:** chốt contract `07` NGAY giờ đầu → 3 luồng chạy song song. *Contract ổn định, impl thay đổi.*

## 8. Success Metrics (định lượng — slide + ô 03)
| Metric | Mục tiêu demo | Mục tiêu pilot |
|---|---|---|
| Grounding accuracy (golden set, có nguồn đúng) | ≥ 90% | ≥ 95% |
| Emergency recall (không sót case cấp cứu) | **100%** | **100%** |
| Chat end-to-end P50 / P95 | ≤ 3s / ≤ 6s | ≤ 2s / ≤ 4s |
| Demo | 5' chạy thật trên URL, ≥ 3 luồng (FAQ/BHYT/cấp cứu) | — |
| Business proxy | giả định giảm 40–60% cuộc gọi lặp | đo thật |

## 9. Rủi ro chính
| Rủi ro | Tác động | Giảm thiểu |
|---|---|---|
| Hallucinate thông tin y tế | mất ô 05, nguy hiểm | grounding cứng + citation + refusal gate + eval set |
| Crawler bị chặn/đổi cấu trúc | KB mỏng | backup: SOP + nội dung BA biên soạn |
| 48h thiếu thời gian | demo hời hợt | lát cắt hẹp, ưu tiên 01+02+03+05 |
| API BV không có | pilot yếu | mock + roadmap thật rõ (ôm ô 03) |
| VPS không GPU | ASR/TTS/local LLM bị cắt | cloud API LLM; ASR/TTS bonus |

## 10. Giả định & mục cần VERIFY (xem `brainstorming.md` §Verify)
LLM provider+credit · cấu hình VPS/GPU · URL site BV + quyền crawl · API/HIS thật · domain+DNS · on-prem documentation. **Chưa chốt — verify trước giờ 2.**

## 11. Liên quan
- Nền tảng: [[00-competition-rubric-and-principles]] · [[00-hospital-domain-rules]]
- Chuỗi: [[02-business-analysis]] → [[03-functional-requirements]] → [[04-non-functional-requirements]]
- Setup/contract: [[07-api-design]] · [[08-development-guide]] · [[09-deployment-guide]]

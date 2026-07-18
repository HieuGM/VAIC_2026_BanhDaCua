# 00 — Team Working Guide (Hướng dẫn làm việc)

> **Đọc ĐẦU TIÊN.** Mọi thành viên & AI agent tuân theo file này.
> Mục đích: để **tất cả mọi người (3 web + 2 AI + 1 BA)** chạy được song song, không chặn nhau, trong 48h.
> Cập nhật: 2026-07-17 · Trạng thái: Living doc.

---

## 1. Docs map — thứ tự đọc

```
docs/
├── 00-team-working-guide.md         ← BẠN ĐANG ĐỌC (vận hành)
├── 00-competition-rubric-and-principles.md  ← tiêu chí chấm điểm (100đ)
├── 00-hospital-domain-rules.md      ← nghiệp vụ BV + 10 domain rule (R1–R10)
├── 00-data-strategy.md              ← KB vs DB + map nguồn data + data còn thiếu
├── brainstorming.md                 ← nháp + danh sách VERIFY (chưa chốt)
├── 01-project-overview.md           ← tầm nhìn, scope, stack, team, metrics
├── 02-business-analysis.md          ← actor, use case, domain model
├── 03-functional-requirements.md    ← FR + MoSCoW + acceptance criteria
├── 04-non-functional-requirements.md ← perf, security, compliance
├── 05-system-architecture.md        ← component/dataflow/deploy + ADR
├── 06-database-design.md            ← ERD, vector schema
├── 07-api-design.md                 ← CONTRACT v0 — chốt giờ đầu
├── 08-development-guide.md          ← setup, git, coding standards
├── 09-deployment-guide.md           ← Docker, CI/CD, on-prem path
├── 10-development-roadmap.md        ← phase 48h + % tiến độ
├── 11-project-changelog.md          ← version history
└── refer/                            ← nguồn: Đề tài.md + SOP Quytrinh.md + PDF
```

**Thứ tự đọc khuyến nghị:** `00-team-working-guide` → `00-competition-rubric` → `00-hospital-domain-rules` → `brainstorming` → `01`→`04`. Stub `08–10` đọc khi vào phase đó; `05/06/07` đã filled v1.0.

---

## 2. Operating model — "Docs-first, Agent-driven"

- **Docs là nguồn sự thật duy nhất.** Mọi spec/chỉ thị chỉ tồn tại trong `docs/`. KHÔNG rải spec trong chat/Zalo.
- **Agent làm việc với docs**: khi giao task cho AI agent (Claude/Cursor…), **luôn trỏ đúng file doc** làm input. Ví dụ: "Implement theo `03-functional-requirements.md` FR-2 và `00-hospital-domain-rules.md` R2".
- **Sửa docs trước, code sau.** Đổi yêu cầu → update doc → commit doc → rồi code theo doc.
- **Mỗi doc có 1 owner** (xem §4). Chỉ owner (hoặc người được assign) mới sửa nội dung chính.

---

## 3. Vai trò & sở hữu (RACI rút gọn)

> ⚠️ **Headcount (2026-07-18):** Có mâu thuẫn giữa docs về số Web FE — `01` §7 ghi **(2)**, bảng đây ghi **(3)**. Lead chốt số cuối. Tạm quy ước bảng dưới = **3 web FE** (theo `00`). Ngoài ra, **Data Backend (1)** được thêm làm luồng riêng — sở hữu `data-api/` và **chat BFF + persistence** (ADR-008), tách khỏi BA.

| Luồng | Role | Sở hữu docs | Sở hữu code |
|---|---|---|---|
| **Web FE** (3) | FE | `04` (UX phần FE), góp ý `07` | `frontend/` (React 18 + CRA — không phải `web/`/Next.js) |
| **Data Backend** (1) | Data dev | `06` (phần hospital + chat tables), `07` (B.5 chat BFF) | `data-api/` (Spring Boot + PG `hospital`) + **chat BFF + persistence** (ADR-008) |
| **AI/Backend** (2) | AI | `05`, `06` (phần ai/Qdrant), `07` (A.1 FastAPI chat), `09` (AI phần) | `chatbot-service/` (FastAPI), `ingest/`, `eval/`, guardrail |
| **Data/Demo** (1) | BA | `02`, `brainstorming` (verify), KB content, golden Q&A | data/KB files, slide, kịch bản |
| **Lead** (1 trong 6) | — | `01`, `03`, `10`, `11`, chốt scope | repo + Docker + deploy |

> Mỗi FR/NFR gán 1 người chịu trách nhiệm chính (assign trong §FR `03`). Code FE dir thực tế = **`frontend/`** (không phải `web/`).

---

## 4. Git workflow

- **Nhánh:**
  - `docs` — tài liệu (hiện tại).
  - `main` — code ổn định, demo deploy từ đây.
  - `feat/<scope>` — vd `feat/rag-pipeline`, `feat/chat-ui`, `feat/guardrail`.
  - `fix/<scope>`, `chore/<scope>`.
- **Commit:** conventional, KHÔNG nhắc AI. Vd: `feat(rag): grounded answer with citation`, `docs(api): lock chat SSE contract`.
- **PR nhỏ**, review chéo (FE↔AI). Squash merge.
- **Không push secrets** (`.env` đã gitignored). Claudekit/toolkit KHÔNG commit.

---

## 5. Nhịp làm việc 48h

- **Standup 10 phút / 4–6h**: mỗi người nói (1) đã xong gì, (2) đang làm, (3) có bị chặn gì.
- **Sync khi chạm contract `07` hoặc KB schema** — đây là 2 điểm giao thoa duy nhất giữa các luồng.
- **Cập nhật `10-development-roadmap.md` (% tiến độ) + `11-changelog` sau mỗi milestone.**
- **Demo rehearsal** trước khi nộp ≥1 lần (≤5').

---

## 6. CHỐT TIẾP — quyết định cần lock (owner · khi nào)

> Thứ tự ưu tiên. Mục chặn càng nhiều luồng càng làm trước.

| # | Quyết định | Owner | Chặn | Khi |
|---|---|---|---|---|
| 1 | **LLM provider + model + ngân sách credit** (GPT-4o-mini/Gemini/Claude) | AI | Demo + chi phí | Giờ 0–1 |
| 2 | **Cấu hình VPS** (CPU/RAM/GPU?, OS, domain) → cloud vs local LLM | Lead/DevOps | Deploy + LLM | Giờ 0–1 |
| 3 | **KB sources**: URL site BV chính thức + được phép crawl? + BA cung cấp gì thêm (FAQ/giá/lịch BS/BHYT) | BA + AI | Grounding | Giờ 0–2 |
| 4 | **Hospital access**: có API/Zalo/hotline thật không? (cho pilot rubric 03) | Lead/BA | Pilot pathway | Giờ 0–2 |
| 5 | **API contract `07` final** (JSON schema `final`, intent codes, ngưỡng confidence) | AI (draft) + FE (review) | Toàn bộ song song | Giờ 1–2 |
| 6 | **Scope cut / MoSCoW**: confirm Must vs Could (đặc biệt ASR/TTS, booking real vs mock) | Lead | Phân việc | Giờ 1–2 |
| 7 | **Emergency criteria list**: tập triệu chứng/khẩu lệnh trigger kill switch | AI + BA (+ confirm y tế) | Ô 05 | Giờ 2–4 |
| 8 | **Brand/UX direction** (tên, màu, tone giọng, layout chat) | FE + BA | Ô 04 | Giờ 2–4 |
| 9 | **Domain + DNS** cho public URL demo | DevOps | Deliverable URL | Giờ 24 |

---

## 7. VERIFY DOCS — review từng file (ai review · tiêu chí)

> Mục tiêu: docs đủ chuẩn để **ai cũng làm việc được** (không hiểu sai nghiệp vụ).

| Doc | Reviewer | Tiêu chí verify | Done khi |
|---|---|---|---|
| `00-competition-rubric` | All | Trọng số + cách hiểu 6 ô đúng đề tài; sub-criteria hợp lý | Cả team đồng ý cách tính điểm ưu tiên |
| `00-hospital-domain-rules` | **BA (+ chuyên gia CS/y tế BV nếu có)** | 11 bước SOP đúng `Quytrinh.md`; R1–R10 thực thi được; danh sách triệu chứng cấp cứu chuẩn | R2 list triệu chứng chốt + test được |
| `01-project-overview` | Lead | Scope/stack/team/metrics thực tế; out-of-sache đúng | Stack chốt |
| `02-business-analysis` | BA | Actor/use case/pain khớp thực tế BV | UC đủ cover 6 yêu cầu đề bài |
| `03-functional-requirements` | Lead + AI + FE | MoSCoW hợp lý; AC test được; map đủ 6 yêu cầu đề bài | Mỗi FR có AC + owner |
| `04-non-functional` | Lead + DevOps | Mục tiêu perf/security/compliance khả thi với VPS | Số liệu thực tế, không viển vông |
| `07-api-design` | AI + FE | Contract đủ để FE mock + AI implement | Cả 2 bên ký duyệt contract |
| `05/06` (đã filled v1.0) | Owner tương ứng | Diagram/ADR đúng code thật (xem ⚠️ notes 2026-07-18) | ADR-008 chốt, reality notes có mặt |
| `08/09/10` (stub) | Owner tương ứng | Điền đủ khi vào phase | Theo roadmap |

**Quy trình verify 1 doc:** đọc → ghi nhận sửa vào `brainstorming.md` §Verify hoặc comment trong file → owner update → commit `docs:`. Lặp đến khi đạt "Done khi".

---

## 8. THẢO LUẬN NHÓM (cần đồng thuận)

1. **Lát cắt chiến lược**: 4 ô nặng `01+02+03+05` đi sâu — cả team có đồng ý không làm trunnng `04`/`06` quá sớm?
2. **Grounding boundary**: thế nào là "thông tin chính thức" đủ để trả lời? Khi nào chuyển "tôi chưa đủ thông tin"?
3. **Emergency criteria**: chốt danh sách dấu hiệu (đau ngực dữ dội, khó thở, ngất, vã mồ hôi lạnh, nửa người tê/yếu…). Có cần confirm cùng chuyên gia y tế BV?
4. **BHYT/giá**: trả lời tới mức nào? Tránh cam kết % cụ thể.
5. **Integration**: mock tới đâu, roadmap thật viết ra sao để "defensible" trước giám khảo (ô 03)?
6. **Demo script**: 3 luồng tình huống (FAQ → BHYT/giá → cấp cứu) + handoff. Ai đóng vai BN?
7. **Privacy story**: nói gì với giám khảo về NĐ13/Luật KBChB + on-prem path.

---

## 9. Definition of Done — phase Docs

- [ ] Tất cả `00–04` đã được owner verify (§7).
- [ ] 9 mục `brainstorming` §Verify đã có trả lời/chốt.
- [ ] `07-api-design` contract ký duyệt 2 bên.
- [ ] Scope/MoSCoW chốt.
- [ ] Repo scaffold + Docker + Qdrant chạy `docker compose up`.
- [ ] KB seed (SOP + site crawl) có trong vector store.
- [ ] Golden Q&A set ≥ 30 câu (BA).

---

## 10. Câu hỏi mở / chờ

- Có chuyên gia/y tá/BS BV Tim HN rà `00-hospital-domain-rules` (đặc biệt R2 emergency) không?
- Có quyền crawl site BV không? (robots.txt + điều khoản)
- Ai là Lead/DevOps duy nhất để tránh xung đột infra?

## Liên quan
- [[00-competition-rubric-and-principles]] · [[00-hospital-domain-rules]] · [[brainstorming]] · [[07-api-design]] · [[10-development-roadmap]]

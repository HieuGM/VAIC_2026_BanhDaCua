# Brainstorming — WORKING DRAFT (cần verify)

> **Nháp làm việc — CHƯA chốt.** Nhiều mục cần xác nhận (xem §Verify). Bản chính dạng ở `00-11`.
> Nguồn: đề bài `docs/refer/Đề tài.md` + SOP `docs/refer/Quytrinh.md` (QT.25.01).
> Cập nhật: 2026-07-17 · Trạng thái: DRAFT.

## Problem
BV Tim HN (2.500–3.000 BN/ngày) quá tải câu hỏi lặp → cần Trợ lý AI CSKH **grounded + an toàn y tế**.

## Solution direction
Chatbot web RAG: ingest (crawl site + SOP) → retrieve + rerank → LLM grounded + citation + guardrail **emergency** (kill switch).

## Quyết định (status)
| Quyết định | Trạng thái |
|---|---|
| RAG thuần, KHÔNG fine-tune | Đề xuất |
| LLM: cloud API (demo) + đường on-prem (pilot) | Đề xuất — verify VPS/GPU |
| Vector DB: Qdrant | Đề xuất |
| FE Next.js + BE FastAPI | Đề xuất |
| ASR/TTS tiếng Việt (PhoWhisper + Viettel/FPT) | Bonus |
| Tích hợp API/Zalo: mock + roadmap | Verify truy cập thật |
| Deploy: Docker Compose + Caddy trên VPS | OK |

## VERIFY — cần xác nhận (chưa chốt)
1. [ ] URL website chính thức BV Tim HN (để crawl KB) + cấu trúc/robots.txt.
2. [ ] Kênh đặt khám thật có không? (Zalo Mini App / web booking / số hotline).
3. [ ] Quyền truy cập API/HIS của BV? (cả pathways rubric 03).
4. [ ] Cấu hình VPS (CPU/RAM/GPU?) → quyết định LLM cloud vs local.
5. [ ] Rà số điều khoản trích dẫn: **NĐ 13/2023/NĐ-CP**, **Luật Khám bệnh, chữa bệnh 2023**.
6. [ ] KB content: ngoài SOP + site, BA có thêm FAQ/bảng giá/lịch BS không?
7. [ ] LLM provider chính (GPT-4o-mini / Gemini / Claude) + ngân sách credit.
8. [ ] Domain + DNS cho public URL demo.
9. [ ] Có cần on-prem-capable chứng minh bằng tài liệu/arch diagram cho giám khảo?

## Team (đã confirm)
**3 web + 2 AI engineer + 1 BA = 6 người**, tất cả dùng AI agent.

## Cấp thiết NGAY (giờ 0–2)
1. Verify §Verify (đặc biệt KB + VPS + LLM provider).
2. **Chốt API contract** (`07-api-design`) → mở 3 luồng song song.
3. Scaffold repo + Docker + env + Qdrant.
4. Seed KB (SOP `Quytrinh.md` + crawl site).

## Liên quan
- [[00-competition-rubric-and-principles]] · [[00-hospital-domain-rules]]
- [[01-project-overview]] → [[04-non-functional-requirements]] · [[07-api-design]] · [[10-development-roadmap]]

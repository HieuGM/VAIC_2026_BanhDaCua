"""Build labeled price/schedule eval questions to complement the document QA set.

Gold labels are RESOLVED, not guessed: each question lists distinctive marker
substrings; a corpus chunk is gold iff its content contains ALL markers. This is
verifiable and robust to re-chunking. Prints the resolved gold count per question
so markers can be tightened until each maps to a small, correct set.

Run: cd chatbot-service && python -m rag.eval.build_extra_qa
Output: appends to rag/eval/data/qa_extra.jsonl (price + schedule groups).
"""

import json
from pathlib import Path

DATA = Path(__file__).parent / "data"

# (question, [markers all-required], group)
QUESTIONS: list[tuple[str, list[str], str]] = [
    # --- price: BHYT (clean pipe rows) ---
    ("Giá khám bệnh theo bảo hiểm y tế là bao nhiêu?", ["Khám bệnh | 42.100"], "price"),
    ("Giường nội khoa giá bao nhiêu theo BHYT?", ["Giường Nội khoa | 255.300"], "price"),
    ("Giường hồi sức cấp cứu giá bao nhiêu?", ["Giường Hồi sức cấp cứu | 474.700"], "price"),
    ("Giường hồi sức tích cực giá bao nhiêu theo bảo hiểm?", ["Giường Hồi sức tích cực | 786.300"], "price"),
    ("Giường ngoại khoa loại 1 giá bao nhiêu?", ["Giường Ngoại khoa loại 1 | 339.000"], "price"),
    ("Xét nghiệm định lượng CRP giá bao nhiêu theo BHYT?", ["CRP", "21.800"], "price"),
    ("Chụp Xquang ngực thẳng số hóa giá bao nhiêu?", ["Xquang ngực thẳng", "68.300"], "price"),
    ("Định lượng Triglycerid trong máu giá bao nhiêu?", ["Triglycerid", "27.300"], "price"),
    # --- schedule: doctor / room (gold = schedule chunks with the doctor/room) ---
    ("Bác sĩ Phạm Như Hùng khám ở phòng nào cơ sở 1?", ["Phạm Như Hùng"], "schedule"),
    ("Bác sĩ Vũ Quỳnh Nga khám phòng khám số mấy?", ["Vũ Quỳnh Nga"], "schedule"),
    ("Lịch khám của bác sĩ Bùi Thị Thanh Hà?", ["Bùi Thị Thanh Hà"], "schedule"),
    ("Phòng khám số 1 cơ sở 1 khám từ mấy giờ?", ["Phòng khám số 1 | 7.30 - 16.30"], "schedule"),
    ("Thứ 2 ngày 29/6 phòng khám số 1 ai khám?", ["Phòng khám số 1", "Thứ 2 (29/6): TS.BS Phạm Như Hùng"], "schedule"),
    ("Bác sĩ Hà Mai Hương khám những ngày nào?", ["Hà Mai Hương"], "schedule"),
    ("Phòng khám đa khoa cơ sở 2 có khám răng hàm mặt không?", ["RHM (P401)"], "schedule"),
    ("Bác sĩ nào khám mắt ở phòng khám đa khoa cơ sở 2?", ["MẮT (P405.D)"], "schedule"),
]


def main() -> None:
    corpus = [json.loads(l) for l in (DATA / "corpus.jsonl").read_text(encoding="utf-8").splitlines()]
    items, unresolved = [], []
    for i, (q, markers, group) in enumerate(QUESTIONS, 1):
        gold = [c["chunk_id"] for c in corpus if all(m in c["content"] for m in markers)]
        status = "OK " if gold else "MISS"
        print(f"[{status}] {group:8} n_gold={len(gold):3}  {q[:50]}")
        if not gold:
            unresolved.append((q, markers))
            continue
        items.append({
            "qa_id": f"EX_{group[:3].upper()}_{i:02d}",
            "question": q, "group": group, "markers": markers, "gold_chunk_ids": gold,
        })
    out = DATA / "qa_extra.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for row in items:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"\nwrote {len(items)} labeled questions to {out}")
    if unresolved:
        print("UNRESOLVED (tighten markers):")
        for q, m in unresolved:
            print(f"  {m} — {q}")


if __name__ == "__main__":
    main()

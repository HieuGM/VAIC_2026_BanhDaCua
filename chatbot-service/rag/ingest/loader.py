"""Source registry + loader for the 6 known hospital data files.

Metadata is hardcoded per file (YAGNI: fixed, known corpus) instead of being
inferred. Adding a new source = adding one registry entry.
"""

from pathlib import Path

from rag.config import get_settings

# Base metadata per source file. Missing keys default in `_base_meta`.
# Each file has a dedicated parser (its structure differs). `source_type` is the
# retrieval/filter category (document/price_table/schedule); `parser` picks the
# per-file chunker.
REGISTRY: list[dict] = [
    {
        "file": "groundtruth_gioi_thieu_benh_vien_tim_ha_noi.txt",
        "source_type": "document",
        "parser": "groundtruth",
        "title": "Giới thiệu Bệnh viện Tim Hà Nội",
        "url": "https://benhvientimhanoi.vn/vn/cong/thong-tin/gioi-thieu-chung",
        "updated_at": "2026-07-17",
    },
    {
        "file": "Huong_dan_dat_lich_kham_Benh_vien_Tim_Ha_Noi.txt",
        "source_type": "document",
        "parser": "booking_guide",
        "title": "Hướng dẫn đặt lịch khám",
        "url": "https://benhvientimhanoi.vn/he-thong/hen-kham/index.html",
    },
    {
        "file": "QUY_TRINH_DON_TIEP_BENH_NHAN_KHU_TU_NGUYEN_1_CS1.txt",
        "source_type": "document",
        "parser": "sop",
        "title": "Quy trình đón tiếp bệnh nhân Khu Tự nguyện 1 CS1",
        "document_code": "QT.25.01",
        "updated_at": "2024-12-05",
    },
    {
        "file": "banggiaBHYT.txt",
        "source_type": "price_table",
        "parser": "price_table",
        "title": "Bảng giá Bảo hiểm Y tế",
    },
    {
        "file": "GiaDVBV_tim_HN.txt",
        "source_type": "price_table",
        "parser": "price_table",
        "title": "Bảng giá dịch vụ Bệnh viện Tim Hà Nội",
    },
    {
        "file": "Lich_kham_benh_29.6-19.7.2026.txt",
        "source_type": "schedule",
        "parser": "schedule",
        "title": "Lịch khám bệnh 29/6–19/7/2026",
        "effective_from": "2026-06-29",
        "effective_to": "2026-07-19",
    },
    # Crawled seed data (data/seed/crawled/) — structured directory info added
    # later; evergreen (no effective dates), so it always passes the date filter.
    {
        "file": "doctors.json",
        "source_type": "document",
        "parser": "doctors",
        "title": "Danh sách bác sĩ Bệnh viện Tim Hà Nội",
        "updated_at": "2026-07-17",
    },
    {
        "file": "departments.json",
        "source_type": "document",
        "parser": "departments",
        "title": "Các khoa/phòng Bệnh viện Tim Hà Nội",
        "updated_at": "2026-07-17",
    },
    {
        "file": "bhyt-policies.json",
        "source_type": "document",
        "parser": "bhyt_policy",
        "title": "Chính sách BHYT Bệnh viện Tim Hà Nội",
        "updated_at": "2026-07-17",
    },
    {
        "file": "channels.json",
        "source_type": "document",
        "parser": "channels",
        "title": "Kênh liên hệ Bệnh viện Tim Hà Nội",
        "updated_at": "2026-07-17",
    },
    {
        "file": "working-hours.md",
        "source_type": "document",
        "parser": "working_hours",
        "title": "Giờ làm việc Bệnh viện Tim Hà Nội",
        "url": "https://benhvientimhanoi.vn/",
        "updated_at": "2026-07-17",
    },
]


def _base_meta(entry: dict) -> dict:
    return {
        "source": entry["file"],
        "source_type": entry["source_type"],
        "parser": entry["parser"],
        "title": entry["title"],
        "url": entry.get("url"),
        "document_code": entry.get("document_code"),
        "updated_at": entry.get("updated_at"),
        "effective_from": entry.get("effective_from"),
        "effective_to": entry.get("effective_to"),
        "approved": True,
        "deprecated": False,
    }


def load_sources(data_dir: str | Path | None = None) -> list[dict]:
    """Return [{"text": file content, "meta": base metadata}] for files that exist.

    Missing files are skipped (reported by run_ingest), never fatal: partial
    knowledge base is better than none.
    """
    root = Path(data_dir or get_settings().data_dir)
    sources = []
    for entry in REGISTRY:
        path = _source_path(root, entry["file"])
        if not path.exists():
            continue
        sources.append(
            {
                "text": path.read_text(encoding="utf-8"),
                "meta": _base_meta(entry),
            }
        )
    return sources


def missing_sources(data_dir: str | Path | None = None) -> list[str]:
    root = Path(data_dir or get_settings().data_dir)
    return [e["file"] for e in REGISTRY if not _source_path(root, e["file"]).exists()]


def _source_path(root: Path, filename: str) -> Path:
    # Search the known source locations in order; the crawled seed data lives in
    # seed/crawled while the original corpus is flat or under raw/.
    for rel in (filename, f"raw/{filename}", f"seed/crawled/{filename}"):
        candidate = root / rel
        if candidate.exists():
            return candidate
    return root / filename  # missing → reported by missing_sources()

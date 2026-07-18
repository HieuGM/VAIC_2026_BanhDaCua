"""Crawled seed parsers: doctors (group+dedupe), departments, bhyt_policy
(confidence caveat), channels (group by type), working_hours (markdown), plus
parse_source dispatch and finalize_chunks schema integration. No network."""

import json
import unittest

from rag.ingest.chunker import finalize_chunks
from rag.ingest.parsers import parse_source
from rag.ingest.parsers.crawled_json_parser import (
    parse_bhyt_policy,
    parse_channels,
    parse_departments,
    parse_doctors,
)
from rag.ingest.parsers.working_hours_parser import parse_working_hours

_META = {"source": "x", "source_type": "document", "title": "T"}


class DoctorsTest(unittest.TestCase):
    def test_groups_by_department_and_dedupes(self):
        data = json.dumps([
            {"fullName": "A", "degree": "TS.BS", "department": "Khoa 1", "specialty": "Tim mạch"},
            {"fullName": "A", "degree": "TS.BS", "department": "Khoa 1", "specialty": "Tim mạch"},  # dup
            {"fullName": "B", "degree": "BS", "department": "Khoa 2"},
        ])
        out = parse_doctors(data, _META)
        self.assertEqual(len(out), 2)  # two departments
        khoa1 = next(p for p in out if "Khoa 1" in p["title"])
        self.assertEqual(khoa1["content"].count("- TS.BS A"), 1)  # A listed once
        self.assertIn("chuyên khoa Tim mạch", khoa1["content"])

    def test_title_and_bio_rendered(self):
        data = json.dumps([{"fullName": "C", "degree": "PGS.TS.BS",
                            "department": "Ban Giám đốc", "title": "Giám đốc",
                            "bio": "Người phê duyệt QT.25.01."}])
        out = parse_doctors(data, _META)
        self.assertIn("Giám đốc", out[0]["content"])
        self.assertIn("Người phê duyệt QT.25.01.", out[0]["content"])

    def test_skips_nameless(self):
        out = parse_doctors(json.dumps([{"degree": "BS", "department": "K"}]), _META)
        self.assertEqual(out, [])


class DepartmentsTest(unittest.TestCase):
    def test_fields_rendered_and_url_passthrough(self):
        data = json.dumps([{
            "code": "khoa-noi", "name": "Khoa Nội",
            "description": "Khoa lâm sàng chẩn đoán và điều trị nội khoa tim mạch.",
            "workingHours": "7:00-16:30", "phone": "19001082",
            "sourceUrl": "http://x/dept",
        }])
        out = parse_departments(data, _META)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["title"], "Khoa Nội")
        self.assertEqual(out[0]["category"], "khoa-noi")
        self.assertEqual(out[0]["url"], "http://x/dept")
        self.assertIn("Giờ làm việc: 7:00-16:30.", out[0]["content"])
        self.assertIn("Điện thoại: 19001082.", out[0]["content"])

    def test_thin_departments_grouped_not_orphaned(self):
        # Tiny admin units are folded into one grouped chunk (>= 80 chars), never
        # emitted as bare orphan chunks.
        data = json.dumps([
            {"code": "p1", "name": "Phòng Tổ chức cán bộ", "description": "Phòng chức năng."},
            {"code": "p2", "name": "Phòng Điều dưỡng", "description": "Phòng chức năng."},
        ])
        out = parse_departments(data, _META)
        self.assertEqual(len(out), 1)  # both grouped into one
        self.assertGreaterEqual(len(out[0]["content"]), 80)
        self.assertIn("Phòng Tổ chức cán bộ", out[0]["content"])
        self.assertIn("Phòng Điều dưỡng", out[0]["content"])


class BhytPolicyTest(unittest.TestCase):
    def test_low_confidence_adds_caveat(self):
        data = json.dumps([{"code": "p1", "title": "Ưu tiên", "summary": "S",
                            "detailsMd": "D", "confidence": "low", "sourceUrl": "u"}])
        out = parse_bhyt_policy(data, _META)
        self.assertIn("Độ tin cậy: low", out[0]["content"])

    def test_high_confidence_no_caveat(self):
        data = json.dumps([{"title": "Giá khám", "summary": "42.100đ", "confidence": "high"}])
        out = parse_bhyt_policy(data, _META)
        self.assertNotIn("Độ tin cậy", out[0]["content"])
        self.assertIn("42.100đ", out[0]["content"])


class ChannelsTest(unittest.TestCase):
    def test_groups_by_channel_type(self):
        data = json.dumps([
            {"channelType": "hotline", "label": "H1", "phone": "19001082", "notes": "24/7"},
            {"channelType": "hotline", "label": "H2", "phone": "0869032338"},
            {"channelType": "email", "label": "E", "url": "mailto:a@b.vn"},
        ])
        out = parse_channels(data, _META)
        self.assertEqual(len(out), 2)  # hotline + email
        hotline = next(p for p in out if p["category"] == "hotline")
        self.assertIn("19001082", hotline["content"])
        self.assertIn("0869032338", hotline["content"])
        self.assertIn("24/7", hotline["content"])


class WorkingHoursTest(unittest.TestCase):
    def test_markdown_sections_split_and_heading_cleaned(self):
        md = (
            "# Giờ làm việc\n\n"
            "## Giờ chung\n"
            "Hotline tổng đài 19001082 hoạt động 24/7 tất cả các ngày trong tuần, "
            "kể cả Chủ nhật và ngày lễ Tết. Khoa Cấp cứu tiếp nhận bệnh nhân 24/7.\n\n"
            "## Cơ sở 2\n"
            "Phòng khám đa khoa Cơ sở 2 làm việc từ 7:30 đến 16:30, thứ 2 đến thứ 6, "
            "nghỉ thứ 7 và Chủ nhật. Một số chuyên khoa có lịch rải theo tuần.\n"
        )
        out = parse_working_hours(md, _META)
        self.assertEqual(len(out), 2)  # two sections, each body long enough
        joined = "\n".join(p["content"] for p in out)
        self.assertIn("Giờ chung", joined)
        self.assertIn("19001082", joined)
        self.assertIn("Cơ sở 2", joined)
        self.assertNotIn("#", joined)  # heading markers stripped


class DispatchAndFinalizeTest(unittest.TestCase):
    def test_parse_source_routes_to_new_parsers(self):
        meta = {**_META, "parser": "channels"}
        data = json.dumps([{"channelType": "web", "label": "W", "url": "http://x"}])
        out = parse_source(data, meta)
        self.assertEqual(out[0]["category"], "web")

    def test_finalize_produces_valid_payload(self):
        base = {"source": "departments.json", "source_type": "document",
                "parser": "departments", "title": "Khoa", "approved": True,
                "deprecated": False, "url": None, "document_code": None,
                "updated_at": "2026-07-17", "effective_from": None, "effective_to": None}
        data = json.dumps([{"code": "k", "name": "Khoa Nội",
                           "description": "Khoa lâm sàng chẩn đoán và điều trị "
                           "nội khoa tim mạch, chuyển hóa, quản lý bệnh mạn tính.",
                           "sourceUrl": "http://x/k"}])
        chunks = finalize_chunks(parse_departments(data, base), base)
        self.assertEqual(len(chunks), 1)
        c = chunks[0]
        for field in ("chunk_id", "title", "source", "content", "snippet",
                     "approved", "deprecated"):
            self.assertIn(field, c)
        self.assertEqual(c["url"], "http://x/k")  # per-record url wins over base None
        self.assertTrue(c["approved"])


if __name__ == "__main__":
    unittest.main()

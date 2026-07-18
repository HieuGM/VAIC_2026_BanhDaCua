from __future__ import annotations

from typing import Any

from core.enums import Route, SourceType
from core.state import ChatState


def generate_public_tool_answer(state: ChatState) -> str | None:
    if state.get("route") != Route.PUBLIC_TOOL.value:
        return None

    metadata = state.get("metadata") or {}
    public_tool = metadata.get("public_tool") if isinstance(metadata, dict) else None
    if not isinstance(public_tool, dict):
        return None

    status = public_tool.get("status")
    if status == "needs_clarification":
        return public_tool.get("message") or "Ban vui long cung cap them thong tin de minh tra cuu chinh xac hon."
    if status == "needs_selection":
        return _selection_answer(public_tool)
    if status == "no_data":
        return public_tool.get("message") or "Minh chua tim thay du lieu phu hop trong nguon cong khai hien co."
    if status == "upstream_error":
        return public_tool.get("message") or "Hien minh chua the lay du lieu cong khai. Vui long thu lai sau hoac lien he kenh ho tro chinh thuc."

    evidence = _public_evidence(state.get("evidence") or [])
    if not evidence:
        return None

    tool = public_tool.get("tool")
    data = evidence[0].get("data") or {}
    if tool == "get_booking_channels":
        return _channels_answer(data)
    if tool == "get_hospital_info":
        return _hospital_info_answer(data)
    if tool == "get_service_prices":
        return _service_price_answer(data)
    if tool == "get_doctor_schedule":
        return _doctor_schedule_answer(data)
    if tool == "get_departments":
        return _departments_answer(data)
    if tool == "get_procedures":
        return _procedures_answer(data)
    if tool == "get_bhyt_policies":
        return _bhyt_answer(data)
    return None


def _selection_answer(public_tool: dict[str, Any]) -> str:
    options = public_tool.get("options") if isinstance(public_tool.get("options"), list) else []
    lines = [public_tool.get("message") or "Minh tim thay nhieu ket qua gan dung. Ban muon chon muc nao?"]
    for index, option in enumerate(options[:5], start=1):
        label = option.get("label") if isinstance(option, dict) else None
        if label:
            lines.append(f"{index}. {label}")
    return "\n".join(lines)


def _public_evidence(items: list[Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in items
        if isinstance(item, dict) and item.get("source_type") == SourceType.PUBLIC_API.value
    ]


def _channels_answer(data: dict[str, Any]) -> str:
    channels = data.get("channels") if isinstance(data.get("channels"), list) else []
    if not channels:
        return "Minh chua tim thay kenh ho tro chinh thuc trong du lieu cong khai."
    lines = ["Cac kenh ho tro/dat lich chinh thuc hien co:"]
    for channel in channels[:6]:
        if not isinstance(channel, dict):
            continue
        parts = [str(channel.get("label") or channel.get("channelType") or "Kenh ho tro")]
        if channel.get("phone"):
            parts.append(f"SDT: {channel['phone']}")
        if channel.get("url"):
            parts.append(f"link: {channel['url']}")
        if channel.get("campus"):
            parts.append(f"co so: {channel['campus']}")
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _hospital_info_answer(data: dict[str, Any]) -> str:
    info = data.get("hospital_info") if isinstance(data.get("hospital_info"), dict) else data
    lines = [f"Thong tin {info.get('name') or 'benh vien'}:"]
    if info.get("hotline"):
        lines.append(f"- Hotline: {info['hotline']}")
    if info.get("website"):
        lines.append(f"- Website: {info['website']}")
    if info.get("grade"):
        lines.append(f"- Hang benh vien: {info['grade']}")
    if info.get("workingHours"):
        lines.append(f"- Gio lam viec: {_readable_value(info['workingHours'])}")
    if info.get("addresses"):
        lines.append(f"- Dia chi: {_readable_value(info['addresses'])}")
    return "\n".join(lines)


def _service_price_answer(data: dict[str, Any]) -> str:
    service = data.get("service") if isinstance(data.get("service"), dict) else {}
    prices = data.get("prices") if isinstance(data.get("prices"), list) else []
    service_name = service.get("name") or "dich vu"
    if not prices:
        return f"Minh chua tim thay bang gia cho {service_name} trong du lieu cong khai hien co."
    lines = [f"Bang gia cong khai cho {service_name}:"]
    for price in prices[:6]:
        if not isinstance(price, dict):
            continue
        parts = []
        if price.get("audience"):
            parts.append(str(price["audience"]))
        if price.get("campus"):
            parts.append(f"co so {price['campus']}")
        if price.get("priceVnd") is not None:
            parts.append(f"{price['priceVnd']} VND")
        if price.get("effectiveDate"):
            parts.append(f"hieu luc {price['effectiveDate']}")
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _doctor_schedule_answer(data: dict[str, Any]) -> str:
    doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
    schedules = data.get("schedules") if isinstance(data.get("schedules"), list) else []
    doctor_name = doctor.get("fullName") or "bac si"
    if not schedules:
        return f"Minh chua tim thay lich lam viec phu hop cua {doctor_name} trong du lieu hien co."
    lines = [f"Lich lam viec cong khai cua {doctor_name}:"]
    for schedule in schedules[:6]:
        if not isinstance(schedule, dict):
            continue
        parts = []
        if schedule.get("effectiveDate"):
            parts.append(str(schedule["effectiveDate"]))
        if schedule.get("dayOfWeek") is not None:
            parts.append(f"thu {schedule['dayOfWeek']}")
        if schedule.get("startTime") or schedule.get("endTime"):
            parts.append(f"{schedule.get('startTime') or ''}-{schedule.get('endTime') or ''}")
        if schedule.get("shift"):
            parts.append(str(schedule["shift"]))
        if schedule.get("room"):
            parts.append(f"phong {schedule['room']}")
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _departments_answer(data: dict[str, Any]) -> str:
    departments = data.get("departments") if isinstance(data.get("departments"), list) else []
    if not departments:
        return "Minh chua tim thay danh sach khoa/phong trong du lieu cong khai."
    lines = ["Danh sach khoa/phong cong khai:"]
    for department in departments[:10]:
        if not isinstance(department, dict):
            continue
        parts = [str(department.get("name") or department.get("code") or "Khoa/phong")]
        if department.get("floor"):
            parts.append(f"tang {department['floor']}")
        if department.get("phone"):
            parts.append(f"SDT: {department['phone']}")
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _procedures_answer(data: dict[str, Any]) -> str:
    procedures = data.get("procedures") if isinstance(data.get("procedures"), list) else []
    if not procedures:
        return "Minh chua tim thay quy trinh phu hop trong du lieu cong khai."
    title = procedures[0].get("title") if isinstance(procedures[0], dict) else "Quy trinh"
    lines = [f"{title or 'Quy trinh'}:"]
    for step in procedures[:8]:
        if not isinstance(step, dict):
            continue
        name = step.get("name") or step.get("description") or "Buoc"
        step_no = step.get("stepNo")
        prefix = f"Buoc {step_no}: " if step_no is not None else "- "
        lines.append(f"{prefix}{name}")
    return "\n".join(lines)


def _bhyt_answer(data: dict[str, Any]) -> str:
    policies = data.get("policies") if isinstance(data.get("policies"), list) else []
    if not policies:
        return "Minh chua tim thay thong tin BHYT phu hop trong du lieu cong khai."
    lines = ["Thong tin BHYT cong khai hien co:"]
    for policy in policies[:6]:
        if not isinstance(policy, dict):
            continue
        title = policy.get("title") or policy.get("code") or "Chinh sach BHYT"
        summary = policy.get("summary") or policy.get("detailsMd") or ""
        lines.append(f"- {title}: {summary}")
    return "\n".join(lines)


def _readable_value(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(part for part in (_readable_value(item) for item in value) if part)
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            if item in (None, "", [], {}):
                continue
            label = str(key).replace("_", " ")
            parts.append(f"{label}: {_readable_value(item)}")
        return "; ".join(parts)
    return str(value)

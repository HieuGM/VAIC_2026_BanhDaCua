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
        return public_tool.get("message") or "Bạn vui lòng cung cấp thêm thông tin để mình tra cứu chính xác hơn."
    if status == "needs_selection":
        return _selection_answer(public_tool)
    if status == "no_data":
        return public_tool.get("message") or "Mình chưa tìm thấy dữ liệu phù hợp trong nguồn công khai hiện có."
    if status == "upstream_error":
        return public_tool.get("message") or "Hiện mình chưa thể lấy dữ liệu công khai. Vui lòng thử lại sau hoặc liên hệ kênh hỗ trợ chính thức."

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
    lines = [public_tool.get("message") or "Mình tìm thấy nhiều kết quả gần đúng. Bạn muốn chọn mục nào?"]
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
        return "Mình chưa tìm thấy kênh hỗ trợ chính thức trong dữ liệu công khai."
    lines = ["Các kênh hỗ trợ/đặt lịch chính thức hiện có:"]
    for channel in channels[:6]:
        if not isinstance(channel, dict):
            continue
        parts = [str(channel.get("label") or channel.get("channelType") or "Kênh hỗ trợ")]
        if channel.get("phone"):
            parts.append(f"SDT: {channel['phone']}")
        if channel.get("url"):
            parts.append(f"link: {channel['url']}")
        if channel.get("campus"):
            parts.append(f"cơ sở: {channel['campus']}")
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _hospital_info_answer(data: dict[str, Any]) -> str:
    info = data.get("hospital_info") if isinstance(data.get("hospital_info"), dict) else data
    lines = [f"Thông tin {info.get('name') or 'bệnh viện'}:"]
    if info.get("hotline"):
        lines.append(f"- Hotline: {info['hotline']}")
    if info.get("website"):
        lines.append(f"- Website: {info['website']}")
    if info.get("grade"):
        lines.append(f"- Hạng bệnh viện: {info['grade']}")
    if info.get("workingHours"):
        lines.append(f"- Giờ làm việc: {_readable_value(info['workingHours'])}")
    if info.get("addresses"):
        lines.append(f"- Địa chỉ: {_readable_value(info['addresses'])}")
    return "\n".join(lines)


def _service_price_answer(data: dict[str, Any]) -> str:
    service = data.get("service") if isinstance(data.get("service"), dict) else {}
    prices = data.get("prices") if isinstance(data.get("prices"), list) else []
    service_name = service.get("name") or "dịch vụ"
    if not prices:
        return f"Mình chưa tìm thấy bảng giá cho {service_name} trong dữ liệu công khai hiện có."
    lines = [f"Bảng giá công khai cho {service_name}:"]
    for price in prices[:6]:
        if not isinstance(price, dict):
            continue
        parts = []
        if price.get("audience"):
            parts.append(str(price["audience"]))
        if price.get("campus"):
            parts.append(f"cơ sở {price['campus']}")
        if price.get("priceVnd") is not None:
            parts.append(f"{price['priceVnd']} VND")
        if price.get("effectiveDate"):
            parts.append(f"hiệu lực {price['effectiveDate']}")
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _doctor_schedule_answer(data: dict[str, Any]) -> str:
    doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
    schedules = data.get("schedules") if isinstance(data.get("schedules"), list) else []
    doctor_name = doctor.get("fullName") or "bác sĩ"
    if not schedules:
        return f"Mình chưa tìm thấy lịch làm việc phù hợp của {doctor_name} trong dữ liệu hiện có."
    lines = [f"Lịch làm việc công khai của {doctor_name}:"]
    for schedule in schedules[:6]:
        if not isinstance(schedule, dict):
            continue
        parts = []
        if schedule.get("effectiveDate"):
            parts.append(str(schedule["effectiveDate"]))
        if schedule.get("dayOfWeek") is not None:
            parts.append(f"thứ {schedule['dayOfWeek']}")
        if schedule.get("startTime") or schedule.get("endTime"):
            parts.append(f"{schedule.get('startTime') or ''}-{schedule.get('endTime') or ''}")
        if schedule.get("shift"):
            parts.append(str(schedule["shift"]))
        if schedule.get("room"):
            parts.append(f"phòng {schedule['room']}")
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _departments_answer(data: dict[str, Any]) -> str:
    departments = data.get("departments") if isinstance(data.get("departments"), list) else []
    if not departments:
        return "Mình chưa tìm thấy danh sách khoa/phòng trong dữ liệu công khai."
    lines = ["Danh sách khoa/phòng công khai:"]
    for department in departments[:10]:
        if not isinstance(department, dict):
            continue
        parts = [str(department.get("name") or department.get("code") or "Khoa/phòng")]
        if department.get("floor"):
            parts.append(f"tầng {department['floor']}")
        if department.get("phone"):
            parts.append(f"SDT: {department['phone']}")
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _procedures_answer(data: dict[str, Any]) -> str:
    procedures = data.get("procedures") if isinstance(data.get("procedures"), list) else []
    if not procedures:
        return "Mình chưa tìm thấy quy trình phù hợp trong dữ liệu công khai."
    title = procedures[0].get("title") if isinstance(procedures[0], dict) else "Quy trình"
    lines = [f"{title or 'Quy trình'}:"]
    for step in procedures[:8]:
        if not isinstance(step, dict):
            continue
        name = step.get("name") or step.get("description") or "Bước"
        step_no = step.get("stepNo")
        prefix = f"Bước {step_no}: " if step_no is not None else "- "
        lines.append(f"{prefix}{name}")
    return "\n".join(lines)


def _bhyt_answer(data: dict[str, Any]) -> str:
    policies = data.get("policies") if isinstance(data.get("policies"), list) else []
    if not policies:
        return "Mình chưa tìm thấy thông tin BHYT phù hợp trong dữ liệu công khai."
    lines = ["Thông tin BHYT công khai hiện có:"]
    for policy in policies[:6]:
        if not isinstance(policy, dict):
            continue
        title = policy.get("title") or policy.get("code") or "Chính sách BHYT"
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

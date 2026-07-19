from __future__ import annotations

from datetime import datetime
from typing import Any

from core.enums import Route, SourceType
from core.state import ChatState


MAX_FHIR_ITEMS = 5
NO_FHIR_DATA_MESSAGE = (
    "Mình chưa tìm thấy dữ liệu phù hợp trong hồ sơ được cấp quyền. "
    "Nếu bạn cần xác minh thêm, vui lòng liên hệ kênh hỗ trợ chính thức của bệnh viện."
)


def generate_fhir_answer(state: ChatState) -> str | None:
    if state.get("route") != Route.AUTHENTICATED_FHIR.value:
        return None

    if state.get("error"):
        return None

    evidence = _fhir_evidence(state.get("evidence") or [])
    if not evidence:
        return NO_FHIR_DATA_MESSAGE

    resource_types = [_resource_type(item) for item in evidence]
    if any(item in {"Observation", "DiagnosticReport"} for item in resource_types):
        return _format_lab_results(evidence)
    if "MedicationRequest" in resource_types:
        return _format_medications(evidence)
    if "Appointment" in resource_types:
        return _format_appointments(evidence)
    if "Encounter" in resource_types:
        return _format_encounters(evidence)
    if "Patient" in resource_types:
        return _format_patient_profile(evidence)

    return _format_generic_fhir(evidence)


def _format_lab_results(evidence: list[dict[str, Any]]) -> str:
    lines = ["Theo dữ liệu hồ sơ y tế của bạn, kết quả xét nghiệm/cận lâm sàng hiện có:"]
    for item in evidence[:MAX_FHIR_ITEMS]:
        data = item.get("data") or {}
        resource_type = data.get("resource_type")
        if resource_type == "Observation":
            lines.append(_format_observation_line(data))
        elif resource_type == "DiagnosticReport":
            lines.append(_format_diagnostic_report_line(data))
    lines.append(_fhir_safety_note())
    return "\n".join(line for line in lines if line)


def _format_medications(evidence: list[dict[str, Any]]) -> str:
    lines = ["Theo dữ liệu đơn thuốc trong hồ sơ y tế của bạn:"]
    for item in _items_of_type(evidence, "MedicationRequest")[:MAX_FHIR_ITEMS]:
        data = item.get("data") or {}
        medication = data.get("medication") or "Thuốc chưa rõ tên"
        parts = [str(medication)]
        if data.get("dosage"):
            parts.append(f"cách dùng: {', '.join(str(value) for value in data['dosage'])}")
        if data.get("authored_on"):
            parts.append(f"ngày kê: {_format_datetime(data['authored_on'])}")
        if data.get("status"):
            parts.append(f"trạng thái: {data['status']}")
        lines.append(f"- {'; '.join(parts)}")
    lines.append("Vui lòng dùng thuốc theo đơn và hướng dẫn trực tiếp của bác sĩ.")
    return "\n".join(lines)


def _format_appointments(evidence: list[dict[str, Any]]) -> str:
    lines = ["Theo dữ liệu lịch hẹn trong hồ sơ y tế của bạn:"]
    for item in _items_of_type(evidence, "Appointment")[:MAX_FHIR_ITEMS]:
        data = item.get("data") or {}
        title = data.get("description") or _first_concept_text(data.get("service_type")) or "Lịch hẹn"
        parts = [str(title)]
        if data.get("start"):
            parts.append(f"bắt đầu: {_format_datetime(data['start'])}")
        if data.get("end"):
            parts.append(f"kết thúc: {_format_datetime(data['end'])}")
        if data.get("status"):
            parts.append(f"trạng thái: {data['status']}")
        participant = _participant_text(data.get("participant"))
        if participant:
            parts.append(participant)
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _format_encounters(evidence: list[dict[str, Any]]) -> str:
    lines = ["Theo dữ liệu các lần khám trong hồ sơ y tế của bạn:"]
    for item in _items_of_type(evidence, "Encounter")[:MAX_FHIR_ITEMS]:
        data = item.get("data") or {}
        title = _first_concept_text(data.get("type")) or _concept_text(data.get("service_type")) or "Lần khám"
        parts = [str(title)]
        period = data.get("period") if isinstance(data.get("period"), dict) else {}
        if period.get("start"):
            parts.append(f"bắt đầu: {_format_datetime(period['start'])}")
        if period.get("end"):
            parts.append(f"kết thúc: {_format_datetime(period['end'])}")
        if data.get("status"):
            parts.append(f"trạng thái: {data['status']}")
        location = _encounter_location_text(data.get("location"))
        if location:
            parts.append(location)
        lines.append(f"- {'; '.join(parts)}")
    return "\n".join(lines)


def _format_patient_profile(evidence: list[dict[str, Any]]) -> str:
    data = (_items_of_type(evidence, "Patient")[0].get("data") or {})
    lines = ["Theo dữ liệu hồ sơ bệnh nhân được cấp quyền:"]
    if data.get("name"):
        lines.append(f"- Họ tên: {data['name']}")
    if data.get("birth_date"):
        lines.append(f"- Ngày sinh: {_format_datetime(data['birth_date'])}")
    if data.get("gender"):
        lines.append(f"- Giới tính: {data['gender']}")
    identifier = _identifier_text(data.get("identifier"))
    if identifier:
        lines.append(f"- Mã định danh: {identifier}")
    telecom = _telecom_text(data.get("telecom"))
    if telecom:
        lines.append(f"- Liên hệ: {telecom}")
    return "\n".join(lines)


def _format_generic_fhir(evidence: list[dict[str, Any]]) -> str:
    lines = ["Theo dữ liệu hồ sơ y tế được cấp quyền:"]
    for item in evidence[:MAX_FHIR_ITEMS]:
        title = item.get("title") or "FHIR"
        lines.append(f"- {title}")
    return "\n".join(lines)


def _format_observation_line(data: dict[str, Any]) -> str:
    code = data.get("code") or "Chỉ số xét nghiệm"
    parts = [str(code)]
    value = _value_text(data.get("value"))
    if value:
        parts.append(f"kết quả: {value}")
    if data.get("effective_time"):
        parts.append(f"thời gian: {_format_datetime(data['effective_time'])}")
    if data.get("status"):
        parts.append(f"trạng thái: {data['status']}")
    reference_range = _reference_range_text(data.get("reference_range"))
    if reference_range:
        parts.append(f"khoảng tham chiếu: {reference_range}")
    component_text = _components_text(data.get("components"))
    if component_text:
        parts.append(f"thành phần: {component_text}")
    return f"- {'; '.join(parts)}"


def _format_diagnostic_report_line(data: dict[str, Any]) -> str:
    code = data.get("code") or "Báo cáo cận lâm sàng"
    parts = [str(code)]
    if data.get("effective_time"):
        parts.append(f"thời gian: {_format_datetime(data['effective_time'])}")
    if data.get("status"):
        parts.append(f"trạng thái: {data['status']}")
    if data.get("conclusion"):
        parts.append(f"kết luận: {data['conclusion']}")
    result_refs = _result_refs_text(data.get("result"))
    if result_refs:
        parts.append(f"kết quả liên quan: {result_refs}")
    return f"- {'; '.join(parts)}"


def _fhir_evidence(items: list[Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        source_type = item.get("source_type")
        if source_type in {SourceType.FHIR.value, SourceType.FHIR}:
            result.append(item)
    return result[:MAX_FHIR_ITEMS]


def _items_of_type(evidence: list[dict[str, Any]], resource_type: str) -> list[dict[str, Any]]:
    return [item for item in evidence if _resource_type(item) == resource_type]


def _resource_type(item: dict[str, Any]) -> str | None:
    data = item.get("data") or {}
    if isinstance(data, dict) and isinstance(data.get("resource_type"), str):
        return data["resource_type"]
    title = item.get("title")
    if isinstance(title, str) and "/" in title:
        return title.split("/", 1)[0]
    return None


def _format_datetime(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return str(value)
    raw = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return value
    if "T" not in value:
        return parsed.strftime("%d/%m/%Y")
    return parsed.strftime("%H:%M ngay %d/%m/%Y")


def _value_text(value: Any) -> str | None:
    if isinstance(value, dict):
        if "value" in value:
            amount = value.get("value")
            unit = value.get("unit") or value.get("code")
            if unit:
                return f"{amount} {unit}".strip()
            return str(amount)
        return _concept_text(value)
    if value is None:
        return None
    return str(value)


def _reference_range_text(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    parts: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        if item.get("text"):
            parts.append(str(item["text"]))
            continue
        low = _value_text(item.get("low"))
        high = _value_text(item.get("high"))
        if low and high:
            parts.append(f"{low} - {high}")
        elif low:
            parts.append(f">= {low}")
        elif high:
            parts.append(f"<= {high}")
    return "; ".join(parts) or None


def _components_text(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    parts: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        code = item.get("code")
        result = _value_text(item.get("value"))
        if code and result:
            parts.append(f"{code}: {result}")
        elif code:
            parts.append(str(code))
    return "; ".join(parts) or None


def _result_refs_text(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    refs: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        refs.append(str(item.get("display") or item.get("reference") or ""))
    return ", ".join(ref for ref in refs if ref) or None


def _concept_text(value: Any) -> str | None:
    if isinstance(value, dict):
        text = value.get("text")
        if isinstance(text, str) and text:
            return text
    return None


def _first_concept_text(value: Any) -> str | None:
    if isinstance(value, list):
        for item in value:
            text = _concept_text(item)
            if text:
                return text
    return _concept_text(value)


def _participant_text(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    names: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        actor = item.get("actor")
        if isinstance(actor, dict) and actor.get("display"):
            names.append(str(actor["display"]))
    return f"người tham gia: {', '.join(names)}" if names else None


def _encounter_location_text(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    names: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        location = item.get("location")
        if isinstance(location, dict) and location.get("display"):
            names.append(str(location["display"]))
    return f"địa điểm: {', '.join(names)}" if names else None


def _identifier_text(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    identifiers = [str(item.get("value")) for item in value if isinstance(item, dict) and item.get("value")]
    return ", ".join(identifiers) or None


def _telecom_text(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    contacts = [str(item.get("value")) for item in value if isinstance(item, dict) and item.get("value")]
    return ", ".join(contacts) or None


def _fhir_safety_note() -> str:
    return "Thông tin trên chỉ là dữ liệu trong hồ sơ; vui lòng trao đổi với bác sĩ để được giải thích và hướng dẫn điều trị."

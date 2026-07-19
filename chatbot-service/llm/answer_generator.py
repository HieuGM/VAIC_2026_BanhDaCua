from core.state import ChatState
from fhir.formatter import generate_fhir_answer
from public_tools.formatter import generate_public_tool_answer


async def generate_grounded_answer(state: ChatState) -> str:
    fhir_answer = generate_fhir_answer(state)
    if fhir_answer:
        return fhir_answer

    public_tool_answer = generate_public_tool_answer(state)
    if public_tool_answer:
        return public_tool_answer

    evidence = state.get("evidence") or []
    if not evidence:
        return (
            "Mình chưa có đủ thông tin chính thức để trả lời câu này. "
            "Vui lòng liên hệ kênh hỗ trợ chính thức của bệnh viện để được xác nhận."
        )

    lines = ["Theo thông tin hiện có:"]
    for item in evidence[:3]:
        title = item.get("title") or "Nguồn"
        content = item.get("content")
        data = item.get("data")
        if content:
            lines.append(f"- {title}: {content}")
        elif data:
            lines.append(f"- {title}: {data}")
        else:
            lines.append(f"- {title}")
    return "\n".join(lines)

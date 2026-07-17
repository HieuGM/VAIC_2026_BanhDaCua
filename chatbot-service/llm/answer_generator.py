from core.state import ChatState


async def generate_grounded_answer(state: ChatState) -> str:
    evidence = state.get("evidence") or []
    if not evidence:
        return (
            "Minh chua co du thong tin chinh thuc de tra loi cau nay. "
            "Vui long lien he kenh ho tro chinh thuc cua benh vien de duoc xac nhan."
        )

    lines = ["Theo thong tin hien co:"]
    for item in evidence[:3]:
        title = item.get("title") or "Nguon"
        content = item.get("content")
        data = item.get("data")
        if content:
            lines.append(f"- {title}: {content}")
        elif data:
            lines.append(f"- {title}: {data}")
        else:
            lines.append(f"- {title}")
    return "\n".join(lines)

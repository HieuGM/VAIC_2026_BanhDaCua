from pydantic import BaseModel


class FhirToolCall(BaseModel):
    tool_name: str
    patient_id: str | None = None
    limit: int = 10

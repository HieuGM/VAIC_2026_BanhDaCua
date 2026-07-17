from typing import Any

from core.contracts import Evidence
from core.enums import SourceType


def normalize_fhir_resource(resource: dict[str, Any]) -> Evidence:
    resource_type = resource.get("resourceType") or "FHIR"
    resource_id = resource.get("id") or "unknown"
    return Evidence(
        source_type=SourceType.FHIR,
        title=f"{resource_type}/{resource_id}",
        data={
            "resource_type": resource_type,
            "id": resource_id,
        },
        confidence=1.0,
    )

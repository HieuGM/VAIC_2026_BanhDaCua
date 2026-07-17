FHIR_TOOL_ALLOWLIST = {
    "get_patient_appointments",
    "get_lab_results",
    "get_medications",
    "get_encounters",
}


def is_allowed_fhir_tool(tool_name: str) -> bool:
    return tool_name in FHIR_TOOL_ALLOWLIST

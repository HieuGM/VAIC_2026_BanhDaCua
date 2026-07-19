FHIR_TOOL_ALLOWLIST = {
    "get_patient_profile",
    "get_patient_appointments",
    "get_patient_encounters",
    "get_lab_results",
    "get_medications",
}

FHIR_PLANNER_TOOL_ALLOWLIST = {
    "get_patient_profile",
    "get_patient_encounters",
    "get_lab_results",
    "get_medications",
}


def is_allowed_fhir_tool(tool_name: str) -> bool:
    return tool_name in FHIR_TOOL_ALLOWLIST


def is_allowed_fhir_planner_tool(tool_name: str) -> bool:
    return tool_name in FHIR_PLANNER_TOOL_ALLOWLIST

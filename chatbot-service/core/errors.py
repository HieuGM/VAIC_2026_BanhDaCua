class ChatbotError(Exception):
    error_code = "CHATBOT_ERROR"


class PermissionDenied(ChatbotError):
    error_code = "PERMISSION_DENIED"


class UpstreamUnavailable(ChatbotError):
    error_code = "UPSTREAM_UNAVAILABLE"


class InvalidToolPlan(ChatbotError):
    error_code = "INVALID_TOOL_PLAN"

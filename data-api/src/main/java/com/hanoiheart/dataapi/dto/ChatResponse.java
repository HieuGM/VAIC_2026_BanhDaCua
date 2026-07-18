package com.hanoiheart.dataapi.dto;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Response của POST /data/v1/chat.
 *
 * <p>{@code sessionId} do data-api sở hữu (chatbot-service không trả về field này).
 * Các field còn lại khớp {@code chatbot-service/api/chat_schemas.py::ChatResponse}.
 */
public record ChatResponse(
        UUID sessionId,
        String answer,
        List<Map<String, Object>> citations,
        double confidence,
        String intent,
        List<String> guardrailFlags,
        Map<String, Object> redirection,
        boolean needsHandoff,
        Map<String, Object> metadata
) {}

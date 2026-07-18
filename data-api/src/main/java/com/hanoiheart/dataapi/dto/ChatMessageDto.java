package com.hanoiheart.dataapi.dto;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * Item trong {@code GET /data/v1/chat/sessions/{sessionId}/messages}.
 * Per docs/07-api-design.md §B.5.
 */
public record ChatMessageDto(
        Long id,
        String role,
        String content,
        List<Map<String, Object>> citations,
        String intent,
        String route,
        List<String> guardrailFlags,
        Instant createdAt
) {}

package com.hanoiheart.dataapi.dto;

import java.time.Instant;
import java.util.UUID;

/**
 * Item trong {@code GET /data/v1/chat/sessions}.
 * Per docs/07-api-design.md §B.5.
 */
public record ChatSessionDto(
        UUID id,
        Instant createdAt,
        Instant updatedAt,
        String lang,
        UUID anonToken,
        long messageCount,
        String lastSnippet
) {}

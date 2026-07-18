package com.hanoiheart.dataapi.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

/**
 * Body của POST /data/v1/chat — FE gửi {@code text} (+optional sessionId, lang).
 * sessionId null/blank → data-api tạo session mới (UUID).
 *
 * <p>Per docs/07-api-design.md §B.5.
 */
public record ChatRequest(
        String sessionId,
        @NotBlank(message = "text is required")
        @Size(max = 4000, message = "text must be at most 4000 characters")
        String text,
        @Pattern(regexp = "^vi$|^en$", message = "lang must be 'vi' or 'en'")
        String lang
) {}

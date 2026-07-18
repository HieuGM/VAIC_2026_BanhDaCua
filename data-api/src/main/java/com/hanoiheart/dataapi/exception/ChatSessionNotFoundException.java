package com.hanoiheart.dataapi.exception;

import java.util.UUID;

/**
 * ChatSession không tồn tại (lookup by id).
 *
 * <p>Extends {@link ResourceNotFoundException} → {@code GlobalExceptionHandler}
 * auto-map HTTP 404 {@code {error:{code:"not_found",message}}}. Không cần thêm
 * handler trong advice.
 */
public class ChatSessionNotFoundException extends ResourceNotFoundException {

    public ChatSessionNotFoundException(UUID sessionId) {
        super("ChatSession not found: id=" + sessionId);
    }
}

package com.hanoiheart.dataapi.client;

/**
 * Chatbot-service không phản hồi (timeout, connection refused, 5xx, JSON lỗi).
 *
 * <p>{@link com.hanoiheart.dataapi.service.ChatService} catch exception này và trả
 * fallback answer cho client (HTTP 200, không 500 — UX). KHÔNG leak ra controller.
 */
public class ChatbotUnavailableException extends RuntimeException {

    public ChatbotUnavailableException(String message, Throwable cause) {
        super(message, cause);
    }
}

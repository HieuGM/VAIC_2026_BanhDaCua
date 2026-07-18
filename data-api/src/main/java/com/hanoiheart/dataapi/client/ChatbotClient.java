package com.hanoiheart.dataapi.client;

import com.hanoiheart.dataapi.dto.ChatRequest;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Proxy JSON đến chatbot-service {@code POST /api/v1/chat} (FastAPI :8000).
 *
 * <p>Map data-api {@link ChatRequest} → chatbot pydantic body (camelCase aliases
 * per {@code chatbot-service/api/chat_schemas.py}). Response deserialize về
 * {@link ChatbotResponse} (không có sessionId — data-api tự thêm từ session của mình).
 *
 * <p>Mọi lỗi network/timeout/deser → {@link ChatbotUnavailableException}.
 */
@Component
public class ChatbotClient {

    /** Wire format matching chatbot-service api/chat_schemas.py ChatResponse. */
    public record ChatbotResponse(
            String answer,
            List<Map<String, Object>> citations,
            double confidence,
            List<String> guardrailFlags,
            String intent,
            String route,
            Map<String, Object> redirection,
            boolean needsHandoff,
            Map<String, Object> metadata
    ) {}

    private final RestClient restClient;

    public ChatbotClient(@Qualifier("chatbotRestClient") RestClient restClient) {
        this.restClient = restClient;
    }

    /**
     * Gọi chatbot {@code /api/v1/chat}.
     *
     * @param req       data-api ChatRequest (text + lang)
     * @param sessionId session id đã được data-api resolve (chuỗi UUID)
     * @return chatbot ChatResponse
     * @throws ChatbotUnavailableException khi timeout / connection / 5xx / parse
     */
    public ChatbotResponse chat(ChatRequest req, String sessionId) {
        Map<String, Object> body = new HashMap<>();
        body.put("sessionId", sessionId);
        body.put("text", req.text());
        body.put("lang", (req.lang() == null || req.lang().isBlank()) ? "vi" : req.lang());
        body.put("userRole", "ANONYMOUS");
        try {
            return restClient.post()
                    .uri("/api/v1/chat")
                    .body(body)
                    .retrieve()
                    .body(ChatbotResponse.class);
        } catch (RestClientException e) {
            throw new ChatbotUnavailableException("chatbot /api/v1/chat failed: " + e.getMessage(), e);
        }
    }
}

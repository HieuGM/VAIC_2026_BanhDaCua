package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.client.ChatbotClient;
import com.hanoiheart.dataapi.client.ChatbotUnavailableException;
import com.hanoiheart.dataapi.dto.ChatMessageDto;
import com.hanoiheart.dataapi.dto.ChatRequest;
import com.hanoiheart.dataapi.dto.ChatResponse;
import com.hanoiheart.dataapi.dto.ChatSessionDto;
import com.hanoiheart.dataapi.dto.PageResponse;
import com.hanoiheart.dataapi.entity.ChatMessage;
import com.hanoiheart.dataapi.entity.ChatSession;
import com.hanoiheart.dataapi.exception.ChatSessionNotFoundException;
import com.hanoiheart.dataapi.repository.ChatMessageRepository;
import com.hanoiheart.dataapi.repository.ChatSessionRepository;
import com.hanoiheart.dataapi.repository.UserPatientLinkRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Chat BFF core: persist user msg → proxy chatbot → persist assistant msg.
 *
 * <p>Session do data-api sở hữu (UUID). anonToken = pseudo-identity từ header
 * {@code X-Anon-Token} (nếu thiếu hoặc không hợp lệ → sinh UUID mới).
 *
 * <p>Chatbot down → fallback answer + {@code guardrailFlags=["upstream_error"]},
 * vẫn HTTP 200 (UX). User msg luôn persist trước khi gọi chatbot.
 *
 * <p>Per docs/07-api-design.md §B.5 + ADR-008.
 */
@Service
@Transactional(readOnly = true)
public class ChatService {

    /** Fallback answer khi chatbot-service không phản hồi. */
    static final String FALLBACK_ANSWER =
            "Tạm thời không kết nối được tới trợ lý. Vui lòng thử lại.";
    static final String FALLBACK_FLAG = "upstream_error";
    static final String DEFAULT_LANG = "vi";
    private static final int LAST_SNIPPET_MAX = 100;

    private final ChatSessionRepository sessionRepository;
    private final ChatMessageRepository messageRepository;
    private final ChatbotClient chatbotClient;
    /** Lookup user→FHIR patient IDs (authorization scope cho chatbot FHIR path). */
    private final UserPatientLinkRepository userPatientLinkRepository;

    public ChatService(ChatSessionRepository sessionRepository,
                       ChatMessageRepository messageRepository,
                       ChatbotClient chatbotClient,
                       UserPatientLinkRepository userPatientLinkRepository) {
        this.sessionRepository = sessionRepository;
        this.messageRepository = messageRepository;
        this.chatbotClient = chatbotClient;
        this.userPatientLinkRepository = userPatientLinkRepository;
    }

    /** POST /data/v1/chat — persist user msg, proxy chatbot, persist assistant msg. */
    @Transactional
    public ChatResponse handleMessage(ChatRequest req, String anonTokenHeader, Long userId) {
        UUID anonToken = resolveAnonToken(anonTokenHeader);
        ChatSession session = resolveSession(req, anonToken);
        sessionRepository.save(session);

        // 1) persist user message BEFORE calling upstream (durable even if chatbot fails)
        ChatMessage userMsg = newMessage(session, "user", req.text(), null, null, null, null, null);
        messageRepository.save(userMsg);

        // 2) resolve FHIR patient scope.
        //    userId=null (anon) hoặc user chưa có link → ANONYMOUS (chatbot fallback generic).
        //    user có link → USER + allowedPatientIds (chatbot access_control bắt
        //    userRole=="USER" + non-empty allowedPatientIds mới trả data cá nhân).
        //    Lưu ý: DB users.role='PATIENT' KHÔNG bao giờ tới chatbot — wire derive "USER".
        List<String> allowedPatientIds = (userId == null)
                ? List.of()
                : userPatientLinkRepository.findFhirPatientIdByUserId(userId);
        String userRole = allowedPatientIds.isEmpty() ? "ANONYMOUS" : "USER";

        // 3) proxy → chatbot (fallback on upstream error)
        try {
            ChatbotClient.ChatbotResponse bot =
                    chatbotClient.chat(req, session.getId().toString(), userRole, allowedPatientIds);
            ChatMessage assistantMsg = newMessage(session, "assistant", bot.answer(),
                    bot.citations(), bot.intent(), bot.route(),
                    bot.guardrailFlags(), (float) bot.confidence());
            messageRepository.save(assistantMsg);
            return new ChatResponse(session.getId(), bot.answer(), bot.citations(),
                    bot.confidence(), bot.intent(), bot.guardrailFlags(),
                    bot.redirection(), bot.needsHandoff(), bot.metadata());
        } catch (ChatbotUnavailableException e) {
            ChatMessage fallback = newMessage(session, "assistant", FALLBACK_ANSWER,
                    null, "UNKNOWN", null, List.of(FALLBACK_FLAG), 0f);
            messageRepository.save(fallback);
            return new ChatResponse(session.getId(), FALLBACK_ANSWER, List.of(), 0.0,
                    "UNKNOWN", List.of(FALLBACK_FLAG), null, false, Map.of());
        }
    }

    /** GET /data/v1/chat/sessions — list theo anonToken (sort updatedAt desc). */
    public PageResponse<ChatSessionDto> listSessions(String anonTokenHeader, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        UUID anonToken = parseUuid(anonTokenHeader);
        Page<ChatSession> sessions = (anonToken != null)
                ? sessionRepository.findByAnonTokenOrderByUpdatedAtDesc(anonToken, pageable)
                : sessionRepository.findAll(pageable);
        return PageResponse.of(sessions.map(this::toSessionDto));
    }

    /** GET /data/v1/chat/sessions/{sessionId}/messages — ASC by createdAt. */
    public PageResponse<ChatMessageDto> listMessages(UUID sessionId, int page, int size) {
        ChatSession session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new ChatSessionNotFoundException(sessionId));
        Pageable pageable = PageRequest.of(page, size);
        Page<ChatMessage> messages =
                messageRepository.findBySessionOrderByCreatedAtAsc(session, pageable);
        return PageResponse.of(messages.map(this::toMessageDto));
    }

    private ChatSession resolveSession(ChatRequest req, UUID anonToken) {
        UUID existing = parseUuid(req.sessionId());
        if (existing != null) {
            ChatSession s = sessionRepository.findById(existing)
                    .orElseThrow(() -> new ChatSessionNotFoundException(existing));
            // attach anonToken if session has none yet (continue session)
            if (s.getAnonToken() == null) {
                s.setAnonToken(anonToken);
            }
            return s;
        }
        ChatSession s = new ChatSession();
        s.setId(UUID.randomUUID());
        s.setAnonToken(anonToken);
        s.setLang((req.lang() == null || req.lang().isBlank()) ? DEFAULT_LANG : req.lang());
        return s;
    }

    private UUID resolveAnonToken(String header) {
        UUID parsed = parseUuid(header);
        return parsed != null ? parsed : UUID.randomUUID();
    }

    private static UUID parseUuid(String raw) {
        if (raw == null || raw.isBlank()) return null;
        try {
            return UUID.fromString(raw.trim());
        } catch (IllegalArgumentException e) {
            return null;
        }
    }

    private ChatMessage newMessage(ChatSession session, String role, String content,
                                   List<Map<String, Object>> citations, String intent,
                                   String route, List<String> guardrailFlags, Float confidence) {
        ChatMessage m = new ChatMessage();
        m.setSession(session);
        m.setRole(role);
        m.setContent(content);
        m.setCitations(citations);
        m.setIntent(intent);
        m.setRoute(route);
        m.setGuardrailFlags(guardrailFlags);
        m.setConfidence(confidence);
        return m;
    }

    private ChatSessionDto toSessionDto(ChatSession s) {
        long count = messageRepository.countBySession(s);
        String lastSnippet = messageRepository.findFirstBySessionOrderByCreatedAtDesc(s)
                .map(ChatMessage::getContent)
                .map(c -> c.length() <= LAST_SNIPPET_MAX ? c : c.substring(0, LAST_SNIPPET_MAX))
                .orElse(null);
        return new ChatSessionDto(s.getId(), s.getCreatedAt(), s.getUpdatedAt(),
                s.getLang(), s.getAnonToken(), count, lastSnippet);
    }

    private ChatMessageDto toMessageDto(ChatMessage m) {
        return new ChatMessageDto(m.getId(), m.getRole(), m.getContent(),
                m.getCitations(), m.getIntent(), m.getRoute(),
                m.getGuardrailFlags(), m.getCreatedAt());
    }
}

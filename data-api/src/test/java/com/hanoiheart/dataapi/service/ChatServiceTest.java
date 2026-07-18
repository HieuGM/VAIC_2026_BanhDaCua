package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.client.ChatbotClient;
import com.hanoiheart.dataapi.client.ChatbotUnavailableException;
import com.hanoiheart.dataapi.dto.ChatRequest;
import com.hanoiheart.dataapi.dto.ChatResponse;
import com.hanoiheart.dataapi.entity.ChatMessage;
import com.hanoiheart.dataapi.entity.ChatSession;
import com.hanoiheart.dataapi.repository.ChatMessageRepository;
import com.hanoiheart.dataapi.repository.ChatSessionRepository;
import com.hanoiheart.dataapi.repository.UserPatientLinkRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Unit test cho {@link ChatService}. Mock ChatbotClient + repos (no DB, no Spring).
 *
 * <p>Cover 2 nhánh wire FHIR scope:
 * <ul>
 *   <li>userId=null (anon) → userRole="ANONYMOUS", allowedPatientIds=[]</li>
 *   <li>userId có link → userRole="USER", allowedPatientIds=[fhir_patient_id]</li>
 * </ul>
 */
@ExtendWith(MockitoExtension.class)
class ChatServiceTest {

    @Mock
    private ChatSessionRepository sessionRepository;
    @Mock
    private ChatMessageRepository messageRepository;
    @Mock
    private ChatbotClient chatbotClient;
    @Mock
    private UserPatientLinkRepository userPatientLinkRepository;

    @InjectMocks
    private ChatService service;

    @Test
    void handleMessage_newSession_persistsUserAndAssistant_returnsAnswer() {
        ChatRequest req = new ChatRequest(null, "Xin chào", "vi");
        List<Map<String, Object>> citations = List.of(Map.of("source", "faq"));
        ChatbotClient.ChatbotResponse bot = new ChatbotClient.ChatbotResponse(
                "Chào bạn", citations, 0.9, List.of(), "GREETING", "CHATBOT",
                null, false, Map.of());

        when(sessionRepository.save(any(ChatSession.class))).thenAnswer(i -> i.getArgument(0));
        when(messageRepository.save(any(ChatMessage.class))).thenAnswer(i -> i.getArgument(0));
        when(chatbotClient.chat(any(ChatRequest.class), any(String.class), any(String.class), any()))
                .thenReturn(bot);

        // userId=null → anon chat
        ChatResponse resp = service.handleMessage(req, null, null);

        assertThat(resp.answer()).isEqualTo("Chào bạn");
        assertThat(resp.confidence()).isEqualTo(0.9);
        assertThat(resp.intent()).isEqualTo("GREETING");
        assertThat(resp.guardrailFlags()).isEmpty();
        assertThat(resp.sessionId()).isNotNull();

        ArgumentCaptor<ChatMessage> captor = ArgumentCaptor.forClass(ChatMessage.class);
        verify(messageRepository, times(2)).save(captor.capture());
        List<ChatMessage> saved = captor.getAllValues();
        assertThat(saved.get(0).getRole()).isEqualTo("user");
        assertThat(saved.get(0).getContent()).isEqualTo("Xin chào");
        assertThat(saved.get(1).getRole()).isEqualTo("assistant");
        assertThat(saved.get(1).getIntent()).isEqualTo("GREETING");
        assertThat(saved.get(1).getCitations()).isEqualTo(citations);
    }

    @Test
    void handleMessage_chatbotDown_returnsFallbackWithUpstreamError() {
        ChatRequest req = new ChatRequest(null, "ôi đau", null);
        when(sessionRepository.save(any(ChatSession.class))).thenAnswer(i -> i.getArgument(0));
        when(messageRepository.save(any(ChatMessage.class))).thenAnswer(i -> i.getArgument(0));
        when(chatbotClient.chat(any(ChatRequest.class), any(String.class), any(String.class), any()))
                .thenThrow(new ChatbotUnavailableException("timeout",
                        new RuntimeException("timeout")));

        ChatResponse resp = service.handleMessage(req, null, null);

        assertThat(resp.answer()).contains("Tạm thời");
        assertThat(resp.guardrailFlags()).contains(ChatService.FALLBACK_FLAG);
        assertThat(resp.confidence()).isZero();
        assertThat(resp.metadata()).isEmpty();

        ArgumentCaptor<ChatMessage> captor = ArgumentCaptor.forClass(ChatMessage.class);
        verify(messageRepository, times(2)).save(captor.capture());
        List<ChatMessage> saved = captor.getAllValues();
        assertThat(saved.get(0).getRole()).isEqualTo("user");   // user msg vẫn persist
        assertThat(saved.get(1).getRole()).isEqualTo("assistant");
        assertThat(saved.get(1).getContent()).contains("Tạm thời");
        assertThat(saved.get(1).getGuardrailFlags()).contains(ChatService.FALLBACK_FLAG);
    }

    @Test
    void handleMessage_existingSessionId_reusesSession() {
        UUID sessionId = UUID.randomUUID();
        UUID anonToken = UUID.randomUUID();
        ChatSession existing = new ChatSession();
        existing.setId(sessionId);
        existing.setAnonToken(anonToken);
        existing.setLang("vi");

        ChatRequest req = new ChatRequest(sessionId.toString(), "hello", "vi");
        when(sessionRepository.findById(sessionId)).thenReturn(Optional.of(existing));
        when(sessionRepository.save(any(ChatSession.class))).thenAnswer(i -> i.getArgument(0));
        when(messageRepository.save(any(ChatMessage.class))).thenAnswer(i -> i.getArgument(0));
        when(chatbotClient.chat(any(), any(), any(), any())).thenReturn(
                new ChatbotClient.ChatbotResponse("hi", List.of(), 0.5, List.of(),
                        "GREETING", "CHATBOT", null, false, Map.of()));

        ChatResponse resp = service.handleMessage(req, anonToken.toString(), null);

        assertThat(resp.sessionId()).isEqualTo(sessionId);
        verify(sessionRepository).findById(sessionId);
    }

    @Test
    void handleMessage_langDefaultsToVi_whenBlank() {
        ChatRequest req = new ChatRequest(null, "hi", "");
        when(sessionRepository.save(any(ChatSession.class))).thenAnswer(i -> i.getArgument(0));
        when(messageRepository.save(any(ChatMessage.class))).thenAnswer(i -> i.getArgument(0));
        when(chatbotClient.chat(any(), any(), any(), any())).thenReturn(
                new ChatbotClient.ChatbotResponse("hi", List.of(), 0.1, List.of(),
                        "GREETING", "CHATBOT", null, false, Map.of()));

        service.handleMessage(req, null, null);

        ArgumentCaptor<ChatSession> sc = ArgumentCaptor.forClass(ChatSession.class);
        verify(sessionRepository).save(sc.capture());
        assertThat(sc.getValue().getLang()).isEqualTo("vi");
    }

    /**
     * Core wire test: user đã login (userId=1L) CÓ link → derive userRole="USER"
     * + allowedPatientIds=["vn-patient-001"] → forward cho chatbot (FHIR path).
     * Đây là điểm khác biệt cốt lõi vs anon (ANONYMOUS + []).
     */
    @Test
    void handleMessage_authenticatedUserWithLink_forwardsUserRoleUserAndPatientIds() {
        ChatRequest req = new ChatRequest(null, "kết quả xét nghiệm của tôi", "vi");
        when(userPatientLinkRepository.findFhirPatientIdByUserId(1L))
                .thenReturn(List.of("vn-patient-001"));
        when(sessionRepository.save(any(ChatSession.class))).thenAnswer(i -> i.getArgument(0));
        when(messageRepository.save(any(ChatMessage.class))).thenAnswer(i -> i.getArgument(0));
        ChatbotClient.ChatbotResponse bot = new ChatbotClient.ChatbotResponse(
                "Glucose 5.2 mmol/L", List.of(), 0.9, List.of(), "LAB_RESULT", "AUTHENTICATED_FHIR",
                null, false, Map.of());
        when(chatbotClient.chat(any(ChatRequest.class), any(String.class), any(String.class), any()))
                .thenReturn(bot);

        ChatResponse resp = service.handleMessage(req, null, 1L);

        // wire forwarded USER scope (KHÔNG phải ANONYMOUS) + đúng patient ID
        verify(chatbotClient).chat(any(ChatRequest.class), any(String.class),
                eq("USER"), eq(List.of("vn-patient-001")));
        // ChatResponse không forward route ra API (chỉ intent) — assert intent thay route.
        assertThat(resp.intent()).isEqualTo("LAB_RESULT");
        assertThat(resp.answer()).contains("Glucose");
    }

    /**
     * User đã login NHƯNG chưa có link (user_patient_links rỗng) → vẫn ANONYMOUS
     * (chatbot fallback generic, không leak data cá nhân).
     */
    @Test
    void handleMessage_authenticatedUserWithoutLink_fallsBackToAnonymous() {
        ChatRequest req = new ChatRequest(null, "kết quả xét nghiệm của tôi", "vi");
        when(userPatientLinkRepository.findFhirPatientIdByUserId(2L))
                .thenReturn(List.of());
        when(sessionRepository.save(any(ChatSession.class))).thenAnswer(i -> i.getArgument(0));
        when(messageRepository.save(any(ChatMessage.class))).thenAnswer(i -> i.getArgument(0));
        when(chatbotClient.chat(any(ChatRequest.class), any(String.class), any(String.class), any()))
                .thenReturn(new ChatbotClient.ChatbotResponse(
                        "Tôi không có thông tin", List.of(), 0.3, List.of(),
                        "UNKNOWN", "CHATBOT", null, false, Map.of()));

        service.handleMessage(req, null, 2L);

        verify(chatbotClient).chat(any(ChatRequest.class), any(String.class),
                eq("ANONYMOUS"), eq(List.of()));
    }
}

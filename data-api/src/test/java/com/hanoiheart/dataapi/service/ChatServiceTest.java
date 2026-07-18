package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.client.ChatbotClient;
import com.hanoiheart.dataapi.client.ChatbotUnavailableException;
import com.hanoiheart.dataapi.dto.ChatRequest;
import com.hanoiheart.dataapi.dto.ChatResponse;
import com.hanoiheart.dataapi.entity.ChatMessage;
import com.hanoiheart.dataapi.entity.ChatSession;
import com.hanoiheart.dataapi.repository.ChatMessageRepository;
import com.hanoiheart.dataapi.repository.ChatSessionRepository;
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
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Unit test cho {@link ChatService}. Mock ChatbotClient + repos (no DB, no Spring).
 */
@ExtendWith(MockitoExtension.class)
class ChatServiceTest {

    @Mock
    private ChatSessionRepository sessionRepository;
    @Mock
    private ChatMessageRepository messageRepository;
    @Mock
    private ChatbotClient chatbotClient;

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
        when(chatbotClient.chat(any(ChatRequest.class), any(String.class))).thenReturn(bot);

        ChatResponse resp = service.handleMessage(req, null);

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
        when(chatbotClient.chat(any(ChatRequest.class), any(String.class)))
                .thenThrow(new ChatbotUnavailableException("timeout",
                        new RuntimeException("timeout")));

        ChatResponse resp = service.handleMessage(req, null);

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
        when(chatbotClient.chat(any(), any())).thenReturn(
                new ChatbotClient.ChatbotResponse("hi", List.of(), 0.5, List.of(),
                        "GREETING", "CHATBOT", null, false, Map.of()));

        ChatResponse resp = service.handleMessage(req, anonToken.toString());

        assertThat(resp.sessionId()).isEqualTo(sessionId);
        verify(sessionRepository).findById(sessionId);
    }

    @Test
    void handleMessage_langDefaultsToVi_whenBlank() {
        ChatRequest req = new ChatRequest(null, "hi", "");
        when(sessionRepository.save(any(ChatSession.class))).thenAnswer(i -> i.getArgument(0));
        when(messageRepository.save(any(ChatMessage.class))).thenAnswer(i -> i.getArgument(0));
        when(chatbotClient.chat(any(), any())).thenReturn(
                new ChatbotClient.ChatbotResponse("hi", List.of(), 0.1, List.of(),
                        "GREETING", "CHATBOT", null, false, Map.of()));

        service.handleMessage(req, null);

        ArgumentCaptor<ChatSession> sc = ArgumentCaptor.forClass(ChatSession.class);
        verify(sessionRepository).save(sc.capture());
        assertThat(sc.getValue().getLang()).isEqualTo("vi");
    }
}

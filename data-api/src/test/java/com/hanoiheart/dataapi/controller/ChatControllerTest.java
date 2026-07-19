package com.hanoiheart.dataapi.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hanoiheart.dataapi.dto.ChatRequest;
import com.hanoiheart.dataapi.dto.ChatResponse;
import com.hanoiheart.dataapi.dto.PageResponse;
import com.hanoiheart.dataapi.exception.GlobalExceptionHandler;
import com.hanoiheart.dataapi.security.JwtUtil;
import com.hanoiheart.dataapi.service.ChatService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Slice test ({@link WebMvcTest}) cho {@link ChatController}.
 * Mock {@link ChatService}; import {@link GlobalExceptionHandler} để verify error envelope.
 */
@WebMvcTest(ChatController.class)
@AutoConfigureMockMvc(addFilters = false) // bỏ security filter chain — test controller contract thuần
@Import(GlobalExceptionHandler.class)
class ChatControllerTest {

    @Autowired
    private MockMvc mockMvc;
    @Autowired
    private ObjectMapper objectMapper;
    @MockBean
    private ChatService service;
    /**
     * Slice test pull SecurityAutoConfiguration (feat/web-api thêm Spring Security) →
     * SecurityFilterChain cần JwtAuthenticationFilter → JwtUtil. Mock để context start;
     * filter skip-safe khi không có Bearer header → @AuthenticationPrincipal=null (anon flow).
     */
    @MockBean
    private JwtUtil jwtUtil;

    @Test
    void postChat_validBody_returns200() throws Exception {
        UUID sessionId = UUID.randomUUID();
        when(service.handleMessage(any(ChatRequest.class), eq(null), eq(null)))
                .thenReturn(new ChatResponse(sessionId, "Chào bạn", List.of(), 0.9,
                        "GREETING", List.of(), null, false, Map.of()));

        mockMvc.perform(post("/data/v1/chat")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"text\":\"Xin chào\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.sessionId").value(sessionId.toString()))
                .andExpect(jsonPath("$.answer").value("Chào bạn"))
                .andExpect(jsonPath("$.intent").value("GREETING"))
                .andExpect(jsonPath("$.confidence").value(0.9));
    }

    @Test
    void postChat_blankText_returns400WithErrorEnvelope() throws Exception {
        mockMvc.perform(post("/data/v1/chat")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"text\":\"\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("bad_request"))
                .andExpect(jsonPath("$.error.message").exists());
    }

    @Test
    void postChat_missingBody_returns400() throws Exception {
        mockMvc.perform(post("/data/v1/chat")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("bad_request"));
    }

    @Test
    void postChat_invalidLang_returns400() throws Exception {
        mockMvc.perform(post("/data/v1/chat")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"text\":\"hi\",\"lang\":\"fr\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("bad_request"));
    }

    @Test
    void getSessions_withAnonToken_returns200PageResponse() throws Exception {
        UUID anonToken = UUID.randomUUID();
        when(service.listSessions(eq(anonToken.toString()), eq(0), eq(20)))
                .thenReturn(new PageResponse<>(0, 0, 20, 0, List.of()));

        mockMvc.perform(get("/data/v1/chat/sessions")
                        .header("X-Anon-Token", anonToken.toString()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").value(0))
                .andExpect(jsonPath("$.page").value(0))
                .andExpect(jsonPath("$.size").value(20));
    }

    @Test
    void getMessages_returns200PageResponse() throws Exception {
        UUID sessionId = UUID.randomUUID();
        when(service.listMessages(eq(sessionId), eq(0), eq(50)))
                .thenReturn(new PageResponse<>(0, 0, 50, 0, List.of()));

        mockMvc.perform(get("/data/v1/chat/sessions/{id}/messages", sessionId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").value(0));
    }
}

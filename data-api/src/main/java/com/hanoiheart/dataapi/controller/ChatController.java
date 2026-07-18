package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.ChatMessageDto;
import com.hanoiheart.dataapi.dto.ChatRequest;
import com.hanoiheart.dataapi.dto.ChatResponse;
import com.hanoiheart.dataapi.dto.ChatSessionDto;
import com.hanoiheart.dataapi.dto.PageResponse;
import com.hanoiheart.dataapi.service.ChatService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

/**
 * Chat BFF endpoints — 3 route per docs/07-api-design.md §B.5.
 *
 * <ul>
 *   <li>{@code POST /data/v1/chat} — gửi message</li>
 *   <li>{@code GET  /data/v1/chat/sessions} — list session của anonToken</li>
 *   <li>{@code GET  /data/v1/chat/sessions/{sessionId}/messages} — history 1 session</li>
 * </ul>
 *
 * <p>No auth (scope đề tài). {@code X-Anon-Token} header = pseudo-identity.
 */
@RestController
@RequestMapping("/data/v1/chat")
public class ChatController {

    private final ChatService service;

    public ChatController(ChatService service) {
        this.service = service;
    }

    @PostMapping
    public ChatResponse send(@Valid @RequestBody ChatRequest req,
                             @RequestHeader(name = "X-Anon-Token", required = false) String anonToken) {
        return service.handleMessage(req, anonToken);
    }

    @GetMapping("/sessions")
    public PageResponse<ChatSessionDto> listSessions(
            @RequestHeader(name = "X-Anon-Token", required = false) String anonToken,
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "20") int size) {
        return service.listSessions(anonToken, page, size);
    }

    @GetMapping("/sessions/{sessionId}/messages")
    public PageResponse<ChatMessageDto> listMessages(
            @PathVariable("sessionId") UUID sessionId,
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "50") int size) {
        return service.listMessages(sessionId, page, size);
    }
}

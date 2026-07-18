package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.ChatMessage;
import com.hanoiheart.dataapi.entity.ChatSession;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

/**
 * Repo cho {@link ChatMessage}.
 * History 1 session (ASC by createdAt). Count + last message để render list-sessions.
 */
public interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {

    Page<ChatMessage> findBySessionOrderByCreatedAtAsc(ChatSession session, Pageable pageable);

    long countBySession(ChatSession session);

    Optional<ChatMessage> findFirstBySessionOrderByCreatedAtDesc(ChatSession session);
}

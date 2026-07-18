package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.ChatSession;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

/**
 * Repo cho {@link ChatSession} (UUID id).
 * List theo anonToken, sort updatedAt desc (session gần nhất trước).
 */
public interface ChatSessionRepository extends JpaRepository<ChatSession, UUID> {

    Page<ChatSession> findByAnonTokenOrderByUpdatedAtDesc(UUID anonToken, Pageable pageable);
}

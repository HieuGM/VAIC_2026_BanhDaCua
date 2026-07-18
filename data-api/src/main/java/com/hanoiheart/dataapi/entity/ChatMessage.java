package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * Tin nhắn trong 1 phiên chat (role: user | assistant | system).
 * Bảng hospital.chat_messages — xem V10 migration.
 *
 * <p>Kế thừa {@link BaseEntity} (Long id bigserial). Tự thêm createdAt —
 * BaseEntity không có timestamp. jsonb qua {@link JdbcTypeCode}({@link SqlTypes#JSON}).
 */
@Entity
@Table(name = "chat_messages", schema = "hospital")
public class ChatMessage extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "session_id")
    private ChatSession session;

    /** user | assistant | system (DB CHECK constraint). */
    @Column(name = "role", nullable = false, length = 16)
    private String role;

    @Column(name = "content", nullable = false)
    private String content;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "citations")
    private List<Map<String, Object>> citations;

    @Column(name = "intent", length = 64)
    private String intent;

    @Column(name = "route", length = 64)
    private String route;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "guardrail_flags")
    private List<String> guardrailFlags;

    @Column(name = "confidence")
    private Float confidence;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    public ChatSession getSession() { return session; }
    public void setSession(ChatSession s) { this.session = s; }
    public String getRole() { return role; }
    public void setRole(String r) { this.role = r; }
    public String getContent() { return content; }
    public void setContent(String c) { this.content = c; }
    public List<Map<String, Object>> getCitations() { return citations; }
    public void setCitations(List<Map<String, Object>> c) { this.citations = c; }
    public String getIntent() { return intent; }
    public void setIntent(String i) { this.intent = i; }
    public String getRoute() { return route; }
    public void setRoute(String r) { this.route = r; }
    public List<String> getGuardrailFlags() { return guardrailFlags; }
    public void setGuardrailFlags(List<String> g) { this.guardrailFlags = g; }
    public Float getConfidence() { return confidence; }
    public void setConfidence(Float c) { this.confidence = c; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant c) { this.createdAt = c; }
}

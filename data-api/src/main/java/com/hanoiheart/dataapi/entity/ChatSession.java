package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.Instant;
import java.util.UUID;

/**
 * Phiên chat (UUID id do data-api sinh, không phải bigserial).
 * Bảng hospital.chat_sessions — xem V10 migration.
 *
 * <p>KHÔNG kế thừa {@link BaseEntity} (BaseEntity chỉ có Long id IDENTITY;
 * ChatSession cần UUID PK). Tự thêm createdAt/updatedAt qua Hibernate timestamp.
 */
@Entity
@Table(name = "chat_sessions", schema = "hospital")
public class ChatSession {

    @Id
    @Column(name = "id", columnDefinition = "uuid")
    private UUID id;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    @Column(name = "lang", length = 8)
    private String lang;

    @Column(name = "anon_token", columnDefinition = "uuid")
    private UUID anonToken;

    @Column(name = "expires_at")
    private Instant expiresAt;

    @Column(name = "deleted_at")
    private Instant deletedAt;

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant c) { this.createdAt = c; }
    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant u) { this.updatedAt = u; }
    public String getLang() { return lang; }
    public void setLang(String l) { this.lang = l; }
    public UUID getAnonToken() { return anonToken; }
    public void setAnonToken(UUID a) { this.anonToken = a; }
    public Instant getExpiresAt() { return expiresAt; }
    public void setExpiresAt(Instant e) { this.expiresAt = e; }
    public Instant getDeletedAt() { return deletedAt; }
    public void setDeletedAt(Instant d) { this.deletedAt = d; }
}

-- =====================================================================
-- V10__create_chat_sessions_and_messages.sql
-- Hanoi Heart Hospital — chat BFF persistence (schema `hospital`)
-- Per docs/07-api-design.md §B.5 + docs/06-database-design.md §4b + ADR-008.
-- =====================================================================

-- ---------- chat_sessions ----------
-- UUID PK do data-api sinh (KHÔNG phải bigserial) — phục vụ anonToken scope.
CREATE TABLE IF NOT EXISTS hospital.chat_sessions (
    id           UUID         PRIMARY KEY,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
    lang         VARCHAR(8),
    anon_token   UUID,
    expires_at   TIMESTAMPTZ,
    deleted_at   TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_anon_token
    ON hospital.chat_sessions (anon_token);

-- ---------- chat_messages ----------
-- bigserial PK (extends BaseEntity). session_id FK → chat_sessions(id) ON DELETE CASCADE.
CREATE TABLE IF NOT EXISTS hospital.chat_messages (
    id              BIGSERIAL    PRIMARY KEY,
    session_id      UUID         NOT NULL REFERENCES hospital.chat_sessions (id) ON DELETE CASCADE,
    role            VARCHAR(16)  NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content         TEXT         NOT NULL,
    citations       JSONB,
    intent          VARCHAR(64),
    route           VARCHAR(64),
    guardrail_flags JSONB,
    confidence      REAL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created
    ON hospital.chat_messages (session_id, created_at);

-- =====================================================================
-- V1__init_hospital.sql
-- Hanoi Heart Hospital — schema `hospital` (business master data)
-- Per docs/06-database-design.md §3.1 + §3.2 (excluding AI/KB tables).
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS hospital;

-- ---------- hospital_info ----------
CREATE TABLE IF NOT EXISTS hospital.hospital_info (
    id               BIGSERIAL PRIMARY KEY,
    name             TEXT        NOT NULL,
    short_name       TEXT,
    name_en          TEXT,
    slogan           TEXT,
    addresses        JSONB,
    hotline          TEXT,
    working_hours    JSONB,
    grade            TEXT,
    established_year INTEGER,
    website          TEXT
);

-- ---------- departments ----------
CREATE TABLE IF NOT EXISTS hospital.departments (
    id            BIGSERIAL PRIMARY KEY,
    code          VARCHAR(64)  NOT NULL UNIQUE,
    name          TEXT         NOT NULL,
    name_en       TEXT,
    description   TEXT,
    campus        TEXT,
    floor         TEXT,
    working_hours TEXT,
    phone         TEXT,
    sort_order    INTEGER,
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_departments_code ON hospital.departments (code);

-- ---------- doctors ----------
CREATE TABLE IF NOT EXISTS hospital.doctors (
    id            BIGSERIAL PRIMARY KEY,
    code          VARCHAR(128) NOT NULL UNIQUE,
    full_name     TEXT         NOT NULL,
    degree        VARCHAR(16),
    specialty     TEXT,
    title         TEXT,
    department_id BIGINT REFERENCES hospital.departments (id),
    bio           TEXT,
    avatar_url    TEXT,
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_doctors_department_id ON hospital.doctors (department_id);
CREATE INDEX IF NOT EXISTS idx_doctors_full_name    ON hospital.doctors (full_name);

-- ---------- doctor_schedules ----------
CREATE TABLE IF NOT EXISTS hospital.doctor_schedules (
    id            BIGSERIAL PRIMARY KEY,
    doctor_id     BIGINT NOT NULL REFERENCES hospital.doctors (id) ON DELETE CASCADE,
    department_id BIGINT REFERENCES hospital.departments (id),
    day_of_week   INTEGER,
    effective_date DATE,
    start_time    TIME,
    end_time      TIME,
    shift         VARCHAR(16),
    room          VARCHAR(64),
    note          TEXT,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_schedules_doctor_id ON hospital.doctor_schedules (doctor_id);
CREATE INDEX IF NOT EXISTS idx_schedules_date_range ON hospital.doctor_schedules (effective_date, doctor_id);
CREATE INDEX IF NOT EXISTS idx_schedules_department ON hospital.doctor_schedules (department_id);

-- ---------- services ----------
CREATE TABLE IF NOT EXISTS hospital.services (
    id            BIGSERIAL PRIMARY KEY,
    code          VARCHAR(64) UNIQUE,
    name          TEXT NOT NULL,
    category      VARCHAR(32),
    department_id BIGINT REFERENCES hospital.departments (id),
    description   TEXT,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_services_category_dept ON hospital.services (category, department_id);

-- ---------- service_prices ----------
CREATE TABLE IF NOT EXISTS hospital.service_prices (
    id             BIGSERIAL PRIMARY KEY,
    service_id     BIGINT NOT NULL REFERENCES hospital.services (id) ON DELETE CASCADE,
    price_vnd      BIGINT  NOT NULL,
    audience       VARCHAR(16) NOT NULL,
    campus         VARCHAR(16),
    effective_date DATE,
    source_url     TEXT,
    note           TEXT
);
CREATE INDEX IF NOT EXISTS idx_prices_service_id ON hospital.service_prices (service_id);
CREATE INDEX IF NOT EXISTS idx_prices_audience   ON hospital.service_prices (audience);

-- ---------- support_channels ----------
CREATE TABLE IF NOT EXISTS hospital.support_channels (
    id           BIGSERIAL PRIMARY KEY,
    channel_type VARCHAR(32) NOT NULL,
    label        TEXT        NOT NULL,
    url          TEXT,
    phone        VARCHAR(32),
    campus       TEXT,
    sort_order   INTEGER,
    is_active    BOOLEAN     NOT NULL DEFAULT TRUE
);

-- ---------- priority_groups ----------
CREATE TABLE IF NOT EXISTS hospital.priority_groups (
    id          BIGSERIAL PRIMARY KEY,
    code        VARCHAR(64) NOT NULL UNIQUE,
    name        TEXT        NOT NULL,
    description TEXT,
    sort_order  INTEGER
);

-- ---------- procedures ----------
CREATE TABLE IF NOT EXISTS hospital.procedures (
    id               BIGSERIAL PRIMARY KEY,
    code             VARCHAR(32) NOT NULL,
    title            TEXT        NOT NULL,
    step_no          INTEGER     NOT NULL,
    name             TEXT,
    description      TEXT,
    responsible_role TEXT,
    related_form     TEXT,
    source_doc       TEXT
);
CREATE INDEX IF NOT EXISTS idx_procedures_code_step ON hospital.procedures (code, step_no);

-- ---------- bhyt_policies ----------
CREATE TABLE IF NOT EXISTS hospital.bhyt_policies (
    id             BIGSERIAL PRIMARY KEY,
    code           VARCHAR(64) NOT NULL UNIQUE,
    title          TEXT        NOT NULL,
    category       VARCHAR(32),
    summary        TEXT,
    details_md     TEXT,
    source_url     TEXT,
    effective_date DATE
);
CREATE INDEX IF NOT EXISTS idx_bhyt_category ON hospital.bhyt_policies (category);

-- ---------- appointment_slots (mock) ----------
CREATE TABLE IF NOT EXISTS hospital.appointment_slots (
    id            BIGSERIAL PRIMARY KEY,
    doctor_id     BIGINT NOT NULL REFERENCES hospital.doctors (id) ON DELETE CASCADE,
    department_id BIGINT REFERENCES hospital.departments (id),
    date          DATE   NOT NULL,
    start_time    TIME   NOT NULL,
    end_time      TIME   NOT NULL,
    capacity      INTEGER NOT NULL,
    booked_count  INTEGER NOT NULL DEFAULT 0,
    is_available  BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_slots_doctor_date ON hospital.appointment_slots (doctor_id, date);
CREATE INDEX IF NOT EXISTS idx_slots_date        ON hospital.appointment_slots (date);

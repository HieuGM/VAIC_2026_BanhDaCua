-- =====================================================================
-- V11__create_users_and_appointments.sql
-- Hanoi Heart Hospital — Authentication & Appointment Business Data
-- Per Prompt.md: users, user_patient_links, patients_profile_cache,
-- appointments tables (schema `hospital`)
-- =====================================================================

-- ---------- users ----------
-- Chỉ phục vụ Authentication / Authorization.
-- Không lưu hồ sơ bệnh nhân, không lưu fhir_patient_id.
CREATE TABLE IF NOT EXISTS hospital.users (
    id              BIGSERIAL    PRIMARY KEY,
    phone           VARCHAR(20)  UNIQUE,
    email           VARCHAR(255) UNIQUE,
    password_hash   TEXT         NOT NULL,
    full_name       TEXT         NOT NULL,
    role            VARCHAR(32)  NOT NULL DEFAULT 'PATIENT',
    status          VARCHAR(32)  NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_users_email ON hospital.users (email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON hospital.users (phone);

-- ---------- user_patient_links ----------
-- Bảng quan trọng nhất: liên kết user (auth) ↔ FHIR Patient ID.
-- Frontend KHÔNG BAO GIỜ biết fhir_patient_id.
-- Backend tự lookup bảng này sau khi xác thực JWT.
CREATE TABLE IF NOT EXISTS hospital.user_patient_links (
    id               BIGSERIAL    PRIMARY KEY,
    user_id          BIGINT       NOT NULL REFERENCES hospital.users (id) ON DELETE CASCADE,
    fhir_patient_id  VARCHAR(255) NOT NULL,
    relationship     VARCHAR(64)  NOT NULL DEFAULT 'self',
    is_primary       BOOLEAN      NOT NULL DEFAULT TRUE,
    verified_at      TIMESTAMPTZ,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_upl_user_id ON hospital.user_patient_links (user_id);
CREATE INDEX IF NOT EXISTS idx_upl_fhir_patient ON hospital.user_patient_links (fhir_patient_id);

-- ---------- patients_profile_cache ----------
-- Chỉ là bảng cache phục vụ hiển thị (từ FHIR server).
-- Không lưu bệnh án, đơn thuốc, xét nghiệm, kết quả khám.
CREATE TABLE IF NOT EXISTS hospital.patients_profile_cache (
    id                  BIGSERIAL    PRIMARY KEY,
    fhir_patient_id     VARCHAR(255) NOT NULL UNIQUE,
    full_name           TEXT,
    phone               VARCHAR(20),
    date_of_birth       DATE,
    gender              VARCHAR(16),
    national_id_masked  VARCHAR(32),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ppc_fhir_patient ON hospital.patients_profile_cache (fhir_patient_id);

-- ---------- appointments ----------
-- Dữ liệu nghiệp vụ của Website (không lưu trong FHIR giai đoạn Hackathon).
-- user_id: ai đặt lịch (auth user).
-- fhir_patient_id: bệnh nhân được khám (backend tự lấy từ user_patient_links).
CREATE TABLE IF NOT EXISTS hospital.appointments (
    id               BIGSERIAL    PRIMARY KEY,
    user_id          BIGINT       NOT NULL REFERENCES hospital.users (id),
    fhir_patient_id  VARCHAR(255),
    doctor_id        BIGINT       REFERENCES hospital.doctors (id),
    department_id    BIGINT       REFERENCES hospital.departments (id),
    slot_id          BIGINT       REFERENCES hospital.appointment_slots (id),
    appointment_time TIMESTAMPTZ,
    reason           TEXT,
    status           VARCHAR(32)  NOT NULL DEFAULT 'PENDING',
    booking_channel  VARCHAR(32)  NOT NULL DEFAULT 'WEB',
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT chk_appointments_status CHECK (
        status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'NO_SHOW')
    )
);
CREATE INDEX IF NOT EXISTS idx_appointments_user_id  ON hospital.appointments (user_id);
CREATE INDEX IF NOT EXISTS idx_appointments_status   ON hospital.appointments (status);
CREATE INDEX IF NOT EXISTS idx_appointments_slot_id  ON hospital.appointments (slot_id);

-- ---------- alter appointment_slots ----------
-- Thêm schedule_id và cột status (nếu chưa có)
ALTER TABLE hospital.appointment_slots
    ADD COLUMN IF NOT EXISTS schedule_id BIGINT REFERENCES hospital.doctor_schedules (id),
    ADD COLUMN IF NOT EXISTS status      VARCHAR(32) NOT NULL DEFAULT 'AVAILABLE';

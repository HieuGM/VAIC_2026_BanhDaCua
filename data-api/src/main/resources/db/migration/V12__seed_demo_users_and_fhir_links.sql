-- =====================================================================
-- V12__seed_demo_users_and_fhir_links.sql
-- Hanoi Heart Hospital — Demo auth accounts + map → FHIR Patient
--
-- FHIR (HAPI) đã seed 20 bệnh nhân vn-patient-001..020 (medical data: labs,
-- meds, conditions). data-api KHÔNG seed lại medical data đó.
-- Cái thiếu là bản đồ authorization user_patient_links: "auth user nào được
-- xem FHIR patient nào". Migration này điền bảng đó cho demo accounts.
--
-- Chat wire (ChatService) lookup user_patient_links → gửi allowedPatientIds
-- cho chatbot; có link → userRole="USER" → chatbot trả data cá nhân.
--
-- pgcrypto bcrypt (gen_salt 'bf' rounds=10) → compatible Spring
-- BCryptPasswordEncoder mặc định (strength 10, $2a$). Login match bình thường.
-- Demo password (tất cả account): Demo@1234
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Bảo vệ trùng link (re-apply idempotent). Bảng đang trống → thêm an toàn.
ALTER TABLE hospital.user_patient_links
    ADD CONSTRAINT IF NOT EXISTS uq_upl_user_patient
    UNIQUE (user_id, fhir_patient_id);

-- ---------- Demo auth accounts (idempotent theo email UNIQUE) ----------
INSERT INTO hospital.users (phone, email, password_hash, full_name, role, status)
VALUES
    ('0900000001', 'demo@hanoiheart.vn',  crypt('Demo@1234', gen_salt('bf', 10)), 'Nguyễn Văn An',  'PATIENT', 'ACTIVE'),
    ('0900000002', 'demo2@hanoiheart.vn', crypt('Demo@1234', gen_salt('bf', 10)), 'Trần Thị Bình',  'PATIENT', 'ACTIVE'),
    ('0900000003', 'demo3@hanoiheart.vn', crypt('Demo@1234', gen_salt('bf', 10)), 'Lê Hoàng Cường', 'PATIENT', 'ACTIVE')
ON CONFLICT (email) DO NOTHING;

-- ---------- Links: demo user → FHIR patient (idempotent) ----------
INSERT INTO hospital.user_patient_links (user_id, fhir_patient_id, relationship, is_primary, verified_at)
SELECT id, 'vn-patient-001', 'self', TRUE, now() FROM hospital.users WHERE email = 'demo@hanoiheart.vn'
ON CONFLICT (user_id, fhir_patient_id) DO NOTHING;

INSERT INTO hospital.user_patient_links (user_id, fhir_patient_id, relationship, is_primary, verified_at)
SELECT id, 'vn-patient-002', 'self', TRUE, now() FROM hospital.users WHERE email = 'demo2@hanoiheart.vn'
ON CONFLICT (user_id, fhir_patient_id) DO NOTHING;

INSERT INTO hospital.user_patient_links (user_id, fhir_patient_id, relationship, is_primary, verified_at)
SELECT id, 'vn-patient-003', 'self', TRUE, now() FROM hospital.users WHERE email = 'demo3@hanoiheart.vn'
ON CONFLICT (user_id, fhir_patient_id) DO NOTHING;

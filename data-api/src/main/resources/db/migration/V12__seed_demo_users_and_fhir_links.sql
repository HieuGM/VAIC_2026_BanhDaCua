-- =====================================================================
-- V12__seed_demo_users_and_fhir_links.sql
-- Hanoi Heart Hospital — UNIQUE constraint cho user_patient_links
--
-- Mục đích DUY NHẤT của migration này: đảm bảo (user_id, fhir_patient_id)
-- unique → demo seed idempotent + chống link trùng runtime.
--
-- Demo auth accounts + map → FHIR Patient (vn-patient-001/002/003) giờ do
-- DemoUserSeeder (Spring ApplicationRunner, gated hanoi-heart.demo-seed.enabled)
-- tạo bằng BCryptPasswordEncoder thật. KHÔNG commit credential/hash trong SQL.
-- Lý do tách: hash bcrypt trong public repo → classifier block PR; password
-- demo phải đến từ env (DEMO_USER_PASSWORD) khi bật seed.
-- =====================================================================

-- Bảng đang trống (chưa có link) → thêm an toàn; IF NOT EXISTS idempotent.
ALTER TABLE hospital.user_patient_links
    ADD CONSTRAINT IF NOT EXISTS uq_upl_user_patient
    UNIQUE (user_id, fhir_patient_id);

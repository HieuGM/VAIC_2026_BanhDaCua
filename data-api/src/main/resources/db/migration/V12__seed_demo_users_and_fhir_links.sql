-- =====================================================================
-- V12__seed_demo_users_and_fhir_links.sql
-- Hanoi Heart Hospital — UNIQUE (user_id, fhir_patient_id) cho user_patient_links
--
-- Mục đích DUY NHẤT: đảm bảo (user_id, fhir_patient_id) unique → demo seed
-- idempotent + chống link trùng runtime.
--
-- Demo auth accounts + map → FHIR Patient (vn-patient-001/002/003) do
-- DemoUserSeeder (Spring ApplicationRunner, gated hanoi-heart.demo-seed.enabled)
-- tạo bằng BCryptPasswordEncoder thật. KHÔNG commit credential/hash trong SQL.
--
-- Dùng CREATE UNIQUE INDEX IF NOT EXISTS (KHÔNG dùng ALTER TABLE ADD CONSTRAINT
-- IF NOT EXISTS — syntax KHÔNG được PostgreSQL hỗ trợ, chỉ CREATE INDEX /
-- ADD COLUMN có IF NOT EXISTS). Flyway track migration → chạy 1 lần/DB, nhưng
-- IF NOT EXISTS giữ an toàn nếu index đã tồn tại từ lần chạy thủ công.
-- =====================================================================

CREATE UNIQUE INDEX IF NOT EXISTS uq_upl_user_patient_uid_pid
    ON hospital.user_patient_links (user_id, fhir_patient_id);

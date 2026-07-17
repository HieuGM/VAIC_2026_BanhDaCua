-- =====================================================================
-- V9__seed_hospital_info.sql
-- Sources:
--   data/raw/groundtruth_gioi_thieu_benh_vien_tim_ha_noi.txt (FACT_HOSPITAL_* / FACT_LEGAL_*)
--   data/raw/Huong_dan_dat_lich_kham_Benh_vien_Tim_Ha_Noi.txt (addresses, hotlines)
--   data/seed/crawled/working-hours.md (working hours per campus)
-- =====================================================================

-- hospital_info (single master row)
INSERT INTO hospital.hospital_info
    (name, short_name, name_en, slogan, addresses, hotline, working_hours, grade, established_year, website)
VALUES (
    'Bệnh viện Tim Hà Nội',
    'BV Tim Hà Nội',
    'Hanoi Heart Hospital',
    'Vì một trái tim khỏe',
    -- addresses (jsonb): CS1 + CS2
    '[
        {"campus":"CS1","label":"Cơ sở 1","address":"Số 92 Trần Hưng Đạo, phường Cửa Nam, Hoàn Kiếm, Hà Nội"},
        {"campus":"CS2","label":"Cơ sở 2","address":"Số 695 Lạc Long Quân, phường Tây Hồ, Hà Nội"}
    ]'::jsonb,
    '19001082',
    -- working_hours (jsonb)
    '{
        "hotline":   "24/7",
        "booking":   "8:00-16:00 Thứ 2 - Thứ 7 (nghỉ CN, Lễ, Tết)",
        "emergency": "24/7",
        "TN1_CS1":   {"Mon-Sat":"7:00/7:30 - 16:00/16:30", "Sun":"theo lịch bác sĩ trực"},
        "TN3_CS1":   {"Mon-Sat":"6:30/7:30 - 16:30", "Sun":"theo lịch bác sĩ trực"},
        "TN_CS2":    {"Mon-Sat":"7:00 - 16:30 (PK311: 7:30)", "Sun":"Nghỉ"},
        "PKDK_CS2":  {"Mon-Sat":"7:30 - 16:30", "Sun":"Nghỉ"}
    }'::jsonb,
    NULL,                  -- grade: not officially published (R1)
    2001,                  -- established per QĐ 6863/QĐ-UB ngày 15/11/2001
    'benhvientimhanoi.vn'
)
ON CONFLICT (id) DO NOTHING;

-- priority_groups placeholder: QĐ154 roster not yet published as structured data
-- (see data gap notes in docs/00-data-strategy.md §4). Seed a single anchor row.
INSERT INTO hospital.priority_groups (code, name, description, sort_order)
VALUES ('QD154-2024',
        'Đối tượng ưu tiên theo Quy định 154/QĐ-BV (12/01/2024)',
        'Danh mục chi tiết các nhóm đối tượng ưu tiên chưa được công bố dưới dạng văn bản cấu trúc trên trang chính thức. Cần xin văn bản Quy định 154/QĐ-BV từ bệnh viện để bổ sung.',
        1)
ON CONFLICT (code) DO NOTHING;

-- =====================================================================
-- Mock appointment_slots: synthesize from doctor_schedules for the next 7 days
-- (2026-07-20 .. 2026-07-26) so /data/v1/appointment-slots returns realistic
-- data in dev. Production booking = HIS via adapter (R6).
-- =====================================================================
INSERT INTO hospital.appointment_slots
    (doctor_id, department_id, date, start_time, end_time, capacity, booked_count, is_available)
SELECT
    ds.doctor_id,
    ds.department_id,
    ('2026-07-20'::date + (ds.day_of_week - 1))::date AS slot_date,
    ds.start_time,
    ds.end_time,
    10 AS capacity,
    0 AS booked_count,
    TRUE AS is_available
FROM hospital.doctor_schedules ds
WHERE ds.shift = 'fullday'
  AND ds.is_active = TRUE
  AND ds.day_of_week BETWEEN 1 AND 6
GROUP BY ds.doctor_id, ds.department_id, ds.day_of_week, ds.start_time, ds.end_time;

-- stats: 1 hospital_info row, 1 priority_group anchor, ~N mock appointment_slots

-- =====================================================================
-- V7__seed_support_channels.sql
-- Source: data/seed/crawled/channels.json (official URLs/phones, with Zalo).
-- =====================================================================

-- support_channels
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('hotline', 'Hotline chung Bệnh viện Tim Hà Nội (24/7)', NULL, '19001082', NULL, 1, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('hotline', 'Tư vấn khám chữa bệnh trong giờ hành chính - CS1 (Khu Tự nguyện)', NULL, '0869032338', NULL, 2, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('hotline', 'Phòng khám đa khoa (CS2) - giờ hành chính', NULL, '02437589090', NULL, 3, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('hotline', 'Phòng khám đa khoa (CS2) - giờ hành chính (thay thế)', NULL, '0961972097', NULL, 4, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('hotline', 'Tư vấn CS2 - trong giờ hành chính', NULL, '02439427791', NULL, 5, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('hotline', 'Tư vấn CS2 - 24/24h', NULL, '0969655335', NULL, 6, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('hotline', 'Trợ giúp/thiện nguyện - Công tác xã hội', NULL, '02439425880', NULL, 7, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('web', 'Web đặt lịch hẹn khám', 'https://benhvientimhanoi.vn/he-thong/hen-kham/index.html', NULL, NULL, 8, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('zalo', 'Zalo Mini App - Bệnh viện Tim Hà Nội Cơ sở 1', 'https://zalo.me/s/2972821668579995579/', NULL, NULL, 9, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('fanpage', 'Fanpage Facebook chính thức', 'https://facebook.com/BenhVienTimHaNoi.vn', NULL, NULL, 10, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('fanpage', 'Kênh YouTube chính thức', 'https://youtube.com/BenhVienTimHaNoi92TranHungDao/featured', NULL, NULL, 11, TRUE);
INSERT INTO hospital.support_channels (channel_type, label, url, phone, campus, sort_order, is_active) VALUES ('email', 'Email chăm sóc khách hàng', 'mailto:cskh@timhanoi.vn', NULL, NULL, 12, TRUE);

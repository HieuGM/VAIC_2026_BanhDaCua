import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  FaClipboardList, FaMoneyBillWave, FaCalendarCheck, FaUserMd,
  FaArrowRight, FaCheckCircle, FaClock, FaPhone, FaMapMarkerAlt,
  FaFileAlt, FaUser, FaHospital, FaRegClock, FaSearch
} from 'react-icons/fa';
import { bhytCategories, bhytPrices } from '../data/bhytPrices';
import './Guide.css';

const steps = [
  {
    num: 'Bước 1',
    role: 'Nhân viên tổ chăm sóc khách hàng – phòng Công tác xã hội',
    action: 'Nhận đặt lịch khám Tự nguyện 1 và tư vấn quy trình khám qua điện thoại, Website, Fanpage',
    desc: 'Bệnh nhân tiếp cận với thông tin đặt lịch trên giấy hẹn khám lại, bìa hồ sơ khám và trên các trang thông tin điện tử để đặt lịch đăng ký khám chọn bác sĩ tại khu khám Tự nguyện 1. Bệnh nhân đặt lịch được nhân viên tư vấn và thông báo thông tin gồm: mã đặt lịch (số thứ tự tiếp nhận), ngày khám và bác sĩ khám (nếu có). Bệnh nhân không đặt lịch đến lấy số trực tiếp tại cây lấy số tự động khu Tự nguyện 1.'
  },
  {
    num: 'Bước 2',
    role: 'Nhân viên tổ tư vấn và tiếp đón khám bệnh – Hướng dẫn viên',
    action: 'Bệnh nhân lấy số để tiếp nhận',
    desc: 'Bệnh nhân đã đặt lịch khi đến khám vào thẳng quầy tư vấn dành cho bệnh nhân đã đặt lịch trước và thông báo thông tin đã đặt khám cho nhân viên tư vấn để làm thủ tục đăng ký khám. Bệnh nhân không đặt lịch trước đến lấy số thứ tự tại cây lấy số tự động và ngồi chờ gọi theo số thứ tự đã lấy. Hướng dẫn viên hướng dẫn bệnh nhân khu vực lấy số và ổn định trật tự khu vực chờ.'
  },
  {
    num: 'Bước 3',
    role: 'Nhân viên tổ tư vấn và tiếp đón khám bệnh',
    action: 'Tiếp nhận thông tin đăng ký khám',
    desc: 'Bệnh nhân đăng ký khám bệnh gồm các đối tượng: có BHYT và không có BHYT, tái khám và khám mới. Bệnh nhân khám lần đầu khai thông tin vào phiếu đăng ký khám bệnh. Bệnh nhân BHYT xuất trình giấy chuyển viện, giấy hẹn khám lại, thẻ BHYT (hoặc hình ảnh BHYT trên ứng dụng VssID/CCCD gắn chíp có tích hợp thẻ BHYT), CCCD hoặc giấy tờ tùy thân có ảnh. Bệnh nhân có giấy chuyển tuyến mới được hướng dẫn ký cam kết đồng ý chi trả khoản chênh lệch giá dịch vụ y tế. Tên bác sĩ bệnh nhân chọn khám được ghi ngoài sổ khám. Đối tượng ưu tiên (theo quy định số 154) sẽ được đóng dấu "ưu tiên".'
  },
  {
    num: 'Bước 4',
    role: 'Nhân viên kế toán',
    action: 'Thực hiện thu phí và tiếp nhận BHYT (nếu có)',
    desc: 'Bệnh nhân có BHYT xuất trình các giấy tờ cần thiết. Nhân viên kế toán thông báo cho bệnh nhân phí khám, phí chênh lệch BHYT (nếu có) và thực hiện thu phí. Hướng dẫn bệnh nhân sang bàn đo dấu hiệu sinh tồn, chiều cao, cân nặng.'
  },
  {
    num: 'Bước 5',
    role: 'Nhân viên đo dấu hiệu sinh tồn',
    action: 'Thực hiện đo dấu hiệu sinh tồn, chiều cao, cân nặng cho bệnh nhân',
    desc: 'Tại bàn đo dấu hiệu sinh tồn, nhân viên thực hiện đo DHST, chiều cao, cân nặng và ghi vào phiếu tiếp nhận bệnh nhân. Ưu tiên thực hiện cho những bệnh nhân thuộc đối tượng ưu tiên. Các trường hợp bất thường sẽ báo bác sĩ hoặc chuyển cấp cứu kịp thời.'
  },
  {
    num: 'Bước 6',
    role: 'Điều dưỡng, Hướng dẫn viên tại bàn phân phòng - Trả kết quả',
    action: 'Thực hiện hướng dẫn bệnh nhân đi làm các chỉ định cận lâm sàng và tổng hợp kết quả trước khi phát số vào kết luận',
    desc: 'Điều dưỡng phát số phân phòng cho bệnh nhân chưa được khám và hướng dẫn về khu vực chờ. Với bệnh nhân đã có chỉ định cận lâm sàng, nhân viên ghi số thứ tự lên các phiếu chỉ định, tích các mục bệnh nhân phải làm vào phiếu hướng dẫn và đưa bệnh nhân đi làm các chỉ định (siêu âm tim, X-quang, điện tim, ABI, xét nghiệm máu...). Sau khi có đầy đủ kết quả, điều dưỡng kiểm soát kết quả, ghim vào hồ sơ khám và phát số hướng dẫn bệnh nhân vào phòng khám bác sĩ kết luận. Các trường hợp bất thường được xử lý hoặc chuyển cấp cứu.'
  },
  {
    num: 'Bước 7',
    role: 'Hướng dẫn viên hành lang',
    action: 'Hướng dẫn bệnh nhân và ổn định khu vực bệnh nhân ngồi chờ khám và chờ làm cận lâm sàng',
    desc: 'Hướng dẫn bệnh nhân ngồi ở sảnh chờ theo số phòng khám của bác sĩ đã đăng ký. Hướng dẫn bệnh nhân chú ý màn hình điện tử (hiển thị số thứ tự khám với 4 chữ số: số đầu là số phòng khám, các số tiếp theo là số thứ tự) và loa gọi số để vào phòng khám khi được gọi. Hướng dẫn viên quan sát bệnh nhân, báo lại điều dưỡng bàn Trả kết quả các trường hợp phát sinh hoặc bất thường.'
  },
  {
    num: 'Bước 8',
    role: 'Bác sĩ tại các phòng khám',
    action: 'Khám bệnh và kê đơn',
    desc: 'Bác sĩ gọi lần lượt bệnh nhân theo số khám trên phần mềm. Thực hiện khám bệnh, khai thác dịch tễ học, bệnh sử, triệu chứng cơ năng và thực thể. Giải thích tình trạng bệnh tật và sự cần thiết của các xét nghiệm cận lâm sàng. Kê đơn thuốc phù hợp, thông báo/tư vấn về loại thuốc và giá thuốc. Hướng dẫn cách sử dụng thuốc, chế độ dinh dưỡng, tập luyện và lịch khám lại.'
  }
];

const pricingPackages = [
  {
    name: 'Gói cơ bản',
    price: '350.000 đ',
    desc: 'Phù hợp cho khám định kỳ',
    color: '#2980b9',
    items: ['Khám tổng quát bác sĩ nội khoa', 'Điện tim (ECG)', 'Xét nghiệm máu cơ bản', 'Đo huyết áp, cân nặng', 'Tư vấn sức khoẻ'],
  },
  {
    name: 'Gói tim mạch',
    price: '950.000 đ',
    desc: 'Tầm soát tim mạch toàn diện',
    color: '#c0392b',
    recommended: true,
    items: ['Khám chuyên khoa tim mạch', 'Siêu âm tim (Echocardiogram)', 'Holter ECG 24 giờ', 'Xét nghiệm lipid máu đầy đủ', 'Chụp X-quang ngực thẳng', 'Tư vấn phòng ngừa tim mạch'],
  },
  {
    name: 'Gói VIP',
    price: '2.500.000 đ',
    desc: 'Trải nghiệm y tế cao cấp nhất',
    color: '#8e44ad',
    items: ['Tất cả dịch vụ gói tim mạch', 'Chụp CT mạch vành 256 lát', 'Xét nghiệm tim mạch nâng cao', 'Khám dinh dưỡng chuyên biệt', 'Phòng VIP riêng tư', 'Báo cáo sức khoẻ toàn diện'],
  },
];

// Doctors lists for Cơ sở 1 - Tự nguyện 1
const cs1_tn1_w1 = [
  { room: 'Phòng khám số 1', time: '7:30 - 16:30', t2: 'TS.BS Phạm Như Hùng', t3: 'TS.BS Phạm Như Hùng', t4: 'TS.BS Phạm Như Hùng', t5: 'TS.BS Phạm Như Hùng', t6: 'Nghỉ', t7: 'Nghỉ', cn: 'ThS.BS Trần Ngọc Dũng' },
  { room: 'Phòng khám số 2', time: '7:30 - 16:30', t2: 'TS.BS Vũ Quỳnh Nga', t3: 'TS.BS Vũ Quỳnh Nga', t4: 'TS.BS Vũ Quỳnh Nga', t5: 'TS.BS Vũ Quỳnh Nga', t6: 'Nghỉ', t7: 'ThS.BS Trần Sinh Cường', cn: 'Nghỉ' },
  { room: 'Phòng khám số 3', time: '7:00 - 16:30', t2: 'TS.BS Bùi Thị Thanh Hà', t3: 'TS.BS Nguyễn Xuân Tuấn', t4: 'TS.BS Bùi Thị Thanh Hà', t5: 'TS.BS Đinh Quang Huy', t6: 'TS.BS Bùi Thị Thanh Hà', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 4', time: '7:30 - 16:30', t2: 'Sáng: TS.BS Hoàng Văn / Chiều: BSCKII Phạm Thị An', t3: 'TS.BS Hà Mai Hương', t4: 'Sáng: TS.BS Hoàng Văn / Chiều: ThS.BS Nguyễn Thị Quỳnh Trang', t5: 'TS.BS Hà Mai Hương', t6: 'Sáng: TS.BS Hoàng Văn / Chiều: ThS.BS Trần Thị Ngọc Lan', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 5', time: '7:00 - 16:30', t2: 'TS.BS Trần Thị Ngọc Lan', t3: 'TS.BS Nguyễn Xuân Tú', t4: 'BSCKII Nguyễn Văn Dần', t5: 'Sáng: ThS.BS Nguyễn Thị Việt Nga / Chiều: TS.BS Ngô Văn Thanh', t6: 'TS.BS Hà Mai Hương', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 6', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Thị Việt Nga', t3: 'BSCKII Phạm Thị An', t4: 'TS.BS Nguyễn Thị Thu Thủy', t5: 'BSCKII Nguyễn Văn Thực', t6: 'ThS.BS Nguyễn Thị Quỳnh Trang', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 7', time: '7:00 - 16:00', t2: 'TS.BS Nguyễn Xuân Tuấn', t3: 'TS.BS Trần Thị An', t4: 'TS.BS Nguyễn Xuân Tú', t5: 'TS.BS Trần Thị Ngọc Lan', t6: 'BSCKII Vũ Thị Trang', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 8', time: '7:00 - 16:00', t2: 'TS.BS Đinh Quang Huy', t3: 'TS.BS Nguyễn Thị Thu Thủy', t4: 'Sáng: TS.BS Trần Thị An / Chiều: BSCKII Vũ Thị Trang', t5: 'Sáng: BS CKII Phạm Quang Huy / Chiều: ThS.BS Nguyễn Thị Quỳnh Trang', t6: 'TS.BS Trần Thị An', t7: 'Nghỉ', cn: 'Nghỉ' }
];

const cs1_tn1_w2 = [
  { room: 'Phòng khám số 1', time: '7:30 - 16:30', t2: 'TS.BS Phạm Như Hùng', t3: 'TS.BS Phạm Như Hùng', t4: 'Sáng: ThS.BS Nguyễn Thị Việt Nga / Chiều: BSCKII Vũ Thị Trang', t5: 'TS.BS Phạm Như Hùng', t6: 'Sáng: BSCKII Phạm Thị An / Chiều: BSCKII Nguyễn Văn Thực', t7: 'Nghỉ', cn: 'ThS.BS Nguyễn Đình Hồng Phúc' },
  { room: 'Phòng khám số 2', time: '7:30 - 16:30', t2: 'TS.BS Vũ Quỳnh Nga', t3: 'TS.BS Vũ Quỳnh Nga', t4: 'TS.BS Vũ Quỳnh Nga', t5: 'TS.BS Vũ Quỳnh Nga', t6: 'TS.BS Vũ Quỳnh Nga', t7: 'Nghỉ', cn: 'ThS.BS Nguyễn Thị Quỳnh Trang' },
  { room: 'Phòng khám số 3', time: '7:00 - 16:30', t2: 'TS.BS Bùi Thị Thanh Hà', t3: 'TS.BS Nguyễn Xuân Tuấn', t4: 'TS.BS Bùi Thị Thanh Hà', t5: 'TS.BS Đinh Quang Huy', t6: 'TS.BS Bùi Thị Thanh Hà', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 4', time: '7:30 - 16:30', t2: 'Sáng: TS.BS Hoàng Văn / Chiều: BSCKII Nguyễn Văn Dần', t3: 'TS.BS Hà Mai Hương', t4: 'Sáng: TS.BS Hoàng Văn / Chiều: ThS.BS Nguyễn Thị Quỳnh Trang', t5: 'TS.BS Hà Mai Hương', t6: 'Sáng: TS.BS Hoàng Văn / Chiều: TS.BS Nguyễn Thị Thu Thủy', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 5', time: '7:00 - 16:30', t2: 'TS.BS Trần Thị Ngọc Lan', t3: 'TS.BS Nguyễn Xuân Tú', t4: 'BSCKII Nguyễn Văn Dần', t5: 'Sáng: ThS.BS Nguyễn Thị Việt Nga / Chiều: TS.BS Ngô Văn Thanh', t6: 'TS.BS Hà Mai Hương', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 6', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Thị Việt Nga', t3: 'BSCKII Phạm Thị An', t4: 'TS.BS Nguyễn Thị Thu Thủy', t5: 'BSCKII Nguyễn Văn Thực', t6: 'BSCKII Vũ Thị Trang', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 7', time: '7:00 - 16:00', t2: 'Sáng: TS.BS Nguyễn Xuân Tuấn / Chiều: TS.BS Trần Thị Ngọc Lan', t3: 'TS.BS Trần Thị An', t4: 'TS.BS Nguyễn Xuân Tú', t5: 'TS.BS Trần Thị Ngọc Lan', t6: 'TS.BS Nguyễn Thị Quỳnh Trang', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 8', time: '7:00 - 16:00', t2: 'TS.BS Đinh Quang Huy', t3: 'TS.BS Nguyễn Thị Thu Thủy', t4: 'Sáng: TS.BS Trần Thị An / Chiều: TS.BS Nguyễn Xuân Tú', t5: 'TS.BS Trần Thị Ngọc Lan', t6: 'TS.BS Trần Thị An', t7: 'Nghỉ', cn: 'Nghỉ' }
];

const cs1_tn1_w3 = [
  { room: 'Phòng khám số 1', time: '7:30 - 16:30', t2: 'TS.BS Phạm Như Hùng', t3: 'TS.BS Phạm Như Hùng', t4: 'TS.BS Phạm Như Hùng', t5: 'TS.BS Nguyễn Thị Thu Thủy', t6: 'BSCKII Nguyễn Văn Thực', t7: 'Nghỉ', cn: 'ThS.BS Đăng Dương' },
  { room: 'Phòng khám số 2', time: '7:30 - 16:30', t2: 'TS.BS Vũ Quỳnh Nga', t3: 'TS.BS Vũ Quỳnh Nga', t4: 'TS.BS Vũ Quỳnh Nga', t5: 'TS.BS Vũ Quỳnh Nga', t6: 'TS.BS Vũ Quỳnh Nga', t7: 'Nghỉ', cn: 'ThS.BS Nguyễn Mai Hương' },
  { room: 'Phòng khám số 3', time: '7:00 - 16:30', t2: 'TS.BS Bùi Thị Thanh Hà', t3: 'TS.BS Nguyễn Xuân Tuấn', t4: 'TS.BS Bùi Thị Thanh Hà', t5: 'TS.BS Đinh Quang Huy', t6: 'TS.BS Bùi Thị Thanh Hà', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 4', time: '7:30 - 16:30', t2: 'Sáng: TS.BS Hoàng Văn / Chiều: BSCKII Nguyễn Văn Dần', t3: 'TS.BS Hà Mai Hương', t4: 'Sáng: TS.BS Hoàng Văn / Chiều: ThS.BS Nguyễn Thị Quỳnh Trang', t5: 'Sáng: TS.BS Hoàng Văn / Chiều: TS.BS Nguyễn Thị Thu Thủy', t6: 'TS.BS Hà Mai Hương', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 5', time: '7:00 - 16:30', t2: 'TS.BS Trần Thị Ngọc Lan', t3: 'TS.BS Nguyễn Xuân Tú', t4: 'BSCKII Nguyễn Văn Dần', t5: 'Sáng: ThS.BS Nguyễn Thị Việt Nga / Chiều: TS.BS Ngô Văn Thanh', t6: 'TS.BS Hà Mai Hương', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 6', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Thị Việt Nga', t3: 'BSCKII Phạm Thị An', t4: 'Sáng: TS.BS Nguyễn Thị Thu Thủy / Chiều: BSCKII Vũ Thị Trang', t5: 'BSCKII Nguyễn Văn Thực', t6: 'BSCKII Vũ Thị Trang', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 7', time: '7:00 - 16:00', t2: 'TS.BS Nguyễn Xuân Tuấn', t3: 'TS.BS Trần Thị An', t4: 'TS.BS Nguyễn Xuân Tú', t5: 'TS.BS Trần Thị Ngọc Lan', t6: 'TS.BS Nguyễn Thị Quỳnh Trang', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 8', time: '7:00 - 16:00', t2: 'TS.BS Đinh Quang Huy', t3: 'TS.BS Nguyễn Thị Thu Thủy', t4: 'Sáng: TS.BS Trần Thị An / Chiều: TS.BS Trần Thị Ngọc Lan', t5: 'BS CKII Phạm Quang Huy', t6: 'ThS.BS Nguyễn Thị Việt Nga', t7: 'Nghỉ', cn: 'Nghỉ' }
];

// Doctors lists for Cơ sở 1 - Tự nguyện 3
const cs1_tn3_w1 = [
  { room: 'Phòng khám số 1', time: '7:30 - 16:30', t2: 'ThS.BS Võ Thị Ngọc Anh', t3: 'ThS.BS Nguyễn Danh Sen', t4: 'ThS.BS Võ Thị Ngọc Anh', t5: 'ThS.BS Lê Thế Kiên', t6: 'BS CKII Trần Thị Thanh Hà', t7: 'ThS.BS Nguyễn Thế Nam Huy', cn: 'Nghỉ' },
  { room: 'Phòng khám số 2', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Xuân Tú', t3: 'BS Đinh Hải Nam', t4: 'ThS.BS. Phạm Đăng Anh', t5: 'Sáng: ThS.BS Trần Sinh Cường / Chiều: ThS.BS. Phạm Đăng Anh', t6: 'Sáng: BSCKII Phạm Thị An / Chiều: BSCKI Nguyễn Trung Hiếu', t7: 'BSCKI Nguyễn Trung Hiếu', cn: 'Nghỉ' },
  { room: 'Phòng khám số 3', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Toàn Thắng', t3: 'ThS. BS Trần Đắc Long', t4: 'ThS.BS Nguyễn Quốc Hùng', t5: 'ThS.BS Nguyễn Toàn Thắng', t6: 'BSCKI Đào Thị Thu Hà', t7: 'TS.BS Trần Thị Ngọc Lan', cn: 'Nghỉ' },
  { room: 'Phòng khám số 4', time: '7:30 - 16:30', t2: 'Sáng: ThS.BS Trần Sinh Cường / Chiều: BS Trần Thanh Hoa', t3: 'BS Trần Thanh Hoa', t4: 'Sáng: BSCKII Vũ Thị Trang / Chiều: ThS.BS Nguyễn Đình Hồng Phúc', t5: 'Sáng: ThS.BS Lê Thị Thảo / Chiều: ThS.BS Nguyễn Thị Minh Nguyệt', t6: 'Sáng: ThS.BS Nguyễn Phương Liên / Chiều: ThS.BS Lê Thị Thảo', t7: 'ThS.BS Lê Thế Kiên', cn: 'Nghỉ' },
  { room: 'Phòng khám số 5', time: '6:30 - 16:30', t2: 'BSCKII Nguyễn Văn Thực', t3: 'ThS.BS Nguyễn Thế Nam Huy', t4: 'ThS.BS Lê Quang Huy', t5: 'Sáng: ThS.BS Nguyễn Đình Hồng Phúc / Chiều: BS. Nguyễn Ngọc Tân', t6: 'ThS.BS Nguyễn Thế Nam Huy', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 6', time: '6:30 - 16:30', t2: 'Sáng: ThS.BS Lê Thị Thảo / Chiều: BS CKII Trần Thị Thanh Hà', t3: 'Sáng: ThS.BS Hoàng Minh Lợi / Chiều: ThS.BS Đỗ Thị Vân Anh', t4: 'Sáng: BS Trần Thanh Hoa / Chiều: BS Đinh Hải Nam', t5: 'Sáng: ThS.BS Nguyễn Danh Sen / Chiều: BSCKII Vũ Thị Trang', t6: 'BS Đinh Hải Nam', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 7', time: '6:30 - 16:30', t2: 'ThS.BS Phạm Văn Tùng', t3: 'ThS.BS Trần Sinh Cường', t4: 'Sáng: ThS.BS Lê Thị Thảo / Chiều: ThS.BS Nguyễn Phương Liên', t5: 'ThS.BS Nguyễn Xuân Tú', t6: 'ThS.BS Lê Thế Kiên', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 8', time: '7:30 - 16:30', t2: 'Sáng: ThS.BS Hoàng Minh Lợi / Chiều: ThS.BS Nguyễn Mai Hương', t3: 'ThS.BS Nguyễn Thị Minh Nguyệt', t4: 'Sáng: ThS.BS Phạm Văn Tùng / Chiều: BS Phạm Thị Hoa', t5: 'Sáng: ThS.BS Nguyễn Thị Quỳnh Trang / Chiều: ThS.BS Lê Quang Huy', t6: 'ThS.BS Nguyễn Xuân Tuấn', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 9', time: '7:30 - 16:30', t2: 'Sáng: ThS.BS Nguyễn Phương Liên / Chiều: TS.BS Ngô Văn Thanh', t3: 'ThS.BS Nguyễn Mai Hương', t4: 'Sáng: ThS.BS Nguyễn Thị Minh Nguyệt / Chiều: ThS.BS Phạm Văn Tùng', t5: 'ThS.BS Nguyễn Phương Liên', t6: 'Sáng: ThS.BS Nguyễn Thị Minh Nguyệt / Chiều: ThS.BS Trần Sinh Cường', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Tăng cường 1 (HC)', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Đình Hồng Phúc', t3: 'ThS.BS Phạm Văn Tùng', t4: 'BS Đinh Hải Nam', t5: 'ThS.BS Đỗ Thị Vân Anh', t6: 'BSCKI Nguyễn Trung Hiếu', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Tăng cường 2 (PK4)', time: '7:30 - 16:30', t2: 'Trống', t3: 'BSCKI Nguyễn Trung Hiếu', t4: 'Trống', t5: 'Trống', t6: 'Trống', t7: 'Nghỉ', cn: 'Nghỉ' }
];

const cs1_tn3_w2 = [
  { room: 'Phòng khám số 1', time: '7:30 - 16:30', t2: 'ThS.BS Võ Thị Ngọc Anh', t3: 'ThS.BS Nguyễn Danh Sen', t4: 'ThS.BS Phạm Văn Tùng', t5: 'ThS.BS Nguyễn Danh Sen', t6: 'BS CKII Trần Thị Thanh Hà', t7: 'ThS.BS Đăng Dương', cn: 'Nghỉ' },
  { room: 'Phòng khám số 2', time: '7:30 - 16:30', t2: 'Sáng: ThS.BS Nguyễn Xuân Tú / Chiều: BS CKII Trần Thị Thanh Hà', t3: 'Sáng: BSCKII Nguyễn Văn Dần / Chiều: ThS.BS Nguyễn Đình Hồng Phúc', t4: 'ThS.BS. Phạm Đăng Anh', t5: 'Sáng: BSCKI Nguyễn Trung Hiếu / Chiều: ThS.BS Nguyễn Phương Liên', t6: 'Sáng: ThS.BS Nguyễn Mai Hương / Chiều: ThS.BS Nguyễn Đình Hồng Phúc', t7: 'ThS.BS Lê Thế Kiên', cn: 'Nghỉ' },
  { room: 'Phòng khám số 3', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Quốc Hùng', t3: 'BSCKI Đào Thị Thu Hà', t4: 'ThS. BS Trần Đắc Long', t5: 'ThS.BS Nguyễn Toàn Thắng', t6: 'BSCKI Đào Thị Thu Hà', t7: 'ThS.BS Trần Sinh Cường', cn: 'Nghỉ' },
  { room: 'Phòng khám số 4', time: '7:30 - 16:30', t2: 'Sáng: ThS.BS Trần Sinh Cường / Chiều: BS. Nguyễn Ngọc Tân', t3: 'ThS.BS Nguyễn Mai Hương', t4: 'BS Đinh Hải Nam', t5: 'BS Trần Thanh Hoa', t6: 'Sáng: ThS.BS Phạm Văn Tùng / Chiều: BS Trần Thanh Hoa', t7: 'ThS.BS Lê Thị Thảo', cn: 'Nghỉ' },
  { room: 'Phòng khám số 5', time: '6:30 - 16:30', t2: 'BSCKII Nguyễn Văn Thực', t3: 'ThS.BS Nguyễn Thế Nam Huy', t4: 'ThS.BS Hoàng Minh Lợi', t5: 'Sáng: ThS.BS Trần Sinh Cường / Chiều: ThS.BS Lê Quang Huy', t6: 'ThS.BS Nguyễn Thế Nam Huy', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 6', time: '6:30 - 16:30', t2: 'ThS.BS Nguyễn Đình Hồng Phúc', t3: 'BS Đinh Hải Nam', t4: 'ThS.BS Đỗ Thị Vân Anh', t5: 'ThS.BS Nguyễn Đình Hồng Phúc', t6: 'Sáng: ThS.BS Lê Thế Kiên / Chiều: ThS.BS Nguyễn Phương Liên', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 7', time: '6:30 - 16:30', t2: 'ThS.BS Phạm Văn Tùng', t3: 'BS Trần Thanh Hoa', t4: 'ThS.BS Lê Thế Kiên', t5: 'ThS.BS Lê Thị Thảo', t6: 'BS Đinh Hải Nam', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 8', time: '7:30 - 16:30', t2: 'Sáng: ThS.BS Lê Quang Huy / Chiều: ThS.BS Ngọ Văn Thanh', t3: 'Sáng: BSCKII Vũ Thị Trang / Chiều: ThS.BS Trần Sinh Cường', t4: 'ThS.BS Trần Sinh Cường', t5: 'Sáng: ThS.BS Nguyễn Thị Minh Nguyệt / Chiều: BS. Nguyễn Ngọc Tân', t6: 'ThS.BS Nguyễn Xuân Tuấn', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 9', time: '7:30 - 16:30', t2: 'ThS.BS Lê Thị Thảo', t3: 'ThS.BS Đỗ Thị Vân Anh', t4: 'Sáng: ThS.BS Nguyễn Phương Liên / Chiều: BS Chu Thị Hằng', t5: 'BSCKII Nguyễn Văn Dần', t6: 'Sáng: BSCKII Nguyễn Văn Dần / Chiều: ThS.BS. Phạm Đăng Anh', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Tăng cường 1 (HC)', time: '7:30 - 16:30', t2: 'BS Trần Thanh Hoa', t3: 'Sáng: ThS.BS Hoàng Minh Lợi', t4: 'Sáng: ThS.BS Nguyễn Đình Hồng Phúc', t5: 'Sáng: ThS.BS Lê Thế Kiên', t6: 'Sáng: ThS.BS Hoàng Minh Lợi', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Tăng cường 2 (PK4)', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Phương Liên', t3: 'ThS.BS Lê Thị Kiến', t4: 'Trống', t5: 'Trống', t6: 'ThS.BS Trần Sinh Cường', t7: 'Nghỉ', cn: 'Nghỉ' }
];

const cs1_tn3_w3 = [
  { room: 'Phòng khám số 1', time: '7:30 - 16:30', t2: 'ThS.BS Võ Thị Ngọc Anh', t3: 'ThS.BS Nguyễn Danh Sen', t4: 'ThS.BS Võ Thị Ngọc Anh', t5: 'BS CKII Trần Thị Thanh Hà', t6: 'Sáng: ThS.BS Nguyễn Danh Sen / Chiều: ThS.BS Nguyễn Đình Hồng Phúc', t7: 'ThS.BS Nguyễn Đình Hồng Phúc', cn: 'Nghỉ' },
  { room: 'Phòng khám số 2', time: '7:30 - 16:30', t2: 'Sáng: ThS.BS Trần Sinh Cường / Chiều: BS CKII Trần Thị Thanh Hà', t3: 'Sáng: BSCKII Nguyễn Văn Dần / Chiều: ThS.BS Trần Sinh Cường', t4: 'Sáng: BSCKI Nguyễn Trung Hiếu / Chiều: ThS.BS. Phạm Đăng Anh', t5: 'Sáng: ThS.BS Nguyễn Thị Minh Nguyệt / Chiều: BS Trần Thanh Hoa', t6: 'BS CKII Phạm Quang Huy', t7: 'ThS.BS Phạm Văn Tùng', cn: 'Nghỉ' },
  { room: 'Phòng khám số 3', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Toàn Thắng', t3: 'ThS. BS Trần Đắc Long', t4: 'ThS.BS Nguyễn Quốc Hùng', t5: 'ThS.BS Nguyễn Toàn Thắng', t6: 'BSCKI Đào Thị Thu Hà', t7: 'ThS.BS Nguyễn Phương Liên', cn: 'Nghỉ' },
  { room: 'Phòng khám số 4', time: '7:30 - 16:30', t2: 'Sáng: ThS.BS Lê Quang Huy / Chiều: ThS.BS Lê Thị Thảo', t3: 'Sáng: ThS.BS Nguyễn Mai Hương / Chiều: ThS.BS Lê Thị Thảo', t4: 'Sáng: ThS.BS Nguyễn Phương Liên / Chiều: ThS.BS Nguyễn Đình Hồng Phúc', t5: 'ThS.BS Hoàng Minh Lợi', t6: 'Sáng: ThS.BS Lê Quang Huy / Chiều: BS Trần Thanh Hoa', t7: 'ThS.BS Lê Quang Huy', cn: 'Nghỉ' },
  { room: 'Phòng khám số 5', time: '6:30 - 16:30', t2: 'BSCKII Nguyễn Văn Thực', t3: 'ThS.BS Nguyễn Thế Nam Huy', t4: 'Sáng: ThS.BS Nguyễn Mai Hương / Chiều: BS. Nguyễn Ngọc Tân', t5: 'ThS.BS Hoàng Minh Lợi', t6: 'ThS.BS Nguyễn Thế Nam Huy', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 6', time: '6:30 - 16:30', t2: 'Sáng: ThS.BS Đỗ Thị Vân Anh / Chiều: ThS.BS Ngọ Văn Thanh', t3: 'ThS.BS Phạm Văn Tùng', t4: 'Sáng: ThS.BS Lê Thị Thảo / Chiều: BS. Nguyễn Ngọc Tân', t5: 'ThS.BS Trần Sinh Cường', t6: 'Sáng: ThS.BS Phạm Văn Tùng / Chiều: BS Đinh Hải Nam', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 7', time: '6:30 - 16:30', t2: 'Sáng: ThS.BS Lê Thế Kiên / Chiều: ThS.BS Nguyễn Đình Hồng Phúc', t3: 'BS Đinh Hải Nam', t4: 'BS Đinh Hải Nam', t5: 'ThS.BS Nguyễn Xuân Tú', t6: 'BSCKII Nguyễn Văn Dần', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 8', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Thị Quỳnh Trang', t3: 'BS Đinh Hải Nam', t4: 'Sáng: BSCKII Vũ Thị Trang / Chiều: BS Trần Thanh Hoa', t5: 'TS.BS Nguyễn Xuân Tuấn', t6: 'Không rõ', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Phòng khám số 9', time: '7:30 - 16:30', t2: 'Sáng: ThS.BS Nguyễn Thị Minh Nguyệt / Chiều: ThS.BS Nguyễn Phương Liên', t3: 'Sáng: ThS.BS Hoàng Minh Lợi / Chiều: ThS.BS Lê Quang Huy', t4: 'ThS.BS Phạm Văn Tùng', t5: 'Sáng: ThS.BS Lê Thế Kiên / Chiều: ThS.BS Nguyễn Phương Liên', t6: 'ThS.BS Lê Thế Kiên', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Tăng cường 1 (HC)', time: '7:30 - 16:30', t2: 'ThS.BS Nguyễn Đình Hồng Phúc', t3: 'Sáng: BS Trần Thanh Hoa', t4: 'ThS.BS Đỗ Thị Vân Anh', t5: 'ThS.BS Đỗ Thị Vân Anh', t6: 'ThS.BS Trần Sinh Cường', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Tăng cường 2 (PK4)', time: '7:30 - 16:30', t2: 'Trống', t3: 'Trống', t4: 'Trống', t5: 'Sáng: BSCKI Nguyễn Trung Hiếu', t6: 'ThS.BS Nguyễn Đình Hồng Phúc', t7: 'Nghỉ', cn: 'Nghỉ' }
];

// Doctors list for Cơ sở 2 - Tự nguyện
const cs2_tn_w1 = [
  { room: 'Phòng khám 306', time: '7:00 - 16:30', t2: 'BS.CKII Lê Thị Hoài Thu', t3: 'BS.CKII Lê Thị Hoài Thu', t4: 'BS.CKII Lê Thị Hoài Thu', t5: 'BS.CKII Lê Thị Hoài Thu', t6: 'BS.CKII Lê Thị Hoài Thu', t7: 'BS Nguyễn Đình Phúc', cn: 'Nghỉ' },
  { room: 'Phòng khám 309', time: '7:00 - 16:30', t2: 'ThS.Bs Nguyễn Duy Chinh', t3: 'ThS.Bs Nguyễn Duy Chinh', t4: 'ThS.Bs Nguyễn Duy Chinh', t5: 'ThS.Bs Nguyễn Duy Chinh', t6: 'ThS.Bs Nguyễn Duy Chinh', t7: 'BS Nguyễn Đình Phúc', cn: 'Nghỉ' },
  { room: 'Phòng khám 308', time: '7:00 - 16:30', t2: 'TS.Bs Trần Thị Linh Tú', t3: 'TS.Bs Trần Thị Linh Tú', t4: 'TS.Bs Trần Thị Linh Tú', t5: 'TS.Bs Trần Thị Linh Tú', t6: 'TS.Bs Trần Thị Linh Tú', t7: 'BS Nguyễn Đình Phúc', cn: 'Nghỉ' },
  { room: 'Phòng khám 310', time: '7:00 - 16:30', t2: 'TC', t3: 'TC', t4: 'TC', t5: 'TC', t6: 'TC', t7: 'BS Nguyễn Đình Phúc', cn: 'Nghỉ' },
  { room: 'Phòng khám 311', time: '7:30 - 16:30', t2: 'ThS.Bs Lê Thuý Ngọc', t3: 'ThS.Bs Lê Thuý Ngọc', t4: 'ThS.Bs Lê Thuý Ngọc', t5: 'ThS.Bs Lê Thuý Ngọc', t6: 'ThS.Bs Lê Thuý Ngọc', t7: 'BS Nguyễn Đình Phúc', cn: 'Nghỉ' }
];

const cs2_tn_w2 = [
  { room: 'Phòng khám 306', time: '7:00 - 16:30', t2: 'BS.CKII Lê Thị Hoài Thu', t3: 'BS.CKII Lê Thị Hoài Thu', t4: 'BS.CKII Lê Thị Hoài Thu', t5: 'BS.CKII Lê Thị Hoài Thu', t6: 'BS.CKII Lê Thị Hoài Thu', t7: 'Bs Phan Thành Nam', cn: 'Nghỉ' },
  { room: 'Phòng khám 309', time: '7:00 - 16:30', t2: 'ThS.Bs Nguyễn Duy Chinh', t3: 'ThS.Bs Nguyễn Duy Chinh', t4: 'ThS.Bs Nguyễn Duy Chinh', t5: 'ThS.Bs Nguyễn Duy Chinh', t6: 'ThS.Bs Nguyễn Duy Chinh', t7: 'Bs Phan Thành Nam', cn: 'Nghỉ' },
  { room: 'Phòng khám 308', time: '7:00 - 16:30', t2: 'Ts.Bs Trần Thị Linh Tú', t3: 'Ts.Bs Trần Thị Linh Tú', t4: 'Ts.Bs Trần Thị Linh Tú', t5: 'Ts.Bs Trần Thị Linh Tú', t6: 'Ts.Bs Trần Thị Linh Tú', t7: 'Bs Phan Thành Nam', cn: 'Nghỉ' },
  { room: 'Phòng khám 310', time: '7:00 - 16:30', t2: 'TC', t3: 'TC', t4: 'TC', t5: 'TC', t6: 'TC', t7: 'Bs Phan Thành Nam', cn: 'Nghỉ' },
  { room: 'Phòng khám 311', time: '7:30 - 16:30', t2: 'ThS.Bs Lê Thuý Ngọc', t3: 'ThS.Bs Lê Thuý Ngọc', t4: 'ThS.Bs Lê Thuý Ngọc', t5: 'ThS.Bs Lê Thuý Ngọc', t6: 'ThS.Bs Lê Thuý Ngọc', t7: 'Bs Phan Thành Nam', cn: 'Nghỉ' }
];

const cs2_tn_w3 = [
  { room: 'Phòng khám 306', time: '7:00 - 16:30', t2: 'BS.CKII Lê Thị Hoài Thu', t3: 'BS.CKII Lê Thị Hoài Thu', t4: 'BS.CKII Lê Thị Hoài Thu', t5: 'BS.CKII Lê Thị Hoài Thu', t6: 'BS.CKII Lê Thị Hoài Thu', t7: 'Bs Lê Thanh Nam', cn: 'Nghỉ' },
  { room: 'Phòng khám 309', time: '7:00 - 16:30', t2: 'Ths.Bs Nguyễn Duy Chinh', t3: 'Ths.Bs Nguyễn Duy Chinh', t4: 'Ths.Bs Nguyễn Duy Chinh', t5: 'Ths.Bs Nguyễn Duy Chinh', t6: 'Ths.Bs Nguyễn Duy Chinh', t7: 'Bs Lê Thanh Nam', cn: 'Nghỉ' },
  { room: 'Phòng khám 308', time: '7:00 - 16:30', t2: 'Ts.Bs Trần Thị Linh Tú', t3: 'Ts.Bs Trần Thị Linh Tú', t4: 'Ts.Bs Trần Thị Linh Tú', t5: 'Ts.Bs Trần Thị Linh Tú', t6: 'Ts.Bs Trần Thị Linh Tú', t7: 'Bs Lê Thanh Nam', cn: 'Nghỉ' },
  { room: 'Phòng khám 310', time: '7:00 - 16:30', t2: 'TC', t3: 'TC', t4: 'TC', t5: 'TC', t6: 'TC', t7: 'Bs Lê Thanh Nam', cn: 'Nghỉ' },
  { room: 'Phòng khám 311', time: '7:30 - 16:30', t2: 'Ths.Bs Lê Thuý Ngọc', t3: 'Ths.Bs Lê Thuý Ngọc', t4: 'Ths.Bs Lê Thuý Ngọc', t5: 'Ths.Bs Lê Thuý Ngọc', t6: 'Ths.Bs Lê Thuý Ngọc', t7: 'Bs Lê Thanh Nam', cn: 'Nghỉ' }
];

// Doctors list for Cơ sở 2 - Phòng khám đa khoa
const cs2_clinic_w1 = [
  { room: 'RHM (P401)', time: '7:30 - 16:30', t2: 'BS Nguyễn Thanh Trà', t3: 'BS Nguyễn Thanh Trà (khám tại CS1-15H)', t4: 'BS Nguyễn Thanh Trà', t5: 'BS Nguyễn Thanh Trà (khám tại CS1-15H)', t6: 'BS Nguyễn Thanh Trà', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'PHCN (P401)', time: '7:30 - 16:30', t2: 'BSNT. Trần Thị Quỳnh Nga', t3: 'BSNT. Trần Thị Quỳnh Nga', t4: 'BSNT. Trần Thị Quỳnh Nga', t5: 'BSNT. Trần Thị Quỳnh Nga', t6: 'Sáng: BSNT. Trần Thị Quỳnh Nga (Chiều nghỉ)', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'TMH (P402)', time: '7:30 - 16:30', t2: 'Trống', t3: 'Trống', t4: 'ThS.Bs Linh Thế Cường', t5: 'ThS.Bs Linh Thế Cường', t6: 'ThS.Bs Linh Thế Cường', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'PK Nhi (P402)', time: '7:30 - 16:30', t2: 'ThS.Bs Dương Thị Thúy Nga', t3: 'ThS.Bs Dương Thị Thúy Nga', t4: 'ThS.Bs Dương Thị Thúy Nga', t5: 'ThS.Bs Dương Thị Thúy Nga', t6: 'ThS.Bs Dương Thị Thúy Nga', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Da Liễu (P403)', time: '7:30 - 16:30', t2: 'ThsBs Nguyễn Thị Minh Hoa', t3: 'ThsBs Nguyễn Thị Minh Hoa', t4: 'ThsBs Nguyễn Thị Minh Hoa', t5: 'ThsBs Nguyễn Thị Minh Hoa', t6: 'ThsBs Nguyễn Thị Minh Hoa', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Sản-Phụ Khoa (P403)', time: '7:30 - 16:30', t2: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t3: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t4: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t5: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t6: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'YHCT (P404)', time: '7:30 - 16:30', t2: 'BSNT. Nguyễn Thị Thuận', t3: 'BSNT. Nguyễn Thị Thuận', t4: 'BSNT. Nguyễn Thị Thuận', t5: 'BSNT. Nguyễn Thị Thuận', t6: 'BSNT. Nguyễn Thị Thuận', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Nội Hô Hấp (P405.A)', time: '7:30 - 16:30', t2: 'ThS.BS Lại Thị Bạch Yến', t3: 'ThS.BS Lại Thị Bạch Yến', t4: 'ThS.BS Lại Thị Bạch Yến', t5: 'ThS.BS Lại Thị Bạch Yến', t6: 'ThS.BS Lại Thị Bạch Yến', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Nội CXK (P405.B)', time: '7:30 - 16:31', t2: 'ThS.BSNT Phạm Thị Oanh', t3: 'ThS.BSNT Phạm Thị Oanh', t4: 'ThS.BSNT Phạm Thị Oanh', t5: 'ThS.BSNT Phạm Thị Oanh', t6: 'ThS.BSNT Phạm Thị Oanh', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'PK NTM-NT (P405.C)', time: '7:30 - 16:30', t2: 'BS TMCH', t3: 'BS TMCH', t4: 'BS TMCH', t5: 'BS TMCH', t6: 'BS TMCH', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Mắt (P405.D)', time: '7:30 - 16:30', t2: 'BSCKI. Nguyễn Thị Huyền', t3: 'BSCKI. Nguyễn Thị Huyền', t4: 'BSCKI. Nguyễn Thị Huyền', t5: 'BSCKI. Nguyễn Thị Huyền', t6: 'BSCKI. Nguyễn Thị Huyền', t7: 'Nghỉ', cn: 'Nghỉ' }
];

const cs2_clinic_w2 = [
  { room: 'RHM (P401)', time: '7:30 - 16:30', t2: 'BS Nguyễn Thanh Trà', t3: 'BS Nguyễn Thanh Trà (khám tại CS1-15H)', t4: 'BS Nguyễn Thanh Trà', t5: 'BS Nguyễn Thanh Trà (khám tại CS1-15H)', t6: 'BS Nguyễn Thanh Trà', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'PHCN (P401)', time: '7:30 - 16:30', t2: 'BSNT. Trần Thị Quỳnh Nga', t3: 'BSNT. Trần Thị Quỳnh Nga', t4: 'BSNT. Trần Thị Quỳnh Nga', t5: 'BSNT. Trần Thị Quỳnh Nga', t6: 'Sáng: BSNT. Trần Thị Quỳnh Nga (Chiều nghỉ)', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'TMH (P402)', time: '7:30 - 16:30', t2: 'Nghỉ', t3: 'Nghỉ', t4: 'Nghỉ', t5: 'Nghỉ', t6: 'Nghỉ', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'PK Nhi (P402)', time: '7:30 - 16:30', t2: 'ThS.Bs Dương Thị Thúy Nga', t3: 'ThS.Bs Dương Thị Thúy Nga', t4: 'ThS.Bs Dương Thị Thúy Nga', t5: 'ThS.Bs Dương Thị Thúy Nga', t6: 'ThS.Bs Dương Thị Thúy Nga', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Da Liễu (P403)', time: '7:30 - 16:30', t2: 'ThsBs Nguyễn Thị Minh Hoa', t3: 'ThsBs Nguyễn Thị Minh Hoa', t4: 'ThsBs Nguyễn Thị Minh Hoa', t5: 'ThsBs Nguyễn Thị Minh Hoa', t6: 'ThsBs Nguyễn Thị Minh Hoa', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Sản-Phụ Khoa (P403)', time: '7:30 - 16:30', t2: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t3: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t4: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t5: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t6: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'YHCT (P404)', time: '7:30 - 16:30', t2: 'BSNT. Nguyễn Thị Thuận', t3: 'BSNT. Nguyễn Thị Thuận', t4: 'BSNT. Nguyễn Thị Thuận', t5: 'BSNT. Nguyễn Thị Thuận', t6: 'BSNT. Nguyễn Thị Thuận', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Nội Hô Hấp (P405.A)', time: '7:30 - 16:30', t2: 'ThS.BS Lại Thị Bạch Yến', t3: 'ThS.BS Lại Thị Bạch Yến', t4: 'ThS.BS Lại Thị Bạch Yến', t5: 'ThS.BS Lại Thị Bạch Yến', t6: 'Nghỉ', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Nội CXK (P405.B)', time: '7:30 - 16:31', t2: 'ThS.BSNT Phạm Thị Oanh', t3: 'ThS.BSNT Phạm Thị Oanh', t4: 'ThS.BSNT Phạm Thị Oanh', t5: 'ThS.BSNT Phạm Thị Oanh', t6: 'ThS.BSNT Phạm Thị Oanh', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'PK NTM-NT (P405.C)', time: '7:30 - 16:30', t2: 'BS TMCH', t3: 'BS TMCH', t4: 'BS TMCH', t5: 'BS TMCH', t6: 'BS TMCH', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Mắt (P405.D)', time: '7:30 - 16:30', t2: 'BSCKI. Nguyễn Thị Huyền', t3: 'BSCKI. Nguyễn Thị Huyền', t4: 'BSCKI. Nguyễn Thị Huyền', t5: 'BSCKI. Nguyễn Thị Huyền', t6: 'BSCKI. Nguyễn Thị Huyền', t7: 'Nghỉ', cn: 'Nghỉ' }
];

const cs2_clinic_w3 = [
  { room: 'RHM (P401)', time: '7:30 - 16:30', t2: 'BS Nguyễn Thanh Trà', t3: 'BS Nguyễn Thanh Trà (khám tại CS1-15H)', t4: 'BS Nguyễn Thanh Trà', t5: 'BS Nguyễn Thanh Trà (khám tại CS1-15H)', t6: 'BS Nguyễn Thanh Trà', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'PHCN (P401)', time: '7:30 - 16:30', t2: 'BSNT. Trần Thị Quỳnh Nga', t3: 'BSNT. Trần Thị Quỳnh Nga', t4: 'BSNT. Trần Thị Quỳnh Nga', t5: 'BSNT. Trần Thị Quỳnh Nga', t6: 'Sáng: BSNT. Trần Thị Quỳnh Nga (Chiều nghỉ)', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'TMH (P402)', time: '7:30 - 16:30', t2: 'ThS.Bs Linh Thế Cường', t3: 'ThS.Bs Linh Thế Cường', t4: 'ThS.Bs Linh Thế Cường', t5: 'ThS.Bs Linh Thế Cường', t6: 'ThS.Bs Linh Thế Cường', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'PK Nhi (P402)', time: '7:30 - 16:30', t2: 'ThS.Bs Dương Thị Thúy Nga', t3: 'ThS.Bs Dương Thị Thúy Nga', t4: 'ThS.Bs Dương Thị Thúy Nga', t5: 'ThS.Bs Dương Thị Thúy Nga', t6: 'ThS.Bs Dương Thị Thúy Nga', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Da Liễu (P403)', time: '7:30 - 16:30', t2: 'ThsBs Nguyễn Thị Minh Hoa', t3: 'ThsBs Nguyễn Thị Minh Hoa', t4: 'ThsBs Nguyễn Thị Minh Hoa', t5: 'ThsBs Nguyễn Thị Minh Hoa', t6: 'ThsBs Nguyễn Thị Minh Hoa', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Sản-Phụ Khoa (P403)', time: '7:30 - 16:30', t2: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t3: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t4: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t5: 'Sáng: BSCK II Nguyễn Thị Tuyết Mai', t6: 'Nghỉ', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'YHCT (P404)', time: '7:30 - 16:30', t2: 'BSNT. Nguyễn Thị Thuận', t3: 'BSNT. Nguyễn Thị Thuận', t4: 'BSNT. Nguyễn Thị Thuận', t5: 'BSNT. Nguyễn Thị Thuận', t6: 'BSNT. Nguyễn Thị Thuận', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Nội Hô Hấp (P405.A)', time: '7:30 - 16:30', t2: 'ThS.BS Lại Thị Bạch Yến', t3: 'ThS.BS Lại Thị Bạch Yến', t4: 'ThS.BS Lại Thị Bạch Yến', t5: 'ThS.BS Lại Thị Bạch Yến', t6: 'ThS.BS Lại Thị Bạch Yến', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Nội CXK (P405.B)', time: '7:30 - 16:31', t2: 'ThS.BSNT Phạm Thị Oanh', t3: 'ThS.BSNT Phạm Thị Oanh', t4: 'ThS.BSNT Phạm Thị Oanh', t5: 'ThS.BSNT Phạm Thị Oanh', t6: 'ThS.BSNT Phạm Thị Oanh', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'PK NTM-NT (P405.C)', time: '7:30 - 16:30', t2: 'BS TMCH', t3: 'BS TMCH', t4: 'BS TMCH', t5: 'BS TMCH', t6: 'BS TMCH', t7: 'Nghỉ', cn: 'Nghỉ' },
  { room: 'Mắt (P405.D)', time: '7:30 - 16:30', t2: 'BSCKI. Nguyễn Thị Huyền', t3: 'BSCKI. Nguyễn Thị Huyền', t4: 'BSCKI. Nguyễn Thị Huyền', t5: 'BSCKI. Nguyễn Thị Huyền', t6: 'BSCKI. Nguyễn Thị Huyền', t7: 'Nghỉ', cn: 'Nghỉ' }
];

const Guide = () => {
  const [activeTab, setActiveTab] = useState('process');
  const location = useLocation();

  // Filters for schedule widget
  const [branch, setBranch] = useState('cs1');
  const [area, setArea] = useState('tn1');
  const [week, setWeek] = useState('week1');

  // Filters for BHYT prices search
  const [priceType, setPriceType] = useState('voluntary'); // 'voluntary' or 'bhyt'
  const [bhytCat, setBhytCat] = useState('all');
  const [bhytSearch, setBhytSearch] = useState('');
  const [bhytPage, setBhytPage] = useState(1);

  const filteredBHYT = bhytPrices.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(bhytSearch.toLowerCase()) ||
                          item.code.toLowerCase().includes(bhytSearch.toLowerCase());
    const matchesCategory = bhytCat === 'all' || item.catId === Number(bhytCat);
    return matchesSearch && matchesCategory;
  });

  const PAGE_SIZE = 15;
  const totalBHYT = filteredBHYT.length;
  const totalPages = Math.ceil(totalBHYT / PAGE_SIZE) || 1;
  const displayedBHYT = filteredBHYT.slice((bhytPage - 1) * PAGE_SIZE, bhytPage * PAGE_SIZE);

  useEffect(() => {
    setBhytPage(1);
  }, [bhytCat, bhytSearch]);

  useEffect(() => {
    const hash = location.hash;
    if (hash) {
      const id = hash.slice(1);
      const exists = ['process', 'pricing', 'schedule', 'how-to-book'].includes(id);
      if (exists) {
        setActiveTab(id);
      }
    }
  }, [location.hash]);

  // Auto-adjust area selection when branch changes
  const handleBranchChange = (newBranch) => {
    setBranch(newBranch);
    setArea(newBranch === 'cs1' ? 'tn1' : 'tn');
  };

  const getFilteredData = () => {
    if (branch === 'cs1') {
      if (area === 'tn1') {
        if (week === 'week1') return cs1_tn1_w1;
        if (week === 'week2') return cs1_tn1_w2;
        return cs1_tn1_w3;
      } else {
        if (week === 'week1') return cs1_tn3_w1;
        if (week === 'week2') return cs1_tn3_w2;
        return cs1_tn3_w3;
      }
    } else {
      if (area === 'tn') {
        if (week === 'week1') return cs2_tn_w1;
        if (week === 'week2') return cs2_tn_w2;
        return cs2_tn_w3;
      } else {
        if (week === 'week1') return cs2_clinic_w1;
        if (week === 'week2') return cs2_clinic_w2;
        return cs2_clinic_w3;
      }
    }
  };

  const tabs = [
    { id: 'process', label: 'Quy trình khám', icon: <FaClipboardList /> },
    { id: 'pricing', label: 'Bảng giá', icon: <FaMoneyBillWave /> },
    { id: 'schedule', label: 'Lịch bác sĩ', icon: <FaUserMd /> },
    { id: 'how-to-book', label: 'Cách đặt lịch', icon: <FaCalendarCheck /> },
  ];

  const currentSchedule = getFilteredData();

  return (
    <div className="guide-page">
      {/* Page Hero */}
      <div className="page-hero">
        <div className="container">
          <div className="badge" style={{background:'rgba(255,255,255,0.15)', color:'#fff', border:'1px solid rgba(255,255,255,0.3)'}}>Hướng dẫn</div>
          <h1>Hướng dẫn khám bệnh</h1>
          <p>Thông tin đầy đủ để bạn có trải nghiệm khám bệnh thuận lợi nhất</p>
          <div className="breadcrumb">
            <a href="/">Trang chủ</a>
            <span className="sep">›</span>
            <span>Hướng dẫn khám bệnh</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="guide-tab-nav">
        <div className="container">
          <div className="guide-tabs">
            {tabs.map((t) => (
              <button
                key={t.id}
                className={`guide-tab ${activeTab === t.id ? 'active' : ''}`}
                onClick={() => setActiveTab(t.id)}
              >
                {t.icon} {t.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="guide-content">
        {/* PROCESS */}
        {activeTab === 'process' && (
          <section className="section" id="process">
            <div className="container">
              <div className="section-header">
                <div className="badge">Quy trình QT.25.01</div>
                <h2 className="section-title">Quy trình <span>khám chữa bệnh ngoại trú</span></h2>
                <div className="divider" />
                <p className="section-subtitle">Áp dụng cho mọi đối tượng bệnh nhân khám chữa bệnh ngoại trú tại Khu Tự nguyện 1 Cơ sở 1</p>
              </div>

              {/* Steps timeline list */}
              <div className="guide-process-list">
                {steps.map((step, i) => (
                  <div key={i} className="process-step-box">
                    <div className="step-badge-left">{step.num}</div>
                    <div className="step-content-right">
                      <div className="step-role"><FaUser /> <strong>Bộ phận phụ trách:</strong> {step.role}</div>
                      <div className="step-action"><FaCheckCircle /> <strong>Nội dung:</strong> {step.action}</div>
                      <div className="step-desc-p">{step.desc}</div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="guide-note" style={{marginTop:'3rem'}}>
                <FaClock className="note-icon" />
                <div>
                  <strong>Thông tin quy trình:</strong> Tài liệu Quy trình Đón tiếp Bệnh nhân Ngoại trú tại khu TN1 – CS1 mã số <strong>QT.25.01</strong>. Ban hành ngày 05/12/2024 (Lần thứ 07). Ký duyệt bởi Ban Giám đốc Bệnh viện Tim Hà Nội.
                </div>
              </div>
            </div>
          </section>
        )}

        {/* PRICING */}
        {activeTab === 'pricing' && (
          <section className="section" id="pricing">
            <div className="container">
              <div className="section-header">
                <h2 className="section-title">Bảng giá <span>dịch vụ</span></h2>
                <div className="divider" />
                <p className="section-subtitle">Công khai, minh bạch — Xem bảng giá các gói khám tự nguyện hoặc tra cứu danh mục BHYT</p>
              </div>

              {/* Sub-tab Selector */}
              <div className="price-type-selector" style={{display:'flex', justifyContent:'center', gap:'1.5rem', marginBottom:'3.5rem'}}>
                <button
                  className={`btn ${priceType === 'voluntary' ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setPriceType('voluntary')}
                  style={{borderRadius:'30px', padding:'1rem 2.5rem', fontSize:'1.45rem'}}
                >
                  Gói khám tự nguyện
                </button>
                <button
                  className={`btn ${priceType === 'bhyt' ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setPriceType('bhyt')}
                  style={{borderRadius:'30px', padding:'1rem 2.5rem', fontSize:'1.45rem'}}
                >
                  Danh mục & Giá BHYT
                </button>
              </div>

              {priceType === 'voluntary' ? (
                <>
                  <div className="pricing-grid">
                    {pricingPackages.map((pkg, i) => (
                      <div key={i} className={`pricing-card ${pkg.recommended ? 'recommended' : ''}`}>
                        {pkg.recommended && <div className="recommended-badge">Phổ biến nhất</div>}
                        <div className="pricing-header" style={{borderColor: pkg.color}}>
                          <h3 style={{color: pkg.color}}>{pkg.name}</h3>
                          <div className="pricing-price" style={{color: pkg.color}}>{pkg.price}</div>
                          <p>{pkg.desc}</p>
                        </div>
                        <ul className="pricing-items">
                          {pkg.items.map((item) => (
                            <li key={item}>
                              <FaCheckCircle style={{color: pkg.color}} />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                        <Link to="/booking" className="btn btn-primary" style={{width:'100%', justifyContent:'center'}}>
                          Đặt lịch gói này
                        </Link>
                      </div>
                    ))}
                  </div>
                  <p className="pricing-note">* Giá trên chưa bao gồm thuế VAT. Bệnh nhân có BHYT đúng tuyến được hưởng chính sách theo quy định của Nhà nước. Liên hệ 1800 6969 để biết thêm chi tiết.</p>
                </>
              ) : (
                <div className="bhyt-search-widget">
                  {/* Category select buttons */}
                  <div className="bhyt-cat-filters" style={{display:'flex', flexWrap:'wrap', gap:'1rem', justifyContent:'center', marginBottom:'2rem'}}>
                    <button
                      className={`btn btn-sm ${bhytCat === 'all' ? 'btn-primary' : 'btn-outline'}`}
                      onClick={() => setBhytCat('all')}
                      style={{borderRadius:'20px', fontSize:'1.3rem', padding:'0.6rem 1.6rem'}}
                    >
                      Tất cả danh mục
                    </button>
                    {bhytCategories.map((cat) => (
                      <button
                        key={cat.id}
                        className={`btn btn-sm ${bhytCat === String(cat.id) ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setBhytCat(String(cat.id))}
                        style={{
                          borderRadius:'20px',
                          fontSize:'1.3rem',
                          padding:'0.6rem 1.6rem',
                          borderColor: bhytCat === String(cat.id) ? cat.color : '',
                          background: bhytCat === String(cat.id) ? cat.color : '',
                          color: bhytCat === String(cat.id) ? '#fff' : ''
                        }}
                      >
                        {cat.name}
                      </button>
                    ))}
                  </div>

                  {/* Search input */}
                  <div className="bhyt-search-bar-wrap" style={{position:'relative', maxWidth:'500px', margin:'0 auto 2.5rem'}}>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Tìm theo tên dịch vụ hoặc mã tương đương..."
                      value={bhytSearch}
                      onChange={(e) => setBhytSearch(e.target.value)}
                      style={{
                        padding:'1.2rem 2rem 1.2rem 4.5rem',
                        fontSize:'1.4rem',
                        borderRadius:'30px',
                        border:'1px solid var(--border-color)',
                        width:'100%',
                        boxShadow:'var(--shadow-sm)'
                      }}
                    />
                    <FaSearch style={{position:'absolute', left:'1.8rem', top:'50%', transform:'translateY(-50%)', color:'var(--text-muted)'}} />
                  </div>

                  {/* Legal information notice */}
                  <div className="guide-note" style={{marginBottom:'2rem', background:'#eef7ff', borderColor:'#bfe0ff'}}>
                    <FaFileAlt className="note-icon" style={{color:'#1e88e5'}} />
                    <div>
                      <strong>Thông tin BHYT:</strong> Danh mục giá dịch vụ kỹ thuật áp dụng cho người bệnh có thẻ BHYT theo <strong>Thông tư số 22/2023/TT-BYT</strong> của Bộ Y tế hiện hành (Đơn vị tính: VNĐ). Đã hiển thị {totalBHYT} kết quả tìm được.
                    </div>
                  </div>

                  {/* Pricing table */}
                  <div className="schedule-table-wrap">
                    <table className="schedule-table">
                      <thead>
                        <tr>
                          <th style={{width:'80px'}}>STT</th>
                          <th style={{width:'180px'}}>Mã tương đương</th>
                          <th>Tên dịch vụ kỹ thuật</th>
                          <th style={{width:'180px'}}>Giá BHYT chi trả tối đa</th>
                          <th>Ghi chú</th>
                        </tr>
                      </thead>
                      <tbody>
                        {displayedBHYT.length > 0 ? (
                          displayedBHYT.map((row, idx) => {
                            const actualIdx = (bhytPage - 1) * PAGE_SIZE + idx + 1;
                            const category = bhytCategories.find(c => c.id === row.catId);
                            return (
                              <tr key={idx}>
                                <td>{actualIdx}</td>
                                <td style={{fontFamily:'monospace', fontWeight:600, color:'var(--text-muted)'}}>{row.code}</td>
                                <td style={{textAlign:'left', paddingLeft:'1.6rem', fontWeight:500, color:'var(--secondary)'}}>
                                  <span
                                    className="badge"
                                    style={{
                                      background: category ? category.color : '#7f8c8d',
                                      color:'#fff',
                                      fontSize:'1.1rem',
                                      marginRight:'0.8rem',
                                      padding:'0.2rem 0.6rem'
                                    }}
                                  >
                                    {category ? category.name : ''}
                                  </span>
                                  {row.name}
                                </td>
                                <td style={{fontWeight:700, color:'var(--primary)', fontSize:'1.45rem'}}>{row.price} đ</td>
                                <td style={{textAlign:'left', fontSize:'1.25rem', color:'var(--text-muted)', fontStyle:'italic'}}>{row.note || '—'}</td>
                              </tr>
                            );
                          })
                        ) : (
                          <tr>
                            <td colSpan="5" style={{padding:'3rem', color:'var(--text-muted)', fontSize:'1.45rem'}}>
                              Không tìm thấy kết quả nào khớp với từ khóa tìm kiếm.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination controls */}
                  {totalPages > 1 && (
                    <div className="pagination" style={{display:'flex', justifyContent:'center', alignItems:'center', gap:'1.5rem', marginTop:'2rem'}}>
                      <button
                        className="btn btn-outline"
                        onClick={() => setBhytPage(prev => Math.max(prev - 1, 1))}
                        disabled={bhytPage === 1}
                        style={{padding:'0.6rem 1.8rem', fontSize:'1.35rem', borderRadius:'20px'}}
                      >
                        Trang trước
                      </button>
                      <span style={{fontSize:'1.35rem', fontWeight:600, color:'var(--text-muted)'}}>
                        Trang {bhytPage} / {totalPages}
                      </span>
                      <button
                        className="btn btn-outline"
                        onClick={() => setBhytPage(prev => Math.min(prev + 1, totalPages))}
                        disabled={bhytPage === totalPages}
                        style={{padding:'0.6rem 1.8rem', fontSize:'1.35rem', borderRadius:'20px'}}
                      >
                        Trang sau
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </section>
        )}

        {/* SCHEDULE */}
        {activeTab === 'schedule' && (
          <section className="section" id="schedule">
            <div className="container">
              <div className="section-header">
                <div className="badge">Lịch khám bệnh 29/6/2026 - 19/7/2026</div>
                <h2 className="section-title">Lịch khám <span>Bác sĩ</span></h2>
                <div className="divider" />
                <p className="section-subtitle">Vui lòng sử dụng bộ lọc dưới đây để tìm lịch làm việc cụ thể tại các cơ sở</p>
              </div>

              {/* Schedule Widget Filters */}
              <div className="schedule-filter-widget">
                <div className="filter-group">
                  <label><FaMapMarkerAlt /> Chọn Cơ sở:</label>
                  <div className="filter-buttons">
                    <button className={branch === 'cs1' ? 'active' : ''} onClick={() => handleBranchChange('cs1')}>Cơ sở 1 (Trần Hưng Đạo)</button>
                    <button className={branch === 'cs2' ? 'active' : ''} onClick={() => handleBranchChange('cs2')}>Cơ sở 2 (Lạc Long Quân)</button>
                  </div>
                </div>

                <div className="filter-group">
                  <label><FaHospital /> Khu vực khám:</label>
                  <div className="filter-buttons">
                    {branch === 'cs1' ? (
                      <>
                        <button className={area === 'tn1' ? 'active' : ''} onClick={() => setArea('tn1')}>Khu Tự Nguyện 1</button>
                        <button className={area === 'tn3' ? 'active' : ''} onClick={() => setArea('tn3')}>Khu Tự Nguyện 3</button>
                      </>
                    ) : (
                      <>
                        <button className={area === 'tn' ? 'active' : ''} onClick={() => setArea('tn')}>Khu Tự Nguyện</button>
                        <button className={area === 'clinic' ? 'active' : ''} onClick={() => setArea('clinic')}>Phòng khám Đa khoa</button>
                      </>
                    )}
                  </div>
                </div>

                <div className="filter-group">
                  <label><FaClock /> Tuần khám:</label>
                  <div className="filter-buttons">
                    <button className={week === 'week1' ? 'active' : ''} onClick={() => setWeek('week1')}>Tuần 1 (29/06 - 05/07)</button>
                    <button className={week === 'week2' ? 'active' : ''} onClick={() => setWeek('week2')}>Tuần 2 (06/07 - 12/07)</button>
                    <button className={week === 'week3' ? 'active' : ''} onClick={() => setWeek('week3')}>Tuần 3 (13/07 - 19/07)</button>
                  </div>
                </div>
              </div>

              {/* Contact Info Header in schedule */}
              <div className="schedule-contact-banner">
                {branch === 'cs1' ? (
                  <p>
                    📞 <strong>Đặt lịch hẹn (24/24h):</strong> 1900.1082 | 📞 <strong>Tư vấn giờ hành chính:</strong> 0869.032.338
                  </p>
                ) : area === 'tn' ? (
                  <p>
                    📞 <strong>Đặt lịch hẹn:</strong> 1900.1082 | 📞 <strong>Tư vấn hành chính:</strong> 024.3942.7791 | 📞 <strong>Tư vấn 24/24h:</strong> 0969.655.335
                  </p>
                ) : (
                  <p>
                    📞 <strong>Điện thoại liên hệ PK Đa khoa:</strong> 0961.972.097 (Giờ hành chính Thứ 2 – Thứ 6)
                  </p>
                )}
              </div>

              {/* Schedule Table */}
              <div className="schedule-table-wrap">
                <table className="schedule-table">
                  <thead>
                    <tr>
                      <th>Phòng khám / Khoa</th>
                      <th>Giờ khám</th>
                      <th>Thứ 2</th>
                      <th>Thứ 3</th>
                      <th>Thứ 4</th>
                      <th>Thứ 5</th>
                      <th>Thứ 6</th>
                      <th>Thứ 7</th>
                      <th>Chủ Nhật</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentSchedule.map((row, i) => (
                      <tr key={i}>
                        <td className="dept-name">{row.room}</td>
                        <td className="time-cell"><FaRegClock /> {row.time}</td>
                        <td className={row.t2 === 'Nghỉ' || row.t2 === 'Trống' ? 'unavailable' : 'available'}>{row.t2}</td>
                        <td className={row.t3 === 'Nghỉ' || row.t3 === 'Trống' ? 'unavailable' : 'available'}>{row.t3}</td>
                        <td className={row.t4 === 'Nghỉ' || row.t4 === 'Trống' ? 'unavailable' : 'available'}>{row.t4}</td>
                        <td className={row.t5 === 'Nghỉ' || row.t5 === 'Trống' ? 'unavailable' : 'available'}>{row.t5}</td>
                        <td className={row.t6 === 'Nghỉ' || row.t6 === 'Trống' ? 'unavailable' : 'available'}>{row.t6}</td>
                        <td className={row.t7 === 'Nghỉ' || row.t7 === 'Trống' ? 'unavailable' : 'available'}>{row.t7}</td>
                        <td className={row.cn === 'Nghỉ' || row.cn === 'Trống' ? 'unavailable' : 'available'}>{row.cn}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="schedule-legend">
                <p><strong>Ghi chú từ bệnh viện:</strong></p>
                <ul>
                  <li><strong>TC:</strong> Bác sĩ tăng cường.</li>
                  <li><strong>SAT:</strong> Bác sĩ trực ngày Thứ 7.</li>
                  <li><strong>TN mức 3:</strong> Khám diện Tự nguyện mức 3.</li>
                  <li>Lịch khám trên có thể thay đổi trong các ngày lễ, Tết theo quy định của Bộ Y tế.</li>
                </ul>
              </div>
            </div>
          </section>
        )}

        {/* HOW TO BOOK */}
        {activeTab === 'how-to-book' && (
          <section className="section" id="how-to-book">
            <div className="container">
              <div className="section-header">
                <h2 className="section-title">Cách <span>đặt lịch</span> khám</h2>
                <div className="divider" />
                <p className="section-subtitle">3 cách đặt lịch nhanh chóng và tiện lợi</p>
              </div>
              <div className="book-methods-grid">
                <div className="book-method">
                  <div className="book-method-icon" style={{background:'#e8f5e9', color:'#27ae60'}}><FaCalendarCheck /></div>
                  <h3>Đặt lịch trực tuyến</h3>
                  <p>Truy cập trang Đặt lịch khám, điền thông tin, chọn khoa và bác sĩ, chọn ngày giờ phù hợp. Xác nhận qua email/SMS.</p>
                  <Link to="/booking" className="btn btn-primary">Đặt lịch ngay <FaArrowRight /></Link>
                </div>
                <div className="book-method">
                  <div className="book-method-icon" style={{background:'#fff3e0', color:'#e67e22'}}><FaPhone /></div>
                  <h3>Gọi hotline</h3>
                  <p>Gọi trực tiếp đường dây nóng <strong>1900 1082</strong> (miễn phí, hoạt động 07:00 – 20:00 từ Thứ 2 – Thứ 7). Nhân viên sẽ hỗ trợ đặt lịch.</p>
                  <a href="tel:19001082" className="btn btn-outline">Gọi ngay 1900 1082</a>
                </div>
                <div className="book-method">
                  <div className="book-method-icon" style={{background:'#fce4ec', color:'#c0392b'}}><FaUserMd /></div>
                  <h3>Đến trực tiếp</h3>
                  <p>Đến Phòng Tiếp nhận tại tầng 1, mang theo CCCD/Hộ chiếu. Nhân viên sẽ hướng dẫn đăng ký khám và xếp lịch cho bạn.</p>
                  <a href="https://maps.google.com" target="_blank" rel="noreferrer" className="btn btn-outline">Xem bản đồ</a>
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default Guide;

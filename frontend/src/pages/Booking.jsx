import React, { useState } from 'react';
import { FaCalendarAlt, FaUser, FaPhone, FaEnvelope, FaHeartbeat, FaNotesMedical, FaClock } from 'react-icons/fa';
import './Booking.css';

const Booking = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    email: '',
    date: '',
    timeSlot: '',
    department: '',
    doctor: '',
    notes: ''
  });
  
  const [submitted, setSubmitted] = useState(false);

  const departments = [
    'Khoa khám bệnh tự nguyện',
    'Chăm sóc mạch vành',
    'Khoa dược & hiệu thuốc',
    'Khám sức khoẻ tổng quát',
    'Chăm sóc tại nhà'
  ];

  const doctors = [
    'GS.TS. Nguyễn Lân Việt',
    'PGS.TS. Trần Văn Hùng',
    'TS.BS. Lê Thị Minh',
    'BS.CKII. Phạm Quốc Bảo',
    'TS.BS. Hoàng Thị Lan',
    'BS.CKI. Đỗ Minh Tâm'
  ];

  const timeSlots = [
    '07:30 – 09:00',
    '09:00 – 10:30',
    '10:30 – 12:00',
    '13:30 – 15:00',
    '15:00 – 16:30'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Simulate API submission
    setSubmitted(true);
  };

  return (
    <div className="booking-page">
      {/* Page Hero */}
      <div className="page-hero">
        <div className="container">
          <div className="badge" style={{background:'rgba(255,255,255,0.15)', color:'#fff', border:'1px solid rgba(255,255,255,0.3)'}}>Đặt lịch hẹn</div>
          <h1>Đặt lịch khám bệnh</h1>
          <p>Điền thông tin của bạn để đặt lịch hẹn khám tim mạch nhanh chóng</p>
          <div className="breadcrumb">
            <a href="/">Trang chủ</a>
            <span className="sep">›</span>
            <span>Đặt lịch khám bệnh</span>
          </div>
        </div>
      </div>

      <section className="section booking-section">
        <div className="container booking-container">
          <div className="booking-info-panel">
            <div className="badge">Liên hệ & Hỗ trợ</div>
            <h2>Tại sao nên đặt lịch trước?</h2>
            <div className="divider" style={{margin: '1.6rem 0'}} />
            <p className="booking-info-desc">
              Việc đặt lịch khám trước giúp Bệnh viện Tim Hà Nội sắp xếp nhân lực tốt nhất và giảm thiểu tối đa thời gian chờ đợi của quý bệnh nhân.
            </p>

            <div className="info-cards">
              <div className="info-card-item">
                <FaClock className="info-card-icon" />
                <div>
                  <h4>Tiết kiệm thời gian</h4>
                  <p>Giảm thiểu thời gian làm thủ tục và chờ đợi tại bệnh viện.</p>
                </div>
              </div>
              <div className="info-card-item">
                <FaUser className="info-card-icon" />
                <div>
                  <h4>Chủ động chọn bác sĩ</h4>
                  <p>Lựa chọn bác sĩ chuyên khoa bạn mong muốn thăm khám.</p>
                </div>
              </div>
              <div className="info-card-item">
                <FaCalendarAlt className="info-card-icon" />
                <div>
                  <h4>Quản lý lịch hẹn</h4>
                  <p>Nhận thông báo xác nhận và nhắc nhở lịch hẹn qua email/SMS.</p>
                </div>
              </div>
            </div>

            <div className="booking-hotline-box">
              <p>Hỗ trợ khẩn cấp hoặc đặt lịch qua điện thoại:</p>
              <a href="tel:18006969" className="booking-hotline-btn">
                <FaPhone /> Hotline: 1800 6969
              </a>
            </div>
          </div>

          <div className="booking-form-panel card">
            {submitted ? (
              <div className="booking-success-message">
                <div className="success-icon-wrap">
                  <FaHeartbeat />
                </div>
                <h3>Đặt lịch thành công!</h3>
                <p>Cảm ơn quý khách <strong>{formData.fullName}</strong> đã đăng ký khám bệnh.</p>
                <div className="success-details">
                  <p><strong>Chuyên khoa:</strong> {formData.department}</p>
                  {formData.doctor && <p><strong>Bác sĩ:</strong> {formData.doctor}</p>}
                  <p><strong>Thời gian:</strong> {formData.timeSlot} - {formData.date}</p>
                </div>
                <p className="success-note">
                  Mã số lịch hẹn và hướng dẫn chi tiết đã được gửi đến SĐT <strong>{formData.phone}</strong> và Email <strong>{formData.email}</strong>. Quý khách vui lòng đến trước giờ hẹn 15 phút để hoàn tất thủ tục khám.
                </p>
                <button className="btn btn-primary" onClick={() => setSubmitted(false)}>
                  Đặt lịch hẹn mới
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="booking-form">
                <h3>Phiếu đăng ký khám bệnh</h3>
                <p className="form-subtitle">Quý bệnh nhân vui lòng điền đầy đủ các thông tin dưới đây</p>
                
                <div className="form-group">
                  <label htmlFor="fullName"><FaUser /> Họ và tên bệnh nhân <span className="required">*</span></label>
                  <input
                    type="text"
                    id="fullName"
                    name="fullName"
                    placeholder="Ví dụ: Nguyễn Văn A"
                    value={formData.fullName}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="phone"><FaPhone /> Số điện thoại <span className="required">*</span></label>
                    <input
                      type="tel"
                      id="phone"
                      name="phone"
                      placeholder="Ví dụ: 0912345678"
                      value={formData.phone}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="email"><FaEnvelope /> Địa chỉ Email</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      placeholder="Ví dụ: nguyenvala@gmail.com"
                      value={formData.email}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="department"><FaNotesMedical /> Chọn chuyên khoa <span className="required">*</span></label>
                    <select
                      id="department"
                      name="department"
                      value={formData.department}
                      onChange={handleChange}
                      required
                    >
                      <option value="">-- Chọn chuyên khoa --</option>
                      {departments.map((dept, i) => (
                        <option key={i} value={dept}>{dept}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label htmlFor="doctor"><FaUser /> Bác sĩ mong muốn</label>
                    <select
                      id="doctor"
                      name="doctor"
                      value={formData.doctor}
                      onChange={handleChange}
                    >
                      <option value="">-- Chọn bác sĩ (Không bắt buộc) --</option>
                      {doctors.map((doc, i) => (
                        <option key={i} value={doc}>{doc}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="date"><FaCalendarAlt /> Ngày khám <span className="required">*</span></label>
                    <input
                      type="date"
                      id="date"
                      name="date"
                      value={formData.date}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="timeSlot"><FaClock /> Khung giờ <span className="required">*</span></label>
                    <select
                      id="timeSlot"
                      name="timeSlot"
                      value={formData.timeSlot}
                      onChange={handleChange}
                      required
                    >
                      <option value="">-- Chọn khung giờ --</option>
                      {timeSlots.map((slot, i) => (
                        <option key={i} value={slot}>{slot}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="notes"><FaNotesMedical /> Triệu chứng lâm sàng / Ghi chú</label>
                  <textarea
                    id="notes"
                    name="notes"
                    rows="3"
                    placeholder="Mô tả ngắn gọn tình trạng sức khoẻ hoặc yêu cầu đặc biệt của bạn..."
                    value={formData.notes}
                    onChange={handleChange}
                  ></textarea>
                </div>

                <button type="submit" className="btn btn-primary form-submit-btn">
                  Xác nhận đặt lịch khám
                </button>
              </form>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Booking;

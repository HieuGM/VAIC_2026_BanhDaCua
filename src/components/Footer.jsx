import React from 'react';
import { Link } from 'react-router-dom';
import { FaPhone, FaEnvelope, FaMapMarkerAlt, FaClock, FaFacebook, FaYoutube, FaLinkedin } from 'react-icons/fa';
import logoImg from '../image/logo.png';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      {/* Main Footer */}
      <div className="footer-main">
        <div className="container footer-grid">
          {/* Brand */}
          <div className="footer-brand">
            <Link to="/" className="footer-logo">
              <img src={logoImg} alt="Bệnh viện tim Hà Nội" className="logo-image-file" />
              <div className="logo-text">
                <span className="footer-logo-name">Bệnh viện tim Hà Nội</span>
                <span className="footer-logo-slogan">Vì một trái tim khoẻ mạnh</span>
              </div>
            </Link>
            <p className="footer-desc">
              Bệnh viện Tim Hà Nội là cơ sở y tế chuyên khoa tim mạch hàng đầu, cung cấp dịch vụ chẩn đoán và điều trị bệnh lý tim mạch tiên tiến nhất.
            </p>
            <div className="footer-socials">
              <a href="#" aria-label="Facebook" className="social-link"><FaFacebook /></a>
              <a href="#" aria-label="Youtube" className="social-link"><FaYoutube /></a>
              <a href="#" aria-label="LinkedIn" className="social-link"><FaLinkedin /></a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="footer-col">
            <h4 className="footer-col-title">Điều hướng nhanh</h4>
            <ul className="footer-links">
              {[
                { to: '/', label: 'Trang chủ' },
                { to: '/about', label: 'Giới thiệu' },
                { to: '/services', label: 'Dịch vụ' },
                { to: '/guide', label: 'Hướng dẫn khám bệnh' },
                { to: '/booking', label: 'Đặt lịch khám' },
              ].map((link) => (
                <li key={link.to}>
                  <Link to={link.to} className="footer-link">
                    <i className="fas fa-chevron-right" /> {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Services */}
          <div className="footer-col">
            <h4 className="footer-col-title">Dịch vụ</h4>
            <ul className="footer-links">
              {[
                'Khoa khám bệnh tự nguyện',
                'Chăm sóc mạch vành',
                'Khoa dược & hiệu thuốc',
                'Khám sức khoẻ tổng quát',
                'Chăm sóc tại nhà',
              ].map((s) => (
                <li key={s}>
                  <Link to="/services" className="footer-link">
                    <i className="fas fa-chevron-right" /> {s}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div className="footer-col">
            <h4 className="footer-col-title">Liên hệ</h4>
            <ul className="footer-contact-list">
              <li>
                <FaMapMarkerAlt className="contact-icon" />
                <span>92 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội</span>
              </li>
              <li>
                <FaPhone className="contact-icon" />
                <span>1800 6969 (Miễn phí)</span>
              </li>
              <li>
                <FaEnvelope className="contact-icon" />
                <span>info@bvtimhanoi.vn</span>
              </li>
              <li>
                <FaClock className="contact-icon" />
                <span>Thứ 2 – Thứ 7: 07:00 – 17:00</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom */}
      <div className="footer-bottom">
        <div className="container footer-bottom-inner">
          <p>© 2025 Bệnh viện Tim Hà Nội. Bảo lưu mọi quyền.</p>
          <div className="footer-bottom-links">
            <a href="#">Chính sách bảo mật</a>
            <a href="#">Điều khoản sử dụng</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

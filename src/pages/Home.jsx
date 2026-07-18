import React from 'react';
import { Link } from 'react-router-dom';
import {
  FaHeartbeat, FaArrowRight, FaHospital, FaUserMd, FaStethoscope,
  FaCalendarCheck, FaHome, FaFlask, FaPhone, FaStar, FaBell, FaCheckCircle
} from 'react-icons/fa';
import img1 from '../image/img1.jpg';
import img2 from '../image/phauthuatim_nguoilon.jpg';
import img3 from '../image/img3.jpg';
import blog1 from '../image/blog1.jpg';
import blog2 from '../image/blog2.jpg';
import blog3 from '../image/blog3.jpg';
import homeImg from '../image/hoisuctichcuc.jpg';
import './Home.css';

const stats = [
  { icon: <FaUserMd />, value: '200+', label: 'Bác sĩ chuyên khoa' },
  { icon: <FaHospital />, value: '50.000+', label: 'Bệnh nhân mỗi năm' },
  { icon: <FaHeartbeat />, value: '30+', label: 'Năm kinh nghiệm' },
  { icon: <FaStar />, value: '98%', label: 'Bệnh nhân hài lòng' },
];

const services = [
  {
    icon: <FaStethoscope />,
    title: 'Khoa khám bệnh tự nguyện',
    desc: 'Dịch vụ khám chữa bệnh toàn diện theo yêu cầu với đội ngũ bác sĩ giàu kinh nghiệm và trang thiết bị hiện đại.',
    path: '/services#voluntary',
  },
  {
    icon: <FaHeartbeat />,
    title: 'Chăm sóc mạch vành',
    desc: 'Chẩn đoán và điều trị chuyên sâu các bệnh lý mạch vành, can thiệp tim mạch bằng kỹ thuật tiên tiến nhất.',
    path: '/services#coronary',
  },
  {
    icon: <FaFlask />,
    title: 'Khoa dược & hiệu thuốc',
    desc: 'Cung cấp thuốc đặc trị tim mạch chất lượng cao, tư vấn dược lý chuyên sâu cho bệnh nhân.',
    path: '/services#pharmacy',
  },
  {
    icon: <FaUserMd />,
    title: 'Khám sức khoẻ toàn diện',
    desc: 'Gói khám sức khoẻ cá nhân và doanh nghiệp, tầm soát bệnh lý tim mạch sớm và hiệu quả.',
    path: '/services#checkup',
  },
  {
    icon: <FaHome />,
    title: 'Chăm sóc tại nhà',
    desc: 'Dịch vụ điều dưỡng, chăm sóc sau phẫu thuật và phục hồi chức năng ngay tại nhà bệnh nhân.',
    path: '/services#homecare',
  },
  {
    icon: <FaCalendarCheck />,
    title: 'Đặt lịch khám trực tuyến',
    desc: 'Đặt lịch khám nhanh chóng, chọn bác sĩ và thời gian phù hợp. Tiết kiệm thời gian chờ đợi.',
    path: '/booking',
  },
];

const testimonials = [
  {
    name: 'Nguyễn Văn An',
    role: 'Bệnh nhân mạch vành',
    img: img1,
    text: '"Đội ngũ bác sĩ tận tâm, thiết bị hiện đại. Sau ca phẫu thuật mạch vành, tôi hồi phục rất nhanh. Bệnh viện Tim Hà Nội thực sự là địa chỉ đáng tin cậy cho những ai bị bệnh tim."',
    stars: 5,
  },
  {
    name: 'Trần Thị Bình',
    role: 'Bệnh nhân tim bẩm sinh',
    img: img2,
    text: '"Tôi đã điều trị tim bẩm sinh ở đây từ nhỏ. Các bác sĩ rất nhiệt tình, hướng dẫn chi tiết từng bước. Giờ tôi đã sống khoẻ mạnh nhờ sự chăm sóc của bệnh viện."',
    stars: 5,
  },
  {
    name: 'Lê Minh Tuấn',
    role: 'Người nhà bệnh nhân',
    img: img3,
    text: '"Bố tôi nhập viện cấp cứu vì nhồi máu cơ tim. Ekip cấp cứu phản ứng rất nhanh, chuyên nghiệp. Bố tôi đã qua khỏi và đang hồi phục tốt. Xin chân thành cảm ơn!"',
    stars: 5,
  },
];

const news = [
  {
    img: blog1,
    date: '10 Tháng 7, 2025',
    category: 'Tin tức',
    title: 'Bệnh viện Tim Hà Nội triển khai kỹ thuật can thiệp mạch vành không tiếp xúc mới nhất',
    excerpt: 'Kỹ thuật mới giúp giảm thiểu rủi ro và rút ngắn thời gian hồi phục cho bệnh nhân tim mạch...',
  },
  {
    img: blog2,
    date: '5 Tháng 7, 2025',
    category: 'Sức khoẻ',
    title: '5 dấu hiệu cảnh báo bệnh tim mạch bạn không nên bỏ qua',
    excerpt: 'Nhận biết sớm các triệu chứng của bệnh tim mạch có thể cứu sống bạn và người thân...',
  },
  {
    img: blog3,
    date: '1 Tháng 7, 2025',
    category: 'Sự kiện',
    title: 'Hội thảo quốc tế về tim mạch can thiệp tại Hà Nội năm 2025',
    excerpt: 'Bệnh viện Tim Hà Nội vinh dự đăng cai hội thảo khoa học quốc tế về tim mạch can thiệp...',
  },
];

const Home = () => {
  return (
    <div className="home-page">

      {/* ===== HERO ===== */}
      <section className="hero">
        <div className="container hero-inner">
          <div className="hero-content">
            <div className="badge">🏥 Chuyên khoa tim mạch hàng đầu</div>
            <h1 className="hero-title">
              Bệnh viện Tim <span>Hà Nội</span>
            </h1>
            <p className="hero-slogan">Vì một trái tim khoẻ mạnh</p>
            <p className="hero-desc">
              Hơn 30 năm đồng hành cùng sức khoẻ tim mạch của người Hà Nội. Đội ngũ 200+ bác sĩ chuyên khoa,
              trang thiết bị hiện đại chuẩn quốc tế.
            </p>
            <div className="hero-actions">
              <Link to="/booking" className="btn btn-primary hero-btn-primary">
                <FaCalendarCheck /> Đặt lịch khám ngay
              </Link>
              <Link to="/about" className="btn btn-outline hero-btn-outline">
                Tìm hiểu thêm <FaArrowRight />
              </Link>
            </div>
            <div className="hero-badges">
              <span><FaCheckCircle className="check-icon" /> Miễn phí tư vấn sơ bộ</span>
              <span><FaCheckCircle className="check-icon" /> Đặt lịch online 24/7</span>
              <span><FaCheckCircle className="check-icon" /> Bác sĩ đầu ngành</span>
            </div>
          </div>
          <div className="hero-image-wrap">
            <div className="hero-image-card">
              <img src={homeImg} alt="Bệnh viện Tim Hà Nội" className="hero-img" />
              <div className="hero-card-badge">
                <FaPhone className="card-icon" />
                <div>
                  <small>Đường dây nóng</small>
                  <strong>1800 6969</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== STATS ===== */}
      <section className="stats-section">
        <div className="container stats-grid">
          {stats.map((s, i) => (
            <div key={i} className="stat-card">
              <div className="stat-icon">{s.icon}</div>
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ===== INTRO ===== */}
      <section className="section intro-section">
        <div className="container intro-inner">
          <div className="intro-image-col">
            <div className="intro-image-wrapper">
              <img src={img2} alt="Bác sĩ tim mạch" />
              <div className="intro-badge-float">
                <FaHeartbeat />
                <div>
                  <div className="badge-float-value">30+</div>
                  <div className="badge-float-label">Năm kinh nghiệm</div>
                </div>
              </div>
            </div>
          </div>
          <div className="intro-content-col">
            <div className="badge">Về chúng tôi</div>
            <h2 className="section-title">
              Chăm sóc tim mạch <span>tận tâm</span> và chuyên nghiệp
            </h2>
            <div className="divider" style={{margin: '1.6rem 0'}} />
            <p className="intro-text">
              Bệnh viện Tim Hà Nội được thành lập năm 1995, là cơ sở y tế chuyên khoa tim mạch hàng đầu Việt Nam. Chúng tôi tự hào với đội ngũ bác sĩ, điều dưỡng tận tâm và cơ sở vật chất đạt chuẩn quốc tế.
            </p>
            <p className="intro-text">
              Với sứ mệnh mang đến dịch vụ y tế tốt nhất, chúng tôi không ngừng đổi mới, áp dụng các kỹ thuật tiên tiến nhất để chẩn đoán và điều trị các bệnh lý tim mạch.
            </p>
            <div className="intro-features">
              {['Can thiệp tim mạch chuẩn quốc tế', 'Phẫu thuật tim hở & tim bẩm sinh', 'Tư vấn dinh dưỡng tim mạch', 'Theo dõi từ xa 24/7'].map((f) => (
                <div key={f} className="intro-feature">
                  <FaCheckCircle className="feature-check" /> {f}
                </div>
              ))}
            </div>
            <Link to="/about" className="btn btn-primary" style={{marginTop: '2rem'}}>
              Xem thêm về bệnh viện <FaArrowRight />
            </Link>
          </div>
        </div>
      </section>

      {/* ===== SERVICES ===== */}
      <section className="section section-alt services-section">
        <div className="container">
          <div className="section-header">
            <div className="badge">Dịch vụ</div>
            <h2 className="section-title">Dịch vụ <span>y tế</span> nổi bật</h2>
            <div className="divider" />
            <p className="section-subtitle">Chúng tôi cung cấp các dịch vụ chăm sóc sức khoẻ tim mạch toàn diện, từ phòng ngừa đến điều trị và phục hồi.</p>
          </div>
          <div className="services-grid">
            {services.map((sv, i) => (
              <Link to={sv.path} key={i} className="service-card card">
                <div className="service-icon">{sv.icon}</div>
                <h3 className="service-title">{sv.title}</h3>
                <p className="service-desc">{sv.desc}</p>
                <span className="service-link">Xem chi tiết <FaArrowRight /></span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ===== TESTIMONIALS ===== */}
      <section className="section testimonials-section">
        <div className="container">
          <div className="section-header">
            <div className="badge">Đánh giá</div>
            <h2 className="section-title">Bệnh nhân <span>nói gì</span> về chúng tôi</h2>
            <div className="divider" />
          </div>
          <div className="testimonials-grid">
            {testimonials.map((t, i) => (
              <div key={i} className="testimonial-card">
                <div className="testimonial-header">
                  <img src={t.img} alt={t.name} />
                  <div>
                    <h4>{t.name}</h4>
                    <span>{t.role}</span>
                  </div>
                </div>
                <div className="testimonial-stars">
                  {[...Array(t.stars)].map((_, si) => <FaStar key={si} />)}
                </div>
                <p className="testimonial-text">{t.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== NEWS ===== */}
      <section className="section section-alt news-section">
        <div className="container">
          <div className="section-header">
            <div className="badge">Tin tức & Sự kiện</div>
            <h2 className="section-title">Tin tức <span>mới nhất</span></h2>
            <div className="divider" />
          </div>
          <div className="news-grid">
            {news.map((n, i) => (
              <div key={i} className="news-card card">
                <div className="news-image">
                  <img src={n.img} alt={n.title} />
                  <span className="news-category">{n.category}</span>
                </div>
                <div className="news-content">
                  <div className="news-date"><FaBell size={12} /> {n.date}</div>
                  <h3 className="news-title">{n.title}</h3>
                  <p className="news-excerpt">{n.excerpt}</p>
                  <a href="#" className="news-readmore">Đọc tiếp <FaArrowRight /></a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== BOOKING CTA ===== */}
      <section className="booking-cta-section">
        <div className="container booking-cta-inner">
          <div className="booking-cta-content">
            <FaHeartbeat className="cta-icon-main" />
            <h2>Đặt lịch khám tim mạch ngay hôm nay</h2>
            <p>Đừng chờ đến khi có triệu chứng. Tầm soát tim mạch định kỳ là bảo vệ cuộc sống của bạn.</p>
          </div>
          <div className="booking-cta-actions">
            <Link to="/booking" className="btn btn-white">
              <FaCalendarCheck /> Đặt lịch khám
            </Link>
            <a href="tel:18006969" className="btn btn-outline-white">
              <FaPhone /> 1800 6969
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;

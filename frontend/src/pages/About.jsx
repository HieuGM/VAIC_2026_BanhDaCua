import React from 'react';
import {
  FaUserMd, FaAward, FaBuilding,
  FaHistory, FaGlobe, FaMusic,
  FaSearch, FaHandHoldingHeart, FaUserFriends,
  FaStethoscope
} from 'react-icons/fa';
import doc1 from '../image/nguyen_sinh_hien.webp';
import doc2 from '../image/quynh_nga.webp';
import doc3 from '../image/pham_nhu_hung.webp';
import doc4 from '../image/hoang_van.webp';
import homeGif from '../image/home.gif';
import './About.css';

const leaders = [
  { img: doc1, name: 'PGS.TS.BS. NGUYỄN SINH HIỀN', role: 'Giám đốc Bệnh viện', specialty: 'Chuyên gia Tim mạch hàng đầu tại Việt Nam' },
  { img: doc2, name: 'TS.BS. VŨ QUỲNH NGA', role: 'Phó Giám đốc Bệnh viện', specialty: 'Chuyên gia Tim mạch hàng đầu tại Việt Nam' },
  { img: doc3, name: 'TS.BS. PHẠM NHƯ HÙNG', role: 'Phó Giám đốc Bệnh viện', specialty: 'Chuyên gia Tim mạch hàng đầu tại Việt Nam' },
  { img: doc4, name: 'TS.BS. HOÀNG VĂN', role: 'Phó Giám đốc Bệnh viện', specialty: 'Chuyên gia Tim mạch hàng đầu tại Việt Nam' },
];

const milestones = [
  { year: '15/11/2001', title: 'Thành lập Bệnh viện', desc: 'Quyết định số 6863/QĐ-UB của UBND TP. Hà Nội chính thức thành lập Bệnh viện Tim Hà Nội trên cơ sở tổ chức lại Bệnh viện Hoàn Kiếm. Ban đầu có 50 giường bệnh, 60 biên chế và 9 khoa phòng.' },
  { year: '2001 – 2004', title: 'Giai đoạn xây dựng & hình thành', desc: 'Đặt nền móng cơ bản với tổng kinh phí đầu tư ban đầu hơn 50 tỷ đồng. Tập trung sửa chữa cơ sở vật chất và cử y bác sĩ đi đào tạo chuyên sâu trong và ngoài nước.' },
  { year: '25/07/2004', title: 'Ca phẫu thuật tim hở đầu tiên', desc: 'Đạt dấu mốc lịch sử khi tiến hành phẫu thuật tim hở thành công đầu tiên cho bệnh nhân Lê Thị Lan, 12 tuổi, khẳng định năng lực điều trị chuyên sâu.' },
  { year: '19/08/2004', title: 'Khánh thành chính thức', desc: 'Bệnh viện khánh thành đi vào hoạt động chính thức nhân dịp Chào mừng kỷ niệm 50 năm giải phóng Thủ đô.' },
  { year: '03/2009', title: 'Thành lập Đơn vị Tim mạch can thiệp', desc: 'Bổ sung mảng can thiệp tim mạch, một trong những mũi nhọn quan trọng nhất giúp xử lý nhanh các ca nhồi máu cơ tim cấp.' },
  { year: '10/10/2013', title: 'Hoàn thành nâng cấp Giai đoạn I', desc: 'Nâng cấp cơ sở vật chất hiện đại, khai trương Đơn vị chăm sóc mạch vành 16 giường điều trị tích cực đầu tiên trong cả nước.' },
  { year: '03/12/2014', title: 'Sáp nhập và Tổ chức lại', desc: 'UBND TP. Hà Nội ban hành Quyết định số 6438/QĐ-UBND sáp nhập Trung tâm Y tế công nghiệp Hà Nội vào Bệnh viện Tim Hà Nội, mở rộng quy mô hoạt động.' },
  { year: '23/03/2015', title: 'Ứng dụng hệ thống định vị 3D', desc: 'Đưa vào sử dụng máy lập bản đồ nội mạc 3 chiều (3D mapping) Ensite Velocity đầu tiên tại Việt Nam trong chẩn đoán và điều trị loạn nhịp tim.' },
  { year: '2014 – nay', title: 'Mở rộng Cơ sở 2', desc: 'Phát triển Cơ sở 2 tại Lạc Long Quân với quy mô 300 giường bệnh, tổng vốn đầu tư hơn 1.000 tỷ đồng, nâng tầm phục vụ toàn quốc.' }
];

const constitution = [
  { title: 'Một mục tiêu', desc: 'VÌ MỘT TRÁI TIM KHỎE' },
  { title: 'Hai cơ sở', desc: 'CS1: 92 Trần Hưng Đạo, Hoàn Kiếm | CS2: 695 Lạc Long Quân, Tây Hồ, Hà Nội' },
  { title: 'Ba tiêu chí (3 Th)', desc: 'Bệnh viện Thân thiện – Dịch vụ Thuận tiện – Nhân viên Thanh lịch' },
  { title: 'Ba phương châm (3H)', desc: 'Head (trí tuệ) – Hand (kỹ năng) – Heart (lương tâm, y đức)' },
  { title: 'Bốn trụ cột', desc: 'Chuyên môn kỹ thuật cao – Dịch vụ tốt – Đào tạo chỉ đạo tuyến – Công tác xã hội' },
  { title: 'Năm mũi nhọn', desc: 'Tim mạch nội khoa – Tim mạch nhi khoa – Tim mạch can thiệp – Phẫu thuật tim mạch – Tim mạch chuyển hóa' }
];

const About = () => {
  return (
    <div className="about-page">
      {/* Page Hero */}
      <div className="page-hero" id="intro">
        <div className="container">
          <div className="badge" style={{background:'rgba(255,255,255,0.15)', color:'#fff', border:'1px solid rgba(255,255,255,0.3)'}}>Về chúng tôi</div>
          <h1>Giới thiệu chung</h1>
          <p>Bệnh viện chuyên khoa tim mạch tuyến cuối của cả nước</p>
          <div className="breadcrumb">
            <a href="/">Trang chủ</a>
            <span className="sep">›</span>
            <span>Giới thiệu</span>
          </div>
        </div>
      </div>

      {/* Intro General */}
      <section className="section about-intro">
        <div className="container about-intro-inner">
          <div className="about-intro-content">
            <div className="badge">Tổng quan bệnh viện</div>
            <h2 className="section-title">Bệnh viện Tim <span>Hà Nội</span></h2>
            <p className="slogan-text-rich">Slogan: VÌ MỘT TRÁI TIM KHỎE</p>
            <div className="divider" style={{margin:'1.6rem 0'}} />
            <p>
              Bệnh viện Tim Hà Nội là bệnh viện chuyên khoa hạng I trực thuộc Sở Y tế Hà Nội. Là đơn vị sự nghiệp tự chủ tài chính toàn bộ, bệnh viện tự hào là cơ sở y khoa đầu ngành tim mạch của Thủ đô và là bệnh viện tuyến cuối của cả nước.
            </p>
            <p>
              Với bài hát truyền thống đầy tự hào <strong>"Bệnh viện Tim Hà Nội niềm tự hào"</strong>, tập thể cán bộ y tế luôn cam kết nỗ lực không ngừng để đem lại chất lượng dịch vụ tốt nhất.
            </p>
            
            {/* Core Pillars */}
            <div className="about-constitution-grid">
              {constitution.map((c, i) => (
                <div key={i} className="const-card">
                  <span className="const-num">{i + 1}</span>
                  <div>
                    <h4>{c.title}</h4>
                    <p>{c.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="about-intro-image">
            <img src={homeGif} alt="Bệnh viện Tim Hà Nội" />
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="section section-alt about-mission-section">
        <div className="container">
          <div className="section-header">
            <div className="badge">Tầm nhìn & Sứ mệnh</div>
            <h2 className="section-title">Sứ mệnh <span>hoạt động</span></h2>
            <div className="divider" />
          </div>
          <div className="mission-grid">
            {[
              { icon: <FaStethoscope />, text: 'Khám & điều trị tim mạch toàn diện ở 5 lĩnh vực: Nội khoa, Ngoại khoa, Nhi khoa, Can thiệp, Chuyển hóa. Khám chữa bệnh đa khoa tại Cơ sở 2.' },
              { icon: <FaGlobe />, text: 'Chỉ đạo tuyến các bệnh viện trực thuộc Sở Y tế Hà Nội và chuyển giao kỹ thuật cho 10 tỉnh thành trong các dự án Vệ tinh và NORRED.' },
              { icon: <FaAward />, text: 'Hợp tác đào tạo, chuyển giao kỹ thuật cho 26 tỉnh thành trên toàn quốc (từ Hà Giang, Quảng Bình tới Gia Lai).' },
              { icon: <FaMusic />, text: 'Hợp tác quốc tế sâu rộng với Đại học Toulouse (Pháp), Viện Tim mạch Quốc gia Singapore, tổ chức MD1 World (Mỹ)...' },
              { icon: <FaHandHoldingHeart />, text: 'Thực hiện tốt các công tác xã hội, khám chữa bệnh và phẫu thuật tim miễn phí cho hàng nghìn trẻ em tim bẩm sinh.' },
              { icon: <FaSearch />, text: 'Đẩy mạnh nghiên cứu khoa học, ứng dụng các công nghệ y học hàng đầu thế giới trong chẩn đoán và điều trị tim mạch.' }
            ].map((m, i) => (
              <div key={i} className="mission-card card">
                <div className="mission-icon-wrap">{m.icon}</div>
                <p>{m.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Infrastructure & Equipment */}
      <section className="section about-infra-section">
        <div className="container">
          <div className="section-header">
            <div className="badge">Cơ sở hạ tầng</div>
            <h2 className="section-title">Trang thiết bị <span>hiện đại</span></h2>
            <div className="divider" />
          </div>
          <div className="infra-stats-grid">
            {[
              { val: '300', label: 'Giường bệnh nội trú' },
              { val: '50', label: 'Phòng khám tiêu chuẩn khách sạn' },
              { val: '3', label: 'Phòng tim mạch can thiệp (Cathlab)' },
              { val: '4', label: 'Phòng mổ tim mở' }
            ].map((inf, i) => (
              <div key={i} className="infra-stat-card">
                <h3>{inf.val}</h3>
                <p>{inf.label}</p>
              </div>
            ))}
          </div>
          <div className="infra-description-box">
            <p>
              Hệ thống cơ sở hạ tầng khang trang, đồng bộ, khu tiếp đón văn minh theo tiêu chuẩn <strong>Bệnh viện Khách sạn</strong>.
            </p>
            <p>
              Trang thiết bị hiện đại ngang tầm khu vực và thế giới: 2 máy chụp mạch DSA hãng Philips, máy CEC, máy cộng hưởng từ 1.5 Tesla, máy chụp cắt lớp vi tính CT 128 dãy, hệ thống 25 máy siêu âm tim chuyên sâu (Vivid E9 4D), siêu âm gắng sức, đặc biệt là hệ thống lập bản đồ nội mạc 3 chiều (3D mapping) Ensite Velocity của hãng St.Jude Medical ứng dụng hàng đầu trong điều trị rối loạn nhịp tim.
            </p>
          </div>
        </div>
      </section>

      {/* Leadership */}
      <section className="section section-alt" id="leadership">
        <div className="container">
          <div className="section-header">
            <div className="badge">Nhân sự</div>
            <h2 className="section-title">Ban <span>Giám đốc</span></h2>
            <div className="divider" />
            <p className="section-subtitle">Đội ngũ lãnh đạo, chuyên gia Tim mạch hàng đầu trực tiếp điều hành hoạt động của bệnh viện</p>
          </div>
          <div className="leaders-grid">
            {leaders.map((l, i) => (
              <div key={i} className="leader-card card">
                <div className="leader-image-wrap">
                  <img src={l.img} alt={l.name} />
                  <div className="leader-overlay">
                    <div className="leader-socials">
                      <a href="#" className="leader-social-btn"><i className="fab fa-facebook-f" /></a>
                      <a href="#" className="leader-social-btn"><i className="fab fa-linkedin" /></a>
                    </div>
                  </div>
                </div>
                <div className="leader-info">
                  <h3>{l.name}</h3>
                  <span className="leader-role">{l.role}</span>
                  <span className="leader-specialty"><FaUserMd /> {l.specialty}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Structure */}
      <section className="section" id="structure">
        <div className="container">
          <div className="section-header">
            <div className="badge">Cơ cấu tổ chức</div>
            <h2 className="section-title">Quy mô <span>tổ chức & nhân lực</span></h2>
            <div className="divider" />
            <p className="section-subtitle">Tổng số <strong>589 cán bộ viên chức</strong> và người lao động đang làm việc tại bệnh viện.</p>
          </div>
          
          <div className="structure-summary-grid">
            <div className="structure-info-card">
              <h4><FaUserFriends /> Biên chế & Nhân sự</h4>
              <ul>
                <li><strong>Biên chế nhà nước:</strong> 161 người</li>
                <li><strong>Lao động hợp đồng NĐ 68:</strong> 03 người</li>
                <li><strong>Hợp đồng lao động bệnh viện:</strong> 425 người</li>
                <li><strong>Lãnh đạo:</strong> 1 Giám đốc và 3 Phó Giám đốc</li>
              </ul>
            </div>
            <div className="structure-info-card">
              <h4><FaBuilding /> Khoa, phòng, đơn nguyên</h4>
              <ul>
                <li><strong>30 Khoa phòng ban:</strong> gồm 16 khoa lâm sàng, 3 khoa cận lâm sàng, 11 phòng chức năng/hậu cần</li>
                <li><strong>11 Khoa lâm sàng:</strong> Khám bệnh, Nội, Nội Nhi, Tim mạch chuyển hóa, Hồi sức tích cực nhi, Gây mê hồi sức, Hồi sức tích cực, Ngoại, Tim mạch can thiệp, Cấp cứu, Các bệnh mạch máu</li>
                <li><strong>05 Khoa cận lâm sàng:</strong> Xét nghiệm, Dược, Kiểm soát nhiễm khuẩn, Chẩn đoán hình ảnh, Dinh dưỡng</li>
                <li><strong>06 Đơn nguyên:</strong> Khám & điều trị tự nguyện, Thăm dò điện sinh lý & rối loạn nhịp, Sơ sinh, Tim mạch can thiệp cơ sở 2, Can thiệp tĩnh mạch, Chẩn đoán hình ảnh kỹ thuật cao</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* History */}
      <section className="section section-alt" id="history">
        <div className="container">
          <div className="section-header">
            <div className="badge">Lịch sử thành lập</div>
            <h2 className="section-title">Quá trình <span>phát triển</span></h2>
            <div className="divider" />
          </div>
          <div className="timeline">
            {milestones.map((m, i) => (
              <div key={i} className={`timeline-item ${i % 2 === 0 ? 'left' : 'right'}`}>
                <div className="timeline-content">
                  <div className="timeline-year">{m.year}</div>
                  <h3 className="timeline-title">{m.title}</h3>
                  <p className="timeline-desc">{m.desc}</p>
                </div>
                <div className="timeline-dot">
                  <FaHistory />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;

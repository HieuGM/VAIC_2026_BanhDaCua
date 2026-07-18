import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  FaStethoscope, FaHeartbeat, FaFlask, FaUserMd, FaHome,
  FaArrowRight, FaUser, FaPhone,
  FaEnvelope, FaTools, FaRegHospital, FaMedkit, FaBriefcase,
  FaFileInvoiceDollar, FaClipboardList
} from 'react-icons/fa';
import './Services.css';

const Services = () => {
  const [active, setActive] = useState('voluntary');
  const location = useLocation();

  useEffect(() => {
    const hash = location.hash;
    if (hash) {
      const id = hash.slice(1);
      const exists = ['voluntary', 'coronary', 'pharmacy', 'checkup', 'homecare'].includes(id);
      if (exists) {
        setActive(id);
      }
    }
  }, [location.hash]);

  // Sub-render 1: Khoa Khám bệnh tự nguyện
  const renderVoluntary = () => (
    <div className="service-detail-rich">
      <div className="rich-header">
        <span className="rich-date">Thành lập tháng 10/2013</span>
        <h2>Khoa Khám bệnh Tự nguyện</h2>
        <p className="rich-intro">
          Khoa hiện có 2 khu khám bệnh: <strong>Khám bệnh tự nguyện 1</strong> và <strong>Khám bệnh tự nguyện 3</strong>.
          Để biết thêm hướng dẫn cụ thể về quy trình khám và đặt hẹn, xin xem <Link to="/guide" className="rich-inline-link">tại đây</Link>.
        </p>
      </div>

      {/* Section I */}
      <div className="rich-section">
        <h3><FaUser /> I. Nhân lực</h3>
        <p className="section-title-sub">DANH SÁCH CÁC BÁC SỸ ĐƯỢC PHÂN CÔNG KHÁM TẠI KHU KHÁM BỆNH TỰ NGUYÊN 1 – CƠ SỞ 1</p>
        
        <div className="doc-list-mini">
          <div className="doc-item">
            <strong>GS.TS. Nguyễn Lân Việt</strong> — Tim mạch can thiệp
          </div>
          <div className="doc-item">
            <strong>PGS.TS. Trần Văn Hùng</strong> — Phẫu thuật tim hở
          </div>
          <div className="doc-item">
            <strong>TS.BS. Lê Thị Minh</strong> — Suy tim & rối loạn nhịp
          </div>
          <div className="doc-item">
            <strong>BS.CKII. Phạm Quốc Bảo</strong> — Cấp cứu tim mạch
          </div>
          <div className="doc-item">
            <strong>TS.BS. Hoàng Thị Lan</strong> — Tăng huyết áp & bệnh mạch vành
          </div>
        </div>

        <p className="rich-text-note">
          Ngoài ra còn các Trưởng, Phó khoa; Bác sĩ chuyên khoa có kinh nghiệm nhiều năm trong các lĩnh vực điều trị, can thiệp và hồi sức tim mạch làm việc thường xuyên tại khoa. Các bác sĩ này đều do trực tiếp Giám đốc bệnh viện tuyển chọn và phê duyệt.
        </p>
      </div>

      {/* Section II */}
      <div className="rich-section">
        <h3><FaTools /> II. Trang thiết bị & Hệ thống phục vụ</h3>
        <p>
          Với hơn 6 năm thành lập, khoa Khám bệnh Tự nguyện được trang bị đồng bộ với hệ thống điều hòa trung tâm và điều hòa từng phòng, hệ thống chiếu sáng và âm thanh hiện đại, các phòng làm việc trang trí hoa, cây cảnh và tranh để mang lại cảm giác thân thiện như ở nhà cho mọi người.
        </p>
        <p>
          Nước uống cho người bệnh đến khám được đảm bảo cung cấp đầy đủ. Việc vệ sinh cảnh quan và các khu vực vệ sinh được các nhân viên chuyên trách thực hiện nhằm đảm bảo luôn sạch kể cả những ngày trời mưa, ẩm.
        </p>
        <div className="rich-highlight-box">
          <strong>Hệ thống quy mô khám chữa bệnh:</strong>
          <ul>
            <li>02 khu KBTN & 16 phòng khám chuyên khoa Tim mạch.</li>
            <li>01 phòng khám Tĩnh mạch chi dưới.</li>
            <li>03 phòng siêu âm được trang bị: 01 máy siêu âm Vivid E9 hiện đại với đầu dò chuyên tim, đầu dò 4D và hệ thống phần mềm tiên tiến; 04 máy siêu âm - Doppler tim Philip; 01 máy siêu âm ổ bụng-mạch giúp giải quyết khám cho tất cả bệnh nhân ngay trong ngày.</li>
            <li>Hệ thống tài chính riêng biệt, đảm bảo bệnh nhân không phải chờ đợi lâu để làm các thủ tục thanh toán.</li>
          </ul>
        </div>
      </div>

      {/* Section III */}
      <div className="rich-section">
        <h3><FaRegHospital /> III. Các dịch vụ</h3>
        <div className="slogan-box">
          Tiêu chí phục vụ: <strong>“Thân thiện – Thuận tiện – Thanh lịch”</strong>
        </div>

        <div className="service-sub-list">
          <div className="service-sub-item">
            <h4>1. Đặt hẹn khám</h4>
            <p>Quý vị có thể đặt hẹn lịch khám và đăng kí bác sĩ khám thông qua số điện thoại <strong>1900 1082</strong> hoặc qua website bệnh viện. Chúng tôi khuyến khích bệnh nhân và người nhà liên hệ đặt hẹn trước để việc phục vụ bệnh nhân đạt hiệu quả tốt nhất.</p>
          </div>

          <div className="service-sub-item">
            <h4>2. Tiếp đón và hướng dẫn</h4>
            <p>Quầy tư vấn sẽ giải thích, hướng dẫn cho bệnh nhân và gia đình các thủ tục khám chữa bệnh, thủ tục bảo hiểm y tế, chọn bác sĩ khám bệnh. Các hướng dẫn viên có nhiệm vụ giải đáp thắc mắc và hỗ trợ đưa bệnh nhân đi thực hiện các dịch vụ cận lâm sàng.</p>
          </div>

          <div className="service-sub-item">
            <h4>3. Bảo hiểm y tế</h4>
            <p>Bệnh nhân có thẻ BHYT và giấy chuyển viện đúng tuyến hoàn toàn có thể lựa chọn khám tại 1 trong 2 khu Tự nguyện để hưởng các quyền lợi BHYT.</p>
          </div>

          <div className="service-sub-item">
            <h4>4. Quy trình khám chữa bệnh</h4>
            <p>Áp dụng quy trình khám chữa bệnh khép kín, tinh giản thủ tục tại cả 2 cơ sở (Cơ sở I và Cơ sở II) của Bệnh viện Tim Hà Nội.</p>
          </div>

          <div className="service-sub-item">
            <h4>5. Các xét nghiệm đang cung cấp</h4>
            <div className="test-grid">
              <div>
                <h5>5.1 Khám sức khỏe thông thường:</h5>
                <ul>
                  <li>Điện tâm đồ (ECG)</li>
                  <li>X-quang tim phổi</li>
                  <li>Siêu âm – Doppler tim thường quy</li>
                  <li>Xét nghiệm máu cơ bản (Công thức máu, đông máu, chức năng gan thận, đường máu, mỡ máu, acid uric...)</li>
                  <li>Siêu âm ổ bụng tổng quát</li>
                </ul>
              </div>
              <div>
                <h5>5.2 Xét nghiệm & Thăm dò chuyên khoa sâu:</h5>
                <ul>
                  <li>Nghiệm pháp gắng sức sàng lọc mạch vành</li>
                  <li>Siêu âm tim Dobutamine</li>
                  <li>Holter huyết áp & Điện tim đồ 24h</li>
                  <li>Siêu âm tim qua thực quản</li>
                  <li>Siêu âm tim 4D</li>
                  <li>Siêu âm Doppler mạch máu toàn thân</li>
                  <li>Đo chỉ số xơ vữa động mạch ABI</li>
                  <li>Xét nghiệm sinh hóa máu chuyên sâu (hs Troponin, pro BNP...)</li>
                  <li>Chụp CT mạch vành 128/256 dãy & MRI toàn thân</li>
                  <li>Siêu âm tim thai (sàng lọc trước sinh từ tuần 18)</li>
                </ul>
              </div>
            </div>
            <p className="pricing-link-text">
              * Quý khách có thể xem <Link to="/guide#pricing" className="rich-inline-link">Bảng giá chi tiết tại đây</Link>.
            </p>
          </div>

          <div className="service-sub-item">
            <h4>6. Bệnh nhân điều trị nội trú</h4>
            <p>Bệnh nhân khám tại khoa Khám bệnh tự nguyện được ưu tiên sắp xếp phòng điều trị nội trú nhanh nhất khi có chỉ định vào viện.</p>
            <p><strong>Về chế độ BHYT:</strong> Trường hợp cấp cứu được hưởng chế độ BHYT cấp cứu. Các trường hợp điều trị chương trình cần xin giấy chuyển tuyến theo quy định BHYT để được hưởng quyền lợi tối đa.</p>
          </div>

          <div className="service-sub-item">
            <h4>7. Đối tượng phục vụ</h4>
            <ul>
              <li>Bệnh nhân mắc bệnh tim mạch – chuyển hóa, sau can thiệp/phẫu thuật tim.</li>
              <li>Bệnh nhân cần kiểm tra tim mạch trước khi thực hiện điều trị chuyên khoa khác (phẫu thuật ngoài tim, hóa trị, sinh con...).</li>
              <li>Khách hàng có nhu cầu kiểm tra sức khỏe tổng quát, định kỳ (6 tháng - 1 năm/lần).</li>
              <li>Mọi lứa tuổi từ sơ sinh đến người cao tuổi.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  // Sub-render 2: Chăm sóc mạch vành
  const renderCoronary = () => (
    <div className="service-detail-rich">
      <div className="rich-header">
        <h2>Chăm sóc Mạch vành</h2>
        <p className="rich-intro">
          Chẩn đoán, can thiệp và điều trị toàn diện các bệnh lý về động mạch vành (ĐMV) bằng các phương pháp kỹ thuật tiên tiến hàng đầu Việt Nam.
        </p>
      </div>

      <div className="rich-section">
        <h3><FaHeartbeat /> Dịch vụ chuyên sâu</h3>
        <div className="rich-highlight-box">
          <ul>
            <li><strong>Chụp và can thiệp mạch vành qua da (PCI):</strong> Nong và đặt stent động mạch vành cấp cứu 24/7 đối với bệnh nhân nhồi máu cơ tim cấp.</li>
            <li><strong>Phẫu thuật bắc cầu nối chủ - vành (CABG):</strong> Thực hiện bởi ekip phẫu thuật tim mạch giàu kinh nghiệm đối với các tổn thương phức tạp.</li>
            <li><strong>Quản lý bệnh mạch vành mãn tính:</strong> Thiết lập phác đồ thuốc tối ưu, kiểm soát các yếu tố nguy cơ (tăng huyết áp, mỡ máu, đái tháo đường).</li>
            <li><strong>Phục hồi chức năng tim mạch:</strong> Hướng dẫn chế độ vận động và dinh dưỡng khoa học sau can thiệp giúp bệnh nhân nhanh chóng trở lại cuộc sống bình thường.</li>
          </ul>
        </div>
      </div>
    </div>
  );

  // Sub-render 3: Khoa dược và hiệu thuốc
  const renderPharmacy = () => (
    <div className="service-detail-rich">
      <div className="rich-header">
        <h2>Khoa Dược và Hiệu thuốc</h2>
        <p className="rich-intro">
          Đảm bảo cung cấp đầy đủ thuốc chất lượng cao, an toàn và tư vấn chuyên môn sâu về dược lâm sàng tim mạch.
        </p>
      </div>

      {/* Section I */}
      <div className="rich-section">
        <h3><FaMedkit /> I. Mô hình tổ chức & Biên chế</h3>
        <p><strong>Tổng số:</strong> 13 cán bộ. Trong đó có: 1 Tiến sĩ, 03 Thạc sĩ, 1 DSCKI, 10 DSĐH, 13 DSCĐ.</p>
        
        <div className="leader-info-box">
          <h4>Lãnh đạo khoa hiện tại:</h4>
          <ul>
            <li><strong>Phụ trách khoa:</strong> TS. DS. Vũ Thị Thanh Huyền</li>
            <li><strong>Phó khoa:</strong> Ths. DS. Nguyễn Thị Phương Lan</li>
          </ul>
        </div>

        <div className="sub-depts">
          <h4>Các tổ chuyên môn:</h4>
          <div className="dept-tags">
            <span className="dept-tag">Tổ Dược chính</span>
            <span className="dept-tag">Tổ cấp phát (Kho chính & Kho BHYT)</span>
            <span className="dept-tag">Nhà thuốc Bệnh viện</span>
          </div>
        </div>
      </div>

      {/* Section II */}
      <div className="rich-section">
        <h3><FaFileInvoiceDollar /> II. Nhiệm vụ chính</h3>
        
        <div className="pharmacy-tasks">
          <div className="task-block">
            <h4>1. Nhiệm vụ chung</h4>
            <ul>
              <li>Xây dựng kế hoạch cung cấp và đảm bảo đầy đủ thuốc có chất lượng kịp thời phục vụ nhu cầu cấp cứu, điều trị nội trú và ngoại trú.</li>
              <li>Kiểm tra, giám sát, hướng dẫn việc sử dụng thuốc an toàn hợp lý trong toàn bệnh viện.</li>
              <li>Thông tin thuốc, tư vấn sử dụng thuốc và cùng các khoa lâm sàng theo dõi phản ứng có hại của thuốc (ADR).</li>
              <li>Bảo quản thuốc đúng quy chế chuyên môn GSP.</li>
              <li>Tham gia đấu thầu cung ứng thuốc chất lượng với giá cả hợp lý, tiết kiệm chống lãng phí.</li>
              <li>Nghiên cứu khoa học về dược lâm sàng.</li>
            </ul>
          </div>

          <div className="task-block">
            <h4>2. Nhiệm vụ chi tiết của các tổ</h4>
            <div className="sub-tasks-grid">
              <div className="sub-task-card">
                <h5>Tổ Dược chính</h5>
                <p>Dự trù thuốc, đấu thầu, kiểm tra giám sát quy chế chuyên môn Dược, thống kê báo cáo và thông tin thuốc.</p>
              </div>
              <div className="sub-task-card">
                <h5>Tổ cấp phát</h5>
                <p>Kiểm nhập, bảo quản thuốc, cung ứng thuốc đến khoa lâm sàng và phát thuốc ngoại trú diện bảo hiểm y tế.</p>
              </div>
              <div className="sub-task-card">
                <h5>Nhà thuốc Bệnh viện</h5>
                <p>Bán lẻ thuốc theo đơn, dụng cụ y tế thông thường đạt tiêu chuẩn GPP, tư vấn cách sử dụng và an toàn thuốc cho người dân.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Sub-render 4: Khám sức khỏe cá nhân và tổ chức
  const renderCheckup = () => (
    <div className="service-detail-rich">
      <div className="rich-header">
        <h2>Dịch vụ Khám sức khỏe cho Cơ quan - Doanh nghiệp</h2>
        <span className="rich-slogan-sub">— Hành trình chăm sóc từ trái tim —</span>
      </div>

      {/* Section I */}
      <div className="rich-section">
        <h3><FaBriefcase /> I. Giới thiệu dịch vụ</h3>
        <p>
          Trong mỗi hành trình phát triển bền vững, con người luôn là yếu tố cốt lõi tạo nên giá trị cho doanh nghiệp. Một đội ngũ nhân sự khỏe mạnh không chỉ giúp cơ quan vận hành hiệu quả mà còn lan tỏa tinh thần tích cực.
        </p>
        <p>
          Bệnh viện Tim Hà Nội trân trọng giới thiệu dịch vụ khám sức khỏe định kỳ chuyên nghiệp, được thiết kế với sự tận tâm và chuyên môn sâu về tim mạch cho các cơ quan, doanh nghiệp.
        </p>

        <div className="advantages-grid">
          <div className="adv-card">
            <h4>1. Vì sao nên khám định kỳ cho nhân viên?</h4>
            <ul>
              <li><strong>Đồng hành sức khỏe:</strong> Phát hiện sớm các bệnh lý âm thầm (tim mạch, huyết áp, tiểu đường...).</li>
              <li><strong>Thể hiện sự quan tâm:</strong> Chăm sóc chu đáo là thông điệp trân trọng gửi tới mỗi nhân viên.</li>
              <li><strong>Tăng năng suất:</strong> Nhân sự khỏe mạnh giúp tăng hiệu quả, giảm rủi ro nghỉ ốm.</li>
              <li><strong>Tuân thủ pháp luật:</strong> Theo Bộ luật Lao động và Luật An toàn – Vệ sinh lao động.</li>
            </ul>
          </div>

          <div className="adv-card">
            <h4>2. Tại sao chọn Bệnh viện Tim Hà Nội?</h4>
            <ul>
              <li><strong>Uy tín hàng đầu:</strong> Đơn vị chuyên khoa đầu ngành tim mạch tại Việt Nam.</li>
              <li><strong>Thiết bị hiện đại:</strong> Quy trình khám nhanh gọn (siêu âm tim, ECG, chụp X-quang, xét nghiệm...).</li>
              <li><strong>Gói khám linh hoạt:</strong> Thiết kế riêng theo quy mô và ngân sách của từng tổ chức.</li>
              <li><strong>Quy trình chuyên nghiệp:</strong> Lấy mẫu, trả kết quả và tư vấn hậu khám liền mạch.</li>
            </ul>
          </div>
        </div>

        <div className="benefits-table-wrap">
          <table className="benefits-table">
            <thead>
              <tr>
                <th>Lợi ích đối với Cơ quan - Doanh nghiệp</th>
                <th>Lợi ích đối với Người lao động</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>✔️ Tuân thủ đúng các quy định pháp luật lao động</td>
                <td>✔️ Phát hiện sớm các bệnh lý tiềm ẩn</td>
              </tr>
              <tr>
                <td>✔️ Nâng cao hình ảnh và uy tín thương hiệu tổ chức</td>
                <td>✔️ Nhận tư vấn chuyên sâu về sức khỏe tim mạch</td>
              </tr>
              <tr>
                <td>✔️ Gắn kết nội bộ, giữ chân nhân sự cốt cán</td>
                <td>✔️ Chủ động điều chỉnh chế độ sinh hoạt, làm việc tốt hơn</td>
              </tr>
              <tr>
                <td>✔️ Giảm thiểu chi phí điều trị phát sinh và nghỉ ốm</td>
                <td>✔️ An tâm công tác và cống hiến cho sự nghiệp</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Section II */}
      <div className="rich-section">
        <h3><FaClipboardList /> II. Quy trình triển khai khám</h3>
        <div className="process-flow">
          <div className="flow-step">
            <span className="flow-num">1</span>
            <strong>Tiếp nhận & tư vấn gói khám</strong>
            <p>Phân tích nhu cầu, ngân sách và đặc điểm lao động để đưa ra gói khám thích hợp.</p>
          </div>
          <div className="flow-step">
            <span className="flow-num">2</span>
            <strong>Bố trí lịch khám linh hoạt</strong>
            <p>Đặt lịch khám tại bệnh viện hoặc tổ chức khám lưu động ngay tại cơ sở của doanh nghiệp.</p>
          </div>
          <div className="flow-step">
            <span className="flow-num">3</span>
            <strong>Thực hiện khám sức khỏe</strong>
            <p>Khám lâm sàng, xét nghiệm máu, nước tiểu, điện tim, siêu âm, chụp X-quang kỹ thuật số...</p>
          </div>
          <div className="flow-step">
            <span className="flow-num">4</span>
            <strong>Trả kết quả & tư vấn riêng</strong>
            <p>Người lao động được bác sĩ trao đổi trực tiếp kết quả và tư vấn chế độ chăm sóc.</p>
          </div>
          <div className="flow-step">
            <span className="flow-num">5</span>
            <strong>Báo cáo tổng hợp cho doanh nghiệp</strong>
            <p>Cung cấp số liệu thống kê toàn diện giúp hoạch định chính sách chăm sóc sức khỏe nhân sự.</p>
          </div>
        </div>

        <div className="contact-box-rich">
          <h4>Liên hệ tư vấn và thiết kế gói khám:</h4>
          <p><strong>Bộ phận CSKH – Bệnh viện Tim Hà Nội</strong></p>
          <p><FaPhone /> Hotline: <strong>1900 1082</strong> hoặc <strong>083 709 1082</strong> / <strong>083 676 1082</strong></p>
          <p><FaEnvelope /> Email: <a href="mailto:cskh@timhanoi.vn">cskh@timhanoi.vn</a></p>
        </div>
      </div>
    </div>
  );

  // Sub-render 5: Chăm sóc tại nhà
  const renderHomecare = () => (
    <div className="service-detail-rich">
      <div className="rich-header">
        <h2>Chăm sóc Sức khỏe tại nhà</h2>
        <p className="rich-intro">
          Giải pháp y tế tiện lợi, mang sự chăm sóc chuẩn bệnh viện tới không gian ấm cúng tại gia đình bạn.
        </p>
      </div>

      <div className="rich-section">
        <h3><FaHome /> Dịch vụ chăm sóc y tế tại nhà</h3>
        <div className="rich-highlight-box">
          <ul>
            <li><strong>Điều dưỡng chăm sóc tim mạch:</strong> Theo dõi huyết áp, nhịp tim, đo điện tâm đồ tại nhà, thay băng cắt chỉ vết mổ tim.</li>
            <li><strong>Lấy mẫu xét nghiệm tại nhà:</strong> Thực hiện lấy máu xét nghiệm theo lịch và trả kết quả qua SMS/Email nhanh chóng.</li>
            <li><strong>Phục hồi chức năng tim mạch:</strong> Hướng dẫn các bài tập thở, vận động phục hồi sau phẫu thuật thay van tim hoặc bắc cầu mạch vành.</li>
            <li><strong>Tư vấn y tế từ xa:</strong> Kết nối trực tiếp với bác sĩ điều trị qua cuộc gọi video để điều chỉnh liều lượng thuốc.</li>
          </ul>
        </div>
      </div>
    </div>
  );

  return (
    <div className="services-page">
      {/* Page Hero */}
      <div className="page-hero">
        <div className="container">
          <div className="badge" style={{background:'rgba(255,255,255,0.15)', color:'#fff', border:'1px solid rgba(255,255,255,0.3)'}}>Dịch vụ y tế</div>
          <h1>Dịch vụ của chúng tôi</h1>
          <p>Chăm sóc tim mạch toàn diện từ phòng ngừa đến điều trị</p>
          <div className="breadcrumb">
            <a href="/">Trang chủ</a>
            <span className="sep">›</span>
            <span>Dịch vụ</span>
          </div>
        </div>
      </div>

      {/* Services Tabs */}
      <section className="section services-tabs-section">
        <div className="container">
          {/* Tab Nav */}
          <div className="service-tabs">
            {[
              { id: 'voluntary', label: 'Khoa khám bệnh tự nguyện', icon: <FaStethoscope /> },
              { id: 'coronary', label: 'Chăm sóc mạch vành', icon: <FaHeartbeat /> },
              { id: 'pharmacy', label: 'Khoa Dược & Hiệu thuốc', icon: <FaFlask /> },
              { id: 'checkup', label: 'Khám sức khoẻ cá nhân – Tổ chức', icon: <FaUserMd /> },
              { id: 'homecare', label: 'Chăm sóc tại nhà', icon: <FaHome /> }
            ].map((s) => (
              <button
                key={s.id}
                className={`service-tab ${active === s.id ? 'active' : ''}`}
                onClick={() => setActive(s.id)}
              >
                <span className="tab-icon">{s.icon}</span>
                <span className="tab-label">{s.label}</span>
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="service-detail">
            {active === 'voluntary' && renderVoluntary()}
            {active === 'coronary' && renderCoronary()}
            {active === 'pharmacy' && renderPharmacy()}
            {active === 'checkup' && renderCheckup()}
            {active === 'homecare' && renderHomecare()}
          </div>
        </div>
      </section>

      {/* All Services Cards */}
      <section className="section section-alt">
        <div className="container">
          <div className="section-header">
            <div className="badge">Tổng quan</div>
            <h2 className="section-title">Tất cả <span>dịch vụ</span></h2>
            <div className="divider" />
          </div>
          <div className="all-services-grid">
            {[
              { id: 'voluntary', title: 'Khoa khám bệnh tự nguyện', shortDesc: 'Dịch vụ khám theo yêu cầu với bác sĩ đầu ngành.', icon: <FaStethoscope />, color: '#c0392b' },
              { id: 'coronary', title: 'Chăm sóc mạch vành', shortDesc: 'Can thiệp và điều trị bệnh lý động mạch vành chuyên sâu.', icon: <FaHeartbeat />, color: '#e74c3c' },
              { id: 'pharmacy', title: 'Khoa Dược & Hiệu thuốc', shortDesc: 'Thuốc chuyên khoa tim mạch chất lượng cao.', icon: <FaFlask />, color: '#8e44ad' },
              { id: 'checkup', title: 'Khám sức khoẻ cá nhân – Tổ chức', shortDesc: 'Tầm soát tim mạch định kỳ cho doanh nghiệp.', icon: <FaUserMd />, color: '#27ae60' },
              { id: 'homecare', title: 'Chăm sóc tại nhà', shortDesc: 'Dịch vụ y tá, điều dưỡng tim mạch tại gia đình.', icon: <FaHome />, color: '#2980b9' }
            ].map((s) => (
              <div
                key={s.id}
                className="all-service-card"
                onClick={() => { setActive(s.id); window.scrollTo({top: 250, behavior:'smooth'}); }}
              >
                <div className="all-service-icon" style={{background:`${s.color}15`, color:s.color}}>{s.icon}</div>
                <h3>{s.title}</h3>
                <p>{s.shortDesc}</p>
                <span className="all-service-link" style={{color:s.color}}>Xem chi tiết <FaArrowRight /></span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Services;

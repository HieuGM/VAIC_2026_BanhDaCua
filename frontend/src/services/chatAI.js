// services/chatAI.js
// Mock AI service - sau này thay bằng API thực (OpenAI, Gemini, RAG...)

const MOCK_RESPONSES = [
  'Cảm ơn bạn đã liên hệ với **Bệnh viện Tim Hà Nội**! Tôi có thể hỗ trợ bạn về thông tin khám bệnh, đặt lịch hẹn và các dịch vụ y tế của chúng tôi.',
  'Để đặt lịch khám, bạn có thể:\n• Gọi hotline **1900 1082**\n• Đặt lịch trực tuyến tại trang **/booking**\n• Đến trực tiếp Phòng Tiếp nhận của bệnh viện\n\nBạn muốn tôi hướng dẫn thêm không?',
  'Bệnh viện Tim Hà Nội hiện có **2 cơ sở**:\n• **Cơ sở 1**: 92 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội\n• **Cơ sở 2**: 695 Lạc Long Quân, Tây Hồ, Hà Nội\n\nBạn muốn đến cơ sở nào?',
  'Về bảo hiểm y tế (BHYT), Bệnh viện Tim Hà Nội thanh toán theo **Thông tư 22/2023/TT-BYT** của Bộ Y tế. Bạn có thể xem chi tiết bảng giá tại trang Hướng dẫn khám bệnh.',
  'Giờ làm việc của Khoa Khám bệnh Tự nguyện:\n• **Khu TN1**: 7:00 – 16:30 (Thứ 2 – Thứ 6)\n• **Khu TN3**: 6:30 – 16:30 (Thứ 2 – Thứ 6)\n• **Thứ 7 & Chủ nhật**: Có một số phòng trực\n\nBạn cần thêm thông tin gì?',
  'Để chuẩn bị cho buổi khám, bạn nên mang theo:\n• **CCCD/Hộ chiếu** (bắt buộc)\n• **Thẻ BHYT** (nếu có)\n• **Giấy chuyển viện** (nếu có)\n• **Các kết quả xét nghiệm cũ** (nếu có)\n\nChúc bạn buổi khám thuận lợi! 🏥',
];

let responseIndex = 0;

/**
 * Giả lập phản hồi AI.
 * Sau này thay thế hàm này bằng API call thực.
 * @param {string} userMessage - Tin nhắn người dùng gửi
 * @returns {Promise<string>} - Phản hồi từ AI
 */
export const sendMessageToAI = async (userMessage) => {
  // Giả lập độ trễ mạng 800-1400ms
  const delay = 800 + Math.random() * 600;
  await new Promise((resolve) => setTimeout(resolve, delay));

  // Phản hồi thông minh theo từ khóa
  const msg = userMessage.toLowerCase();

  if (msg.includes('đặt lịch') || msg.includes('hẹn')) {
    return MOCK_RESPONSES[1];
  }
  if (msg.includes('địa chỉ') || msg.includes('cơ sở') || msg.includes('ở đâu')) {
    return MOCK_RESPONSES[2];
  }
  if (msg.includes('bhyt') || msg.includes('bảo hiểm') || msg.includes('giá')) {
    return MOCK_RESPONSES[3];
  }
  if (msg.includes('giờ') || msg.includes('lịch') || msg.includes('thứ')) {
    return MOCK_RESPONSES[4];
  }
  if (msg.includes('chuẩn bị') || msg.includes('mang theo') || msg.includes('hồ sơ')) {
    return MOCK_RESPONSES[5];
  }

  // Mặc định: xoay vòng các câu trả lời
  const response = MOCK_RESPONSES[responseIndex % MOCK_RESPONSES.length];
  responseIndex++;
  return response;
};

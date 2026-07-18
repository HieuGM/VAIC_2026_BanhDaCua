// services/chatAI.js
//
// Data layer cho chat widget: gọi POST /data/v1/chat trên data-api BFF.
//
// TODO(future): render markdown (react-markdown + remark-gfm + rehype-sanitize)
// trong ChatMessage thay vì plain text — backend có thể trả answer chứa markdown.
// Hiện tại MVP giữ plain-text render.

import api from './api';

/**
 * Gửi tin nhắn tới AI qua data-api BFF và nhận câu trả lời.
 *
 * @param {string} text - Nội dung tin nhắn người dùng.
 * @param {string|null} [sessionId=null] - sessionId từ response trước (nếu có)
 *   để BFF duy trì ngữ cảnh phía server.
 * @returns {Promise<{answer: string, sessionId: string, citations: Array}>}
 *   - answer:        chuỗi câu trả lời (có thể chứa markdown).
 *   - sessionId:     id phiên do BFF cấp (FE lưu lại để gửi ở request sau).
 *   - citations:     mảng trích nguồn (có thể rỗng).
 */
export const sendMessageToAI = async (text, sessionId = null) => {
  try {
    const response = await api.post('/data/v1/chat', {
      sessionId,
      text,
      lang: 'vi',
    });

    const data = response.data || {};
    return {
      answer: typeof data.answer === 'string' ? data.answer : '',
      sessionId: typeof data.sessionId === 'string' ? data.sessionId : '',
      citations: Array.isArray(data.citations) ? data.citations : [],
    };
  } catch (err) {
    // Axios error: chuẩn hoá thành message thân thiện để useChat hiển thị.
    if (err.response) {
      const status = err.response.status;
      const serverMsg =
        err.response.data && (err.response.data.message || err.response.data.error);
      throw new Error(
        serverMsg
          ? `Lỗi máy chủ (${status}): ${serverMsg}`
          : `Lỗi máy chủ (${status}). Vui lòng thử lại sau.`
      );
    }
    if (err.request) {
      // Request đã gửi nhưng không nhận được response (timeout / network / CORS).
      throw new Error(
        'Không kết nối được đến máy chủ. Vui lòng kiểm tra mạng và thử lại.'
      );
    }
    throw new Error(err.message || 'Lỗi không xác định khi gửi tin nhắn.');
  }
};

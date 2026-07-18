// services/chatStorage.js
// Quản lý lưu trữ conversation trên localStorage

const STORAGE_KEY = 'bvthn_chat_conversations';
const ACTIVE_KEY = 'bvthn_chat_active';

export const chatStorage = {
  /** Lấy toàn bộ conversations */
  getAll() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  },

  /** Lưu toàn bộ conversations */
  saveAll(conversations) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    } catch (e) {
      console.error('chatStorage.saveAll error:', e);
    }
  },

  /** Lấy active conversation id */
  getActiveId() {
    return localStorage.getItem(ACTIVE_KEY) || null;
  },

  /** Lưu active conversation id */
  saveActiveId(id) {
    if (id) {
      localStorage.setItem(ACTIVE_KEY, id);
    } else {
      localStorage.removeItem(ACTIVE_KEY);
    }
  },

  /** Xóa tất cả */
  clearAll() {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(ACTIVE_KEY);
  },
};

// services/authService.js
// Tất cả calls đến /data/v1/auth đi qua service này.
// Component KHÔNG gọi axios/fetch trực tiếp.

import api from './api';

const authService = {
  /** Đăng ký tài khoản mới */
  register: async (data) => {
    const res = await api.post('/data/v1/auth/register', data);
    return res.data;
  },

  /** Đăng nhập — trả { token, user } */
  login: async (data) => {
    const res = await api.post('/data/v1/auth/login', data);
    return res.data;
  },

  /** Đăng xuất — chỉ xóa local storage (stateless JWT) */
  logout: async () => {
    try {
      await api.post('/data/v1/auth/logout');
    } catch (_) {
      // ignore errors — luôn xóa local storage
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    }
  },

  /** Lấy thông tin user đang đăng nhập */
  getMe: async () => {
    const res = await api.get('/data/v1/auth/me');
    return res.data;
  },
};

export default authService;

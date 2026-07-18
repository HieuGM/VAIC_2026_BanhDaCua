// services/profileService.js
// Tất cả calls đến /api/profile đi qua service này.

import api from './api';

const profileService = {
  /** Lấy hồ sơ cá nhân của user đang đăng nhập */
  getProfile: async () => {
    const res = await api.get('/api/profile');
    return res.data;
  },
};

export default profileService;

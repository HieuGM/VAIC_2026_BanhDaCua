// services/profileService.js
// Tất cả calls đến /data/v1/profile đi qua service này.

import api from './api';

const profileService = {
  /** Lấy hồ sơ cá nhân của user đang đăng nhập */
  getProfile: async () => {
    const res = await api.get('/data/v1/profile');
    return res.data;
  },
};

export default profileService;

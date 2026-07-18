// services/api.js
// Axios instance dùng chung cho các lời gọi tới data-api (BFF).
//
// baseURL lấy từ biến môi trường CRA (REACT_APP_ prefix bắt buộc).
// Mặc định trỏ về data-api BFF local trên :8081.
//
// TODO(phase-03+): thêm request interceptor để gắn X-Anon-Token header
// (anonymous session scoping) khi backend sẵn sàng.

import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8081',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

export default api;

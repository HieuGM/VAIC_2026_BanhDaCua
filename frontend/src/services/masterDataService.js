// services/masterDataService.js
// Calls đến master data APIs (departments, doctors, services, slots)

import api from './api';

const masterDataService = {
  getDepartments: async () => {
    const res = await api.get('/api/departments');
    return res.data;
  },

  getDoctors: async (params = {}) => {
    const res = await api.get('/api/doctors', { params });
    return res.data;
  },

  getDoctorById: async (id) => {
    const res = await api.get(`/api/doctors/${id}`);
    return res.data;
  },

  getSlotsByDoctor: async (doctorId, date) => {
    const res = await api.get('/api/appointment-slots', {
      params: { doctorId, date },
    });
    return res.data;
  },
};

export default masterDataService;

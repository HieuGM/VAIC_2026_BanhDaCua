// services/masterDataService.js
// Calls đến master data APIs (departments, doctors, services, slots)

import api from './api';

const masterDataService = {
  getDepartments: async () => {
    const res = await api.get('/data/v1/departments');
    return res.data;
  },

  getDoctors: async (params = {}) => {
    const res = await api.get('/data/v1/doctors', { params });
    return res.data;
  },

  getDoctorById: async (id) => {
    const res = await api.get(`/data/v1/doctors/${id}`);
    return res.data;
  },

  getSlotsByDoctor: async (doctorId, date) => {
    const res = await api.get('/data/v1/appointment-slots', {
      params: { doctorId, date },
    });
    return res.data;
  },
};

export default masterDataService;

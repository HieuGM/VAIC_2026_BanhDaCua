// services/appointmentService.js
// Tất cả calls đến /data/v1/appointments đi qua service này.
// Frontend KHÔNG truyền fhir_patient_id — backend tự resolve.

import api from './api';

const appointmentService = {
  /** Lấy danh sách lịch khám của user */
  getMyAppointments: async () => {
    const res = await api.get('/data/v1/appointments/me');
    return res.data;
  },

  /** Tạo lịch khám mới — chỉ gửi slotId + reason */
  createAppointment: async ({ slotId, reason }) => {
    const res = await api.post('/data/v1/appointments', { slotId, reason });
    return res.data;
  },

  /** Hủy lịch khám */
  cancelAppointment: async (id) => {
    const res = await api.patch(`/data/v1/appointments/${id}/cancel`);
    return res.data;
  },
};

export default appointmentService;

// pages/portal/Appointments.jsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import appointmentService from '../../services/appointmentService';
import './Appointments.css';

const STATUS_CONFIG = {
  PENDING:   { label: 'Chờ xác nhận', color: '#f6ad55', bg: 'rgba(246,173,85,0.12)' },
  CONFIRMED: { label: 'Đã xác nhận',  color: '#68d391', bg: 'rgba(72,187,120,0.12)' },
  CANCELLED: { label: 'Đã hủy',       color: '#fc8181', bg: 'rgba(252,129,129,0.12)' },
  COMPLETED: { label: 'Hoàn thành',   color: '#63b3ed', bg: 'rgba(99,179,237,0.12)' },
  NO_SHOW:   { label: 'Vắng mặt',     color: '#a0aec0', bg: 'rgba(160,174,192,0.12)' },
};

const FILTER_OPTIONS = [
  { value: 'all',       label: 'Tất cả' },
  { value: 'PENDING',   label: 'Chờ xác nhận' },
  { value: 'CONFIRMED', label: 'Đã xác nhận' },
  { value: 'COMPLETED', label: 'Hoàn thành' },
  { value: 'CANCELLED', label: 'Đã hủy' },
];

const formatDateTime = (iso) => {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
};

const Appointments = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [cancellingId, setCancellingId] = useState(null);
  const [toast, setToast] = useState('');

  const fetchAppointments = () => {
    setLoading(true);
    appointmentService.getMyAppointments()
      .then(setAppointments)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchAppointments(); }, []);

  const handleCancel = async (id) => {
    if (!window.confirm('Bạn có chắc muốn hủy lịch khám này?')) return;
    setCancellingId(id);
    try {
      await appointmentService.cancelAppointment(id);
      setAppointments((prev) =>
        prev.map((a) => a.id === id ? { ...a, status: 'CANCELLED' } : a)
      );
      setToast('Hủy lịch khám thành công');
      setTimeout(() => setToast(''), 3000);
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Hủy lịch thất bại';
      setToast(`❌ ${msg}`);
      setTimeout(() => setToast(''), 3500);
    } finally {
      setCancellingId(null);
    }
  };

  const filtered = filter === 'all'
    ? appointments
    : appointments.filter((a) => a.status === filter);

  return (
    <div className="appointments-page">
      {/* Toast */}
      {toast && <div className="appt-toast">{toast}</div>}

      {/* Header */}
      <div className="appt-page-header">
        <div>
          <h2 className="appt-page-title">📅 Lịch khám của tôi</h2>
          <p className="appt-page-subtitle">
            Quản lý lịch hẹn và theo dõi trạng thái khám bệnh
          </p>
        </div>
        <Link to="/portal/book" className="appt-new-btn" id="btn-new-appointment">
          + Đặt lịch mới
        </Link>
      </div>

      {/* Filter tabs */}
      <div className="appt-filter-bar">
        {FILTER_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            className={`appt-filter-btn ${filter === opt.value ? 'active' : ''}`}
            onClick={() => setFilter(opt.value)}
          >
            {opt.label}
            {opt.value === 'all' && (
              <span className="filter-count">{appointments.length}</span>
            )}
            {opt.value !== 'all' && (
              <span className="filter-count">
                {appointments.filter((a) => a.status === opt.value).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* List */}
      {loading ? (
        <div className="appt-loading">
          <div className="appt-spinner" />
          <span>Đang tải lịch khám...</span>
        </div>
      ) : filtered.length === 0 ? (
        <div className="appt-empty">
          <div style={{ fontSize: 64, marginBottom: 16 }}>📭</div>
          <h3>Không có lịch khám nào</h3>
          <p>
            {filter === 'all'
              ? 'Bạn chưa có lịch khám nào.'
              : `Không có lịch khám với trạng thái "${FILTER_OPTIONS.find(f => f.value === filter)?.label}".`}
          </p>
          <Link to="/portal/book" className="appt-new-btn" style={{ display: 'inline-flex', marginTop: 20 }}>
            + Đặt lịch ngay
          </Link>
        </div>
      ) : (
        <div className="appt-list">
          {filtered.map((appt) => {
            const sc = STATUS_CONFIG[appt.status] || STATUS_CONFIG.PENDING;
            const canCancel = appt.status === 'PENDING' || appt.status === 'CONFIRMED';
            return (
              <div key={appt.id} className="appt-card">
                {/* Left: status bar */}
                <div
                  className="appt-card-bar"
                  style={{ background: sc.color }}
                />
                <div className="appt-card-body">
                  <div className="appt-card-top">
                    <div className="appt-card-main">
                      <div className="appt-doctor-name">
                        {appt.doctorDegree} {appt.doctorName || '—'}
                      </div>
                      <div className="appt-specialty">
                        {appt.doctorSpecialty || appt.departmentName || '—'}
                      </div>
                    </div>
                    <div
                      className="appt-status-badge"
                      style={{ background: sc.bg, color: sc.color }}
                    >
                      {sc.label}
                    </div>
                  </div>

                  <div className="appt-card-details">
                    <div className="appt-detail-item">
                      <span className="detail-icon">🏥</span>
                      <span>{appt.departmentName || '—'}</span>
                    </div>
                    <div className="appt-detail-item">
                      <span className="detail-icon">🕐</span>
                      <span>{formatDateTime(appt.appointmentTime)}</span>
                    </div>
                    {appt.reason && (
                      <div className="appt-detail-item">
                        <span className="detail-icon">📝</span>
                        <span>{appt.reason}</span>
                      </div>
                    )}
                  </div>

                  {canCancel && (
                    <div className="appt-card-actions">
                      <button
                        className="appt-cancel-btn"
                        onClick={() => handleCancel(appt.id)}
                        disabled={cancellingId === appt.id}
                        id={`btn-cancel-${appt.id}`}
                      >
                        {cancellingId === appt.id ? '⏳ Đang hủy...' : '🗑 Hủy lịch'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Appointments;

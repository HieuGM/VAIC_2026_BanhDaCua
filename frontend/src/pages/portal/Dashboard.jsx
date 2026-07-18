// pages/portal/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import appointmentService from '../../services/appointmentService';
import './Dashboard.css';

const SHORTCUTS = [
  {
    to: '/portal/book',
    icon: '📅',
    label: 'Đặt lịch khám',
    color: 'rgba(66,153,225,0.15)',
  },
  {
    to: '/portal/profile',
    icon: '👤',
    label: 'Hồ sơ cá nhân',
    color: 'rgba(72,187,120,0.15)',
  },
  {
    to: '/services',
    icon: '🏥',
    label: 'Dịch vụ & Giá',
    color: 'rgba(237,137,54,0.15)',
  },
];

const formatDate = (iso) => {
  if (!iso) return null;
  const d = new Date(iso);
  return {
    day: d.getDate(),
    month: d.toLocaleString('vi-VN', { month: 'short' }),
    time: d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
  };
};

const Dashboard = () => {
  const { currentUser } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    appointmentService.getMyAppointments()
      .then(setAppointments)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const upcoming = appointments.filter(
    (a) => a.status === 'PENDING' || a.status === 'CONFIRMED'
  );
  const total = appointments.length;
  const completed = appointments.filter((a) => a.status === 'COMPLETED').length;
  const cancelled = appointments.filter((a) => a.status === 'CANCELLED').length;

  const firstName = currentUser?.fullName?.split(' ').pop() || 'bạn';

  return (
    <div className="dashboard-page">
      {/* Welcome Banner */}
      <div className="dash-welcome">
        <div className="dash-welcome-text">
          <h2>Xin chào, <span>{firstName}</span>! 👋</h2>
          <p>
            {new Date().toLocaleDateString('vi-VN', {
              weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
            })}
          </p>
        </div>
        <div className="dash-welcome-icon">❤️</div>
      </div>

      {/* Stats */}
      <div className="dash-stats">
        <div className="dash-stat-card">
          <div className="stat-icon blue">📅</div>
          <div className="stat-info">
            <div className="stat-value">{total}</div>
            <div className="stat-label">Tổng lịch khám</div>
          </div>
        </div>
        <div className="dash-stat-card">
          <div className="stat-icon green">✅</div>
          <div className="stat-info">
            <div className="stat-value">{completed}</div>
            <div className="stat-label">Đã hoàn thành</div>
          </div>
        </div>
        <div className="dash-stat-card">
          <div className="stat-icon red">🔜</div>
          <div className="stat-info">
            <div className="stat-value">{upcoming.length}</div>
            <div className="stat-label">Sắp tới</div>
          </div>
        </div>
      </div>

      {/* Upcoming Appointments */}
      <div className="dash-upcoming">
        <h3 className="dash-section-title">📋 Lịch khám sắp tới</h3>
        {loading ? (
          <div className="empty-state">
            <div className="empty-state-icon">⏳</div>
            <div>Đang tải...</div>
          </div>
        ) : upcoming.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📭</div>
            <div>Bạn chưa có lịch khám nào sắp tới</div>
            <Link
              to="/portal/book"
              style={{
                display: 'inline-block', marginTop: 16,
                color: '#63b3ed', textDecoration: 'none', fontWeight: 600,
              }}
            >
              Đặt lịch ngay →
            </Link>
          </div>
        ) : (
          <div className="upcoming-list">
            {upcoming.slice(0, 5).map((appt) => {
              const dateInfo = formatDate(appt.appointmentTime);
              return (
                <div key={appt.id} className="upcoming-item">
                  {dateInfo ? (
                    <div className="upcoming-date">
                      <div className="day">{dateInfo.day}</div>
                      <div className="month">{dateInfo.month}</div>
                    </div>
                  ) : (
                    <div className="upcoming-date">
                      <div className="day">—</div>
                    </div>
                  )}
                  <div className="upcoming-info">
                    <div className="upcoming-doctor">
                      {appt.doctorDegree} {appt.doctorName || 'Bác sĩ'}
                    </div>
                    <div className="upcoming-dept">
                      {appt.departmentName || 'Khoa phòng'}
                    </div>
                  </div>
                  {dateInfo && (
                    <div className="upcoming-time">{dateInfo.time}</div>
                  )}
                  <div className={`status-badge ${appt.status}`}>
                    {appt.status === 'PENDING' ? 'Chờ xác nhận'
                      : appt.status === 'CONFIRMED' ? 'Đã xác nhận'
                      : appt.status}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Shortcuts */}
      <div>
        <h3 className="dash-section-title">⚡ Truy cập nhanh</h3>
        <div className="dash-shortcuts">
          {SHORTCUTS.map((sc) => (
            <Link key={sc.to} to={sc.to} className="shortcut-card">
              <div className="shortcut-icon" style={{ background: sc.color }}>
                {sc.icon}
              </div>
              <div className="shortcut-label">{sc.label}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

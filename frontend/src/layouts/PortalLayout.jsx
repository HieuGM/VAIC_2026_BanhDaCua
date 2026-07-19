// layouts/PortalLayout.jsx
import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './PortalLayout.css';

const NAV_ITEMS = [
  { to: '/portal/dashboard', icon: '🏠', label: 'Dashboard' },
  { to: '/portal/profile',   icon: '👤', label: 'Hồ sơ cá nhân' },
  { to: '/portal/appointments', icon: '📅', label: 'Lịch khám của tôi' },
  { to: '/portal/book',      icon: '➕', label: 'Đặt lịch mới' },
];

const PortalLayout = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/', { replace: true });
  };

  const avatarInitial = currentUser?.fullName
    ? currentUser.fullName.charAt(0).toUpperCase()
    : '?';

  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div className="portal-wrapper">
      {/* Mobile topbar */}
      <div className="portal-mobile-topbar">
        <button
          className="mobile-menu-btn"
          onClick={() => setSidebarOpen(true)}
          aria-label="Mở menu"
        >
          ☰
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ fontSize: 20 }}>❤️</div>
          <span style={{ fontSize: 14, fontWeight: 700 }}>Patient Portal</span>
        </div>
        <div style={{ width: 36 }} />
      </div>

      {/* Sidebar overlay (mobile) */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'visible' : ''}`}
        onClick={closeSidebar}
      />

      {/* Sidebar */}
      <aside className={`portal-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">❤️</div>
          <div className="sidebar-logo-text">
            Bệnh viện Tim HN
            <span>Patient Portal</span>
          </div>
        </div>

        <div className="sidebar-section-label">Menu chính</div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `sidebar-nav-item ${isActive ? 'active' : ''}`
              }
              onClick={closeSidebar}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-section-label" style={{ marginTop: 16 }}>
          Hỗ trợ
        </div>
        <nav className="sidebar-nav">
          <NavLink
            to="/"
            className="sidebar-nav-item"
            onClick={closeSidebar}
          >
            <span className="nav-icon">🌐</span>
            Trang chủ
          </NavLink>
        </nav>

        {/* User card */}
        <div className="sidebar-user">
          <div className="sidebar-user-card">
            <div className="sidebar-user-avatar">{avatarInitial}</div>
            <div className="sidebar-user-info">
              <div className="sidebar-user-name">
                {currentUser?.fullName || 'Người dùng'}
              </div>
              <div className="sidebar-user-role">
                {currentUser?.role === 'PATIENT' ? 'Bệnh nhân' : currentUser?.role}
              </div>
            </div>
            <button
              className="sidebar-logout-btn"
              onClick={handleLogout}
              title="Đăng xuất"
              aria-label="Đăng xuất"
            >
              🚪
            </button>
          </div>
        </div>
      </aside>

      {/* Main content area */}
      <main className="portal-main">
        {/* Desktop topbar */}
        <div className="portal-topbar">
          <div>
            <div className="topbar-title">Patient Portal</div>
            <div className="topbar-subtitle">Bệnh viện Tim Hà Nội</div>
          </div>
          <div className="topbar-greeting">
            Xin chào, <strong>{currentUser?.fullName?.split(' ').pop() || 'bạn'}</strong>
          </div>
        </div>

        <div className="portal-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default PortalLayout;

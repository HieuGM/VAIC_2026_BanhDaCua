// pages/Login.jsx
import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/portal/dashboard';

  const [form, setForm] = useState({ identifier: '', password: '' });
  const [errors, setErrors] = useState({});
  const [globalError, setGlobalError] = useState('');
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const errs = {};
    if (!form.identifier.trim()) errs.identifier = 'Vui lòng nhập email hoặc số điện thoại';
    if (!form.password) errs.password = 'Vui lòng nhập mật khẩu';
    return errs;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: '' }));
    setGlobalError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    setLoading(true);
    try {
      await login(form.identifier, form.password);
      navigate(from, { replace: true });
    } catch (err) {
      const msg = err.response?.data?.error?.message
        || err.response?.data?.message
        || 'Đăng nhập thất bại. Vui lòng thử lại.';
      setGlobalError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        {/* Left — Branding */}
        <div className="login-brand">
          <div className="brand-logo">
            <div className="brand-logo-icon">❤️</div>
            <div className="brand-logo-text">
              Bệnh viện Tim Hà Nội
              <span>Hanoi Heart Hospital</span>
            </div>
          </div>
          <h1 className="brand-title">
            Chào mừng đến<br />
            <em>Patient Portal</em>
          </h1>
          <p className="brand-desc">
            Hệ thống quản lý chăm sóc sức khỏe thông minh, giúp bạn đặt lịch khám, 
            theo dõi lịch sử và quản lý thông tin cá nhân một cách tiện lợi.
          </p>
          <div className="brand-features">
            <div className="brand-feature">
              <span>Đặt lịch khám trực tuyến nhanh chóng</span>
            </div>
            <div className="brand-feature">
              <span>Bảo mật thông tin cá nhân tuyệt đối</span>
            </div>
            <div className="brand-feature">
              <span>Hỗ trợ AI Chatbot 24/7</span>
            </div>
          </div>
        </div>

        {/* Right — Form */}
        <div className="login-form-panel">
          <h2 className="login-form-title">Đăng nhập</h2>
          <p className="login-form-subtitle">Nhập thông tin tài khoản để tiếp tục</p>

          {globalError && (
            <div className="login-global-error">
              {globalError}
            </div>
          )}

          <form className="login-form" onSubmit={handleSubmit} noValidate>
            <div className="form-group">
              <label className="form-label" htmlFor="login-identifier">
                Email hoặc Số điện thoại
              </label>
              <div className="form-input-wrapper">
                <input
                  id="login-identifier"
                  className={`form-input ${errors.identifier ? 'error' : ''}`}
                  type="text"
                  name="identifier"
                  placeholder="email@example.com hoặc 0912..."
                  value={form.identifier}
                  onChange={handleChange}
                  autoComplete="username"
                  autoFocus
                />
              </div>
              {errors.identifier && (
                <span className="form-error">{errors.identifier}</span>
              )}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="login-password">
                Mật khẩu
              </label>
              <div className="form-input-wrapper">
                <input
                  id="login-password"
                  className={`form-input ${errors.password ? 'error' : ''}`}
                  type="password"
                  name="password"
                  placeholder="Nhập mật khẩu"
                  value={form.password}
                  onChange={handleChange}
                  autoComplete="current-password"
                />
              </div>
              {errors.password && (
                <span className="form-error">{errors.password}</span>
              )}
            </div>

            <button
              id="login-submit-btn"
              type="submit"
              className="login-submit-btn"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="btn-spinner" />
                  Đang đăng nhập...
                </>
              ) : (
                'Đăng nhập'
              )}
            </button>
          </form>

          <div className="login-divider">
            <span>Chưa có tài khoản?</span>
          </div>

          <p className="login-footer">
            <Link to="/register">Đăng ký tài khoản mới</Link>
          </p>
          <p className="login-footer" style={{ marginTop: 8 }}>
            <Link to="/">← Về trang chủ</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

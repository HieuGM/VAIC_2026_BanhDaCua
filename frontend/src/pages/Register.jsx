// pages/Register.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Register.css';

const Register = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    fullName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [globalError, setGlobalError] = useState('');
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const errs = {};
    if (!form.fullName.trim()) errs.fullName = 'Vui lòng nhập họ tên';
    if (!form.email.trim() && !form.phone.trim()) {
      errs.email = 'Vui lòng nhập email hoặc số điện thoại';
    }
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      errs.email = 'Email không hợp lệ';
    }
    if (!form.password) errs.password = 'Vui lòng nhập mật khẩu';
    else if (form.password.length < 8) errs.password = 'Mật khẩu phải có ít nhất 8 ký tự';
    if (form.password !== form.confirmPassword) {
      errs.confirmPassword = 'Mật khẩu xác nhận không khớp';
    }
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
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }

    setLoading(true);
    try {
      await register({
        fullName: form.fullName,
        email: form.email || undefined,
        phone: form.phone || undefined,
        password: form.password,
      });
      navigate('/portal/dashboard', { replace: true });
    } catch (err) {
      const msg = err.response?.data?.error?.message
        || err.response?.data?.message
        || 'Đăng ký thất bại. Vui lòng thử lại.';
      setGlobalError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="register-card">
        <div className="register-header">
          <div className="register-logo">❤️</div>
          <h1 className="register-title">Tạo tài khoản</h1>
          <p className="register-subtitle">Đăng ký để sử dụng Patient Portal</p>
        </div>

        {globalError && (
          <div className="register-global-error">
            {globalError}
          </div>
        )}

        <form className="register-form" onSubmit={handleSubmit} noValidate>
          {/* Họ tên */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-fullname">Họ và tên *</label>
            <div className="form-input-wrapper">
              <input
                id="reg-fullname"
                className={`form-input ${errors.fullName ? 'error' : ''}`}
                type="text"
                name="fullName"
                placeholder="Nguyễn Văn A"
                value={form.fullName}
                onChange={handleChange}
                autoFocus
              />
            </div>
            {errors.fullName && <span className="form-error">{errors.fullName}</span>}
          </div>

          {/* Email */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">Email</label>
            <div className="form-input-wrapper">
              <input
                id="reg-email"
                className={`form-input ${errors.email ? 'error' : ''}`}
                type="email"
                name="email"
                placeholder="email@example.com"
                value={form.email}
                onChange={handleChange}
                autoComplete="email"
              />
            </div>
            {errors.email && <span className="form-error">{errors.email}</span>}
            <span className="register-hint">Nhập email hoặc số điện thoại (ít nhất một)</span>
          </div>

          {/* Số điện thoại */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-phone">Số điện thoại</label>
            <div className="form-input-wrapper">
              <input
                id="reg-phone"
                className="form-input"
                type="tel"
                name="phone"
                placeholder="0912 345 678"
                value={form.phone}
                onChange={handleChange}
                autoComplete="tel"
              />
            </div>
          </div>

          {/* Mật khẩu */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-password">Mật khẩu *</label>
            <div className="form-input-wrapper">
              <input
                id="reg-password"
                className={`form-input ${errors.password ? 'error' : ''}`}
                type="password"
                name="password"
                placeholder="Tối thiểu 8 ký tự"
                value={form.password}
                onChange={handleChange}
                autoComplete="new-password"
              />
            </div>
            {errors.password && <span className="form-error">{errors.password}</span>}
          </div>

          {/* Xác nhận mật khẩu */}
          <div className="form-group">
            <label className="form-label" htmlFor="reg-confirm">Xác nhận mật khẩu *</label>
            <div className="form-input-wrapper">
              <input
                id="reg-confirm"
                className={`form-input ${errors.confirmPassword ? 'error' : ''}`}
                type="password"
                name="confirmPassword"
                placeholder="Nhập lại mật khẩu"
                value={form.confirmPassword}
                onChange={handleChange}
                autoComplete="new-password"
              />
            </div>
            {errors.confirmPassword && (
              <span className="form-error">{errors.confirmPassword}</span>
            )}
          </div>

          <button
            id="register-submit-btn"
            type="submit"
            className="register-submit-btn"
            disabled={loading}
          >
            {loading ? (
              <><div className="btn-spinner" /> Đang tạo tài khoản...</>
            ) : 'Tạo tài khoản'}
          </button>
        </form>

        <p className="register-footer">
          Đã có tài khoản? <Link to="/login">Đăng nhập ngay</Link>
        </p>
        <p className="register-footer" style={{ marginTop: 8 }}>
          <Link to="/" style={{ color: '#718096' }}>← Về trang chủ</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;

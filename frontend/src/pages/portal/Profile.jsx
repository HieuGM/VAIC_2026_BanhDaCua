// pages/portal/Profile.jsx
import React, { useEffect, useState } from 'react';
import profileService from '../../services/profileService';
import './Profile.css';

const InfoRow = ({ icon, label, value, masked }) => (
  <div className="profile-info-row">
    <div className="info-row-icon">{icon}</div>
    <div className="info-row-body">
      <div className="info-row-label">{label}</div>
      <div className={`info-row-value ${masked ? 'masked' : ''}`}>
        {value || <span className="info-empty">Chưa cập nhật</span>}
      </div>
    </div>
  </div>
);

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    profileService.getProfile()
      .then(setProfile)
      .catch(() => setError('Không thể tải thông tin hồ sơ'))
      .finally(() => setLoading(false));
  }, []);

  const formatDob = (dob) => {
    if (!dob) return null;
    return new Date(dob).toLocaleDateString('vi-VN', {
      day: '2-digit', month: '2-digit', year: 'numeric',
    });
  };

  const genderLabel = (g) => {
    if (g === 'male' || g === 'M') return '♂ Nam';
    if (g === 'female' || g === 'F') return '♀ Nữ';
    return g;
  };

  if (loading) {
    return (
      <div className="profile-loading">
        <div className="profile-spinner" />
        <span>Đang tải hồ sơ...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-error">
        <span>⚠️</span> {error}
      </div>
    );
  }

  const avatarInitial = profile?.fullName
    ? profile.fullName.charAt(0).toUpperCase()
    : '?';

  return (
    <div className="profile-page">
      {/* Header */}
      <div className="profile-header-card">
        <div className="profile-avatar-large">{avatarInitial}</div>
        <div className="profile-header-info">
          <h2 className="profile-header-name">{profile?.fullName}</h2>
          <div className="profile-header-role">
            {profile?.role === 'PATIENT' ? '🏥 Bệnh nhân' : profile?.role}
          </div>
          {profile?.hasFhirProfile && (
            <div className="profile-fhir-badge">✅ Hồ sơ FHIR đã liên kết</div>
          )}
        </div>
      </div>

      {/* Auth Info */}
      <div className="profile-section-card">
        <h3 className="profile-section-title">📋 Thông tin tài khoản</h3>
        <div className="profile-info-list">
          <InfoRow icon="👤" label="Họ và tên"  value={profile?.fullName} />
          <InfoRow icon="✉️" label="Email"       value={profile?.email} />
          <InfoRow icon="📱" label="Số điện thoại" value={profile?.phone} />
        </div>
      </div>

      {/* Personal Info (from FHIR cache) */}
      {profile?.hasFhirProfile && (
        <div className="profile-section-card">
          <h3 className="profile-section-title">🏥 Thông tin bệnh nhân</h3>
          <div className="profile-info-list">
            <InfoRow
              icon="🎂"
              label="Ngày sinh"
              value={formatDob(profile?.dateOfBirth)}
            />
            <InfoRow
              icon="⚧"
              label="Giới tính"
              value={genderLabel(profile?.gender)}
            />
            <InfoRow
              icon="🪪"
              label="CCCD / CMND"
              value={profile?.nationalIdMasked}
              masked
            />
          </div>
          <p className="profile-note">
            ⓘ Thông tin bệnh nhân được quản lý bởi hệ thống FHIR của bệnh viện. 
            Để cập nhật, vui lòng liên hệ bộ phận tiếp nhận.
          </p>
        </div>
      )}

      {!profile?.hasFhirProfile && (
        <div className="profile-no-fhir">
          <div style={{ fontSize: 48, marginBottom: 12 }}>🔗</div>
          <h4>Chưa có hồ sơ bệnh nhân</h4>
          <p>
            Hồ sơ FHIR của bạn chưa được liên kết.
            Vui lòng đến quầy tiếp nhận để đăng ký.
          </p>
        </div>
      )}
    </div>
  );
};

export default Profile;

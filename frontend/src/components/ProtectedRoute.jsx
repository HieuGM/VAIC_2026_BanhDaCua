// components/ProtectedRoute.jsx
// Redirect về /login nếu chưa xác thực.
// Hiện loading spinner trong khi kiểm tra session.

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a1628 0%, #1a2744 100%)',
      }}>
        <div style={{
          width: 48,
          height: 48,
          border: '3px solid rgba(99, 179, 237, 0.3)',
          borderTop: '3px solid #63b3ed',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Ghi nhớ trang người dùng đang muốn vào để redirect sau khi login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;

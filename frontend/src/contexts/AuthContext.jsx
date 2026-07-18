// contexts/AuthContext.jsx
// Quản lý trạng thái xác thực toàn cục.
// KHÔNG lưu fhir_patient_id ở bất kỳ đâu trong frontend.

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Khởi tạo từ localStorage khi app load
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');

    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setCurrentUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
      }
    }
    setIsLoading(false);
  }, []);

  /**
   * Đăng nhập — nhận AuthResponse từ server, lưu token vào localStorage.
   * KHÔNG lưu fhir_patient_id.
   */
  const login = useCallback(async (identifier, password) => {
    const data = await authService.login({ identifier, password });
    const { token: newToken, user } = data;

    localStorage.setItem('auth_token', newToken);
    localStorage.setItem('auth_user', JSON.stringify(user));

    setToken(newToken);
    setCurrentUser(user);

    return user;
  }, []);

  /**
   * Đăng ký — tự động đăng nhập sau khi tạo tài khoản.
   */
  const register = useCallback(async (formData) => {
    const data = await authService.register(formData);
    const { token: newToken, user } = data;

    localStorage.setItem('auth_token', newToken);
    localStorage.setItem('auth_user', JSON.stringify(user));

    setToken(newToken);
    setCurrentUser(user);

    return user;
  }, []);

  /**
   * Đăng xuất — xóa toàn bộ state và localStorage.
   */
  const logout = useCallback(async () => {
    await authService.logout();
    setToken(null);
    setCurrentUser(null);
  }, []);

  const isAuthenticated = !!token && !!currentUser;

  return (
    <AuthContext.Provider value={{
      currentUser,
      token,
      isAuthenticated,
      isLoading,
      login,
      register,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook tiện lợi để dùng trong component
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};

export default AuthContext;

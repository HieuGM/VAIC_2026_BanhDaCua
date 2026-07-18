import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import PortalLayout from '../layouts/PortalLayout';
import Home from '../pages/Home';
import About from '../pages/About';
import Services from '../pages/Services';
import Guide from '../pages/Guide';
import Booking from '../pages/Booking';
import Login from '../pages/Login';
import Register from '../pages/Register';
import ProtectedRoute from '../components/ProtectedRoute';

// Portal Pages
import Dashboard from '../pages/portal/Dashboard';
import Profile from '../pages/portal/Profile';
import Appointments from '../pages/portal/Appointments';
import BookAppointment from '../pages/portal/BookAppointment';

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Pages with MainLayout */}
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/services" element={<Services />} />
        <Route path="/guide" element={<Guide />} />
        <Route path="/booking" element={<Booking />} />
      </Route>

      {/* Auth Pages (no layouts or separate layout) */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected Patient Portal */}
      <Route
        path="/portal"
        element={
          <ProtectedRoute>
            <PortalLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/portal/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="appointments" element={<Appointments />} />
        <Route path="book" element={<BookAppointment />} />
      </Route>

      {/* Fallback to Home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;

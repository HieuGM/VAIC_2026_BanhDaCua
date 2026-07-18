// pages/portal/BookAppointment.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import masterDataService from '../../services/masterDataService';
import appointmentService from '../../services/appointmentService';
import './BookAppointment.css';

const STEPS = ['Chọn chuyên khoa', 'Chọn bác sĩ', 'Chọn lịch', 'Xác nhận'];

const BookAppointment = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);

  // Data
  const [departments, setDepartments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [slots, setSlots] = useState([]);

  // Selections
  const [selectedDept, setSelectedDept] = useState(null);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [slotDate, setSlotDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [reason, setReason] = useState('');

  // UI state
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Load departments
  useEffect(() => {
    setLoading(true);
    masterDataService.getDepartments()
      .then((data) => {
        const arr = Array.isArray(data) ? data : data.content ?? [];
        setDepartments(arr.filter((d) => d.isActive !== false));
      })
      .catch(() => setError('Không thể tải danh sách chuyên khoa'))
      .finally(() => setLoading(false));
  }, []);

  // Load doctors when dept changes
  useEffect(() => {
    if (!selectedDept) return;
    setLoading(true);
    setDoctors([]);
    setSelectedDoctor(null);
    masterDataService.getDoctors({ departmentId: selectedDept.id })
      .then((data) => {
        const arr = Array.isArray(data) ? data : data.content ?? [];
        setDoctors(arr.filter((d) => d.isActive !== false));
      })
      .catch(() => setError('Không thể tải danh sách bác sĩ'))
      .finally(() => setLoading(false));
  }, [selectedDept]);

  // Load slots when doctor/date changes
  useEffect(() => {
    if (!selectedDoctor || !slotDate) return;
    setLoading(true);
    setSlots([]);
    setSelectedSlot(null);
    masterDataService.getSlotsByDoctor(selectedDoctor.id, slotDate)
      .then((data) => {
        const arr = Array.isArray(data) ? data : data.content ?? [];
        setSlots(arr.filter((s) => s.isAvailable !== false && s.bookedCount < s.capacity));
      })
      .catch(() => setError('Không thể tải lịch trống'))
      .finally(() => setLoading(false));
  }, [selectedDoctor, slotDate]);

  const handleSubmit = async () => {
    if (!selectedSlot) return;
    setSubmitting(true);
    setError('');
    try {
      await appointmentService.createAppointment({
        slotId: selectedSlot.id,
        reason: reason.trim() || undefined,
      });
      setSuccess(true);
    } catch (err) {
      setError(
        err.response?.data?.error?.message || 'Đặt lịch thất bại. Vui lòng thử lại.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="book-success">
        <div className="book-success-icon">🎉</div>
        <h2>Đặt lịch thành công!</h2>
        <p>
          Lịch khám với <strong>{selectedDoctor?.fullName}</strong> vào ngày{' '}
          <strong>{new Date(slotDate).toLocaleDateString('vi-VN')}</strong>{' '}
          đã được ghi nhận.
        </p>
        <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)', marginTop: 8 }}>
          Bệnh viện sẽ liên hệ xác nhận trong thời gian sớm nhất.
        </p>
        <div className="book-success-actions">
          <button
            className="book-btn-primary"
            onClick={() => navigate('/portal/appointments')}
          >
            Xem lịch khám của tôi
          </button>
          <button
            className="book-btn-secondary"
            onClick={() => {
              setSuccess(false);
              setStep(0);
              setSelectedDept(null);
              setSelectedDoctor(null);
              setSelectedSlot(null);
              setReason('');
            }}
          >
            Đặt lịch khác
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="book-page">
      {/* Stepper */}
      <div className="book-stepper">
        {STEPS.map((s, i) => (
          <React.Fragment key={s}>
            <div className={`step-item ${i === step ? 'active' : i < step ? 'done' : ''}`}>
              <div className="step-circle">
                {i < step ? '✓' : i + 1}
              </div>
              <div className="step-label">{s}</div>
            </div>
            {i < STEPS.length - 1 && (
              <div className={`step-connector ${i < step ? 'done' : ''}`} />
            )}
          </React.Fragment>
        ))}
      </div>

      {error && (
        <div className="book-error">⚠️ {error}</div>
      )}

      <div className="book-panel">
        {/* Step 0: Chuyên khoa */}
        {step === 0 && (
          <div className="book-step">
            <h3 className="book-step-title">🏥 Chọn chuyên khoa</h3>
            {loading ? (
              <div className="book-loading"><div className="book-spinner" /> Đang tải...</div>
            ) : (
              <div className="dept-grid">
                {departments.map((dept) => (
                  <button
                    key={dept.id}
                    className={`dept-card ${selectedDept?.id === dept.id ? 'selected' : ''}`}
                    onClick={() => { setSelectedDept(dept); setStep(1); }}
                    id={`btn-dept-${dept.id}`}
                  >
                    <div className="dept-icon">🏥</div>
                    <div className="dept-name">{dept.name}</div>
                    {dept.campus && (
                      <div className="dept-campus">{dept.campus}</div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 1: Bác sĩ */}
        {step === 1 && (
          <div className="book-step">
            <div className="book-step-header">
              <button className="book-back-btn" onClick={() => setStep(0)}>← Quay lại</button>
              <h3 className="book-step-title">
                👨‍⚕️ Bác sĩ — <span style={{ color: '#63b3ed' }}>{selectedDept?.name}</span>
              </h3>
            </div>
            {loading ? (
              <div className="book-loading"><div className="book-spinner" /> Đang tải...</div>
            ) : doctors.length === 0 ? (
              <div className="book-empty">Không có bác sĩ trong khoa này</div>
            ) : (
              <div className="doctor-list">
                {doctors.map((doc) => (
                  <button
                    key={doc.id}
                    className={`doctor-card ${selectedDoctor?.id === doc.id ? 'selected' : ''}`}
                    onClick={() => { setSelectedDoctor(doc); setStep(2); }}
                    id={`btn-doctor-${doc.id}`}
                  >
                    <div className="doctor-avatar">
                      {doc.fullName?.charAt(0) || '?'}
                    </div>
                    <div className="doctor-info">
                      <div className="doctor-name">
                        {doc.degree} {doc.fullName}
                      </div>
                      <div className="doctor-specialty">{doc.specialty}</div>
                    </div>
                    <div className="doctor-arrow">→</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 2: Slot */}
        {step === 2 && (
          <div className="book-step">
            <div className="book-step-header">
              <button className="book-back-btn" onClick={() => setStep(1)}>← Quay lại</button>
              <h3 className="book-step-title">
                📅 Lịch trống — <span style={{ color: '#63b3ed' }}>{selectedDoctor?.fullName}</span>
              </h3>
            </div>

            <div className="book-date-picker">
              <label className="book-date-label">Chọn ngày khám:</label>
              <input
                id="book-date-input"
                type="date"
                className="book-date-input"
                value={slotDate}
                min={new Date().toISOString().split('T')[0]}
                onChange={(e) => setSlotDate(e.target.value)}
              />
            </div>

            {loading ? (
              <div className="book-loading"><div className="book-spinner" /> Đang tải lịch trống...</div>
            ) : slots.length === 0 ? (
              <div className="book-empty">
                Không có lịch trống vào ngày này.<br />Vui lòng chọn ngày khác.
              </div>
            ) : (
              <div className="slot-grid">
                {slots.map((slot) => (
                  <button
                    key={slot.id}
                    className={`slot-card ${selectedSlot?.id === slot.id ? 'selected' : ''}`}
                    onClick={() => setSelectedSlot(slot)}
                    id={`btn-slot-${slot.id}`}
                  >
                    <div className="slot-time">
                      {slot.startTime?.slice(0, 5)} – {slot.endTime?.slice(0, 5)}
                    </div>
                    <div className="slot-avail">
                      {slot.capacity - slot.bookedCount} chỗ trống
                    </div>
                  </button>
                ))}
              </div>
            )}

            {selectedSlot && (
              <button
                className="book-btn-primary"
                style={{ marginTop: 24 }}
                onClick={() => setStep(3)}
              >
                Tiếp theo →
              </button>
            )}
          </div>
        )}

        {/* Step 3: Xác nhận */}
        {step === 3 && (
          <div className="book-step">
            <div className="book-step-header">
              <button className="book-back-btn" onClick={() => setStep(2)}>← Quay lại</button>
              <h3 className="book-step-title">✅ Xác nhận đặt lịch</h3>
            </div>

            <div className="confirm-card">
              <div className="confirm-row">
                <span className="confirm-label">Chuyên khoa</span>
                <span className="confirm-value">{selectedDept?.name}</span>
              </div>
              <div className="confirm-row">
                <span className="confirm-label">Bác sĩ</span>
                <span className="confirm-value">
                  {selectedDoctor?.degree} {selectedDoctor?.fullName}
                </span>
              </div>
              <div className="confirm-row">
                <span className="confirm-label">Ngày khám</span>
                <span className="confirm-value">
                  {new Date(slotDate).toLocaleDateString('vi-VN', {
                    weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric',
                  })}
                </span>
              </div>
              <div className="confirm-row">
                <span className="confirm-label">Giờ khám</span>
                <span className="confirm-value">
                  {selectedSlot?.startTime?.slice(0, 5)} – {selectedSlot?.endTime?.slice(0, 5)}
                </span>
              </div>
            </div>

            <div className="book-reason">
              <label className="book-date-label" htmlFor="book-reason">
                Lý do khám (tuỳ chọn)
              </label>
              <textarea
                id="book-reason"
                className="book-reason-input"
                placeholder="Mô tả triệu chứng hoặc lý do khám..."
                rows={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </div>

            <button
              id="btn-confirm-booking"
              className="book-btn-primary"
              style={{ marginTop: 8 }}
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting ? (
                <><div className="book-spinner-sm" /> Đang đặt lịch...</>
              ) : '🎯 Xác nhận đặt lịch'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default BookAppointment;

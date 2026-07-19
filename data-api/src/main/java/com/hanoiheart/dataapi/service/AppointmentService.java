package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.appointment.AppointmentDto;
import com.hanoiheart.dataapi.dto.appointment.AppointmentRequest;
import com.hanoiheart.dataapi.entity.*;
import com.hanoiheart.dataapi.exception.BadRequestException;
import com.hanoiheart.dataapi.exception.NotFoundException;
import com.hanoiheart.dataapi.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Appointment service — quản lý lịch khám nghiệp vụ.
 * Backend tự lấy fhir_patient_id từ user_patient_links.
 * Frontend KHÔNG truyền fhir_patient_id.
 *
 * Controller → AppointmentService → Repository → Entity → DTO
 */
@Service
@RequiredArgsConstructor
public class AppointmentService {

    private final AppointmentRepository appointmentRepository;
    private final AppointmentSlotRepository slotRepository;
    private final UserRepository userRepository;
    private final UserPatientLinkRepository userPatientLinkRepository;

    /**
     * Lấy danh sách lịch khám của user đang đăng nhập.
     */
    @Transactional(readOnly = true)
    public List<AppointmentDto> getMyAppointments(Long userId) {
        return appointmentRepository.findByUserIdWithDetails(userId)
                .stream()
                .map(this::toDto)
                .collect(Collectors.toList());
    }

    /**
     * Tạo lịch khám mới.
     * Backend tự resolve fhir_patient_id từ user_patient_links.
     */
    @Transactional
    public AppointmentDto createAppointment(Long userId, AppointmentRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new NotFoundException("Người dùng không tồn tại"));

        AppointmentSlot slot = slotRepository.findById(request.getSlotId())
                .orElseThrow(() -> new NotFoundException("Slot không tồn tại"));

        // Kiểm tra slot còn chỗ
        if (slot.getBookedCount() >= slot.getCapacity()) {
            throw new BadRequestException("Slot đã đầy, vui lòng chọn slot khác");
        }
        if (!Boolean.TRUE.equals(slot.getIsAvailable())) {
            throw new BadRequestException("Slot không còn khả dụng");
        }

        // Backend tự lấy fhir_patient_id — frontend không biết
        String fhirPatientId = userPatientLinkRepository
                .findByUserIdAndIsPrimaryTrue(userId)
                .map(UserPatientLink::getFhirPatientId)
                .orElse(null);

        // Tạo appointment
        OffsetDateTime appointmentTime = slot.getDate()
                .atTime(slot.getStartTime())
                .atOffset(ZoneOffset.ofHours(7));

        Appointment appointment = Appointment.builder()
                .user(user)
                .fhirPatientId(fhirPatientId)
                .doctor(slot.getDoctor())
                .department(slot.getDepartment())
                .slot(slot)
                .appointmentTime(appointmentTime)
                .reason(request.getReason())
                .status("PENDING")
                .bookingChannel("WEB")
                .build();

        appointmentRepository.save(appointment);

        // Cập nhật booked_count
        slot.setBookedCount(slot.getBookedCount() + 1);
        if (slot.getBookedCount() >= slot.getCapacity()) {
            slot.setIsAvailable(false);
        }
        slotRepository.save(slot);

        return toDto(appointment);
    }

    /**
     * Hủy lịch khám — chỉ user sở hữu mới được hủy.
     */
    @Transactional
    public AppointmentDto cancelAppointment(Long userId, Long appointmentId) {
        Appointment appointment = appointmentRepository
                .findByIdAndUserId(appointmentId, userId)
                .orElseThrow(() -> new NotFoundException("Lịch khám không tồn tại"));

        if ("CANCELLED".equals(appointment.getStatus())) {
            throw new BadRequestException("Lịch khám đã được hủy trước đó");
        }
        if ("COMPLETED".equals(appointment.getStatus())) {
            throw new BadRequestException("Không thể hủy lịch khám đã hoàn thành");
        }

        appointment.setStatus("CANCELLED");

        // Hoàn lại slot
        AppointmentSlot slot = appointment.getSlot();
        if (slot != null && slot.getBookedCount() > 0) {
            slot.setBookedCount(slot.getBookedCount() - 1);
            slot.setIsAvailable(true);
            slotRepository.save(slot);
        }

        return toDto(appointmentRepository.save(appointment));
    }

    // ─── private helpers ─────────────────────────────────────────────────

    private AppointmentDto toDto(Appointment a) {
        AppointmentDto.AppointmentDtoBuilder b = AppointmentDto.builder()
                .id(a.getId())
                .appointmentTime(a.getAppointmentTime())
                .reason(a.getReason())
                .status(a.getStatus())
                .bookingChannel(a.getBookingChannel())
                .createdAt(a.getCreatedAt());

        if (a.getDoctor() != null) {
            b.doctorId(a.getDoctor().getId())
             .doctorName(a.getDoctor().getFullName())
             .doctorDegree(a.getDoctor().getDegree())
             .doctorSpecialty(a.getDoctor().getSpecialty());
        }
        if (a.getDepartment() != null) {
            b.departmentId(a.getDepartment().getId())
             .departmentName(a.getDepartment().getName());
        }
        if (a.getSlot() != null) {
            b.slotId(a.getSlot().getId());
        }

        return b.build();
    }
}

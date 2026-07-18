package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.appointment.AppointmentDto;
import com.hanoiheart.dataapi.dto.appointment.AppointmentRequest;
import com.hanoiheart.dataapi.service.AppointmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Appointment Controller.
 * GET    /api/appointments/me        — danh sách lịch khám của user
 * POST   /api/appointments           — tạo lịch khám mới
 * PATCH  /api/appointments/{id}/cancel — hủy lịch khám
 *
 * Frontend KHÔNG truyền fhir_patient_id — backend tự resolve.
 */
@RestController
@RequestMapping("/api/appointments")
@RequiredArgsConstructor
public class AppointmentController {

    private final AppointmentService appointmentService;

    /** Lấy danh sách lịch khám của user đang đăng nhập */
    @GetMapping("/me")
    public ResponseEntity<List<AppointmentDto>> getMyAppointments(
            @AuthenticationPrincipal Long userId) {
        return ResponseEntity.ok(appointmentService.getMyAppointments(userId));
    }

    /** Tạo lịch khám mới */
    @PostMapping
    public ResponseEntity<AppointmentDto> createAppointment(
            @AuthenticationPrincipal Long userId,
            @Valid @RequestBody AppointmentRequest request) {
        AppointmentDto dto = appointmentService.createAppointment(userId, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(dto);
    }

    /** Hủy lịch khám */
    @PatchMapping("/{id}/cancel")
    public ResponseEntity<AppointmentDto> cancelAppointment(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long id) {
        return ResponseEntity.ok(appointmentService.cancelAppointment(userId, id));
    }
}

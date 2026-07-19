package com.hanoiheart.dataapi.dto.appointment;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.OffsetDateTime;

/**
 * Response DTO cho lịch khám.
 * KHÔNG chứa fhir_patient_id.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AppointmentDto {

    private Long id;

    // Thông tin bác sĩ
    private Long doctorId;
    private String doctorName;
    private String doctorDegree;
    private String doctorSpecialty;

    // Thông tin khoa
    private Long departmentId;
    private String departmentName;
    private String room;

    // Thông tin slot
    private Long slotId;
    private OffsetDateTime appointmentTime;

    private String reason;

    /** PENDING | CONFIRMED | CANCELLED | COMPLETED | NO_SHOW */
    private String status;

    private String bookingChannel;
    private OffsetDateTime createdAt;
}

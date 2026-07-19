package com.hanoiheart.dataapi.dto.appointment;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * Request body cho POST /data/v1/appointments
 * Frontend chọn: slotId (hoặc doctorId + departmentId).
 * Frontend KHÔNG truyền fhir_patient_id — backend tự resolve.
 */
@Data
public class AppointmentRequest {

    @NotNull(message = "Vui lòng chọn slot")
    private Long slotId;

    /** Lý do khám (tùy chọn) */
    private String reason;
}

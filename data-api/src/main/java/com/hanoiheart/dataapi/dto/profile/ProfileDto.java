package com.hanoiheart.dataapi.dto.profile;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

/**
 * DTO cho GET /api/profile
 * Kết hợp thông tin từ users + patients_profile_cache.
 * KHÔNG chứa hồ sơ bệnh án, đơn thuốc, xét nghiệm, kết quả khám.
 * KHÔNG chứa fhir_patient_id.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProfileDto {

    // Từ bảng users
    private Long userId;
    private String fullName;
    private String email;
    private String phone;
    private String role;

    // Từ patients_profile_cache (nếu có liên kết FHIR)
    private LocalDate dateOfBirth;
    private String gender;
    private String nationalIdMasked;    // CCCD ẩn một phần

    /** true nếu đã có hồ sơ FHIR được liên kết */
    private boolean hasFhirProfile;
}

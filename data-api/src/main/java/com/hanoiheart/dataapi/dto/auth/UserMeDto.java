package com.hanoiheart.dataapi.dto.auth;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO cho GET /data/v1/auth/me
 * Chỉ trả thông tin auth user — KHÔNG chứa fhir_patient_id.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserMeDto {

    private Long id;
    private String fullName;
    private String email;
    private String phone;
    private String role;
    private String status;
}

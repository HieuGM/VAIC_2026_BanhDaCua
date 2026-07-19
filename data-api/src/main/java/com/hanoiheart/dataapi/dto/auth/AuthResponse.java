package com.hanoiheart.dataapi.dto.auth;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response for POST /data/v1/auth/login and POST /data/v1/auth/register.
 * KHÔNG chứa fhir_patient_id.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponse {

    private String token;
    private String tokenType;
    private Long expiresIn;

    /** Thông tin user cơ bản — không chứa dữ liệu y tế */
    private UserMeDto user;
}

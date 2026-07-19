package com.hanoiheart.dataapi.dto.auth;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * Request body for POST /data/v1/auth/login
 */
@Data
public class LoginRequest {

    /** Email hoặc phone */
    @NotBlank(message = "Email/SĐT không được để trống")
    private String identifier;

    @NotBlank(message = "Mật khẩu không được để trống")
    private String password;
}

package com.hanoiheart.dataapi.dto.auth;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * Request body for POST /data/v1/auth/register
 */
@Data
public class RegisterRequest {

    @NotBlank(message = "Họ tên không được để trống")
    private String fullName;

    @Email(message = "Email không hợp lệ")
    private String email;

    private String phone;

    @NotBlank(message = "Mật khẩu không được để trống")
    @Size(min = 8, message = "Mật khẩu phải có ít nhất 8 ký tự")
    private String password;
}

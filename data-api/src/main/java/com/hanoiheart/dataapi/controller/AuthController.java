package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.auth.*;
import com.hanoiheart.dataapi.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * Authentication Controller.
 * POST /data/v1/auth/register
 * POST /data/v1/auth/login
 * POST /data/v1/auth/logout
 * GET  /data/v1/auth/me
 *
 * Frontend KHÔNG truyền fhir_patient_id — backend tự resolve.
 * Convention /data/v1/* để đi qua nginx proxy (location /data/).
 */
@RestController
@RequestMapping("/data/v1/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    /** Đăng ký tài khoản mới */
    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        AuthResponse response = authService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /** Đăng nhập — trả JWT */
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        AuthResponse response = authService.login(request);
        return ResponseEntity.ok(response);
    }

    /**
     * Đăng xuất — stateless JWT nên chỉ trả 200.
     * Client tự xóa token khỏi storage.
     */
    @PostMapping("/logout")
    public ResponseEntity<Map<String, String>> logout() {
        return ResponseEntity.ok(Map.of("message", "Đăng xuất thành công"));
    }

    /** Lấy thông tin user hiện tại từ JWT */
    @GetMapping("/me")
    public ResponseEntity<UserMeDto> me(@AuthenticationPrincipal Long userId) {
        UserMeDto dto = authService.getMe(userId);
        return ResponseEntity.ok(dto);
    }
}

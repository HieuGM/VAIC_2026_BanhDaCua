package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.auth.*;
import com.hanoiheart.dataapi.entity.User;
import com.hanoiheart.dataapi.exception.BadRequestException;
import com.hanoiheart.dataapi.exception.NotFoundException;
import com.hanoiheart.dataapi.repository.UserRepository;
import com.hanoiheart.dataapi.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Business logic cho Authentication.
 * Controller → AuthService → UserRepository
 */
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Value("${hanoi-heart.jwt.expiration-ms}")
    private long expirationMs;

    /**
     * Đăng ký tài khoản mới.
     */
    @Transactional
    public AuthResponse register(RegisterRequest request) {
        // Kiểm tra email đã tồn tại
        if (request.getEmail() != null && userRepository.existsByEmail(request.getEmail())) {
            throw new BadRequestException("Email đã được sử dụng");
        }
        // Kiểm tra phone đã tồn tại
        if (request.getPhone() != null && userRepository.existsByPhone(request.getPhone())) {
            throw new BadRequestException("Số điện thoại đã được sử dụng");
        }

        User user = User.builder()
                .fullName(request.getFullName())
                .email(request.getEmail())
                .phone(request.getPhone())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .role("PATIENT")
                .status("ACTIVE")
                .build();

        userRepository.save(user);

        String token = jwtUtil.generateToken(user.getId(), user.getRole());
        return buildAuthResponse(token, user);
    }

    /**
     * Đăng nhập — xác thực email/phone + password, trả JWT.
     */
    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmailOrPhone(request.getIdentifier())
                .orElseThrow(() -> new BadRequestException("Email/SĐT hoặc mật khẩu không đúng"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new BadRequestException("Email/SĐT hoặc mật khẩu không đúng");
        }

        if (!"ACTIVE".equals(user.getStatus())) {
            throw new BadRequestException("Tài khoản đã bị vô hiệu hóa");
        }

        String token = jwtUtil.generateToken(user.getId(), user.getRole());
        return buildAuthResponse(token, user);
    }

    /**
     * Lấy thông tin user hiện tại từ userId (đã xác thực qua JWT filter).
     */
    public UserMeDto getMe(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new NotFoundException("Người dùng không tồn tại"));
        return toUserMeDto(user);
    }

    // ─── private helpers ─────────────────────────────────────────────────

    private AuthResponse buildAuthResponse(String token, User user) {
        return AuthResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .expiresIn(expirationMs / 1000)
                .user(toUserMeDto(user))
                .build();
    }

    private UserMeDto toUserMeDto(User user) {
        return UserMeDto.builder()
                .id(user.getId())
                .fullName(user.getFullName())
                .email(user.getEmail())
                .phone(user.getPhone())
                .role(user.getRole())
                .status(user.getStatus())
                .build();
    }
}

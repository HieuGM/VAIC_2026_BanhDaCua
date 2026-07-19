package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.profile.ProfileDto;
import com.hanoiheart.dataapi.service.ProfileService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * GET /data/v1/profile — lấy hồ sơ cá nhân của user đang đăng nhập.
 * Backend tự lấy fhir_patient_id từ JWT → user_patient_links.
 * Convention /data/v1/* để đi qua nginx proxy (location /data/).
 */
@RestController
@RequestMapping("/data/v1/profile")
@RequiredArgsConstructor
public class ProfileController {

    private final ProfileService profileService;

    @GetMapping
    public ResponseEntity<ProfileDto> getProfile(@AuthenticationPrincipal Long userId) {
        return ResponseEntity.ok(profileService.getProfile(userId));
    }
}

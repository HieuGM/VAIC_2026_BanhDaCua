package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.profile.ProfileDto;
import com.hanoiheart.dataapi.entity.PatientProfileCache;
import com.hanoiheart.dataapi.entity.User;
import com.hanoiheart.dataapi.entity.UserPatientLink;
import com.hanoiheart.dataapi.exception.NotFoundException;
import com.hanoiheart.dataapi.repository.PatientProfileCacheRepository;
import com.hanoiheart.dataapi.repository.UserPatientLinkRepository;
import com.hanoiheart.dataapi.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

/**
 * Profile service — trả thông tin cá nhân của user hiện tại.
 * Kết hợp: users + user_patient_links + patients_profile_cache.
 * KHÔNG trả fhir_patient_id ra ngoài.
 */
@Service
@RequiredArgsConstructor
public class ProfileService {

    private final UserRepository userRepository;
    private final UserPatientLinkRepository userPatientLinkRepository;
    private final PatientProfileCacheRepository patientProfileCacheRepository;

    /**
     * Lấy profile của user đã đăng nhập.
     * Backend tự tra cứu fhir_patient_id để lấy cache.
     */
    @Transactional(readOnly = true)
    public ProfileDto getProfile(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new NotFoundException("Người dùng không tồn tại"));

        ProfileDto.ProfileDtoBuilder builder = ProfileDto.builder()
                .userId(user.getId())
                .fullName(user.getFullName())
                .email(user.getEmail())
                .phone(user.getPhone())
                .role(user.getRole());

        // Tìm liên kết FHIR chính — backend tự xử lý, không lộ ra ngoài
        Optional<UserPatientLink> primaryLink =
                userPatientLinkRepository.findByUserIdAndIsPrimaryTrue(userId);

        if (primaryLink.isPresent()) {
            String fhirId = primaryLink.get().getFhirPatientId();
            patientProfileCacheRepository.findByFhirPatientId(fhirId)
                    .ifPresent(cache -> {
                        builder.dateOfBirth(cache.getDateOfBirth());
                        builder.gender(cache.getGender());
                        builder.nationalIdMasked(cache.getNationalIdMasked());
                        // Override fullName và phone từ cache nếu có
                        if (cache.getFullName() != null) builder.fullName(cache.getFullName());
                        if (cache.getPhone() != null) builder.phone(cache.getPhone());
                    });
            builder.hasFhirProfile(true);
        } else {
            builder.hasFhirProfile(false);
        }

        return builder.build();
    }
}

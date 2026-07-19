package com.hanoiheart.dataapi.config;

import com.hanoiheart.dataapi.entity.User;
import com.hanoiheart.dataapi.entity.UserPatientLink;
import com.hanoiheart.dataapi.repository.UserPatientLinkRepository;
import com.hanoiheart.dataapi.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.OffsetDateTime;
import java.util.List;

/**
 * Seed 3 demo auth accounts map → FHIR Patient có sẵn trong HAPI
 * (vn-patient-001/002/003: Nguyễn Minh Khang / Trần Thị Lan / Lê Văn Tùng).
 *
 * <p>Chỉ chạy khi {@code hanoi-heart.demo-seed.enabled=true} (mặc định false).
 * Password từ {@code hanoi-heart.demo-seed.password} (env DEMO_USER_PASSWORD) —
 * <b>không có default commit</b>. Nếu enabled nhưng password trống → log error
 * + skip (fail-safe: không tạo account yếu).
 *
 * <p>Idempotent: skip account/link đã tồn tại → re-run an toàn. Dùng
 * {@link PasswordEncoder} bean (BCrypt strength 10, SecurityConfig) — không pgcrypto,
 * không hash commit. Khớp seed trong infra/hapi-fhir/seed.
 */
@Component
@ConditionalOnProperty(name = "hanoi-heart.demo-seed.enabled", havingValue = "true")
public class DemoUserSeeder implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(DemoUserSeeder.class);

    /** Demo account → FHIR patient (khớp infra/hapi-fhir/seed bundle). */
    private static final List<DemoAccount> ACCOUNTS = List.of(
            new DemoAccount("minh.khang001@example.vn", "0903100001",
                    "Nguyễn Minh Khang", "vn-patient-001"),
            new DemoAccount("thi.lan002@example.vn", "0903100002",
                    "Trần Thị Lan", "vn-patient-002"),
            new DemoAccount("van.tung003@example.vn", "0903100003",
                    "Lê Văn Tùng", "vn-patient-003"));

    private final UserRepository userRepository;
    private final UserPatientLinkRepository linkRepository;
    private final PasswordEncoder passwordEncoder;
    private final String password;

    public DemoUserSeeder(UserRepository userRepository,
                          UserPatientLinkRepository linkRepository,
                          PasswordEncoder passwordEncoder,
                          @Value("${hanoi-heart.demo-seed.password:}") String password) {
        this.userRepository = userRepository;
        this.linkRepository = linkRepository;
        this.passwordEncoder = passwordEncoder;
        this.password = password;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (password == null || password.isBlank()) {
            log.error("[demo-seed] Enabled nhưng hanoi-heart.demo-seed.password trống — skip. "
                    + "Set DEMO_USER_PASSWORD để tạo demo accounts.");
            return;
        }
        int newLinks = 0;
        for (DemoAccount a : ACCOUNTS) {
            User user = userRepository.findByEmail(a.email()).orElseGet(() -> {
                User u = User.builder()
                        .email(a.email())
                        .phone(a.phone())
                        .fullName(a.fullName())
                        .passwordHash(passwordEncoder.encode(password))
                        .role("PATIENT")
                        .status("ACTIVE")
                        .build();
                log.info("[demo-seed] Tạo user {} ({})", a.email(), a.fullName());
                return userRepository.save(u);
            });
            if (!linkRepository.existsByUserIdAndFhirPatientId(user.getId(), a.fhirPatientId())) {
                linkRepository.save(UserPatientLink.builder()
                        .user(user)
                        .fhirPatientId(a.fhirPatientId())
                        .relationship("self")
                        .isPrimary(true)
                        .verifiedAt(OffsetDateTime.now())
                        .build());
                log.info("[demo-seed] Link {} → {}", a.email(), a.fhirPatientId());
                newLinks++;
            }
        }
        log.info("[demo-seed] Xong. {} link mới ({} accounts).", newLinks, ACCOUNTS.size());
    }

    private record DemoAccount(String email, String phone, String fullName, String fhirPatientId) {}
}

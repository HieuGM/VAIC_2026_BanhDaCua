package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.UserPatientLink;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface UserPatientLinkRepository extends JpaRepository<UserPatientLink, Long> {

    List<UserPatientLink> findByUserId(Long userId);

    /** Lấy link chính (is_primary = true) cho user */
    Optional<UserPatientLink> findByUserIdAndIsPrimaryTrue(Long userId);

    /** Kiểm tra user có được phép truy cập fhir patient này không */
    boolean existsByUserIdAndFhirPatientId(Long userId, String fhirPatientId);

    /** Lấy tất cả fhir patient IDs của một user */
    List<String> findFhirPatientIdByUserId(Long userId);
}

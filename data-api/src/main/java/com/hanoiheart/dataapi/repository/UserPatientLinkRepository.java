package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.UserPatientLink;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
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

    /**
     * Lấy tất cả fhir patient IDs của một user.
     * PHẢI dùng @Query tường minh (SELECT l.fhirPatientId) — derived query
     * 'findFhirPatientIdByUserId' bị Spring Data parse 'FhirPatientId' thành subject
     * hint (bị bỏ qua) → select cả entity UserPatientLink → QueryTypeMismatchException
     * ở runtime (Hibernate 6 strict). Xem ChatService.handleMessage.
     */
    @Query("SELECT l.fhirPatientId FROM UserPatientLink l WHERE l.user.id = :userId")
    List<String> findFhirPatientIdByUserId(@Param("userId") Long userId);
}

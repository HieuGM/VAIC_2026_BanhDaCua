package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.Doctor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface DoctorRepository extends JpaRepository<Doctor, Long> {

    Optional<Doctor> findByCode(String code);

    /**
     * Optional-predicate filter: both departmentId and specialty are nullable
     * (null ⇒ no constraint). Specialty is matched case-insensitively as a
     * substring (Vietnamese free-text, e.g. "Tim mạch").
     */
    @Query("""
           SELECT d FROM Doctor d
           WHERE d.isActive = true
             AND (:departmentId IS NULL OR d.department.id = :departmentId)
             AND (:specialty IS NULL OR LOWER(d.specialty) LIKE LOWER(CONCAT('%', CAST(:specialty AS string), '%')))
           """)
    Page<Doctor> findByFilter(@Param("departmentId") Long departmentId,
                              @Param("specialty") String specialty,
                              Pageable pageable);
}

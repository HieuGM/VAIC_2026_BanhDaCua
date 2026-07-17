package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.Doctor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DoctorRepository extends JpaRepository<Doctor, Long> {

    Optional<Doctor> findByCode(String code);

    Page<Doctor> findByDepartmentIdAndIsActiveTrue(Long departmentId, Pageable pageable);

    Page<Doctor> findByIsActiveTrue(Pageable pageable);
}

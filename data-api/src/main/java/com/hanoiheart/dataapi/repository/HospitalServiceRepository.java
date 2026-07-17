package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.HospitalService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface HospitalServiceRepository extends JpaRepository<HospitalService, Long> {

    Optional<HospitalService> findByCode(String code);

    @Query("""
        select s from HospitalService s
        where (:category is null or s.category = :category)
          and (:departmentId is null or s.department.id = :departmentId)
          and s.isActive = true
        order by s.category, s.name
    """)
    Page<HospitalService> findByFilter(@Param("category") String category,
                                       @Param("departmentId") Long departmentId,
                                       Pageable pageable);
}

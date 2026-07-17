package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.Procedure;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ProcedureRepository extends JpaRepository<Procedure, Long> {
    List<Procedure> findByCodeOrderByStepNoAsc(String code);
    List<Procedure> findAllByOrderByCodeAscStepNoAsc();
}

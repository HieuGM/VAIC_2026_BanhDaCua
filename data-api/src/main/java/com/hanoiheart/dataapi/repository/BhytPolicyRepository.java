package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.BhytPolicy;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface BhytPolicyRepository extends JpaRepository<BhytPolicy, Long> {
    List<BhytPolicy> findByCategoryOrderByCode(String category);
    List<BhytPolicy> findAllByOrderByCategoryAscCodeAsc();
}

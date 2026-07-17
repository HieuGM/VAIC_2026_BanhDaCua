package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.PriorityGroup;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface PriorityGroupRepository extends JpaRepository<PriorityGroup, Long> {
    List<PriorityGroup> findAllByOrderBySortOrderAscIdAsc();
}

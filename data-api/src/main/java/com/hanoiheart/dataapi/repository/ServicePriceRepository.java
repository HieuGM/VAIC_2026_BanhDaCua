package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.ServicePrice;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ServicePriceRepository extends JpaRepository<ServicePrice, Long> {
    List<ServicePrice> findByServiceIdOrderByAudienceAscCampusAsc(Long serviceId);
}

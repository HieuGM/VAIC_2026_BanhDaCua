package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.HospitalInfo;
import org.springframework.data.jpa.repository.JpaRepository;

public interface HospitalInfoRepository extends JpaRepository<HospitalInfo, Long> {
}

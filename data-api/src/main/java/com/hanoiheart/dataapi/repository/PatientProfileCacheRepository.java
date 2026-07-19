package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.PatientProfileCache;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PatientProfileCacheRepository extends JpaRepository<PatientProfileCache, Long> {

    Optional<PatientProfileCache> findByFhirPatientId(String fhirPatientId);
}

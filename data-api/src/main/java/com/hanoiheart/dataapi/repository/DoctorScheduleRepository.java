package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.DoctorSchedule;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;
import java.util.List;

public interface DoctorScheduleRepository extends JpaRepository<DoctorSchedule, Long> {

    List<DoctorSchedule> findByDoctorIdAndEffectiveDateBetweenOrderByEffectiveDateAscStartTimeAsc(
            Long doctorId, LocalDate from, LocalDate to);

    List<DoctorSchedule> findByDoctorIdOrderByEffectiveDateAscStartTimeAsc(Long doctorId);
}

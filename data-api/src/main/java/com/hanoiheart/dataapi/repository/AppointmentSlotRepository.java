package com.hanoiheart.dataapi.repository;

import com.hanoiheart.dataapi.entity.AppointmentSlot;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;
import java.util.List;

public interface AppointmentSlotRepository extends JpaRepository<AppointmentSlot, Long> {

    List<AppointmentSlot> findByDoctorIdAndDateOrderByStartTimeAsc(Long doctorId, LocalDate date);

    List<AppointmentSlot> findByDateOrderByStartTimeAsc(LocalDate date);
}

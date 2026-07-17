package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.AppointmentSlotDto;
import com.hanoiheart.dataapi.entity.AppointmentSlot;
import com.hanoiheart.dataapi.repository.AppointmentSlotRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class AppointmentSlotService {

    private final AppointmentSlotRepository repository;

    public AppointmentSlotService(AppointmentSlotRepository repository) {
        this.repository = repository;
    }

    public List<AppointmentSlotDto> query(Long doctorId, LocalDate date) {
        List<AppointmentSlot> rows;
        if (doctorId != null && date != null) {
            rows = repository.findByDoctorIdAndDateOrderByStartTimeAsc(doctorId, date);
        } else if (date != null) {
            rows = repository.findByDateOrderByStartTimeAsc(date);
        } else {
            rows = List.of();
        }
        return rows.stream().map(this::toDto).toList();
    }

    private AppointmentSlotDto toDto(AppointmentSlot s) {
        int booked = s.getBookedCount() == null ? 0 : s.getBookedCount();
        int cap = s.getCapacity() == null ? 0 : s.getCapacity();
        return new AppointmentSlotDto(s.getId(), s.getDoctor().getId(),
                s.getDepartment() == null ? null : s.getDepartment().getId(),
                s.getDate(), s.getStartTime(), s.getEndTime(),
                cap, booked, Math.max(0, cap - booked), s.getIsAvailable());
    }
}

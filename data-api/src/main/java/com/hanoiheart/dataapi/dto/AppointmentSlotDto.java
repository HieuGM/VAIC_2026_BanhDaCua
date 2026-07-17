package com.hanoiheart.dataapi.dto;

import java.time.LocalDate;
import java.time.LocalTime;

public record AppointmentSlotDto(
        Long id,
        Long doctorId,
        Long departmentId,
        LocalDate date,
        LocalTime startTime,
        LocalTime endTime,
        Integer capacity,
        Integer bookedCount,
        Integer available,
        Boolean isAvailable
) {}

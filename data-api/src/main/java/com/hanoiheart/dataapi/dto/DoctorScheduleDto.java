package com.hanoiheart.dataapi.dto;

import java.time.LocalDate;
import java.time.LocalTime;

public record DoctorScheduleDto(
        Long id,
        Long doctorId,
        Long departmentId,
        Integer dayOfWeek,
        LocalDate effectiveDate,
        LocalTime startTime,
        LocalTime endTime,
        String shift,
        String room,
        String note
) {}

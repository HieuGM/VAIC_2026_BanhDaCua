package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.DoctorDto;
import com.hanoiheart.dataapi.dto.DoctorScheduleDto;
import com.hanoiheart.dataapi.dto.PageResponse;
import com.hanoiheart.dataapi.entity.Department;
import com.hanoiheart.dataapi.entity.Doctor;
import com.hanoiheart.dataapi.entity.DoctorSchedule;
import com.hanoiheart.dataapi.repository.DoctorRepository;
import com.hanoiheart.dataapi.repository.DoctorScheduleRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class DoctorService {

    private final DoctorRepository doctorRepository;
    private final DoctorScheduleRepository scheduleRepository;

    public DoctorService(DoctorRepository doctorRepository,
                         DoctorScheduleRepository scheduleRepository) {
        this.doctorRepository = doctorRepository;
        this.scheduleRepository = scheduleRepository;
    }

    public PageResponse<DoctorDto> list(Long departmentId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Doctor> result = (departmentId == null)
                ? doctorRepository.findByIsActiveTrue(pageable)
                : doctorRepository.findByDepartmentIdAndIsActiveTrue(departmentId, pageable);
        return PageResponse.of(result.map(this::toDto));
    }

    public DoctorDto get(Long id) {
        return doctorRepository.findById(id).map(this::toDto).orElse(null);
    }

    public List<DoctorScheduleDto> schedules(Long doctorId, LocalDate from, LocalDate to) {
        List<DoctorSchedule> rows = (from != null && to != null)
                ? scheduleRepository.findByDoctorIdAndEffectiveDateBetweenOrderByEffectiveDateAscStartTimeAsc(doctorId, from, to)
                : scheduleRepository.findByDoctorIdOrderByEffectiveDateAscStartTimeAsc(doctorId);
        return rows.stream().map(this::toScheduleDto).toList();
    }

    public DoctorDto toDto(Doctor d) {
        Department dept = d.getDepartment();
        return new DoctorDto(d.getId(), d.getCode(), d.getFullName(), d.getDegree(),
                d.getTitle(),
                dept == null ? null : dept.getId(),
                dept == null ? null : dept.getCode(),
                dept == null ? null : dept.getName(),
                d.getBio(), d.getAvatarUrl());
    }

    private DoctorScheduleDto toScheduleDto(DoctorSchedule s) {
        return new DoctorScheduleDto(s.getId(), s.getDoctor().getId(),
                s.getDepartment() == null ? null : s.getDepartment().getId(),
                s.getDayOfWeek(), s.getEffectiveDate(), s.getStartTime(), s.getEndTime(),
                s.getShift(), s.getRoom(), s.getNote());
    }
}

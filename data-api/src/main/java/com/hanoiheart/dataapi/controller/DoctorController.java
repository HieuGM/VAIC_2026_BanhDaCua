package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.DoctorDto;
import com.hanoiheart.dataapi.dto.DoctorScheduleDto;
import com.hanoiheart.dataapi.dto.PageResponse;
import com.hanoiheart.dataapi.service.DoctorService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/data/v1/doctors")
public class DoctorController {

    private final DoctorService service;

    public DoctorController(DoctorService service) {
        this.service = service;
    }

    @GetMapping
    public PageResponse<DoctorDto> list(
            @RequestParam(name = "department", required = false) Long departmentId,
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "20") int size) {
        return service.list(departmentId, page, size);
    }

    @GetMapping("/{id}")
    public DoctorDto get(@PathVariable Long id) {
        return service.get(id);
    }

    @GetMapping("/{id}/schedules")
    public List<DoctorScheduleDto> schedules(
            @PathVariable Long id,
            @RequestParam(name = "from", required = false)
                @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
            @RequestParam(name = "to", required = false)
                @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {
        return service.schedules(id, from, to);
    }
}

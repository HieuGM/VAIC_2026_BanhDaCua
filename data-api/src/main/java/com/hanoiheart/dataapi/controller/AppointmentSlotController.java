package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.AppointmentSlotDto;
import com.hanoiheart.dataapi.service.AppointmentSlotService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/data/v1/appointment-slots")
public class AppointmentSlotController {

    private final AppointmentSlotService service;

    public AppointmentSlotController(AppointmentSlotService service) {
        this.service = service;
    }

    @GetMapping
    public List<AppointmentSlotDto> list(
            @RequestParam(name = "doctor", required = false) Long doctorId,
            @RequestParam(name = "date", required = false)
                @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return service.query(doctorId, date);
    }
}

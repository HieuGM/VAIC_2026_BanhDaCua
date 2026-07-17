package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.HospitalInfoDto;
import com.hanoiheart.dataapi.service.HospitalInfoService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/data/v1/hospital-info")
public class HospitalInfoController {

    private final HospitalInfoService service;

    public HospitalInfoController(HospitalInfoService service) {
        this.service = service;
    }

    @GetMapping
    public HospitalInfoDto get() {
        return service.getCurrent();
    }
}

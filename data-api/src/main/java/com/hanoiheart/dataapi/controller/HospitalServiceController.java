package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.HospitalServiceDto;
import com.hanoiheart.dataapi.dto.PageResponse;
import com.hanoiheart.dataapi.dto.ServicePriceDto;
import com.hanoiheart.dataapi.service.HospitalServiceService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/data/v1/services")
public class HospitalServiceController {

    private final HospitalServiceService service;

    public HospitalServiceController(HospitalServiceService service) {
        this.service = service;
    }

    @GetMapping
    public PageResponse<HospitalServiceDto> list(
            @RequestParam(name = "category", required = false) String category,
            @RequestParam(name = "department", required = false) Long departmentId,
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "50") int size) {
        return service.list(category, departmentId, page, size);
    }

    @GetMapping("/{id}/prices")
    public List<ServicePriceDto> prices(@PathVariable Long id) {
        return service.prices(id);
    }
}

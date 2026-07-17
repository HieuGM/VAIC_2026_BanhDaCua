package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.DepartmentDto;
import com.hanoiheart.dataapi.dto.PageResponse;
import com.hanoiheart.dataapi.service.DepartmentService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/data/v1/departments")
public class DepartmentController {

    private final DepartmentService service;

    public DepartmentController(DepartmentService service) {
        this.service = service;
    }

    @GetMapping
    public PageResponse<DepartmentDto> list(
            @RequestParam(name = "active", required = false) Boolean active,
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "50") int size) {
        List<DepartmentDto> all = service.list(active);
        int from = Math.min(page * size, all.size());
        int to = Math.min(from + size, all.size());
        return PageResponse.ofList(all.size(), page, size, all.subList(from, to));
    }
}

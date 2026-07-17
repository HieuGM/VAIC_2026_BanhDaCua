package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.ProcedureDto;
import com.hanoiheart.dataapi.service.ProcedureService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/data/v1/procedures")
public class ProcedureController {

    private final ProcedureService service;

    public ProcedureController(ProcedureService service) {
        this.service = service;
    }

    @GetMapping
    public List<ProcedureDto> list(@RequestParam(name = "code", required = false) String code) {
        return service.list(code);
    }
}

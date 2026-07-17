package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.BhytPolicyDto;
import com.hanoiheart.dataapi.service.BhytPolicyService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/data/v1/bhyt-policies")
public class BhytPolicyController {

    private final BhytPolicyService service;

    public BhytPolicyController(BhytPolicyService service) {
        this.service = service;
    }

    @GetMapping
    public List<BhytPolicyDto> list(@RequestParam(name = "category", required = false) String category) {
        return service.list(category);
    }
}

package com.hanoiheart.dataapi.controller;

import com.hanoiheart.dataapi.dto.SupportChannelDto;
import com.hanoiheart.dataapi.service.SupportChannelService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/data/v1/channels")
public class SupportChannelController {

    private final SupportChannelService service;

    public SupportChannelController(SupportChannelService service) {
        this.service = service;
    }

    @GetMapping
    public List<SupportChannelDto> list() {
        return service.list();
    }
}

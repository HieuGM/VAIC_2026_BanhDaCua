package com.hanoiheart.dataapi.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.hanoiheart.dataapi.dto.HospitalInfoDto;
import com.hanoiheart.dataapi.entity.HospitalInfo;
import com.hanoiheart.dataapi.repository.HospitalInfoRepository;
import org.springframework.stereotype.Service;

@Service
public class HospitalInfoService {

    private final HospitalInfoRepository repository;
    private final ObjectMapper json;

    public HospitalInfoService(HospitalInfoRepository repository, ObjectMapper json) {
        this.repository = repository;
        this.json = json;
    }

    public HospitalInfoDto getCurrent() {
        return repository.findAll().stream().findFirst()
                .map(this::toDto)
                .orElse(null);
    }

    private HospitalInfoDto toDto(HospitalInfo h) {
        return new HospitalInfoDto(
                h.getId(), h.getName(), h.getShortName(), h.getNameEn(), h.getSlogan(),
                parseJson(h.getAddresses()), h.getHotline(),
                parseJson(h.getWorkingHours()), h.getGrade(),
                h.getEstablishedYear(), h.getWebsite()
        );
    }

    private JsonNode parseJson(String raw) {
        if (raw == null || raw.isBlank()) return null;
        try {
            return json.readTree(raw);
        } catch (JsonProcessingException e) {
            return null;
        }
    }
}

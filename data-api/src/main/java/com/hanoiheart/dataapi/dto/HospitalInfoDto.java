package com.hanoiheart.dataapi.dto;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * Response shape for {@code GET /data/v1/hospital-info}.
 */
public record HospitalInfoDto(
        Long id,
        String name,
        String shortName,
        String nameEn,
        String slogan,
        JsonNode addresses,
        String hotline,
        JsonNode workingHours,
        String grade,
        Integer establishedYear,
        String website
) {}

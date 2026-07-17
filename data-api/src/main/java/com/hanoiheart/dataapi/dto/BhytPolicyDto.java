package com.hanoiheart.dataapi.dto;

import java.time.LocalDate;

public record BhytPolicyDto(
        Long id,
        String code,
        String title,
        String category,
        String summary,
        String detailsMd,
        String sourceUrl,
        LocalDate effectiveDate
) {}

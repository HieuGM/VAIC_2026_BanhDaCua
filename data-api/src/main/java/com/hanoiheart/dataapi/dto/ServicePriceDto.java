package com.hanoiheart.dataapi.dto;

import java.math.BigInteger;
import java.time.LocalDate;

public record ServicePriceDto(
        Long id,
        BigInteger priceVnd,
        String audience,
        String campus,
        LocalDate effectiveDate,
        String sourceUrl,
        String note
) {}

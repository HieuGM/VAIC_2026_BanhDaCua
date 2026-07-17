package com.hanoiheart.dataapi.dto;

public record HospitalServiceDto(
        Long id,
        String code,
        String name,
        String category,
        Long departmentId,
        String description
) {}

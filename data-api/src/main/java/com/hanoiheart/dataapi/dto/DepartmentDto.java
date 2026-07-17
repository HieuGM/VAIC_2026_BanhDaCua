package com.hanoiheart.dataapi.dto;

public record DepartmentDto(
        Long id,
        String code,
        String name,
        String nameEn,
        String description,
        String campus,
        String floor,
        String workingHours,
        String phone,
        Integer sortOrder,
        Boolean isActive
) {}

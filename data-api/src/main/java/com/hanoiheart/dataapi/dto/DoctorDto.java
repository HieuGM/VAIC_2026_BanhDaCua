package com.hanoiheart.dataapi.dto;

public record DoctorDto(
        Long id,
        String code,
        String fullName,
        String degree,
        String specialty,
        String title,
        Long departmentId,
        String departmentCode,
        String departmentName,
        String bio,
        String avatarUrl
) {}

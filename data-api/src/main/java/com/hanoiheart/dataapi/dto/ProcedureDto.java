package com.hanoiheart.dataapi.dto;

public record ProcedureDto(
        Long id,
        String code,
        String title,
        Integer stepNo,
        String name,
        String description,
        String responsibleRole,
        String relatedForm,
        String sourceDoc
) {}

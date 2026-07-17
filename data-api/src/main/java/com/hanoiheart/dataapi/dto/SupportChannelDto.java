package com.hanoiheart.dataapi.dto;

public record SupportChannelDto(
        Long id,
        String channelType,
        String label,
        String url,
        String phone,
        String campus,
        Integer sortOrder
) {}

package com.hanoiheart.dataapi.dto;

import org.springframework.data.domain.Page;

import java.util.List;

/**
 * Generic paginated list envelope for /data/v1 list endpoints.
 */
public record PageResponse<T>(
        long total,
        int page,
        int size,
        int totalPages,
        List<T> items
) {
    public static <T> PageResponse<T> of(Page<T> p) {
        return new PageResponse<>(
                p.getTotalElements(),
                p.getNumber(),
                p.getSize(),
                p.getTotalPages(),
                p.getContent()
        );
    }

    public static <T> PageResponse<T> ofList(long total, int page, int size, List<T> items) {
        int totalPages = size > 0 ? (int) Math.ceil((double) total / size) : 1;
        return new PageResponse<>(total, page, size, totalPages, items);
    }
}

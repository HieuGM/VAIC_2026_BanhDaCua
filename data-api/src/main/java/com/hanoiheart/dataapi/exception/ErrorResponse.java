package com.hanoiheart.dataapi.exception;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

/**
 * Uniform error envelope per docs/07-api-design.md §7.
 * Serializes exactly to {@code {"error":{"code","message"}}}.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record ErrorResponse(ErrorBody error) {

    /** Factory for the common case of a single code+message pair. */
    public static ErrorResponse of(String code, String message) {
        return new ErrorResponse(new ErrorBody(code, message));
    }

    /** Inner {@code error} object: stable field order for client parsing. */
    @JsonPropertyOrder({"code", "message"})
    public record ErrorBody(String code, String message) {}
}

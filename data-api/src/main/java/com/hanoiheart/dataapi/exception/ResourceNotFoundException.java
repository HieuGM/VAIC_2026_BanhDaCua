package com.hanoiheart.dataapi.exception;

/**
 * Thrown when a requested resource (lookup by id) does not exist.
 * Mapped by {@link GlobalExceptionHandler} to HTTP 404 with code {@code not_found}.
 */
public class ResourceNotFoundException extends RuntimeException {

    public ResourceNotFoundException(String message) {
        super(message);
    }

    public ResourceNotFoundException(String resource, Long id) {
        super(resource + " not found: id=" + id);
    }
}

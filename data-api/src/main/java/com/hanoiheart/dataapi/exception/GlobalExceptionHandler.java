package com.hanoiheart.dataapi.exception;

import jakarta.persistence.EntityNotFoundException;
import jakarta.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

import java.util.NoSuchElementException;

/**
 * Maps domain &amp; framework exceptions to the uniform error envelope
 * {@code {"error":{"code","message"}}} per docs/07-api-design.md §7.
 *
 * <p>Status mapping:
 * <ul>
 *   <li><b>404 not_found</b> — {@link NoSuchElementException},
 *       {@link ResourceNotFoundException}, {@link EntityNotFoundException},
 *       {@link EmptyResultDataAccessException}</li>
 *   <li><b>400 bad_request</b> — {@link MethodArgumentNotValidException},
 *       {@link ConstraintViolationException},
 *       {@link MissingServletRequestParameterException},
 *       {@link MethodArgumentTypeMismatchException},
 *       {@link IllegalArgumentException},
 *       {@link HttpMessageNotReadableException}</li>
 *   <li><b>500 internal_error</b> — fallback {@link Exception}</li>
 * </ul>
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /** 404 — resource not found. */
    @ExceptionHandler({
            NoSuchElementException.class,
            ResourceNotFoundException.class,
            NotFoundException.class,
            EntityNotFoundException.class,
            EmptyResultDataAccessException.class
    })
    public ResponseEntity<ErrorResponse> notFound(Exception ex) {
        return body(HttpStatus.NOT_FOUND, "not_found", messageOf(ex));
    }

    /** 400 — business validation failure. */
    @ExceptionHandler(BadRequestException.class)
    public ResponseEntity<ErrorResponse> badRequestBusiness(BadRequestException ex) {
        return body(HttpStatus.BAD_REQUEST, "bad_request", ex.getMessage());
    }

    /** 403 — access denied. */
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> accessDenied(AccessDeniedException ex) {
        return body(HttpStatus.FORBIDDEN, "forbidden", "Bạn không có quyền thực hiện thao tác này");
    }

    /** 400 — bean validation failure on @Valid request body. */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> validation(MethodArgumentNotValidException ex) {
        String msg = ex.getBindingResult().getFieldErrors().stream()
                .findFirst()
                .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
                .orElse("validation failed");
        return body(HttpStatus.BAD_REQUEST, "bad_request", msg);
    }

    /** 400 — @RequestParam / @PathVariable constraint violation. */
    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ErrorResponse> constraint(ConstraintViolationException ex) {
        return body(HttpStatus.BAD_REQUEST, "bad_request", messageOf(ex));
    }

    /** 400 — required query/form parameter missing. */
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<ErrorResponse> missingParam(MissingServletRequestParameterException ex) {
        return body(HttpStatus.BAD_REQUEST, "bad_request",
                "Missing required parameter: " + ex.getParameterName());
    }

    /** 400 — path/query param cannot be coerced to target type. */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<ErrorResponse> typeMismatch(MethodArgumentTypeMismatchException ex) {
        return body(HttpStatus.BAD_REQUEST, "bad_request", "Invalid parameter: " + ex.getName());
    }

    /** 400 — illegal argument or malformed JSON body. */
    @ExceptionHandler({IllegalArgumentException.class, HttpMessageNotReadableException.class})
    public ResponseEntity<ErrorResponse> badRequest(Exception ex) {
        return body(HttpStatus.BAD_REQUEST, "bad_request", messageOf(ex));
    }

    /** 500 — catch-all for unexpected server errors (message not leaked). */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> internal(Exception ex) {
        log.error("Unhandled exception propagated to advice", ex);
        return body(HttpStatus.INTERNAL_SERVER_ERROR, "internal_error", "Unexpected server error");
    }

    private ResponseEntity<ErrorResponse> body(HttpStatus status, String code, String message) {
        return ResponseEntity.status(status).body(ErrorResponse.of(code, message));
    }

    private static String messageOf(Exception ex) {
        String msg = ex.getMessage();
        return (msg == null || msg.isBlank()) ? "no detail" : msg;
    }
}

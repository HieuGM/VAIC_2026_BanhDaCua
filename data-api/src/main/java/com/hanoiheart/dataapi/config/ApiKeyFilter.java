package com.hanoiheart.dataapi.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

/**
 * Demo-only API key filter. If {@code hanoi-heart.api-key} is blank the filter
 * is a no-op (open access for local dev). When set, every /data/** request must
 * carry {@code X-API-Key: <key>}.
 */
@Configuration
public class ApiKeyFilter extends OncePerRequestFilter {

    private static final String HEADER = "X-API-Key";

    @Value("${hanoi-heart.api-key:}")
    private String expectedKey;

    @Override
    protected void doFilterInternal(HttpServletRequest req,
                                    HttpServletResponse resp,
                                    FilterChain chain) throws ServletException, IOException {
        if (expectedKey != null && !expectedKey.isBlank()
                && req.getRequestURI().startsWith("/data/")) {
            String provided = req.getHeader(HEADER);
            if (!expectedKey.equals(provided)) {
                resp.setStatus(HttpStatus.UNAUTHORIZED.value());
                resp.setContentType("application/json;charset=UTF-8");
                resp.getWriter().write("{\"error\":{\"code\":\"unauthorized\",\"message\":\"Missing or invalid X-API-Key\"}}");
                return;
            }
        }
        chain.doFilter(req, resp);
    }
}

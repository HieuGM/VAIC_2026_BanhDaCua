package com.hanoiheart.dataapi.config;

import com.hanoiheart.dataapi.security.JwtAuthenticationFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

/**
 * Spring Security configuration.
 * Public routes: auth, master data (departments, doctors, services, support-channels)
 * Protected routes: profile, appointments, chat sessions
 */
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Value("${hanoi-heart.cors.allowed-origins}")
    private String allowedOrigins;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                // Auth — register/login công khai; me/logout yêu cầu JWT (anyRequest)
                .requestMatchers(HttpMethod.POST, "/data/v1/auth/register").permitAll()
                .requestMatchers(HttpMethod.POST, "/data/v1/auth/login").permitAll()
                // Master data — public read-only (controller thật ở /data/v1/*, đi qua nginx /data/)
                .requestMatchers(HttpMethod.GET, "/data/v1/departments/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/data/v1/doctors/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/data/v1/services/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/data/v1/channels/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/data/v1/appointment-slots/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/data/v1/hospital-info/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/data/v1/bhyt-policies/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/data/v1/procedures/**").permitAll()
                // Chat — anonymous (giữ như develop/VPS LIVE)
                .requestMatchers("/data/v1/chat/**").permitAll()
                // Actuator health — public
                .requestMatchers("/actuator/health", "/actuator/info").permitAll()
                // Tất cả endpoint khác (profile, appointments, auth/me, auth/logout) yêu cầu JWT
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter,
                UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of(allowedOrigins.split(",")));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}

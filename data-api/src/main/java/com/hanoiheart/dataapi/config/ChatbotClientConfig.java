package com.hanoiheart.dataapi.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

import java.time.Duration;

/**
 * Cấu hình {@link RestClient} cho chatbot-service (FastAPI :8000).
 * Base-url + timeout lấy từ {@code application.yml} ({@code hanoi-heart.chatbot.*}).
 *
 * <p>Bean name {@code chatbotRestClient} — inject vào {@code ChatbotClient} qua {@code @Qualifier}.
 */
@Configuration
public class ChatbotClientConfig {

    @Value("${hanoi-heart.chatbot.base-url:http://localhost:8000}")
    private String baseUrl;

    @Value("${hanoi-heart.chatbot.connect-timeout-ms:10000}")
    private long connectTimeoutMs;

    @Value("${hanoi-heart.chatbot.read-timeout-ms:10000}")
    private long readTimeoutMs;

    @Bean
    public RestClient chatbotRestClient() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(Duration.ofMillis(connectTimeoutMs));
        factory.setReadTimeout(Duration.ofMillis(readTimeoutMs));
        return RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(factory)
                .build();
    }
}

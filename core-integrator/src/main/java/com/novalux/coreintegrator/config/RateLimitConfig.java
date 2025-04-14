package com.novalux.coreintegrator.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.cloud.gateway.filter.ratelimit.KeyResolver;
import org.springframework.cloud.gateway.filter.ratelimit.RedisRateLimiter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import lombok.Data;
import reactor.core.publisher.Mono;

@Configuration
@EnableConfigurationProperties
public class RateLimitConfig {

    private final RateLimitProperties rateLimitProperties;

    public RateLimitConfig(RateLimitProperties rateLimitProperties) {
        this.rateLimitProperties = rateLimitProperties;
    }

    @Bean
    public RedisRateLimiter redisRateLimiter() {
        return new RedisRateLimiter(
            rateLimitProperties.getDefaultLimit(),
            rateLimitProperties.getDefaultLimit() * 2, // burstCapacity = 2x defaultLimit
            1 // replenishRate = 1 second
        );
    }

    @Bean
    public KeyResolver ipKeyResolver() {
        return exchange -> Mono.just(
            exchange.getRequest().getRemoteAddress().getHostName()
        );
    }
    
    @Configuration
    @ConfigurationProperties(prefix = "api-gateway.rate-limit")
    @Data
    public static class RateLimitProperties {
        private boolean enabled;
        private int defaultLimit;
        private String defaultRefreshPeriod;
    }
}

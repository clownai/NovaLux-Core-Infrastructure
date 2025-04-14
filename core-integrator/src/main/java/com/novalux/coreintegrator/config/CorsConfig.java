package com.novalux.coreintegrator.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import lombok.Data;

import java.util.Arrays;
import java.util.List;

@Configuration
@EnableConfigurationProperties
public class CorsConfig {

    private final ApiGatewayProperties apiGatewayProperties;

    public CorsConfig(ApiGatewayProperties apiGatewayProperties) {
        this.apiGatewayProperties = apiGatewayProperties;
    }

    @Bean
    public CorsWebFilter corsWebFilter() {
        CorsConfiguration corsConfig = new CorsConfiguration();
        
        // Parse allowed origins
        String allowedOrigins = apiGatewayProperties.getCors().getAllowedOrigins();
        if (allowedOrigins.equals("*")) {
            corsConfig.addAllowedOrigin("*");
        } else {
            Arrays.stream(allowedOrigins.split(","))
                  .forEach(corsConfig::addAllowedOrigin);
        }
        
        // Parse allowed methods
        String allowedMethods = apiGatewayProperties.getCors().getAllowedMethods();
        Arrays.stream(allowedMethods.split(","))
              .forEach(corsConfig::addAllowedMethod);
        
        // Parse allowed headers
        String allowedHeaders = apiGatewayProperties.getCors().getAllowedHeaders();
        if (allowedHeaders.equals("*")) {
            corsConfig.addAllowedHeader("*");
        } else {
            Arrays.stream(allowedHeaders.split(","))
                  .forEach(corsConfig::addAllowedHeader);
        }
        
        corsConfig.setMaxAge(apiGatewayProperties.getCors().getMaxAge());
        corsConfig.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfig);
        
        return new CorsWebFilter(source);
    }
    
    @Configuration
    @ConfigurationProperties(prefix = "api-gateway")
    @Data
    public static class ApiGatewayProperties {
        private RateLimit rateLimit;
        private Cors cors;
        
        @Data
        public static class RateLimit {
            private boolean enabled;
            private int defaultLimit;
            private String defaultRefreshPeriod;
        }
        
        @Data
        public static class Cors {
            private String allowedOrigins;
            private String allowedMethods;
            private String allowedHeaders;
            private long maxAge;
        }
    }
}

package com.novalux.adaptivecore.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "ai-integration")
@Data
public class AIIntegrationConfig {
    private String modelServerUrl;
    private String inferenceTimeout;
    private int batchSize;
    private String cacheTtl;
}

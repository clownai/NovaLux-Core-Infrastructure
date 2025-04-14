package com.novalux.adaptivecore.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "feedback-loop")
@Data
public class FeedbackLoopConfig {
    private boolean enabled;
    private String updateInterval;
    private double optimizationThreshold;
    private int maxConcurrentOptimizations;
}

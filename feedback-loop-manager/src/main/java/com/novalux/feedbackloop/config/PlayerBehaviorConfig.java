package com.novalux.feedbackloop.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "player-behavior.analysis")
@Data
public class PlayerBehaviorConfig {
    private boolean enabled;
    private String updateInterval;
    private int minDataPoints;
    private double confidenceThreshold;
    private int maxConcurrentAnalyses;
}

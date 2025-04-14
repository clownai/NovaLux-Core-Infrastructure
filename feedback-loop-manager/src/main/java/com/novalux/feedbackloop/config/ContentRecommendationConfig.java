package com.novalux.feedbackloop.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "content-recommendation")
@Data
public class ContentRecommendationConfig {
    private boolean enabled;
    private String updateInterval;
    private double noveltyWeight;
    private double personalizationWeight;
    private int maxRecommendations;
}

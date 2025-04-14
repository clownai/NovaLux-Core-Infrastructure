package com.novalux.feedbackloop.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "responsible-gaming.monitoring")
@Data
public class ResponsibleGamingConfig {
    private boolean enabled;
    private String updateInterval;
    private double riskThreshold;
    private String interventionCooldown;
}

package com.novalux.feedbackloop.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

@Configuration
@ConfigurationProperties(prefix = "game-balance.optimization")
@Data
public class GameBalanceConfig {
    private boolean enabled;
    private String updateInterval;
    private int minPlayerCount;
    private double adjustmentThreshold;
    private double maxAdjustmentPercentage;
}

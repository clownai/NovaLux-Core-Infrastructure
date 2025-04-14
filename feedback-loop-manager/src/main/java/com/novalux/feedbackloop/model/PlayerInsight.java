package com.novalux.feedbackloop.model;

import java.time.Instant;
import lombok.Data;
import lombok.Builder;

@Data
@Builder
public class PlayerInsight {
    private String id;
    private String playerId;
    private Instant timestamp;
    private String insightType;
    private double confidenceScore;
    private String description;
    private PlayerBehaviorMetrics metrics;
    
    @Data
    @Builder
    public static class PlayerBehaviorMetrics {
        private double engagementScore;
        private double skillLevel;
        private double riskTolerance;
        private double socialInteraction;
        private double contentPreference;
        private double spendingPattern;
        private double timeInvestment;
    }
}

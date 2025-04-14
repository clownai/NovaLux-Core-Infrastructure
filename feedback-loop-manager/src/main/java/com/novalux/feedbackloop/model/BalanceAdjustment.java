package com.novalux.feedbackloop.model;

import java.time.Instant;
import lombok.Data;
import lombok.Builder;

@Data
@Builder
public class BalanceAdjustment {
    private String id;
    private String gameId;
    private Instant timestamp;
    private String adjustmentType;
    private String parameter;
    private double previousValue;
    private double newValue;
    private double adjustmentPercentage;
    private double confidenceScore;
    private String reason;
    private GameMetrics metrics;
    
    @Data
    @Builder
    public static class GameMetrics {
        private double playerRetention;
        private double averageSessionLength;
        private double completionRate;
        private double difficultyRating;
        private double revenuePerPlayer;
        private double playerSatisfaction;
        private int activePlayerCount;
    }
}

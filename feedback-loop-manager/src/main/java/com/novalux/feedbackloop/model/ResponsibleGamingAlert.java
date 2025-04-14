package com.novalux.feedbackloop.model;

import java.time.Instant;
import lombok.Data;
import lombok.Builder;

@Data
@Builder
public class ResponsibleGamingAlert {
    private String id;
    private String playerId;
    private Instant timestamp;
    private String alertType;
    private double riskScore;
    private String description;
    private String recommendedAction;
    private boolean requiresImmediate;
    private RiskIndicators indicators;
    
    @Data
    @Builder
    public static class RiskIndicators {
        private double playTimeExcess;
        private double spendingPattern;
        private double chasePattern;
        private double volatilityPreference;
        private double timeOfDayPattern;
        private double socialIsolation;
        private double emotionalState;
    }
}

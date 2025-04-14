package com.novalux.adaptivecore.model;

import java.time.Instant;
import lombok.Data;
import lombok.Builder;

@Data
@Builder
public class OptimizationEvent {
    private String id;
    private String type;
    private Instant timestamp;
    private String targetComponent;
    private String targetParameter;
    private double currentValue;
    private double suggestedValue;
    private double confidenceScore;
    private String reason;
    private String modelId;
    private String modelVersion;
}

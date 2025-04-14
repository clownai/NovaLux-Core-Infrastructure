package com.novalux.adaptivecore.model;

import java.time.Instant;
import lombok.Data;
import lombok.Builder;

@Data
@Builder
public class ParameterAdjustment {
    private String id;
    private String type;
    private Instant timestamp;
    private String targetComponent;
    private String targetParameter;
    private double previousValue;
    private double newValue;
    private String optimizationEventId;
    private String appliedBy;
    private String status;
    private Instant appliedAt;
}

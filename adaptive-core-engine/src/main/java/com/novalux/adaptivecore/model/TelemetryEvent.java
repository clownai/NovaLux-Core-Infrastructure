package com.novalux.adaptivecore.model;

import java.time.Instant;
import lombok.Data;
import lombok.Builder;

@Data
@Builder
public class TelemetryEvent {
    private String id;
    private String type;
    private String source;
    private Instant timestamp;
    private String playerId;
    private EventData data;
    
    @Data
    public static class EventData {
        private String action;
        private String gameId;
        private String sessionId;
        private String districtId;
        private String factionId;
        private Object parameters;
    }
}

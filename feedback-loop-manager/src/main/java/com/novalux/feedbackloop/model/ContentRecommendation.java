package com.novalux.feedbackloop.model;

import java.time.Instant;
import java.util.List;
import lombok.Data;
import lombok.Builder;

@Data
@Builder
public class ContentRecommendation {
    private String id;
    private String playerId;
    private Instant timestamp;
    private List<RecommendedContent> recommendations;
    private double personalizedScore;
    private String playerSegment;
    
    @Data
    @Builder
    public static class RecommendedContent {
        private String contentId;
        private String contentType;
        private String title;
        private double relevanceScore;
        private double noveltyScore;
        private double overallScore;
        private List<String> tags;
    }
}

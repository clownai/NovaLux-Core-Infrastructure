package com.novalux.feedbackloop.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.feedbackloop.config.PlayerBehaviorConfig;
import com.novalux.feedbackloop.model.PlayerInsight;
import com.novalux.feedbackloop.model.TelemetryEvent;

import java.time.Instant;
import java.util.UUID;
import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

@Service
@Slf4j
public class PlayerBehaviorService {

    private final PlayerBehaviorConfig config;
    private final ConcurrentHashMap<String, Map<String, Object>> playerDataCache = new ConcurrentHashMap<>();
    private final AtomicInteger activeAnalyses = new AtomicInteger(0);

    @Autowired
    public PlayerBehaviorService(PlayerBehaviorConfig config) {
        this.config = config;
    }

    public void processTelemetryEvent(TelemetryEvent event) {
        if (!config.isEnabled()) {
            log.debug("Player behavior analysis is disabled, ignoring event: {}", event.getId());
            return;
        }

        String playerId = event.getPlayerId();
        if (playerId == null || playerId.isEmpty()) {
            log.debug("Event has no player ID, ignoring: {}", event.getId());
            return;
        }

        // Update player data cache
        updatePlayerDataCache(playerId, event);

        // Check if we have enough data points for analysis
        Map<String, Object> playerData = playerDataCache.get(playerId);
        if (playerData != null && getDataPointCount(playerData) >= config.getMinDataPoints()) {
            // Schedule analysis if we're not at capacity
            if (activeAnalyses.get() < config.getMaxConcurrentAnalyses()) {
                analyzePlayerBehavior(playerId);
            }
        }
    }

    private void updatePlayerDataCache(String playerId, TelemetryEvent event) {
        Map<String, Object> playerData = playerDataCache.computeIfAbsent(playerId, k -> new HashMap<>());
        
        // Update event count
        int eventCount = (int) playerData.getOrDefault("eventCount", 0);
        playerData.put("eventCount", eventCount + 1);
        
        // Update last event timestamp
        playerData.put("lastEventTimestamp", event.getTimestamp());
        
        // Update first event timestamp if not set
        if (!playerData.containsKey("firstEventTimestamp")) {
            playerData.put("firstEventTimestamp", event.getTimestamp());
        }
        
        // Update event type counts
        String eventType = event.getType();
        if (eventType != null) {
            Map<String, Integer> eventTypeCounts = (Map<String, Integer>) playerData.computeIfAbsent("eventTypeCounts", k -> new HashMap<>());
            int typeCount = eventTypeCounts.getOrDefault(eventType, 0);
            eventTypeCounts.put(eventType, typeCount + 1);
        }
        
        // Update game-specific data if available
        if (event.getData() != null && event.getData().getGameId() != null) {
            String gameId = event.getData().getGameId();
            Map<String, Integer> gamePlayCounts = (Map<String, Integer>) playerData.computeIfAbsent("gamePlayCounts", k -> new HashMap<>());
            int gameCount = gamePlayCounts.getOrDefault(gameId, 0);
            gamePlayCounts.put(gameId, gameCount + 1);
        }
    }

    private int getDataPointCount(Map<String, Object> playerData) {
        return (int) playerData.getOrDefault("eventCount", 0);
    }

    private void analyzePlayerBehavior(String playerId) {
        activeAnalyses.incrementAndGet();
        
        try {
            log.info("Analyzing behavior for player: {}", playerId);
            Map<String, Object> playerData = playerDataCache.get(playerId);
            
            if (playerData == null) {
                log.warn("Player data not found for player: {}", playerId);
                return;
            }
            
            // In a real implementation, this would use more sophisticated analysis
            // For now, we'll create a simulated insight
            PlayerInsight insight = createPlayerInsight(playerId, playerData);
            
            log.info("Generated player insight: {} for player: {}", insight.getId(), playerId);
            
            // In a real implementation, this would be published to Kafka
            // and potentially stored in Elasticsearch
            
        } catch (Exception e) {
            log.error("Error analyzing player behavior: {}", playerId, e);
        } finally {
            activeAnalyses.decrementAndGet();
        }
    }
    
    private PlayerInsight createPlayerInsight(String playerId, Map<String, Object> playerData) {
        // Create a simulated player insight based on the data
        int eventCount = (int) playerData.getOrDefault("eventCount", 0);
        Map<String, Integer> eventTypeCounts = (Map<String, Integer>) playerData.getOrDefault("eventTypeCounts", new HashMap<>());
        Map<String, Integer> gamePlayCounts = (Map<String, Integer>) playerData.getOrDefault("gamePlayCounts", new HashMap<>());
        
        // Calculate some basic metrics
        double engagementScore = Math.min(1.0, eventCount / 1000.0);
        double skillLevel = 0.5 + (Math.random() * 0.5); // Simulated
        double riskTolerance = Math.random();
        double socialInteraction = Math.random();
        double contentPreference = Math.random();
        double spendingPattern = Math.random();
        double timeInvestment = Math.random();
        
        // Create the metrics object
        PlayerInsight.PlayerBehaviorMetrics metrics = PlayerInsight.PlayerBehaviorMetrics.builder()
                .engagementScore(engagementScore)
                .skillLevel(skillLevel)
                .riskTolerance(riskTolerance)
                .socialInteraction(socialInteraction)
                .contentPreference(contentPreference)
                .spendingPattern(spendingPattern)
                .timeInvestment(timeInvestment)
                .build();
        
        // Determine insight type based on the highest metric
        String insightType;
        if (engagementScore > 0.8) insightType = "HIGH_ENGAGEMENT";
        else if (skillLevel > 0.8) insightType = "HIGH_SKILL";
        else if (riskTolerance > 0.8) insightType = "RISK_TAKER";
        else if (socialInteraction > 0.8) insightType = "SOCIAL_PLAYER";
        else if (contentPreference > 0.8) insightType = "CONTENT_EXPLORER";
        else if (spendingPattern > 0.8) insightType = "PREMIUM_PLAYER";
        else if (timeInvestment > 0.8) insightType = "TIME_INVESTOR";
        else insightType = "BALANCED_PLAYER";
        
        // Create the insight
        return PlayerInsight.builder()
                .id(UUID.randomUUID().toString())
                .playerId(playerId)
                .timestamp(Instant.now())
                .insightType(insightType)
                .confidenceScore(0.7 + (Math.random() * 0.3)) // 0.7 to 1.0
                .description("Player shows " + insightType.toLowerCase().replace('_', ' ') + " behavior pattern")
                .metrics(metrics)
                .build();
    }
}

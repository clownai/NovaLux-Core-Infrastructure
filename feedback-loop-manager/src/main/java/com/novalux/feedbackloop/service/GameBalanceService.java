package com.novalux.feedbackloop.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.feedbackloop.config.GameBalanceConfig;
import com.novalux.feedbackloop.model.BalanceAdjustment;
import com.novalux.feedbackloop.model.TelemetryEvent;

import java.time.Instant;
import java.util.UUID;
import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.ConcurrentHashMap;

@Service
@Slf4j
public class GameBalanceService {

    private final GameBalanceConfig config;
    private final ConcurrentHashMap<String, Map<String, Object>> gameDataCache = new ConcurrentHashMap<>();

    @Autowired
    public GameBalanceService(GameBalanceConfig config) {
        this.config = config;
    }

    public void processTelemetryEvent(TelemetryEvent event) {
        if (!config.isEnabled()) {
            log.debug("Game balance optimization is disabled, ignoring event: {}", event.getId());
            return;
        }

        if (event.getData() == null || event.getData().getGameId() == null) {
            log.debug("Event has no game ID, ignoring: {}", event.getId());
            return;
        }

        String gameId = event.getData().getGameId();
        
        // Update game data cache
        updateGameDataCache(gameId, event);
        
        // Check if we have enough data for optimization
        Map<String, Object> gameData = gameDataCache.get(gameId);
        if (gameData != null && getPlayerCount(gameData) >= config.getMinPlayerCount()) {
            // Analyze game balance and generate adjustments if needed
            analyzeGameBalance(gameId);
        }
    }

    private void updateGameDataCache(String gameId, TelemetryEvent event) {
        Map<String, Object> gameData = gameDataCache.computeIfAbsent(gameId, k -> new HashMap<>());
        
        // Update event count
        int eventCount = (int) gameData.getOrDefault("eventCount", 0);
        gameData.put("eventCount", eventCount + 1);
        
        // Update last event timestamp
        gameData.put("lastEventTimestamp", event.getTimestamp());
        
        // Update first event timestamp if not set
        if (!gameData.containsKey("firstEventTimestamp")) {
            gameData.put("firstEventTimestamp", event.getTimestamp());
        }
        
        // Update player set
        Map<String, Boolean> players = (Map<String, Boolean>) gameData.computeIfAbsent("players", k -> new HashMap<>());
        players.put(event.getPlayerId(), true);
        
        // Update event type counts
        String eventType = event.getType();
        if (eventType != null) {
            Map<String, Integer> eventTypeCounts = (Map<String, Integer>) gameData.computeIfAbsent("eventTypeCounts", k -> new HashMap<>());
            int typeCount = eventTypeCounts.getOrDefault(eventType, 0);
            eventTypeCounts.put(eventType, typeCount + 1);
        }
        
        // Update session data if available
        if (event.getData() != null && event.getData().getSessionId() != null) {
            String sessionId = event.getData().getSessionId();
            Map<String, Object> sessions = (Map<String, Object>) gameData.computeIfAbsent("sessions", k -> new HashMap<>());
            
            Map<String, Object> sessionData = (Map<String, Object>) sessions.computeIfAbsent(sessionId, k -> new HashMap<>());
            int sessionEventCount = (int) sessionData.getOrDefault("eventCount", 0);
            sessionData.put("eventCount", sessionEventCount + 1);
            sessionData.put("lastEventTimestamp", event.getTimestamp());
            
            if (!sessionData.containsKey("firstEventTimestamp")) {
                sessionData.put("firstEventTimestamp", event.getTimestamp());
                sessionData.put("playerId", event.getPlayerId());
            }
        }
    }

    private int getPlayerCount(Map<String, Object> gameData) {
        Map<String, Boolean> players = (Map<String, Boolean>) gameData.getOrDefault("players", new HashMap<>());
        return players.size();
    }

    private void analyzeGameBalance(String gameId) {
        try {
            log.info("Analyzing game balance for game: {}", gameId);
            Map<String, Object> gameData = gameDataCache.get(gameId);
            
            if (gameData == null) {
                log.warn("Game data not found for game: {}", gameId);
                return;
            }
            
            // In a real implementation, this would use more sophisticated analysis
            // For now, we'll create a simulated balance adjustment
            BalanceAdjustment adjustment = createBalanceAdjustment(gameId, gameData);
            
            // Check if the adjustment exceeds the threshold
            if (Math.abs(adjustment.getAdjustmentPercentage()) >= config.getAdjustmentThreshold()) {
                log.info("Generated balance adjustment: {} for game: {}", adjustment.getId(), gameId);
                
                // In a real implementation, this would be published to Kafka
                // and potentially stored in Elasticsearch
            } else {
                log.debug("Balance adjustment below threshold, ignoring: {}", adjustment.getId());
            }
            
        } catch (Exception e) {
            log.error("Error analyzing game balance: {}", gameId, e);
        }
    }
    
    private BalanceAdjustment createBalanceAdjustment(String gameId, Map<String, Object> gameData) {
        // Create a simulated balance adjustment based on the data
        int eventCount = (int) gameData.getOrDefault("eventCount", 0);
        Map<String, Boolean> players = (Map<String, Boolean>) gameData.getOrDefault("players", new HashMap<>());
        int playerCount = players.size();
        
        // Calculate some basic metrics
        double playerRetention = 0.7 + (Math.random() * 0.3); // Simulated
        double averageSessionLength = 10 + (Math.random() * 20); // minutes
        double completionRate = 0.5 + (Math.random() * 0.5);
        double difficultyRating = 0.3 + (Math.random() * 0.7);
        double revenuePerPlayer = 5 + (Math.random() * 15);
        double playerSatisfaction = 0.6 + (Math.random() * 0.4);
        
        // Create the metrics object
        BalanceAdjustment.GameMetrics metrics = BalanceAdjustment.GameMetrics.builder()
                .playerRetention(playerRetention)
                .averageSessionLength(averageSessionLength)
                .completionRate(completionRate)
                .difficultyRating(difficultyRating)
                .revenuePerPlayer(revenuePerPlayer)
                .playerSatisfaction(playerSatisfaction)
                .activePlayerCount(playerCount)
                .build();
        
        // Determine adjustment type based on the metrics
        String adjustmentType;
        String parameter;
        double previousValue;
        double adjustmentPercentage;
        String reason;
        
        if (completionRate < 0.6) {
            adjustmentType = "DIFFICULTY_DECREASE";
            parameter = "difficulty_factor";
            previousValue = 0.7;
            adjustmentPercentage = -0.15 - (Math.random() * 0.1); // -15% to -25%
            reason = "Low completion rate indicates excessive difficulty";
        } else if (playerSatisfaction < 0.7) {
            adjustmentType = "REWARD_INCREASE";
            parameter = "reward_multiplier";
            previousValue = 1.0;
            adjustmentPercentage = 0.1 + (Math.random() * 0.1); // 10% to 20%
            reason = "Low player satisfaction indicates insufficient rewards";
        } else if (averageSessionLength < 15) {
            adjustmentType = "CONTENT_VARIETY_INCREASE";
            parameter = "content_variety_factor";
            previousValue = 0.5;
            adjustmentPercentage = 0.2 + (Math.random() * 0.1); // 20% to 30%
            reason = "Short session length indicates lack of engaging content";
        } else if (difficultyRating > 0.8) {
            adjustmentType = "DIFFICULTY_DECREASE";
            parameter = "difficulty_factor";
            previousValue = 0.9;
            adjustmentPercentage = -0.1 - (Math.random() * 0.1); // -10% to -20%
            reason = "High difficulty rating indicates potential player frustration";
        } else if (difficultyRating < 0.4) {
            adjustmentType = "DIFFICULTY_INCREASE";
            parameter = "difficulty_factor";
            previousValue = 0.3;
            adjustmentPercentage = 0.1 + (Math.random() * 0.1); // 10% to 20%
            reason = "Low difficulty rating indicates potential player boredom";
        } else {
            adjustmentType = "MINOR_TUNING";
            parameter = "engagement_factor";
            previousValue = 0.5;
            adjustmentPercentage = 0.05 + (Math.random() * 0.05); // 5% to 10%
            reason = "Regular tuning to maintain optimal player engagement";
        }
        
        // Ensure we don't exceed the maximum adjustment percentage
        if (Math.abs(adjustmentPercentage) > config.getMaxAdjustmentPercentage()) {
            adjustmentPercentage = adjustmentPercentage > 0 
                ? config.getMaxAdjustmentPercentage() 
                : -config.getMaxAdjustmentPercentage();
        }
        
        double newValue = previousValue * (1 + adjustmentPercentage);
        
        // Create the balance adjustment
        return BalanceAdjustment.builder()
                .id(UUID.randomUUID().toString())
                .gameId(gameId)
                .timestamp(Instant.now())
                .adjustmentType(adjustmentType)
                .parameter(parameter)
                .previousValue(previousValue)
                .newValue(newValue)
                .adjustmentPercentage(adjustmentPercentage)
                .confidenceScore(0.7 + (Math.random() * 0.3)) // 0.7 to 1.0
                .reason(reason)
                .metrics(metrics)
                .build();
    }
}

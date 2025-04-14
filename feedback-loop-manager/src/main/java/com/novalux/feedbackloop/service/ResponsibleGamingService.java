package com.novalux.feedbackloop.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.feedbackloop.config.ResponsibleGamingConfig;
import com.novalux.feedbackloop.model.ResponsibleGamingAlert;
import com.novalux.feedbackloop.model.TelemetryEvent;
import com.novalux.feedbackloop.model.PlayerInsight;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Service
@Slf4j
public class ResponsibleGamingService {

    private final ResponsibleGamingConfig config;
    private final ConcurrentHashMap<String, Map<String, Object>> playerRiskCache = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, Instant> interventionCooldowns = new ConcurrentHashMap<>();

    @Autowired
    public ResponsibleGamingService(ResponsibleGamingConfig config) {
        this.config = config;
    }

    public void processTelemetryEvent(TelemetryEvent event) {
        if (!config.isEnabled()) {
            log.debug("Responsible gaming monitoring is disabled, ignoring event: {}", event.getId());
            return;
        }

        String playerId = event.getPlayerId();
        if (playerId == null || playerId.isEmpty()) {
            log.debug("Event has no player ID, ignoring: {}", event.getId());
            return;
        }

        // Update player risk data
        updatePlayerRiskData(playerId, event);
        
        // Check if we need to generate an alert
        checkForRiskyBehavior(playerId);
    }
    
    public void processPlayerInsight(PlayerInsight insight) {
        if (!config.isEnabled()) {
            log.debug("Responsible gaming monitoring is disabled, ignoring player insight: {}", insight.getId());
            return;
        }
        
        String playerId = insight.getPlayerId();
        if (playerId == null || playerId.isEmpty()) {
            log.debug("Insight has no player ID, ignoring: {}", insight.getId());
            return;
        }
        
        // Update player risk data with insight
        updatePlayerRiskDataFromInsight(playerId, insight);
        
        // Check if we need to generate an alert
        checkForRiskyBehavior(playerId);
    }

    private void updatePlayerRiskData(String playerId, TelemetryEvent event) {
        Map<String, Object> riskData = playerRiskCache.computeIfAbsent(playerId, k -> new HashMap<>());
        
        // Update event count
        int eventCount = (int) riskData.getOrDefault("eventCount", 0);
        riskData.put("eventCount", eventCount + 1);
        
        // Update last activity timestamp
        Instant lastActivity = event.getTimestamp();
        riskData.put("lastActivityTimestamp", lastActivity);
        
        // Update first activity timestamp if not set
        if (!riskData.containsKey("firstActivityTimestamp")) {
            riskData.put("firstActivityTimestamp", lastActivity);
        }
        
        // Update session data
        if (event.getData() != null && event.getData().getSessionId() != null) {
            String sessionId = event.getData().getSessionId();
            Map<String, Object> sessions = (Map<String, Object>) riskData.computeIfAbsent("sessions", k -> new HashMap<>());
            
            Map<String, Object> sessionData = (Map<String, Object>) sessions.computeIfAbsent(sessionId, k -> new HashMap<>());
            int sessionEventCount = (int) sessionData.getOrDefault("eventCount", 0);
            sessionData.put("eventCount", sessionEventCount + 1);
            
            Instant sessionStart = (Instant) sessionData.getOrDefault("startTimestamp", lastActivity);
            sessionData.put("startTimestamp", sessionStart);
            sessionData.put("lastActivityTimestamp", lastActivity);
            
            // Calculate session duration
            long sessionDurationSeconds = lastActivity.getEpochSecond() - sessionStart.getEpochSecond();
            sessionData.put("durationSeconds", sessionDurationSeconds);
            
            // Update total play time
            long totalPlayTimeSeconds = (long) riskData.getOrDefault("totalPlayTimeSeconds", 0L);
            riskData.put("totalPlayTimeSeconds", totalPlayTimeSeconds + 1); // Increment by 1 second per event as an approximation
            
            // Update daily play time
            String today = lastActivity.toString().substring(0, 10); // YYYY-MM-DD
            Map<String, Long> dailyPlayTime = (Map<String, Long>) riskData.computeIfAbsent("dailyPlayTime", k -> new HashMap<>());
            long todayPlayTime = dailyPlayTime.getOrDefault(today, 0L);
            dailyPlayTime.put(today, todayPlayTime + 1); // Increment by 1 second per event as an approximation
        }
        
        // Update spending data if available
        if (event.getType() != null && event.getType().equals("PURCHASE") && event.getData() != null && event.getData().getParameters() != null) {
            try {
                // In a real implementation, this would parse the parameters to extract purchase amount
                // For now, we'll simulate a purchase amount
                double amount = 5 + (Math.random() * 95); // $5 to $100
                
                // Update total spending
                double totalSpending = (double) riskData.getOrDefault("totalSpending", 0.0);
                riskData.put("totalSpending", totalSpending + amount);
                
                // Update daily spending
                String today = lastActivity.toString().substring(0, 10); // YYYY-MM-DD
                Map<String, Double> dailySpending = (Map<String, Double>) riskData.computeIfAbsent("dailySpending", k -> new HashMap<>());
                double todaySpending = dailySpending.getOrDefault(today, 0.0);
                dailySpending.put(today, todaySpending + amount);
                
                // Update purchase count
                int purchaseCount = (int) riskData.getOrDefault("purchaseCount", 0);
                riskData.put("purchaseCount", purchaseCount + 1);
                
                // Update purchase timestamps
                List<Instant> purchaseTimestamps = (List<Instant>) riskData.computeIfAbsent("purchaseTimestamps", k -> new ArrayList<>());
                purchaseTimestamps.add(lastActivity);
            } catch (Exception e) {
                log.warn("Error processing purchase data: {}", e.getMessage());
            }
        }
        
        // Update loss data if available
        if (event.getType() != null && event.getType().equals("GAME_LOSS") && event.getData() != null) {
            // Update loss count
            int lossCount = (int) riskData.getOrDefault("lossCount", 0);
            riskData.put("lossCount", lossCount + 1);
            
            // Update consecutive losses
            int consecutiveLosses = (int) riskData.getOrDefault("consecutiveLosses", 0);
            riskData.put("consecutiveLosses", consecutiveLosses + 1);
        }
        
        // Reset consecutive losses on win
        if (event.getType() != null && event.getType().equals("GAME_WIN")) {
            riskData.put("consecutiveLosses", 0);
        }
    }
    
    private void updatePlayerRiskDataFromInsight(String playerId, PlayerInsight insight) {
        Map<String, Object> riskData = playerRiskCache.computeIfAbsent(playerId, k -> new HashMap<>());
        
        // Update insight data
        riskData.put("lastInsightTimestamp", insight.getTimestamp());
        riskData.put("lastInsightType", insight.getInsightType());
        
        // Update risk factors based on insight metrics
        if (insight.getMetrics() != null) {
            Map<String, Double> riskFactors = (Map<String, Double>) riskData.computeIfAbsent("riskFactors", k -> new HashMap<>());
            
            // Map player metrics to risk factors
            riskFactors.put("riskTolerance", insight.getMetrics().getRiskTolerance());
            riskFactors.put("spendingPattern", insight.getMetrics().getSpendingPattern());
            riskFactors.put("timeInvestment", insight.getMetrics().getTimeInvestment());
            riskFactors.put("socialInteraction", 1.0 - insight.getMetrics().getSocialInteraction()); // Invert, lower social interaction is higher risk
            
            // Flag high-risk players based on insight type
            if (insight.getInsightType().equals("RISK_TAKER")) {
                riskFactors.put("riskTolerance", Math.min(1.0, riskFactors.getOrDefault("riskTolerance", 0.5) + 0.2));
            } else if (insight.getInsightType().equals("PREMIUM_PLAYER")) {
                riskFactors.put("spendingPattern", Math.min(1.0, riskFactors.getOrDefault("spendingPattern", 0.5) + 0.2));
            } else if (insight.getInsightType().equals("TIME_INVESTOR")) {
                riskFactors.put("timeInvestment", Math.min(1.0, riskFactors.getOrDefault("timeInvestment", 0.5) + 0.2));
            }
        }
    }
    
    private void checkForRiskyBehavior(String playerId) {
        try {
            // Check if player is in cooldown period
            if (interventionCooldowns.containsKey(playerId)) {
                Instant cooldownEnd = interventionCooldowns.get(playerId);
                if (Instant.now().isBefore(cooldownEnd)) {
                    log.debug("Player {} is in intervention cooldown until {}", playerId, cooldownEnd);
                    return;
                } else {
                    // Cooldown expired
                    interventionCooldowns.remove(playerId);
                }
            }
            
            Map<String, Object> riskData = playerRiskCache.get(playerId);
            if (riskData == null) {
                return;
            }
            
            // Calculate risk score
            double riskScore = calculateRiskScore(riskData);
            
            // Check if risk score exceeds threshold
            if (riskScore >= config.getRiskThreshold()) {
                // Generate alert
                ResponsibleGamingAlert alert = createResponsibleGamingAlert(playerId, riskData, riskScore);
                
                log.info("Generated responsible gaming alert: {} for player: {} with risk score: {}", 
                        alert.getId(), playerId, riskScore);
                
                // Set cooldown period
                interventionCooldowns.put(playerId, Instant.now().plusSeconds(parseDuration(config.getInterventionCooldown())));
                
                // In a real implementation, this would be published to Kafka
                // and potentially stored in Elasticsearch
            }
            
        } catch (Exception e) {
            log.error("Error checking for risky behavior: {}", playerId, e);
        }
    }
    
    private double calculateRiskScore(Map<String, Object> riskData) {
        // In a real implementation, this would use a more sophisticated algorithm
        // For now, we'll use a simple heuristic based on several risk factors
        
        double score = 0.0;
        int factors = 0;
        
        // Check play time
        long totalPlayTimeSeconds = (long) riskData.getOrDefault("totalPlayTimeSeconds", 0L);
        if (totalPlayTimeSeconds > 0) {
            // Convert to hours
            double totalPlayTimeHours = totalPlayTimeSeconds / 3600.0;
            
            // Check daily play time
            Map<String, Long> dailyPlayTime = (Map<String, Long>) riskData.getOrDefault("dailyPlayTime", Collections.emptyMap());
            if (!dailyPlayTime.isEmpty()) {
                // Get today's play time
                String today = Instant.now().toString().substring(0, 10); // YYYY-MM-DD
                long todayPlayTimeSeconds = dailyPlayTime.getOrDefault(today, 0L);
                double todayPlayTimeHours = todayPlayTimeSeconds / 3600.0;
                
                // Score based on today's play time
                // 0-2 hours: low risk, 2-4 hours: medium risk, 4+ hours: high risk
                double playTimeScore;
                if (todayPlayTimeHours < 2) {
                    playTimeScore = todayPlayTimeHours / 4; // 0 to 0.5
                } else if (todayPlayTimeHours < 4) {
                    playTimeScore = 0.5 + ((todayPlayTimeHours - 2) / 4); // 0.5 to 0.75
                } else {
                    playTimeScore = 0.75 + (Math.min(todayPlayTimeHours - 4, 4) / 16); // 0.75 to 1.0
                }
                
                score += playTimeScore;
                factors++;
            }
        }
        
        // Check spending pattern
        double totalSpending = (double) riskData.getOrDefault("totalSpending", 0.0);
        if (totalSpending > 0) {
            // Check daily spending
            Map<String, Double> dailySpending = (Map<String, Double>) riskData.getOrDefault("dailySpending", Collections.emptyMap());
            if (!dailySpending.isEmpty()) {
                // Get today's spending
                String today = Instant.now().toString().substring(0, 10); // YYYY-MM-DD
                double todaySpending = dailySpending.getOrDefault(today, 0.0);
                
                // Score based on today's spending
                // $0-$20: low risk, $20-$100: medium risk, $100+: high risk
                double spendingScore;
                if (todaySpending < 20) {
                    spendingScore = todaySpending / 40; // 0 to 0.5
                } else if (todaySpending < 100) {
                    spendingScore = 0.5 + ((todaySpending - 20) / 160); // 0.5 to 0.75
                } else {
                    spendingScore = 0.75 + (Math.min(todaySpending - 100, 400) / 1600); // 0.75 to 1.0
                }
                
                score += spendingScore;
                factors++;
            }
        }
        
        // Check chase pattern (consecutive losses)
        int consecutiveLosses = (int) riskData.getOrDefault("consecutiveLosses", 0);
        if (consecutiveLosses > 0) {
            // Score based on consecutive losses
            // 1-3: low risk, 4-7: medium risk, 8+: high risk
            double chaseScore;
            if (consecutiveLosses < 4) {
                chaseScore = consecutiveLosses / 8.0; // 0 to 0.5
            } else if (consecutiveLosses < 8) {
                chaseScore = 0.5 + ((consecutiveLosses - 4) / 8.0); // 0.5 to 0.75
            } else {
                chaseScore = 0.75 + (Math.min(consecutiveLosses - 8, 8) / 32.0); // 0.75 to 1.0
            }
            
            score += chaseScore;
            factors++;
        }
        
        // Check time of day pattern
        Instant lastActivity = (Instant) riskData.get("lastActivityTimestamp");
        if (lastActivity != null) {
            // Get hour of day (0-23)
            int hour = lastActivity.atZone(java.time.ZoneOffset.UTC).getHour();
            
            // Late night gaming (11pm-5am) is higher risk
            double timeOfDayScore;
            if (hour >= 23 || hour < 5) {
                timeOfDayScore = 0.75; // High risk
            } else {
                timeOfDayScore = 0.25; // Low risk
            }
            
            score += timeOfDayScore;
            factors++;
        }
        
        // Include risk factors from player insights
        Map<String, Double> riskFactors = (Map<String, Double>) riskData.getOrDefault("riskFactors", Collections.emptyMap());
        for (Map.Entry<String, Double> factor : riskFactors.entrySet()) {
            score += factor.getValue();
            factors++;
        }
        
        // Calculate average score
        return factors > 0 ? score / factors : 0.0;
    }
    
    private ResponsibleGamingAlert createResponsibleGamingAlert(String playerId, Map<String, Object> riskData, double riskScore) {
        // Determine alert type based on risk factors
        String alertType;
        String description;
        String recommendedAction;
        boolean requiresImmediate = false;
        
        // Get risk factors
        long totalPlayTimeSeconds = (long) riskData.getOrDefault("totalPlayTimeSeconds", 0L);
        double totalPlayTimeHours = totalPlayTimeSeconds / 3600.0;
        
        double totalSpending = (double) riskData.getOrDefault("totalSpending", 0.0);
        
        int consecutiveLosses = (int) riskData.getOrDefault("consecutiveLosses", 0);
        
        Map<String, Double> riskFactors = (Map<String, Double>) riskData.getOrDefault("riskFactors", Collections.emptyMap());
        
        // Determine primary risk factor
        if (totalPlayTimeHours > 6 && (riskFactors.getOrDefault("timeInvestment", 0.0) > 0.7 || 
                                      riskScore > 0.9)) {
            alertType = "EXCESSIVE_PLAYTIME";
            description = "Player has been active for an extended period without significant breaks";
            recommendedAction = "Suggest taking a break and display play time statistics";
            requiresImmediate = riskScore > 0.9;
        } else if (totalSpending > 200 && (riskFactors.getOrDefault("spendingPattern", 0.0) > 0.7 || 
                                          riskScore > 0.9)) {
            alertType = "SPENDING_CONCERN";
            description = "Player has made significant purchases in a short time period";
            recommendedAction = "Display spending summary and offer spending limits";
            requiresImmediate = riskScore > 0.9;
        } else if (consecutiveLosses > 7 && (riskFactors.getOrDefault("riskTolerance", 0.0) > 0.7 || 
                                           riskScore > 0.9)) {
            alertType = "CHASE_BEHAVIOR";
            description = "Player has experienced multiple consecutive losses and continues to play";
            recommendedAction = "Suggest taking a break and display win/loss statistics";
            requiresImmediate = riskScore > 0.9;
        } else if (riskFactors.getOrDefault("socialInteraction", 0.0) > 0.8) {
            alertType = "SOCIAL_ISOLATION";
            description = "Player shows minimal social interaction within the platform";
            recommendedAction = "Suggest social features and community events";
            requiresImmediate = false;
        } else {
            alertType = "GENERAL_CONCERN";
            description = "Multiple risk factors have triggered a responsible gaming alert";
            recommendedAction = "Display responsible gaming information and self-assessment tools";
            requiresImmediate = riskScore > 0.95;
        }
        
        // Create risk indicators
        ResponsibleGamingAlert.RiskIndicators indicators = ResponsibleGamingAlert.RiskIndicators.builder()
                .playTimeExcess(Math.min(1.0, totalPlayTimeHours / 8.0))
                .spendingPattern(Math.min(1.0, totalSpending / 300.0))
                .chasePattern(Math.min(1.0, consecutiveLosses / 10.0))
                .volatilityPreference(riskFactors.getOrDefault("riskTolerance", 0.5))
                .timeOfDayPattern(riskFactors.getOrDefault("timeOfDayPattern", 0.5))
                .socialIsolation(riskFactors.getOrDefault("socialInteraction", 0.5))
                .emotionalState(riskFactors.getOrDefault("emotionalState", 0.5))
                .build();
        
        // Create the alert
        return ResponsibleGamingAlert.builder()
                .id(UUID.randomUUID().toString())
                .playerId(playerId)
                .timestamp(Instant.now())
                .alertType(alertType)
                .riskScore(riskScore)
                .description(description)
                .recommendedAction(recommendedAction)
                .requiresImmediate(requiresImmediate)
                .indicators(indicators)
                .build();
    }
    
    private long parseDuration(String duration) {
        // Simple duration parser for strings like "86400s" (1 day in seconds)
        if (duration == null || duration.isEmpty()) {
            return 86400; // Default to 1 day
        }
        
        try {
            String value = duration.substring(0, duration.length() - 1);
            String unit = duration.substring(duration.length() - 1);
            
            long seconds = Long.parseLong(value);
            
            switch (unit) {
                case "s":
                    return seconds;
                case "m":
                    return seconds * 60;
                case "h":
                    return seconds * 3600;
                case "d":
                    return seconds * 86400;
                default:
                    return seconds;
            }
        } catch (Exception e) {
            log.warn("Error parsing duration: {}", duration);
            return 86400; // Default to 1 day
        }
    }
}

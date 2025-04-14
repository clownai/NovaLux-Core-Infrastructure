package com.novalux.feedbackloop.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.feedbackloop.config.ContentRecommendationConfig;
import com.novalux.feedbackloop.model.ContentRecommendation;
import com.novalux.feedbackloop.model.TelemetryEvent;
import com.novalux.feedbackloop.model.PlayerInsight;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Service
@Slf4j
public class ContentRecommendationService {

    private final ContentRecommendationConfig config;
    private final ConcurrentHashMap<String, Map<String, Object>> playerPreferencesCache = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, Map<String, Object>> contentCatalogCache = new ConcurrentHashMap<>();

    @Autowired
    public ContentRecommendationService(ContentRecommendationConfig config) {
        this.config = config;
        initializeContentCatalog();
    }

    public void processTelemetryEvent(TelemetryEvent event) {
        if (!config.isEnabled()) {
            log.debug("Content recommendation is disabled, ignoring event: {}", event.getId());
            return;
        }

        String playerId = event.getPlayerId();
        if (playerId == null || playerId.isEmpty()) {
            log.debug("Event has no player ID, ignoring: {}", event.getId());
            return;
        }

        // Update player preferences cache
        updatePlayerPreferences(playerId, event);
    }
    
    public void processPlayerInsight(PlayerInsight insight) {
        if (!config.isEnabled()) {
            log.debug("Content recommendation is disabled, ignoring player insight: {}", insight.getId());
            return;
        }
        
        String playerId = insight.getPlayerId();
        if (playerId == null || playerId.isEmpty()) {
            log.debug("Insight has no player ID, ignoring: {}", insight.getId());
            return;
        }
        
        // Update player preferences with insight data
        updatePlayerPreferencesFromInsight(playerId, insight);
        
        // Generate recommendations based on updated preferences
        generateRecommendations(playerId);
    }

    private void updatePlayerPreferences(String playerId, TelemetryEvent event) {
        Map<String, Object> preferences = playerPreferencesCache.computeIfAbsent(playerId, k -> new HashMap<>());
        
        // Update event count
        int eventCount = (int) preferences.getOrDefault("eventCount", 0);
        preferences.put("eventCount", eventCount + 1);
        
        // Update last activity timestamp
        preferences.put("lastActivityTimestamp", event.getTimestamp());
        
        // Update first activity timestamp if not set
        if (!preferences.containsKey("firstActivityTimestamp")) {
            preferences.put("firstActivityTimestamp", event.getTimestamp());
        }
        
        // Update content interaction data if available
        if (event.getData() != null && event.getData().getParameters() != null) {
            try {
                // In a real implementation, this would parse the parameters to extract content interactions
                // For now, we'll simulate some content interactions
                if (Math.random() > 0.7) { // 30% chance of content interaction
                    String contentId = "content_" + (int)(Math.random() * 100);
                    String contentType = getRandomContentType();
                    double interactionStrength = 0.5 + (Math.random() * 0.5); // 0.5 to 1.0
                    
                    // Update content interactions
                    Map<String, Map<String, Object>> contentInteractions = 
                            (Map<String, Map<String, Object>>) preferences.computeIfAbsent("contentInteractions", k -> new HashMap<>());
                    
                    Map<String, Object> interaction = contentInteractions.computeIfAbsent(contentId, k -> new HashMap<>());
                    interaction.put("contentType", contentType);
                    interaction.put("lastInteraction", event.getTimestamp());
                    interaction.put("interactionCount", (int)interaction.getOrDefault("interactionCount", 0) + 1);
                    interaction.put("interactionStrength", interactionStrength);
                }
            } catch (Exception e) {
                log.warn("Error processing content interaction data: {}", e.getMessage());
            }
        }
    }
    
    private void updatePlayerPreferencesFromInsight(String playerId, PlayerInsight insight) {
        Map<String, Object> preferences = playerPreferencesCache.computeIfAbsent(playerId, k -> new HashMap<>());
        
        // Update insight data
        preferences.put("lastInsightTimestamp", insight.getTimestamp());
        preferences.put("lastInsightType", insight.getInsightType());
        preferences.put("lastInsightConfidence", insight.getConfidenceScore());
        
        // Update player segment based on insight type
        String segment;
        switch (insight.getInsightType()) {
            case "HIGH_ENGAGEMENT":
                segment = "ENGAGED";
                break;
            case "HIGH_SKILL":
                segment = "SKILLED";
                break;
            case "RISK_TAKER":
                segment = "ADVENTUROUS";
                break;
            case "SOCIAL_PLAYER":
                segment = "SOCIAL";
                break;
            case "CONTENT_EXPLORER":
                segment = "EXPLORER";
                break;
            case "PREMIUM_PLAYER":
                segment = "PREMIUM";
                break;
            case "TIME_INVESTOR":
                segment = "DEDICATED";
                break;
            default:
                segment = "BALANCED";
        }
        preferences.put("playerSegment", segment);
        
        // Update preference metrics if available
        if (insight.getMetrics() != null) {
            Map<String, Double> metrics = new HashMap<>();
            metrics.put("engagementScore", insight.getMetrics().getEngagementScore());
            metrics.put("skillLevel", insight.getMetrics().getSkillLevel());
            metrics.put("riskTolerance", insight.getMetrics().getRiskTolerance());
            metrics.put("socialInteraction", insight.getMetrics().getSocialInteraction());
            metrics.put("contentPreference", insight.getMetrics().getContentPreference());
            metrics.put("spendingPattern", insight.getMetrics().getSpendingPattern());
            metrics.put("timeInvestment", insight.getMetrics().getTimeInvestment());
            
            preferences.put("metrics", metrics);
        }
    }
    
    private void generateRecommendations(String playerId) {
        try {
            log.info("Generating content recommendations for player: {}", playerId);
            Map<String, Object> preferences = playerPreferencesCache.get(playerId);
            
            if (preferences == null) {
                log.warn("Player preferences not found for player: {}", playerId);
                return;
            }
            
            // Get player segment
            String playerSegment = (String) preferences.getOrDefault("playerSegment", "BALANCED");
            
            // Get player metrics
            Map<String, Double> metrics = (Map<String, Double>) preferences.getOrDefault("metrics", new HashMap<>());
            
            // Generate recommendations
            List<ContentRecommendation.RecommendedContent> recommendations = new ArrayList<>();
            
            // In a real implementation, this would use a recommendation algorithm
            // For now, we'll create simulated recommendations
            for (int i = 0; i < config.getMaxRecommendations(); i++) {
                if (recommendations.size() >= config.getMaxRecommendations()) {
                    break;
                }
                
                // Get a random content item
                String contentId = getRandomContentId();
                Map<String, Object> content = contentCatalogCache.get(contentId);
                
                if (content == null) {
                    continue;
                }
                
                // Calculate relevance score based on player segment and content tags
                double relevanceScore = calculateRelevanceScore(content, playerSegment, metrics);
                
                // Calculate novelty score based on player interactions
                double noveltyScore = calculateNoveltyScore(content, preferences);
                
                // Calculate overall score
                double overallScore = (relevanceScore * (1 - config.getNoveltyWeight())) + 
                                     (noveltyScore * config.getNoveltyWeight());
                
                // Create recommendation
                ContentRecommendation.RecommendedContent recommendation = ContentRecommendation.RecommendedContent.builder()
                        .contentId(contentId)
                        .contentType((String) content.get("contentType"))
                        .title((String) content.get("title"))
                        .relevanceScore(relevanceScore)
                        .noveltyScore(noveltyScore)
                        .overallScore(overallScore)
                        .tags((List<String>) content.get("tags"))
                        .build();
                
                recommendations.add(recommendation);
            }
            
            // Sort recommendations by overall score
            recommendations.sort((r1, r2) -> Double.compare(r2.getOverallScore(), r1.getOverallScore()));
            
            // Limit to max recommendations
            if (recommendations.size() > config.getMaxRecommendations()) {
                recommendations = recommendations.subList(0, config.getMaxRecommendations());
            }
            
            // Create the recommendation object
            ContentRecommendation recommendation = ContentRecommendation.builder()
                    .id(UUID.randomUUID().toString())
                    .playerId(playerId)
                    .timestamp(Instant.now())
                    .recommendations(recommendations)
                    .personalizedScore(calculatePersonalizedScore(recommendations))
                    .playerSegment(playerSegment)
                    .build();
            
            log.info("Generated content recommendation: {} for player: {}", recommendation.getId(), playerId);
            
            // In a real implementation, this would be published to Kafka
            // and potentially stored in Elasticsearch
            
        } catch (Exception e) {
            log.error("Error generating content recommendations: {}", playerId, e);
        }
    }
    
    private double calculateRelevanceScore(Map<String, Object> content, String playerSegment, Map<String, Double> metrics) {
        // In a real implementation, this would use a more sophisticated algorithm
        // For now, we'll use a simple heuristic
        
        // Base score
        double score = 0.5;
        
        // Adjust based on content-segment match
        List<String> targetSegments = (List<String>) content.getOrDefault("targetSegments", Collections.emptyList());
        if (targetSegments.contains(playerSegment)) {
            score += 0.3;
        }
        
        // Adjust based on metrics
        if (metrics != null && !metrics.isEmpty()) {
            String contentType = (String) content.get("contentType");
            
            switch (contentType) {
                case "GAME":
                    score += metrics.getOrDefault("skillLevel", 0.5) * 0.1;
                    score += metrics.getOrDefault("riskTolerance", 0.5) * 0.1;
                    break;
                case "STORY":
                    score += metrics.getOrDefault("contentPreference", 0.5) * 0.2;
                    break;
                case "EVENT":
                    score += metrics.getOrDefault("socialInteraction", 0.5) * 0.2;
                    break;
                case "ITEM":
                    score += metrics.getOrDefault("spendingPattern", 0.5) * 0.2;
                    break;
                case "QUEST":
                    score += metrics.getOrDefault("timeInvestment", 0.5) * 0.2;
                    break;
            }
        }
        
        // Add some randomness
        score += (Math.random() * 0.1) - 0.05;
        
        // Clamp to 0-1 range
        return Math.max(0, Math.min(1, score));
    }
    
    private double calculateNoveltyScore(Map<String, Object> content, Map<String, Object> preferences) {
        // In a real implementation, this would use a more sophisticated algorithm
        // For now, we'll use a simple heuristic
        
        // Check if player has interacted with this content
        Map<String, Map<String, Object>> contentInteractions = 
                (Map<String, Map<String, Object>>) preferences.getOrDefault("contentInteractions", Collections.emptyMap());
        
        String contentId = (String) content.get("id");
        if (contentInteractions.containsKey(contentId)) {
            // Player has interacted with this content before
            // Lower novelty based on interaction count
            Map<String, Object> interaction = contentInteractions.get(contentId);
            int interactionCount = (int) interaction.getOrDefault("interactionCount", 0);
            
            // Novelty decreases with more interactions
            return Math.max(0, 1.0 - (interactionCount * 0.2));
        }
        
        // Player has not interacted with this content
        return 1.0;
    }
    
    private double calculatePersonalizedScore(List<ContentRecommendation.RecommendedContent> recommendations) {
        if (recommendations.isEmpty()) {
            return 0.0;
        }
        
        // Calculate average overall score
        double sum = 0.0;
        for (ContentRecommendation.RecommendedContent recommendation : recommendations) {
            sum += recommendation.getOverallScore();
        }
        
        return sum / recommendations.size();
    }
    
    private void initializeContentCatalog() {
        // In a real implementation, this would load content from a database
        // For now, we'll create a simulated content catalog
        for (int i = 0; i < 100; i++) {
            String contentId = "content_" + i;
            String contentType = getRandomContentType();
            String title = generateTitle(contentType, i);
            List<String> tags = generateTags(contentType);
            List<String> targetSegments = generateTargetSegments();
            
            Map<String, Object> content = new HashMap<>();
            content.put("id", contentId);
            content.put("contentType", contentType);
            content.put("title", title);
            content.put("tags", tags);
            content.put("targetSegments", targetSegments);
            content.put("createdAt", Instant.now().minusSeconds((long)(Math.random() * 86400 * 30))); // Random time in last 30 days
            
            contentCatalogCache.put(contentId, content);
        }
        
        log.info("Initialized content catalog with {} items", contentCatalogCache.size());
    }
    
    private String getRandomContentType() {
        String[] types = {"GAME", "STORY", "EVENT", "ITEM", "QUEST"};
        return types[(int)(Math.random() * types.length)];
    }
    
    private String getRandomContentId() {
        return "content_" + (int)(Math.random() * 100);
    }
    
    private String generateTitle(String contentType, int index) {
        switch (contentType) {
            case "GAME":
                String[] gameNames = {"Neon", "Cyber", "Quantum", "Digital", "Virtual", "Synth", "Techno", "Crypto"};
                String[] gameSuffixes = {"Racer", "Hunter", "Warrior", "Defender", "Conquest", "Challenge", "Arena", "Showdown"};
                return gameNames[index % gameNames.length] + " " + gameSuffixes[index % gameSuffixes.length];
            case "STORY":
                String[] storyPrefixes = {"The", "A", "Chronicles of", "Tales from", "Legends of", "Secrets of", "Rise of", "Fall of"};
                String[] storySubjects = {"Neon City", "Cyber District", "Digital Wasteland", "Virtual Reality", "Synthetic Dreams", "Techno Future", "Crypto Revolution", "AI Uprising"};
                return storyPrefixes[index % storyPrefixes.length] + " " + storySubjects[index % storySubjects.length];
            case "EVENT":
                String[] eventTypes = {"Tournament", "Competition", "Festival", "Gathering", "Showdown", "Challenge", "Contest", "Celebration"};
                String[] eventThemes = {"Neon", "Cyber", "Digital", "Virtual", "Synthetic", "Techno", "Crypto", "AI"};
                return eventThemes[index % eventThemes.length] + " " + eventTypes[index % eventTypes.length];
            case "ITEM":
                String[] itemTypes = {"Weapon", "Armor", "Gadget", "Tool", "Vehicle", "Accessory", "Implant", "Enhancement"};
                String[] itemQualities = {"Rare", "Legendary", "Unique", "Prototype", "Experimental", "Advanced", "Futuristic", "Alien"};
                return itemQualities[index % itemQualities.length] + " " + itemTypes[index % itemTypes.length];
            case "QUEST":
                String[] questTypes = {"Mission", "Heist", "Infiltration", "Extraction", "Sabotage", "Rescue", "Assassination", "Investigation"};
                String[] questTargets = {"Corporation", "Gang", "AI", "Government", "Underground", "Syndicate", "Resistance", "Cult"};
                return questTypes[index % questTypes.length] + ": " + questTargets[index % questTargets.length];
            default:
                return "Content " + index;
        }
    }
    
    private List<String> generateTags(String contentType) {
        List<String> tags = new ArrayList<>();
        
        // Add content type as tag
        tags.add(contentType);
        
        // Add random tags
        String[] commonTags = {"CYBERPUNK", "NEON", "FUTURISTIC", "DYSTOPIAN", "TECH", "NOIR", "RETRO", "CORPORATE"};
        for (int i = 0; i < 3; i++) {
            if (Math.random() > 0.5) {
                tags.add(commonTags[(int)(Math.random() * commonTags.length)]);
            }
        }
        
        // Add content-specific tags
        switch (contentType) {
            case "GAME":
                String[] gameTags = {"ACTION", "STRATEGY", "PUZZLE", "RACING", "SHOOTER", "RPG", "SIMULATION", "MULTIPLAYER"};
                tags.add(gameTags[(int)(Math.random() * gameTags.length)]);
                break;
            case "STORY":
                String[] storyTags = {"NARRATIVE", "LORE", "BACKGROUND", "CHARACTER", "PLOT", "WORLDBUILDING", "FICTION", "CANON"};
                tags.add(storyTags[(int)(Math.random() * storyTags.length)]);
                break;
            case "EVENT":
                String[] eventTags = {"TIMED", "COMPETITIVE", "COOPERATIVE", "SEASONAL", "SPECIAL", "LIMITED", "RECURRING", "COMMUNITY"};
                tags.add(eventTags[(int)(Math.random() * eventTags.length)]);
                break;
            case "ITEM":
                String[] itemTags = {"EQUIPMENT", "CONSUMABLE", "COLLECTIBLE", "COSMETIC", "FUNCTIONAL", "RARE", "CRAFTABLE", "UPGRADABLE"};
                tags.add(itemTags[(int)(Math.random() * itemTags.length)]);
                break;
            case "QUEST":
                String[] questTags = {"MAIN", "SIDE", "REPEATABLE", "CHAIN", "DAILY", "WEEKLY", "FACTION", "HIDDEN"};
                tags.add(questTags[(int)(Math.random() * questTags.length)]);
                break;
        }
        
        return new ArrayList<>(new HashSet<>(tags)); // Remove duplicates
    }
    
    private List<String> generateTargetSegments() {
        List<String> segments = new ArrayList<>();
        String[] allSegments = {"ENGAGED", "SKILLED", "ADVENTUROUS", "SOCIAL", "EXPLORER", "PREMIUM", "DEDICATED", "BALANCED"};
        
        // Add 1-3 random segments
        int count = 1 + (int)(Math.random() * 3);
        for (int i = 0; i < count; i++) {
            segments.add(allSegments[(int)(Math.random() * allSegments.length)]);
        }
        
        return new ArrayList<>(new HashSet<>(segments)); // Remove duplicates
    }
}

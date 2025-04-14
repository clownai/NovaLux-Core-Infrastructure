package com.novalux.feedbackloop.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.feedbackloop.config.PlayerBehaviorConfig;
import com.novalux.feedbackloop.config.GameBalanceConfig;
import com.novalux.feedbackloop.config.ContentRecommendationConfig;
import com.novalux.feedbackloop.config.ResponsibleGamingConfig;
import com.novalux.feedbackloop.config.KafkaConfig;
import com.novalux.feedbackloop.config.ElasticsearchConfig;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/")
@Slf4j
public class HealthController {

    private final PlayerBehaviorConfig playerBehaviorConfig;
    private final GameBalanceConfig gameBalanceConfig;
    private final ContentRecommendationConfig contentRecommendationConfig;
    private final ResponsibleGamingConfig responsibleGamingConfig;
    private final KafkaConfig kafkaConfig;
    private final ElasticsearchConfig elasticsearchConfig;

    @Autowired
    public HealthController(
            PlayerBehaviorConfig playerBehaviorConfig,
            GameBalanceConfig gameBalanceConfig,
            ContentRecommendationConfig contentRecommendationConfig,
            ResponsibleGamingConfig responsibleGamingConfig,
            KafkaConfig kafkaConfig,
            ElasticsearchConfig elasticsearchConfig) {
        this.playerBehaviorConfig = playerBehaviorConfig;
        this.gameBalanceConfig = gameBalanceConfig;
        this.contentRecommendationConfig = contentRecommendationConfig;
        this.responsibleGamingConfig = responsibleGamingConfig;
        this.kafkaConfig = kafkaConfig;
        this.elasticsearchConfig = elasticsearchConfig;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        log.debug("Health check requested");
        
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.ok(health);
    }

    @GetMapping("/ready")
    public ResponseEntity<Map<String, Object>> ready() {
        log.debug("Readiness check requested");
        
        Map<String, Object> ready = new HashMap<>();
        ready.put("status", "READY");
        ready.put("timestamp", System.currentTimeMillis());
        
        // Add component status
        Map<String, Object> components = new HashMap<>();
        
        components.put("playerBehavior", Map.of(
            "enabled", playerBehaviorConfig.isEnabled(),
            "status", "UP"
        ));
        
        components.put("gameBalance", Map.of(
            "enabled", gameBalanceConfig.isEnabled(),
            "status", "UP"
        ));
        
        components.put("contentRecommendation", Map.of(
            "enabled", contentRecommendationConfig.isEnabled(),
            "status", "UP"
        ));
        
        components.put("responsibleGaming", Map.of(
            "enabled", responsibleGamingConfig.isEnabled(),
            "status", "UP"
        ));
        
        components.put("kafka", Map.of(
            "bootstrapServers", kafkaConfig.getBootstrapServers(),
            "status", "UP"
        ));
        
        components.put("elasticsearch", Map.of(
            "hosts", elasticsearchConfig.getHosts(),
            "status", "UP"
        ));
        
        ready.put("components", components);
        
        return ResponseEntity.ok(ready);
    }
}

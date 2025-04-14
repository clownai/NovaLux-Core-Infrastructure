package com.novalux.adaptivecore.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.adaptivecore.config.FeedbackLoopConfig;
import com.novalux.adaptivecore.config.AIIntegrationConfig;
import com.novalux.adaptivecore.config.KafkaConfig;
import com.novalux.adaptivecore.config.ElasticsearchConfig;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/")
@Slf4j
public class HealthController {

    private final FeedbackLoopConfig feedbackLoopConfig;
    private final AIIntegrationConfig aiIntegrationConfig;
    private final KafkaConfig kafkaConfig;
    private final ElasticsearchConfig elasticsearchConfig;

    @Autowired
    public HealthController(FeedbackLoopConfig feedbackLoopConfig,
                           AIIntegrationConfig aiIntegrationConfig,
                           KafkaConfig kafkaConfig,
                           ElasticsearchConfig elasticsearchConfig) {
        this.feedbackLoopConfig = feedbackLoopConfig;
        this.aiIntegrationConfig = aiIntegrationConfig;
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
        
        components.put("feedbackLoop", Map.of(
            "enabled", feedbackLoopConfig.isEnabled(),
            "status", "UP"
        ));
        
        components.put("aiIntegration", Map.of(
            "modelServerUrl", aiIntegrationConfig.getModelServerUrl(),
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

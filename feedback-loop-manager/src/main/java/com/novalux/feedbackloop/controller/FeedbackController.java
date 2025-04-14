package com.novalux.feedbackloop.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.feedbackloop.service.PlayerBehaviorService;
import com.novalux.feedbackloop.service.GameBalanceService;
import com.novalux.feedbackloop.service.ContentRecommendationService;
import com.novalux.feedbackloop.service.ResponsibleGamingService;
import com.novalux.feedbackloop.model.TelemetryEvent;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1")
@Slf4j
public class FeedbackController {

    private final PlayerBehaviorService playerBehaviorService;
    private final GameBalanceService gameBalanceService;
    private final ContentRecommendationService contentRecommendationService;
    private final ResponsibleGamingService responsibleGamingService;

    @Autowired
    public FeedbackController(
            PlayerBehaviorService playerBehaviorService,
            GameBalanceService gameBalanceService,
            ContentRecommendationService contentRecommendationService,
            ResponsibleGamingService responsibleGamingService) {
        this.playerBehaviorService = playerBehaviorService;
        this.gameBalanceService = gameBalanceService;
        this.contentRecommendationService = contentRecommendationService;
        this.responsibleGamingService = responsibleGamingService;
    }

    @PostMapping("/telemetry")
    public ResponseEntity<Map<String, Object>> processTelemetry(@RequestBody TelemetryEvent event) {
        log.info("Received telemetry event via API: {}", event.getId());
        
        // Generate ID if not provided
        if (event.getId() == null || event.getId().isEmpty()) {
            event.setId(UUID.randomUUID().toString());
        }
        
        // Process the event through all services
        playerBehaviorService.processTelemetryEvent(event);
        gameBalanceService.processTelemetryEvent(event);
        contentRecommendationService.processTelemetryEvent(event);
        responsibleGamingService.processTelemetryEvent(event);
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "success");
        response.put("id", event.getId());
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getStatus() {
        log.debug("Status check requested");
        
        Map<String, Object> status = new HashMap<>();
        status.put("status", "operational");
        status.put("timestamp", System.currentTimeMillis());
        
        // Add component status
        Map<String, Object> components = new HashMap<>();
        
        components.put("playerBehavior", Map.of(
            "status", "operational"
        ));
        
        components.put("gameBalance", Map.of(
            "status", "operational"
        ));
        
        components.put("contentRecommendation", Map.of(
            "status", "operational"
        ));
        
        components.put("responsibleGaming", Map.of(
            "status", "operational"
        ));
        
        status.put("components", components);
        
        return ResponseEntity.ok(status);
    }
}

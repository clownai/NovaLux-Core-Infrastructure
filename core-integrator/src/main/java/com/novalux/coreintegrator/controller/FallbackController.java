package com.novalux.coreintegrator.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/fallback")
@Slf4j
public class FallbackController {

    @GetMapping("/adaptive-core")
    public ResponseEntity<Map<String, Object>> adaptiveCoreFallback() {
        log.warn("Fallback triggered for Adaptive Core service");
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "error");
        response.put("message", "Adaptive Core service is currently unavailable");
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(503).body(response);
    }
    
    @GetMapping("/feedback-loop")
    public ResponseEntity<Map<String, Object>> feedbackLoopFallback() {
        log.warn("Fallback triggered for Feedback Loop Manager service");
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "error");
        response.put("message", "Feedback Loop Manager service is currently unavailable");
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(503).body(response);
    }
    
    @GetMapping("/game-service")
    public ResponseEntity<Map<String, Object>> gameServiceFallback() {
        log.warn("Fallback triggered for Game service");
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "error");
        response.put("message", "Game service is currently unavailable");
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(503).body(response);
    }
    
    @GetMapping("/player-service")
    public ResponseEntity<Map<String, Object>> playerServiceFallback() {
        log.warn("Fallback triggered for Player service");
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "error");
        response.put("message", "Player service is currently unavailable");
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(503).body(response);
    }
    
    @GetMapping("/analytics-service")
    public ResponseEntity<Map<String, Object>> analyticsServiceFallback() {
        log.warn("Fallback triggered for Analytics service");
        
        Map<String, Object> response = new HashMap<>();
        response.put("status", "error");
        response.put("message", "Analytics service is currently unavailable");
        response.put("timestamp", System.currentTimeMillis());
        
        return ResponseEntity.status(503).body(response);
    }
}

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
@RequestMapping("/")
@Slf4j
public class HealthController {

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
        
        components.put("gateway", Map.of(
            "status", "UP"
        ));
        
        components.put("serviceDiscovery", Map.of(
            "status", "UP"
        ));
        
        components.put("circuitBreaker", Map.of(
            "status", "UP"
        ));
        
        ready.put("components", components);
        
        return ResponseEntity.ok(ready);
    }
}

package com.novalux.adaptivecore.controller;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import lombok.extern.slf4j.Slf4j;

import com.novalux.adaptivecore.model.OptimizationEvent;
import com.novalux.adaptivecore.service.FeedbackLoopService;
import com.novalux.adaptivecore.kafka.OptimizationProducer;

@RestController
@RequestMapping("/api/v1/optimizations")
@Slf4j
public class OptimizationController {

    private final FeedbackLoopService feedbackLoopService;
    private final OptimizationProducer optimizationProducer;

    @Autowired
    public OptimizationController(FeedbackLoopService feedbackLoopService, 
                                 OptimizationProducer optimizationProducer) {
        this.feedbackLoopService = feedbackLoopService;
        this.optimizationProducer = optimizationProducer;
    }

    @PostMapping
    public ResponseEntity<String> processOptimization(@RequestBody OptimizationEvent event) {
        log.info("Received optimization request: {}", event.getId());
        
        // Publish the event to Kafka
        optimizationProducer.sendOptimizationEvent(event);
        
        // Process the optimization
        boolean success = feedbackLoopService.processOptimizationEvent(event);
        
        if (success) {
            return ResponseEntity.ok("Optimization processed successfully");
        } else {
            return ResponseEntity.accepted().body("Optimization queued for processing");
        }
    }
}

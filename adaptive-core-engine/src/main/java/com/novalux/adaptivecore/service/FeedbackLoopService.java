package com.novalux.adaptivecore.service;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.adaptivecore.config.FeedbackLoopConfig;
import com.novalux.adaptivecore.model.OptimizationEvent;
import com.novalux.adaptivecore.model.ParameterAdjustment;

import java.time.Instant;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

@Service
@Slf4j
public class FeedbackLoopService {

    private final FeedbackLoopConfig config;
    private final ConcurrentHashMap<String, OptimizationEvent> pendingOptimizations = new ConcurrentHashMap<>();
    private final AtomicInteger activeOptimizations = new AtomicInteger(0);

    @Autowired
    public FeedbackLoopService(FeedbackLoopConfig config) {
        this.config = config;
    }

    public boolean processOptimizationEvent(OptimizationEvent event) {
        if (!config.isEnabled()) {
            log.info("Feedback loop is disabled, ignoring optimization event: {}", event.getId());
            return false;
        }

        if (event.getConfidenceScore() < config.getOptimizationThreshold()) {
            log.info("Optimization event {} below threshold ({} < {}), ignoring", 
                    event.getId(), event.getConfidenceScore(), config.getOptimizationThreshold());
            return false;
        }

        if (activeOptimizations.get() >= config.getMaxConcurrentOptimizations()) {
            log.warn("Maximum concurrent optimizations reached ({}), queuing event: {}", 
                    config.getMaxConcurrentOptimizations(), event.getId());
            pendingOptimizations.put(event.getId(), event);
            return false;
        }

        log.info("Processing optimization event: {}", event.getId());
        activeOptimizations.incrementAndGet();
        
        try {
            // Apply the optimization
            ParameterAdjustment adjustment = createParameterAdjustment(event);
            applyParameterAdjustment(adjustment);
            
            log.info("Successfully applied parameter adjustment: {}", adjustment.getId());
            return true;
        } catch (Exception e) {
            log.error("Failed to apply optimization: {}", event.getId(), e);
            return false;
        } finally {
            activeOptimizations.decrementAndGet();
            processPendingOptimizations();
        }
    }

    private ParameterAdjustment createParameterAdjustment(OptimizationEvent event) {
        return ParameterAdjustment.builder()
                .id(UUID.randomUUID().toString())
                .type("PARAMETER_ADJUSTMENT")
                .timestamp(Instant.now())
                .targetComponent(event.getTargetComponent())
                .targetParameter(event.getTargetParameter())
                .previousValue(event.getCurrentValue())
                .newValue(event.getSuggestedValue())
                .optimizationEventId(event.getId())
                .appliedBy("adaptive-core")
                .status("PENDING")
                .build();
    }

    private void applyParameterAdjustment(ParameterAdjustment adjustment) {
        // In a real implementation, this would apply the adjustment to the target component
        // For now, we'll just simulate the application
        log.info("Applying parameter adjustment: {} -> {} for {}.{}", 
                adjustment.getPreviousValue(), 
                adjustment.getNewValue(), 
                adjustment.getTargetComponent(), 
                adjustment.getTargetParameter());
        
        // Simulate some processing time
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        adjustment.setStatus("APPLIED");
        adjustment.setAppliedAt(Instant.now());
    }

    private void processPendingOptimizations() {
        if (pendingOptimizations.isEmpty() || 
            activeOptimizations.get() >= config.getMaxConcurrentOptimizations()) {
            return;
        }

        // Process one pending optimization
        String nextEventId = pendingOptimizations.keySet().iterator().next();
        OptimizationEvent event = pendingOptimizations.remove(nextEventId);
        
        if (event != null) {
            log.info("Processing pending optimization event: {}", event.getId());
            processOptimizationEvent(event);
        }
    }
}

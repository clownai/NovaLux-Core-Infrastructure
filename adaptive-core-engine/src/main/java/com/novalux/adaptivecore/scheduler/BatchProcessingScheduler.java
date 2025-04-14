package com.novalux.adaptivecore.scheduler;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.adaptivecore.service.AIIntegrationService;
import com.novalux.adaptivecore.config.FeedbackLoopConfig;

@Component
@Slf4j
public class BatchProcessingScheduler {

    private final AIIntegrationService aiIntegrationService;
    private final FeedbackLoopConfig feedbackLoopConfig;

    @Autowired
    public BatchProcessingScheduler(AIIntegrationService aiIntegrationService,
                                   FeedbackLoopConfig feedbackLoopConfig) {
        this.aiIntegrationService = aiIntegrationService;
        this.feedbackLoopConfig = feedbackLoopConfig;
    }

    @Scheduled(fixedDelayString = "5000") // Process every 5 seconds
    public void processBatch() {
        if (!feedbackLoopConfig.isEnabled()) {
            return;
        }
        
        log.debug("Scheduled batch processing triggered");
        aiIntegrationService.processBatch();
    }
}

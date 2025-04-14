package com.novalux.feedbackloop.kafka;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;

import com.novalux.feedbackloop.model.TelemetryEvent;
import com.novalux.feedbackloop.service.PlayerBehaviorService;
import com.novalux.feedbackloop.service.GameBalanceService;
import com.novalux.feedbackloop.service.ContentRecommendationService;
import com.novalux.feedbackloop.service.ResponsibleGamingService;
import com.novalux.feedbackloop.config.KafkaConfig;

@Component
@Slf4j
public class TelemetryConsumer {

    private final PlayerBehaviorService playerBehaviorService;
    private final GameBalanceService gameBalanceService;
    private final ContentRecommendationService contentRecommendationService;
    private final ResponsibleGamingService responsibleGamingService;
    private final KafkaConfig kafkaConfig;

    @Autowired
    public TelemetryConsumer(
            PlayerBehaviorService playerBehaviorService,
            GameBalanceService gameBalanceService,
            ContentRecommendationService contentRecommendationService,
            ResponsibleGamingService responsibleGamingService,
            KafkaConfig kafkaConfig) {
        this.playerBehaviorService = playerBehaviorService;
        this.gameBalanceService = gameBalanceService;
        this.contentRecommendationService = contentRecommendationService;
        this.responsibleGamingService = responsibleGamingService;
        this.kafkaConfig = kafkaConfig;
    }

    @KafkaListener(
            topics = "#{kafkaConfig.topics.input}",
            groupId = "#{kafkaConfig.consumerGroup}",
            containerFactory = "kafkaListenerContainerFactory"
    )
    public void consume(TelemetryEvent event) {
        try {
            log.debug("Received telemetry event: {}", event.getId());
            
            // Process the event through all services
            playerBehaviorService.processTelemetryEvent(event);
            gameBalanceService.processTelemetryEvent(event);
            contentRecommendationService.processTelemetryEvent(event);
            responsibleGamingService.processTelemetryEvent(event);
            
            log.debug("Processed telemetry event: {}", event.getId());
        } catch (Exception e) {
            log.error("Error processing telemetry event: {}", event.getId(), e);
        }
    }
}
